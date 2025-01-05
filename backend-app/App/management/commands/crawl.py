import pickle

from django.core.management.base import BaseCommand, CommandError
# from App.utils.crawler import get_product_urls
from App.utils.crawler import HLJCrawler


class Command(BaseCommand):
    help = 'Crawl HLJ website to extract figure details and throw into MongoDB'

    def add_arguments(self, parser):
        parser.add_argument('--dev', type=int, default=0)

    def handle(self, *args, **options):

        # Run Extraction Script
        if options["dev"] < 2:
            c = HLJCrawler(is_headless=options["dev"] == 0)
            fr_df = c.get_latest_release("All Future Release")

            if options["dev"] == 1:
                with open("data.pickle", "wb") as wf:
                    pickle.dump(fr_df, wf)
        else:
            with open("data.pickle", "rb") as rf:
                fr_df = pickle.load(rf)

        # Run Update Database Script
        if options["dev"] == 0 or options["dev"] == 2:
            self._update_db(fr_df)

        self.stdout.write(self.style.SUCCESS(f'Ran Process in Mode: DEV={options["dev"]}'))

    def _update_db(self, new_df):
        """
        Compare new_df with database df and add those that does not exist in database df.

        :param DataFrame new_df: Dataframe to update MongoDb.
        """

