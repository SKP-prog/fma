import pymongo
from pymongo import MongoClient
import pandas as pd
from math import ceil


class DB:
    def __init__(self, host=None, port=None, dbname=None, table_name=None):
        client = MongoClient(host, port)
        self.db = client[dbname]
        self.table = self.db["Main" if table_name is None else table_name]

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

    def get_figurine(self, page_num=1, page_size=20):
        self.table = self.db["Main"]
        # TODO: add method to filter for individual figurine
        # Create Filter Aggregate. Get unique JAN_code with all its required fields
        group = {
            "$group": {
                # Name each column to its new column name
                "_id": {"JAN_code": "$JAN_code"},
                "JAN_code": {"$first": "$JAN_code"},
                "img_url": {"$first": "$img_url"},
                "title": {"$first": "$title"},
                "page_url": {"$first": "$page_url"},
                "maker": {"$first": "$maker"},
                "release_date": {"$first": "$release_date"},
            }
        }
        sort = {
            "$sort": {
                "release_date": pymongo.DESCENDING,
                "JAN_code": pymongo.DESCENDING
            }
        }

        pipeline = [
            {
                "$facet": {
                    "data": [
                        group,
                        sort,
                        {"$skip": (page_num - 1) * page_size},
                        {"$limit": page_size}
                    ],
                    "metadata": [
                        group,
                        {"$count": "totalRecords"}
                    ],
                }
            }
        ]
        # if jan_code is not None:
        #     pipeline = [{"$match": {"JAN_code": jan_code}}] + pipeline

        # Get Mongo Results
        mongo_results = list(self.table.aggregate(pipeline))[0]
        data = mongo_results['data']

        # Add Meta Data
        meta_data = mongo_results['metadata'][0]
        meta_data["pageSize"] = page_size
        meta_data["totalPages"] = ceil(meta_data["totalRecords"] / page_size)

        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(columns=["JAN_code", "img_url", "title", "page_url", "maker", "release_date"])

        # Check if figure is in Favourite List
        self.table = self.db["Favourite"]
        fav_list = pd.DataFrame(list(self.table.find({})))
        # Check dataframe if it has item in fav list
        df['is_fav'] = df['JAN_code'].isin(fav_list['JAN_code']).astype(int)

        return df[["JAN_code", "img_url", "title", "page_url", "maker", "release_date", "is_fav"]], meta_data

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