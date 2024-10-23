# 気象庁のデータをスクレイピングするクラス
import requests
import time
from bs4 import BeautifulSoup
import os
import json
from logging import getLogger, config
import pandas as pd
import sys
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.my_error import ScrapeError, LessXXXXIDError
from src.utils._variables import KIND_OF_TICKET

# ログの設定
logger = getLogger("project").getChild(__name__)
log_config_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "log_config.json"
)
with open(log_config_path, "r") as file:
    log_conf = json.load(file)
config.dictConfig(log_conf)


place2prec_no = {
    "札幌": "14",
    "函館": "23",
    "福島": "36",
    "新潟": "54",
    "東京": "44",
    "中山": "45",
    "中京": "51",
    "京都": "61",
    "阪神": "63",
    "小倉": "82",
    "帯広": "20",
    "門別": "22",
    "盛岡": "33",
    "水沢": "33",
    "浦和": "33",
    "船橋": "45",
    "大井": "44",
    "川崎": "46",
    "金沢": "56",
    "笠松": "52",
    "名古屋": "51",
    "姫路": "63",
    "園田": "63",
    "高知": "74",
    "佐賀": "85",
    "上山": "35",
    "荒尾": "86",
    "旭川": "12",
    "福山": "67",
    "高崎": "42",
}
place2block_no = {
    "札幌": "47412",
    "函館": "47430",
    "福島": "47595",
    "新潟": "47604",
    "東京": "1133",
    "中山": "1236",
    "中京": "47636",
    "京都": "47759",
    "阪神": "47770",
    "小倉": "0780",
    "帯広": "47417",
    "門別": "0136",
    "盛岡": "47584",
    "水沢": "0230",
    "浦和": "0230",
    "船橋": "1236",
    "大井": "47662",
    "川崎": "47670",
    "金沢": "47605",
    "笠松": "47632",
    "名古屋": "47636",
    "姫路": "47769",
    "園田": "47770",
    "高知": "47893",
    "佐賀": "47813",
    "上山": "47588",
    "荒尾": "47819",
    "旭川": "47407",
    "福山": "47767",
    "高崎": "47624",
}


class MeteorologicalAgencyScraper:
    def __init__(self, place, date):
        """
        Args:
            place (str): 場所の名前
            date (datetime.date): 日付
        """
        self.place = place
        try:
            self.prec_no = place2prec_no[place]
            self.block_no = place2block_no[place]
        except:
            logger.error(f"placeが不正です: {place}")
            raise ScrapeError(f"placeが不正です: {place}")
        self.year = date.year
        self.month = date.month
        self.day = date.day

    def scrape(self):
        try:
            base_url = "https://www.data.jma.go.jp/obd/stats/etrn/view/hourly_a1.php?"
            url = (
                base_url
                + f"prec_no={self.prec_no}&block_no={self.block_no}&year={self.year}&month={self.month}&day={self.day}&view="
            )
            time.sleep(1)
            x = pd.read_html(url)[0]
            return x
        except:
            try:
                base_url = (
                    "https://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php?"
                )
                url = (
                    base_url
                    + f"prec_no={self.prec_no}&block_no={self.block_no}&year={self.year}&month={self.month}&day={self.day}&view="
                )
                time.sleep(1)
                x = pd.read_html(url)[0]
                return x
            except:
                logger.error(
                    f"気象庁のデータをスクレイピングできませんでした: \n{self.place}-{self.year}-{self.month}-{self.day}"
                )
                raise ScrapeError(
                    f"気象庁のデータをスクレイピングできませんでした: \n{self.place}-{self.year}-{self.month}-{self.day}"
                )


if __name__ == "__main__":
    # place = "東京"
    # race_date = date(2021, 1, 1)
    # meteorological_agency_scraper = MeteorologicalAgencyScraper(place, race_date)
    # x = meteorological_agency_scraper.scrape()

    place = "船橋"
    race_date = date(2023, 11, 27)
    meteorological_agency_scraper = MeteorologicalAgencyScraper(place, race_date)
    x = meteorological_agency_scraper.scrape()
    print(x)
