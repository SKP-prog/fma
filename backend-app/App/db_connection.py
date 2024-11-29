import pymongo
from pymongo import MongoClient
import pandas as pd
from math import ceil


class DB:
    def __init__(self, host=None, port=None, dbname=None):
        client = MongoClient(host, port)
        self.db = client[dbname]
        self.table = self.db['Main']

    def add_row(self, table_name: str, row_entry: dict):
        """
        add row to collection (TABLE)
        table_name: table name
        row_entry: dictionary for the table {column: value}
        """
        self.db[table_name].insert_one(row_entry)

    def show_table(self, table_name: str, flt: dict = None):
        """
        table_name: Table Collection
        flt: dictionary filter
        """
        if flt is None:
            flt = {}
        df = pd.DataFrame(list(self.db[table_name].find(flt)))
        if not df.empty:
            del df["_id"]
        return df

    def get_figurine(self, jan_code: int = None, page_num=1, page_size=20):
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

        return df[["JAN_code", "img_url", "title", "page_url", "maker", "release_date"]], meta_data
