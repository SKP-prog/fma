from requests import request
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import tqdm
import pandas as pd
from datetime import datetime

URL = "https://www.hlj.com"
HEAD = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/130.0.0.0 Safari/537.36"
}


def main():
    # check if previously extracted data
    path = "./results.csv"
    prev_df = pd.read_csv(path)

    # Go to HLJ website and crawl all latest in stock figures
    entries = []
    for item in get_items(max_pages=3):
        entries.append(item)

    df = pd.DataFrame(entries)
    df.to_csv(path, index=False, lineterminator="\n")
    # TODO: we need to mege the two df together.
    #  As long as there is a full row that is exactly the same, we merge. else keep both.
    #  date extracted do not need to be compared. always take the latest date


def get_items(max_pages: int = 1) -> list:
    for page in tqdm.tqdm(range(1, max_pages + 1), total=max_pages, desc="Crawling Data"):
        new_url = get_url(page=page, category="Figures",
                          stock="In Stock", scale=[8, 7, 6, 5, 4],
                          sort="releaseDate desc")
        rsp = request("GET", new_url, headers=HEAD)

        sp = BeautifulSoup(rsp.text, 'html.parser')
        grid_items = sp.find("div", attrs={"class": "search search-widget-blocks"})
        items = grid_items.find_all("div", attrs={"class": "search-widget-block"})

        # Per Page, crawl each grid box
        for i in items:
            product_link = i.find("p", attrs={"class": "product-item-name"})
            page_url = "https://www.hlj.com" + product_link.a["href"]
            price, maker, jan, release = get_page_details(page_url)

            data = {
                "img_url": "https:" + i.find("a", attrs={"class": "item-img-wrapper"}).img["src"],
                "title": product_link.a.text.strip(),
                "page_url": page_url,
                "price": price,
                "maker": maker,
                "JAN_code": jan,
                "release_date": release,
                "date_extracted": datetime.now()
            }

            yield data


def get_page_details(url) -> tuple:
    def get_text(parent):
        return "".join(parent.find_all(string=True, recursive=False)).strip()

    rsp = request("GET", url, headers=HEAD)
    sp = BeautifulSoup(rsp.text, "html.parser")

    p_info = sp.find("div", attrs={"class": "product-info"})
    price = get_text(p_info.find("p", attrs={"price"}))
    # stock = p_info.find("p", attrs={"class": "product-stock"}).text.strip()
    maker = p_info.find("a", id="details_makername").text.strip()

    # Product Details
    details = sp.find("div", attrs={"class": "product-details"}).find_all("li")
    details = [x.text.strip() for x in details if "Release Date:" in x.text or "JAN Code:" in x.text]

    return (price, maker,
            details[0].replace("JAN Code:", "").strip(),
            details[1].replace("Release Date:", "").strip())


def get_url(stock: str = None, page: int = None,
            category: str = None, scale: list = None,
            sort: str = None) -> str:
    """
    Create Filter URL for HLJ
    :param stock:  In Stock / Order Stop / Out of Stock
    :param page: 1 / 2 / 3 / 4
    :param category: Figurines / Action Figures / Dolls
    :param scale: a list of scales E.g. 8 means 1/8 or 4 means 1/4 or 6 means 1/6
    :param sort: text for sort type
    :return: a string url with params
    """
    url = "/".join([URL, "search"])

    params = [
        ("StockLevel", stock),
        ("Page", page),
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
        return url + "/?" + param_string


if __name__ == "__main__":
    main()
