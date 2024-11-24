from pymongo import MongoClient
import pandas as pd


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

    def get_figurine(self, jan_code=None):
        flt = {}
        if jan_code is not None:
            flt["JAN_code"] = jan_code

        df = pd.DataFrame(list(self.table.find(flt)))
        df.drop_duplicates(subset=["JAN_code"], inplace=True)
        return df[["JAN_code", "img_url", "title", "page_url", "maker", "release_date"]]

