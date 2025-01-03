from requests import request
from bs4 import BeautifulSoup
from selenium_driver import Selenium
from urllib.parse import urlencode
import tqdm
import pandas as pd
from datetime import datetime
from App.db_connection import DB
import json

URL = "https://www.hlj.com"
HEAD = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/130.0.0.0 Safari/537.36"
}
S = Selenium()
D = S.get_driver()


def main():
    mg = DB("localhost", 27017, dbname="HLJ")

    # Get DB Server Tables

    # Extract from Portal
    fr_data, pages = [], 2
    url_template = get_url(category="Figures", stock="All Future Release",
                           scale=[8, 7, 6, 5, 4], sort="releaseDate desc")
    # Iterate through each page url to extract data
    for page_url in tqdm.tqdm(get_product_urls(url_template, pages=pages),
                              total=pages * 24, desc="Extracting Future Releases"):
        data = get_page("https://www.hlj.com" + page_url)
        fr_data.append(data)

    fr_df = pd.DataFrame(fr_data)
    fr_df['date_added'] = datetime.now()
    update_db(fr_df)


def update_db(new_df):
    """
    Compare new_df with database df and add those that does not exist in database df.
    """



def get_product_urls(template_url, pages=5):
    """
    Go to HLJ List from URL
    """
    all_page_urls = []
    for i in range(1, pages + 1):
        url = template_url.format(page_num=i)
        D.get(url)

        crawl_ele = S.find_element("//div[@class='search search-widget-blocks']")
        sp = BeautifulSoup(crawl_ele.get_attribute("outerHTML"), "html.parser")
        urls = [ele.a['href'] for ele in list(sp.div.find_all("div", recursive=False))]
        for uri in urls:
            yield uri


def get_page(url: str) -> dict:
    """
    Crawl HLJ Figure Page. This page should only contain data of a single item.
    url -> URL of page to extract
    return dictionary of all the label and value
    """
    D.get(url)

    # Check if Cookies Dialog appear, if appear click on accept

    elem = S.find_element("//script[@type='application/ld+json']")
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
    details = get_fields(details, fields)

    # Get Release Date
    sp = BeautifulSoup(D.page_source, 'html.parser')
    release_date = [
        e.text.split(":")[1].strip()
        for e in sp.find("div", attrs={"class": "product-details"}).find_all("li")
        if e.text.strip().split(":")[0] == "Release Date"
    ][0]
    details["release_date"] = release_date

    return details


def get_fields(data: dict, field_names: dict) -> dict:
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


def get_url(stock: str = None, sort: str = None,
            category: str = None, scale: list = None) -> str:
    """
    Create Filter URL for HLJ
    :param stock:  In Stock / Order Stop / Out of Stock
    :param category: Figurines / Action Figures / Dolls
    :param scale: a list of scales E.g. 8 means 1/8 or 4 means 1/4 or 6 means 1/6
    :param sort: text for sort type
    :return: a string url with params
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


if __name__ == "__main__":
    main()
