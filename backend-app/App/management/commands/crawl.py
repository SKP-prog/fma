import pickle

import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from App.utils.crawler import HLJCrawler
from App.utils.db_connection import DB


class Command(BaseCommand):
    help = 'Crawl HLJ website to extract figure details and throw into MongoDB'

    def add_arguments(self, parser):
        parser.add_argument('--dev', type=int, default=0)

    def handle(self, *args, **options):
        # Run Extraction Script
        if options["dev"] < 2:
            c = HLJCrawler(is_headless=options["dev"] == 0)
            fr_df = c.get_latest_release("All Future Release")
            po_df = c.get_latest_release("In Stock")
            df = pd.concat([fr_df, po_df])

            if options["dev"] == 1:
                with open("data.pickle", "wb") as wf:
                    pickle.dump(df, wf)
        else:
            with open("data.pickle", "rb") as rf:
                df = pickle.load(rf)

        # Run Update Database Script
        fig_update, pri_update = 0, 0
        if options["dev"] == 0 or options["dev"] == 2:
            fig_update, pri_update = self._update_db(df)

        self.stdout.write(self.style.SUCCESS(f'Ran Process in Mode: DEV={options["dev"]}. '
                                             f'Number of Figures Added: {fig_update}, '
                                             f'Number of Prices Added: {pri_update}'))

    def _update_db(self, new_df):
        """
        Compare new_df with database df and add those that does not exist in database df.

        :param DataFrame new_df: Dataframe to update MongoDb.
        :return: Respectively, number of Figure entries added, number of price entries added
        """
        # TODO: I want to remove table name from DB class. since its just use to initialize connection
        #  we can do the selection of table in the actions instead of init.
        m_db = DB(host="localhost", port=27017, dbname="HLJ", table_name="figurine")

        # Convert Extracted Data into appropriate Dataframes to upload to mongodb
        f_df, p_df = self._process_df(new_df)

        # Get the diff between database and extracted data
        db_df = m_db.show_table()
        f_df = self._get_diff(db_df, f_df)
        # process price
        m_db.set_table("price")
        db_df = m_db.show_table()
        p_df = self._get_diff(db_df, p_df, keys=["jan_code", "price"])

        # Update Database
        if not f_df.empty:
            m_db.add_rows(f_df.to_dict("records"), "figurine")  # add figurine
        if not p_df.empty:
            m_db.add_rows(p_df.to_dict("records"), "price")  # add prices

        return f_df.shape[0], p_df.shape[0]

    @staticmethod
    def _process_df(df: pd.DataFrame) -> tuple:
        """
        Convert Dataframe from all data into specific data tables to be inserted into the Figurine and Price Tables.

        :param DataFrame df: dataframe to be split into two datatables
        :return: a tuple of Figurine Dataframe and Price Dataframe respectively
        """
        # Get all figurine details
        # - title
        # - image_url
        # - brand
        # - product_url
        # - jan_code
        # - release_date
        # - date_added
        f_cols = ["title", "image_url", "brand", "product_url", "jan_code", "release_date"]
        f_df = df[f_cols].copy()
        f_df.drop_duplicates(inplace=True, ignore_index=True, subset=["jan_code"])

        # Get all Price details
        # - currency
        # - price
        # - date_added
        # - jan_code
        p_cols = ["jan_code", "price", "currency"]
        p_df = df[p_cols].copy()
        p_df.drop_duplicates(inplace=True, ignore_index=True)

        # Add date_added
        f_df['date_added'] = datetime.now()
        p_df['date_added'] = datetime.now()

        return f_df, p_df

    @staticmethod
    def _get_diff(db_df, ex_df, keys=None) -> pd.DataFrame:
        """
        Compare db_df and ex_df, return entries that are not in db_df.
        :param DataFrame db_df: Dataframe from Mongo Database
        :param DataFrame ex_df: Dataframe that was extracted by crawler
        :param list keys: the primary keys use to identify a unique row
        :return: Dataframe in ex_df but not in db_df
        """
        if keys is None:
            keys = ["jan_code"]

        if db_df.empty:
            db_df = pd.DataFrame(columns=ex_df.columns)

        out_df = pd.merge(db_df, ex_df, how="outer", left_on=keys, right_on=keys, indicator=True)
        out_df = out_df.loc[(out_df["_merge"] == "right_only")]
        # Replace empty columns with the values to be updated
        for col in db_df.columns:
            if col in keys:
                continue
            out_df[col] = out_df[col + "_y"]

        return out_df[db_df.columns]


