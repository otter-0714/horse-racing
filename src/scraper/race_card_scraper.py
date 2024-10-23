# 出馬表をスクレイピングするクラス
import requests
import time
from bs4 import BeautifulSoup
import os
import json
from logging import getLogger, config
import pandas as pd
import sys

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


class RaceCardScraper:
    def __init__(self, race_id):
        self.race_id = race_id
        race_url = f"https://db.netkeiba.com/race/{self.race_id}"
        try:
            time.sleep(1)
            r = requests.get(race_url)
            r.encoding = r.apparent_encoding
            self.soup = BeautifulSoup(r.text, "lxml")
            self.dfs = [
                pd.read_html(str(t))[0] for t in self.soup.select("table:has(tr td)")
            ]  ##########ここで工夫をする tdを持っていない<table>が悪さしている
        except:  # dfsを採用するときにエラーが起こる
            logger.error(
                f"RaceCardScraperで{self.race_id}をスクレイピングできませんでした"
            )
            raise ScrapeError(
                f"RaceCardScraperで{self.race_id}をスクレイピングできませんでした"
            )
        if len(self.dfs) <= 1:
            logger.error(f"{self.race_id} has only {len(self.dfs)} df.")
            raise ScrapeError(f"{self.race_id} has only {len(self.dfs)} df.")

    def _scrape_result(self):
        result = self.dfs[0]
        soup_table = self.soup.find_all("table")[0]

        horses = []  # 馬のID
        jockeys = []  # 騎手のID
        trainers = []  # 調教師のID
        owners = []  # 馬主のID
        soup_a = soup_table.find_all("a")
        for item in soup_a:
            item_url = item.get("href")
            if item_url is None:
                continue
            if "horse/" in item_url:
                horses.append(item_url)
            elif "jockey/" in item_url:
                jockeys.append(item_url)
            elif "trainer/" in item_url:
                trainers.append(item_url)
            elif "owner/" in item_url:
                owners.append(item_url)
        if len(horses) != len(result):
            raise LessXXXXIDError(
                f"{self.race_id}:horsesのidの数とdfの大きさが合わない"
            )
        if len(jockeys) != len(result):
            raise LessXXXXIDError(
                f"{self.race_id}:jockeysのidの数とdfの大きさが合わない"
            )
        if len(trainers) != len(result):
            raise LessXXXXIDError(
                f"{self.race_id}:trainersのidの数とdfの大きさが合わない"
            )
        if len(owners) != len(result):
            raise LessXXXXIDError(
                f"{self.race_id}:ownersのidの数とdfの大きさが合わない"
            )
        result["horse id"] = horses
        result["jockey id"] = jockeys
        result["trainer id"] = trainers
        result["owner id"] = owners

        prize = []  # 　賞金
        soup_tr = soup_table.find_all("tr")
        for item in soup_tr:
            try:
                prize.append(item.find_all("td", class_="txt_r")[-1].text)
            except:
                pass
        result["prize"] = prize

        tsuuka = []  # 通過
        agari = []  # 上がり
        soup_tr = soup_table.find_all("tr")
        for temp in soup_tr[1:]:
            soup_td = temp.find_all("td")
            tsuuka.append(soup_td[10].text)
            agari.append(soup_td[11].text)
        result["通過"] = tsuuka
        result["上がり"] = agari

        return result

    def _scrape_payback(self):
        payback = []
        for df_ind in range(1, len(self.dfs)):
            try:
                index_set = set(self.dfs[df_ind][0].tolist())
                if not set(KIND_OF_TICKET).isdisjoint(
                    index_set
                ):  # payback用の列名が存在すれば採用
                    payback.append(self.dfs[df_ind])
            except:
                pass
        payback = pd.concat(payback)

        return payback

    def _scrape_race_info(self):
        race_info = []
        item = self.soup.find("dl", class_="racedata fc")
        for x in item.find_all("h1"):
            race_info.append(x.text)
        for x in item.find_all("span"):
            race_info.append(x.text)

        item = self.soup.find("p", class_="smalltxt")
        race_info.append(item.text)

        if len(race_info) != 3:
            logger.error(
                f"race_infoの個数が{len(race_info)}となった.3個であることを想定していた．\n{race_info}"
            )
            raise ScrapeError(
                f"race_infoの個数が{len(race_info)}となった.3個であることを想定していた．\n{race_info}"
            )
        return race_info

    def scrape(self):
        result = self._scrape_result()
        payback = self._scrape_payback()
        race_info = self._scrape_race_info()
        logger.info(f"{self.race_id}のレース結果のスクレイピングが完了しました")

        return result, payback, race_info


if __name__ == "__main__":
    race_id = 202406040307
    sc = RaceCardScraper(race_id)
    result, payback, race_info = sc.scrape()
