# レースIDの一覧をスクレイピングするクラス
import requests
import time
from bs4 import BeautifulSoup
import os
import json
from logging import getLogger, config

# ログの設定
logger = getLogger("project").getChild(__name__)
log_config_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "log_config.json"
)
with open(log_config_path, "r") as file:
    log_conf = json.load(file)
config.dictConfig(log_conf)


class RaceIdListScraper:
    def __init__(self, start_year, end_year):
        self.start_year = start_year
        self.end_year = end_year
        self.race_id_list = []

    def _scrape_raceid_list_of_page_and_year(self, year, page):
        list_url = f"https://db.netkeiba.com//?pid=race_list&word=&start_year={year}&start_mon=none&end_year={year}&end_mon=none&kyori_min=&kyori_max=&sort=date&list=100&page={page}"
        r = requests.get(list_url)
        time.sleep(1)  # サーバーの負荷を減らすため1秒待機
        soup = BeautifulSoup(r.content.decode("euc-jp", "ignore"), "html.parser")
        soup_table = soup.find_all("table")[0]
        soup_a = soup_table.find_all("a")
        raceid_list_of_page_and_year = []
        for item in soup_a:
            u = item.get("href")
            if (
                ("race" in u)
                and ("sum" not in u)
                and ("list" not in u)
                and ("asc" not in u)
                and ("movie" not in u)
            ):
                u = u.split("/")[2]
                raceid_list_of_page_and_year.append(u)
        return raceid_list_of_page_and_year

    def scrape_raceid_list(self):
        for year in range(self.start_year, self.end_year + 1):
            page = 1
            while True:
                raceid_list_of_page_and_year = (
                    self._scrape_raceid_list_of_page_and_year(year, page)
                )
                self.race_id_list.extend(raceid_list_of_page_and_year)
                logger.info(f"{year}年{page}ページ目のレースIDリストを取得")
                if len(raceid_list_of_page_and_year) == 0:
                    break
                page += 1
        return self.race_id_list


if __name__ == "__main__":
    scraper = RaceIdListScraper(2023, 2023)
    print(scraper.scrape_raceid_list())
    with open("save.txt", "w") as f:
        f.write("\n".join(scraper.race_id_list))
