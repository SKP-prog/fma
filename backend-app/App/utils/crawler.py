"""
    Crawls HLJ Websites and returns a dataframe.
    That's it. It does not interact with the Database
"""
import json
from datetime import datetime
from typing import Literal
from urllib.parse import urlencode

import pandas as pd
import tqdm
from bs4 import BeautifulSoup

# Custom Classes
from App.utils.selenium_driver import Selenium

HEAD = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/130.0.0.0 Safari/537.36"
}
URL = "https://www.hlj.com"


class HLJCrawler:
    def __init__(self, is_headless=False):
        """
        Class to crawl Hobby Link Japan Website. Use get_release_date() method to extract latest figure details

        :param bool is_headless: Determine to run Selenium with Browser spawning (is headless)
                                or browser not appearing (none headless)
        """
        self.s = Selenium(is_headless=is_headless)
        self.d = self.s.get_driver()

    def get_latest_release(self, stock_type: Literal['In Stock', 'All Future Release'], num_pages=5) -> pd.DataFrame:
        """
        Extract all Scaled figures from 4-8, sorted by release date. By selecting stock type between In Stock
        and All Future Release, we can extract In Stock Figures or Pre-Order Figures
        """
        url_temp = self._get_url_template(category="Figures", stock=stock_type, scale=[8, 7, 6, 5, 4],
                                          sort="releaseDate desc")

        all_data = []
        for page_url in tqdm.tqdm(self._get_product_urls(url_temp, pages=num_pages),
                                  total=num_pages * 24, desc=f"Extracting {stock_type}"):
            # Iterate through each page url to extract data
            data = self._get_page("https://www.hlj.com" + page_url)
            all_data.append(data)

        df = pd.DataFrame(all_data)
        df['date_added'] = datetime.now()

        return df

    @staticmethod
    def _get_url_template(stock: str = None, sort: str = None,
                          category: str = None, scale: list = None) -> str:
        """
        Create Filter URL for HLJ
        :param stock:  In Stock / Order Stop / Out of Stock
        :param category: Figurines / Action Figures / Dolls
        :param scale: a list of scales E.g. 8 means 1/8 or 4 means 1/4 or 6 means 1/6
        :param sort: text for sort type
        :return: a string url with params, need to format {page_num} to the page number you need
        """
        url = "/".join([URL, "search"])

        params = [
            ("StockLevel", stock),
            ("GenreCode2", category),
            ("Sort", sort)
        ]
        scale_params = []
        if scale is not None:
            scale_params = [("Scale2", x) for x in scale]
        params += scale_params

        params = [(k, v) for k, v in params if v is not None]
        param_string = urlencode(params).replace("In+Stock", "In%C2%A0Stock")

        if param_string == "":
            return url
        else:
            param_string += "&Page={page_num}"
            return url + "/?" + param_string

    def _get_product_urls(self, template_url, pages=5):
        """
        Go to HLJ List from URL
        """
        for i in range(1, pages + 1):
            url = template_url.format(page_num=i)
            self.d.get(url)

            crawl_ele = self.s.find_element("//div[@class='search search-widget-blocks']")
            sp = BeautifulSoup(crawl_ele.get_attribute("outerHTML"), "html.parser")
            urls = [ele.a['href'] for ele in list(sp.div.find_all("div", recursive=False))]
            for uri in urls:
                yield uri

    def _get_page(self, url: str) -> dict:
        """
        Crawl HLJ Figure Page. This page should only contain data of a single item.
        url -> URL of page to extract
        return dictionary of all the label and value
        """
        self.d.get(url)

        # Check if Cookies Dialog appear, if appear click on accept

        elem = self.s.find_element("//script[@type='application/ld+json']")
        details = json.loads(elem.get_attribute("innerHTML"))
        fields = {
            'title': 'name',
            'image_url': 'image',
            'brand': ['brand', 'name'],
            'currency': ['offers', 'priceCurrency'],
            'price': ['offers', 'price'],
            'product_url': ['offers', 'url'],
            'jan_code': 'gtin13'
        }

        # Check Product Details fields
        details = self._get_fields(details, fields)

        # Get Release Date
        sp = BeautifulSoup(self.d.page_source, 'html.parser')
        release_date = [
            e.text.split(":")[1].strip()
            for e in sp.find("div", attrs={"class": "product-details"}).find_all("li")
            if e.text.strip().split(":")[0] == "Release Date"
        ][0]
        details["release_date"] = release_date

        return details

    @staticmethod
    def _get_fields(data: dict, field_names: dict) -> dict:
        """
        Check if the following require fields to extract exist in the dict data and return data
        """
        fields = {}
        for key, search in field_names.items():
            if isinstance(search, list):
                #  iterate through search to find the lowest level value
                v = data[search[0]]
                for s in search[1:]:
                    v = v[s]
                fields[key] = v
            else:  # if it's a single string
                fields[key] = data[search]

        return fields
