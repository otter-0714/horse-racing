# 血統をスクレイピングするクラス
import requests
import time
from bs4 import BeautifulSoup
import os
import json
from logging import getLogger, config
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.utils.my_error import ScrapeError

# ログの設定
logger = getLogger("project").getChild(__name__)
log_config_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "log_config.json"
)
with open(log_config_path, "r") as file:
    log_conf = json.load(file)
config.dictConfig(log_conf)


class PedScraper:
    def __init__(self, horse_id):
        self.horse_id = horse_id

    def generate_pedigree(self, n):
        if n == 1:
            return ["f", "m"]
        else:
            previous_generation = self.generate_pedigree(n - 1)
            current_generation = []
            for x in previous_generation:
                current_generation.append(x)
                if len(x) == n - 1:
                    current_generation.append(x + "f")
                    current_generation.append(x + "m")
            return current_generation

    def scrape(self):
        time.sleep(1)
        url = f"https://db.netkeiba.com/horse/ped/{self.horse_id}/"
        r = requests.get(url)
        soup = BeautifulSoup(
            r.content.decode("euc-jp", "ignore"), "html.parser"
        )  # バグ対策でdecode
        table = soup.find_all("table")[0]
        ped = []
        for item in table.find_all("a"):
            url = item.get("href")
            if (
                ("horse" in url)
                and (not "ped" in url)
                and (not "sire" in url)
                and (not "mare" in url)
            ):
                ped.append(url.split("/")[-2])
        if len(ped) != 62:
            logger.error(f"PedScraperで{self.horse_id}をスクレイピングできませんでした")
            raise ScrapeError(
                f"PedScraperで{self.horse_id}をスクレイピングできませんでした"
            )
        ped_name = self.generate_pedigree(5)
        ped_name = [f"{name}_id" for name in ped_name]
        ped = dict(zip(ped_name, ped))
        logger.info(f"{self.horse_id}の血統のスクレイピングが完了しました")
        return ped


if __name__ == "__main__":
    horse_id = "2021100189"
    ped_scraper = PedScraper(horse_id)
    ped = ped_scraper.scrape()
    print(ped)
