# horse_idやjockey_id, trainer_id, owner_idからスクレイピングして
# 名前を取得するクラス
import requests
import time
from bs4 import BeautifulSoup
import os
import json
from logging import getLogger, config
import sys
import re

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


class HorseIdScraper:
    def __init__(self, horse_id):
        self.horse_id = horse_id

    def scrape(self):
        time.sleep(1)
        url = f"https://db.netkeiba.com/horse/{self.horse_id}"
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        soup = soup.find("div", attrs={"class": "horse_title"})
        soup = soup.find("h1")
        name = soup.text

        logger.info(f"horse_id: {self.horse_id}, name: {name}を取得しました")
        return name


class JockyIdScraper:
    def __init__(self, jockey_id):
        self.jockey_id = jockey_id

    def scrape(self):
        time.sleep(1)
        url = f"https://db.netkeiba.com/jockey/result/recent/{self.jockey_id}"
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        soup = soup.find("div", attrs={"class": "db_head_name"})
        soup = soup.find("h1")
        name = soup.text
        name = name.strip()
        name = re.sub(r"\s*\(.*?\)\s*", "", name)
        logger.info(f"jockey_id: {self.jockey_id}, name: {name}を取得しました")
        return name


class TrainerIdScraper:
    def __init__(self, trainer_id):
        self.trainer_id = trainer_id

    def scrape(self):
        time.sleep(1)
        url = f"https://db.netkeiba.com/trainer/result/recent/{self.trainer_id}/"
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        soup = soup.find("div", attrs={"class": "db_head_name"})
        soup = soup.find("h1")
        name = soup.text
        name = name.strip()
        name = re.sub(r"\s*\(.*?\)\s*", "", name)
        logger.info(f"trainer_id: {self.trainer_id}, name: {name}を取得しました")
        return name


class OwnerIdScraper:
    def __init__(self, owner_id):
        self.owner_id = owner_id

    def scrape(self):
        time.sleep(1)
        url = f"https://db.netkeiba.com/owner/result/recent/{self.owner_id}/"
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        soup = soup.find("div", attrs={"class": "db_head_name"})
        soup = soup.find("h1")
        name = soup.text
        name = name.strip()
        name = re.sub(r"\s*\(.*?\)\s*", "", name)
        logger.info(f"owner_id: {self.owner_id}, name: {name}を取得しました")
        return name


if __name__ == "__main__":
    horse_id = "2020103120"
    scraper = HorseIdScraper(horse_id)
    print(scraper.scrape())

    jockey_id = "05339"
    scraper = JockyIdScraper(jockey_id)
    print(scraper.scrape())

    trainer_id = "01126"
    scraper = TrainerIdScraper(trainer_id)
    print(scraper.scrape())

    owner_id = "415800"
    scraper = OwnerIdScraper(owner_id)
    print(scraper.scrape())
