import pymongo
from pymongo import MongoClient
import pandas as pd
from math import ceil
from datetime import datetime


class DB:
    def __init__(self, host=None, port=None, dbname=None, table_name=None):
        """
        Connection to Mongo DB
        :param str host: url to local/remote mongo db
        :param int port: Port number that the mongo db is using
        :param str dbname: Name of database you want to connect to
        :param str table_name: Initial Collection you want to connect to. This can be changed later.
        """
        client = MongoClient(host, port)
        self.db = client[dbname]
        self.table = self.db["Main" if table_name is None else table_name]

    def get_figurine(self, page_num=1, page_size=20, flt=None) -> tuple:
        """
        Get dataframe of figurines. by using page number and filter

        :param int page_num: we use pagination. this returns the data at this page number
        :param int page_size: the number of entries to show in a single page
        :param dict flt: a dictionary to filter using certain fields
        :return: two dataframes respectively, figurine extracted and metadata
        """
        if flt is None:
            flt = {}

        match = {
            "$match": flt
        }
        sort = {
            "$sort": {
                "release_date": pymongo.DESCENDING,
                "title": pymongo.DESCENDING,
            }
        }
        pipeline = [
            {
                "$facet": {
                    "data": [
                        match,
                        sort,
                        {"$skip": (page_num - 1) * page_size},
                        {"$limit": page_size}
                    ],
                    "metadata": [
                        match,
                        {"$count": "totalRecords"}
                    ]
                }
            }
        ]

        # Get Mongo Results
        # mongo_results = list(self.db["figurine"].aggregate(pipeline))[0]
        mongo_results = list(self.db["figurine"].aggregate(pipeline))[0]
        data = mongo_results['data']

        cols = ["jan_code", "image_url", "title", "product_url", "brand", "release_date", "is_preorder"]

        # Add Meta Data
        if len(mongo_results['metadata']) > 0:
            meta_data = mongo_results['metadata'][0]
            meta_data["pageSize"] = page_size
            meta_data['totalPages'] = ceil(meta_data["totalRecords"] / page_size)
        else:
            meta_data = {
                "pageSize": 0,
                "totalPages": 0
            }

        df = pd.DataFrame(data)

        if df.empty:
            return pd.DataFrame(columns=cols), meta_data
        else:
            # Check if preorder
            df["is_preorder"] = df["release_date"] > datetime.now()

        return df[cols], meta_data

    def set_table(self, table_name: str):
        """
        Just set the table name for other functions to access
        """
        self.table = self.db[table_name]

    def add_row(self, row_entry: dict):
        """
        add row to collection (TABLE)
        row_entry: dictionary for the table {column: value}
        """
        self.table.insert_one(row_entry)

    def add_rows(self, entries: list, table_name: str):
        """
        Add Multiple Rows to database

        :param list entries: A list of dictionary to insert to database
        :param str table_name: table name to update
        """
        assert hasattr(self.db, table_name), f"Unable to identify collection with name: {table_name}"
        self.db[table_name].insert_many(entries)

    def del_row(self, row_entry: dict):
        """
        remove row from collection (Table)
        row_entry: dictionary to filter a single entry to delete {column: value}
        """
        self.table.delete_one(row_entry)

    def show_table(self, flt: dict = None):
        """
        table_name: Table Collection
        flt: dictionary filter
        """
        if flt is None:
            flt = {}
        df = pd.DataFrame(list(self.table.find(flt)))
        if not df.empty:
            del df["_id"]
        return df

    def get_favs(self, page_num=1, page_size=20):
        lookup = {
            "$lookup": {
                "from": "Main",
                "localField": "JAN_code",
                "foreignField": "JAN_code",
                "as": "all_details"
            }
        }
        add_fields = {
            "$addFields": {
                "title": {"$first": "$all_details.title"},
                "img_url": {"$first": "$all_details.img_url"},
                "page_url": {"$first": "$all_details.page_url"},
                "maker": {"$first": "$all_details.maker"},
                "release_date": {"$first": "$all_details.release_date"},
            }
        }
        pipeline = [
            {
                "$facet": {
                    "data": [
                        lookup,
                        add_fields,
                        {"$skip": (page_num - 1) * page_size},
                        {"$limit": page_size}
                    ],
                    "metadata": [
                        lookup,
                        {"$count": "totalRecords"}
                    ]
                }
            }
        ]

        # Extract Data From MongoDB
        self.table = self.db["Favourite"]
        mongo_results = list(self.table.aggregate(pipeline))[0]
        data = mongo_results['data']

        # Add Meta Data
        meta_data = mongo_results['metadata'][0]
        meta_data["pageSize"] = page_size
        meta_data["totalPages"] = ceil(meta_data["totalRecords"] / page_size)

        # Get All Results
        df = pd.DataFrame(data)
        df["is_fav"] = True

        return df[["JAN_code", "img_url", "title", "page_url", "maker", "release_date", "is_fav"]], meta_data