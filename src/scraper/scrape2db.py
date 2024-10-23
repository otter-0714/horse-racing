# er.dioの青色のテーブルにデータを格納する

import requests
import re
import time
from bs4 import BeautifulSoup
import os
import json
from logging import getLogger, config
from datetime import time, datetime, date
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.scraper.race_card_scraper import RaceCardScraper
from src.scraper.ped_scraper import PedScraper
from src.scraper.meteorological_agency_scraper import MeteorologicalAgencyScraper
from src.mysql.initialize_db import get_session
from src.utils.my_error import LessRaceinfoError, PreprocessError
from src.utils._variables import KIND_OF_TICKET
from src.mysql.models.db1 import RaceInfo, Result, Ped, Weather, Payback


# ログの設定
logger = getLogger("project").getChild(__name__)
log_config_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "log_config.json"
)
with open(log_config_path, "r") as file:
    log_conf = json.load(file)
config.dictConfig(log_conf)


# コーナー分解
def split_and_fill(entry):
    parts = entry.split("-")
    if len(parts) == 1:
        return [parts[0], parts[0], parts[0], parts[0]]
    elif len(parts) == 2:
        return [parts[0], parts[0], parts[1], parts[1]]
    elif len(parts) == 3:
        t0 = int(parts[0])
        t1 = int(parts[1])
        t2 = int(parts[2])
        return [t0, (t0 + t1) / 2, (t1 + t2) / 2, t2]
    elif len(parts) == 4:
        return [parts[0], parts[1], parts[2], parts[3]]
    else:
        raise ValueError("split_and_fill error")


# 一つのrace_idをscrapeしてresult, payback, race_infoに格納する
class RaceCard2DB:
    def __init__(self, race_id):
        self.race_id = race_id
        rc_scraper = RaceCardScraper(race_id)
        self.result, self.payback, self.race_info = rc_scraper.scrape()
        self.session = get_session()

    def _insert_payback(self):
        try:
            self.payback.index = self.payback[0]
            hukusyo_s = self.payback[2]["複勝"].split()
            if len(hukusyo_s) == 3:
                self.payback.loc["複勝1着", 2] = hukusyo_s[0]
                self.payback.loc["複勝2着", 2] = hukusyo_s[1]
                self.payback.loc["複勝3着", 2] = hukusyo_s[2]
            elif len(hukusyo_s) == 2:
                self.payback.loc["複勝1着", 2] = hukusyo_s[0]
                self.payback.loc["複勝2着", 2] = hukusyo_s[1]
                self.payback.loc["複勝3着", 2] = "NoData"

            payback_data = [self.payback.at[x, 2] for x in KIND_OF_TICKET]
            payback_data = [x.replace(",", "") for x in payback_data]
        except:
            logger.warning(
                f"{self.race_id}で払い戻し情報が取得できませんでした.\n{self.payback}"
            )
            payback_data = [None for _ in KIND_OF_TICKET]

        # paybackテーブルに格納
        payback = Payback(
            race_id=self.race_id,
            win=payback_data[0],
            show1=payback_data[1],
            show2=payback_data[2],
            show3=payback_data[3],
            quinella=payback_data[4],
            exacta=payback_data[5],
            trio=payback_data[6],
            trifecta=payback_data[7],
        )
        self.session.add(payback)

    def _insert_raceinfo(self):
        conditions1 = self.race_info[1].replace("直線", "直")
        conditions1 = conditions1.split("/")
        conditions2 = self.race_info[2]
        if len(conditions1) != 4:
            logger.error(
                f"{self.race_id}のrace_infoの一つ目がおかしい↓. \n{self.race_info[1]}"
            )
            raise LessRaceinfoError(self.race_id)

        race_id = self.race_id

        # race_info[1]から情報を抽出
        track = (conditions1[0][0],)  # 芝，ダート，障害
        direction = (conditions1[0][1],)  # 左右
        temp = conditions1[0][2:].strip()  # 距離等
        distance = re.search(r"(\d+)", temp).group(1)  # 距離
        detail_course = temp.replace(distance, "")  # 内外（存在すれば）
        weather = conditions1[1].split(" : ")[1].strip()  # 天気
        track_condition = conditions1[2].split(" : ")[1].strip()  # レース場の環境
        temp = conditions1[3].split(" : ")[1].strip()
        _hour = int(temp.split(":")[0])
        _minute = int(temp.split(":")[1])
        starting_time = time(_hour, _minute)  # 発走時刻

        # race_info[2]から情報を抽出
        date = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)", conditions2).group(1)  # 日付
        date = datetime.strptime(date, "%Y年%m月%d日")
        inning = re.search(r"(\d{1,2}回)", conditions2).group(1)  # 回
        inning = int(inning.replace("回", ""))
        day = re.search(r"(\d{1,2}日目)", conditions2).group(1)  # 日目
        day = int(day.replace("日目", ""))
        place = conditions2.split(" ")[1]
        place = re.search(r"(\d{1,2})回(.+?)(\d{1,2})日目", place).group(2)  # 場所
        round = int(str(self.race_id)[10:12])  # ラウンド
        other_info = conditions2.split(" ")[2].strip()  # その他の情報

        # 前処理
        _hour = starting_time.hour
        _minute = starting_time.minute
        cos_starting_time = np.cos(
            2 * np.pi * (_hour + _minute / 60) / 24
        )  # 出走時刻_cos
        sin_starting_time = np.sin(
            2 * np.pi * (_hour + _minute / 60) / 24
        )  # 出走時刻_sin
        _month = date.month
        _day = date.day
        cos_date = np.cos(2 * np.pi * (_month + _day / 31) / 12)  # 日付_cos
        sin_date = np.sin(2 * np.pi * (_month + _day / 31) / 12)  # 日付_sin

        # resultから計算される統計量
        sum_prize = pd.to_numeric(
            self.result["prize"], errors="coerce"
        ).sum()  # レース合計賞金
        log_sum_prize = np.log(sum_prize)  # レース合計賞金の対数
        num_horse = len(self.result)  # 馬数

        # race_infoテーブルに格納
        race_info = RaceInfo(
            race_id=race_id,
            track=track,
            direction=direction,
            distance=distance,
            detail_course=detail_course,
            weather=weather,
            track_condition=track_condition,
            starting_time=starting_time,
            date=date,
            inning=inning,
            day=day,
            place=place,
            round=round,
            cos_starting_time=cos_starting_time,
            sin_starting_time=sin_starting_time,
            cos_date=cos_date,
            sin_date=sin_date,
            other_info=other_info,
            sum_prize=sum_prize,
            log_sum_prize=log_sum_prize,
            num_horse=num_horse,
        )
        self.session.add(race_info)

    def _preprocess_result(self):
        result_df = self.result

        result_df["jockey_id"] = result_df["jockey id"].str.split("/").str.get(-2)
        result_df["horse_id"] = result_df["horse id"].str.split("/").str.get(-2)
        result_df["trainer_id"] = result_df["trainer id"].str.split("/").str.get(-2)
        result_df["owner_id"] = result_df["owner id"].str.split("/").str.get(-2)
        result_df = result_df.drop(
            columns=["jockey id", "horse id", "trainer id", "owner id"]
        )

        result_df = result_df[
            ~result_df["着 順"].isin(["中", "取", "失", "除", np.nan])
        ]
        result_df["着 順"] = (
            result_df["着 順"]
            .replace("\(降\)", "", regex=True)
            .replace("\(再\)", "", regex=True)
        )

        # 馬数が5から18でない場合はエラー
        if len(result_df) < 5 or len(result_df) > 18:
            logger.error(
                f"{self.race_id}は馬数が{len(result_df)}頭です.\n{self.result}"
            )
            raise PreprocessError(
                f"{self.race_id}は馬数が{len(result_df)}頭です.\n{self.result}"
            )
        # horse_idに'x000000000'が含まれる場合はエラー
        if "x000000000" in result_df["horse_id"].values:
            logger.error(f"{self.race_id}にx000000000が含まれています.\n{self.result}")
            raise PreprocessError(
                f"{self.race_id}の馬にx000000000が含まれています.\n{self.result}"
            )

        result_df["タイム"] = result_df["タイム"].str.replace(".", ":", regex=False)
        result_df[["分", "秒", "ミリ秒"]] = (
            result_df["タイム"].str.split(":", expand=True).astype(float)
        )
        result_df["タイム"] = (
            result_df["分"] * 60 + result_df["秒"] + 0.1 * result_df["ミリ秒"]
        )
        result_df = result_df.drop(columns=["分", "秒", "ミリ秒"])

        result_df[["体重", "体重増減"]] = (
            result_df["馬体重"]
            .str.replace(")", "", regex=False)
            .str.split("(", regex=False, expand=True)
        )
        result_df[["性", "年齢"]] = result_df["性齢"].str.extract(
            r"(牡|牝|セ)(\d+)", expand=True
        )

        result_df["単勝オッズ"] = (
            result_df["単勝"]
            .astype("str")
            .str.replace(",", "")
            .replace("---", None)
            .astype(float)
        )

        result_df["prize"] = result_df["prize"].astype(str).str.replace(",", "")
        result_df["prize"] = result_df["prize"].replace("", 0).astype(float)
        df_split = result_df["通過"].apply(split_and_fill)
        df_split = pd.DataFrame(
            df_split.tolist(),
            columns=["corner_1", "corner_2", "corner_3", "corner_4"],
        )
        result_df = pd.concat([result_df.reset_index(drop=True), df_split], axis=1)

        return result_df

    def _insert_result(self):
        df = self._preprocess_result()
        num_horse = len(df)

        df = df.rename(
            columns={
                "タイム": "time",
                "着 順": "rank",
                "枠 番": "barrier_number",
                "馬 番": "horse_number",
                "斤量": "handicap",
                "人 気": "popularity",
                "通過": "passing_order",
                "上がり": "second_half_time",
                "体重": "weight",
                "体重増減": "weight_difference",
                "性": "sex",
                "年齢": "age",
                "単勝オッズ": "odds",
            }
        )
        df["race_id"] = self.race_id
        df["time_difference"] = df["time"] - df["time"].min()
        df["relative_corner_1"] = df["corner_1"].astype(float) / num_horse
        df["relative_corner_2"] = df["corner_2"].astype(float) / num_horse
        df["relative_corner_3"] = df["corner_3"].astype(float) / num_horse
        df["relative_corner_4"] = df["corner_4"].astype(float) / num_horse
        df["diff_corner_1_2"] = df["relative_corner_1"] - df["relative_corner_2"]
        df["diff_corner_1_3"] = df["relative_corner_1"] - df["relative_corner_3"]
        df["diff_corner_1_4"] = df["relative_corner_1"] - df["relative_corner_4"]
        df["diff_corner_2_3"] = df["relative_corner_2"] - df["relative_corner_3"]
        df["diff_corner_2_4"] = df["relative_corner_2"] - df["relative_corner_4"]
        df["diff_corner_3_4"] = df["relative_corner_3"] - df["relative_corner_4"]
        df["relative_rank"] = df["rank"].astype(float) / num_horse
        df["inverse_odds"] = 1 / df["odds"].astype(float)
        df["log_odds"] = np.log(df["odds"].astype(float))
        df["log_prize"] = np.log(df["prize"].astype(float) + 1)
        df["relative_popularity"] = df["inverse_odds"] / df["inverse_odds"].sum()

        for index, row in df.iterrows():
            result = Result(
                race_id=row["race_id"],
                horse_number=row["horse_number"],
                time=row.get("time"),
                prize=row.get("prize"),
                passing_order=row.get("passing_order"),
                second_half_time=row.get("second_half_time"),
                rank=row.get("rank"),
                barrier_number=row.get("barrier_number"),
                horse_id=row.get("horse_id"),
                jockey_id=row.get("jockey_id"),
                trainer_id=row.get("trainer_id"),
                owner_id=row.get("owner_id"),
                sex=row.get("sex"),
                age=row.get("age"),
                handicap=row.get("handicap"),
                popularity=row.get("popularity"),
                time_difference=row.get("time_difference"),
                odds=row.get("odds"),
                weight=row.get("weight"),
                weight_difference=row.get("weight_difference"),
                corner_1=row.get("corner_1"),
                corner_2=row.get("corner_2"),
                corner_3=row.get("corner_3"),
                corner_4=row.get("corner_4"),
                relative_corner_1=row.get("relative_corner_1"),
                relative_corner_2=row.get("relative_corner_2"),
                relative_corner_3=row.get("relative_corner_3"),
                relative_corner_4=row.get("relative_corner_4"),
                diff_corner_1_2=row.get("diff_corner_1_2"),
                diff_corner_1_3=row.get("diff_corner_1_3"),
                diff_corner_1_4=row.get("diff_corner_1_4"),
                diff_corner_2_3=row.get("diff_corner_2_3"),
                diff_corner_2_4=row.get("diff_corner_2_4"),
                diff_corner_3_4=row.get("diff_corner_3_4"),
                relative_rank=row.get("relative_rank"),
                relative_popularity=row.get("relative_popularity"),
                inverse_odds=row.get("inverse_odds"),
                log_odds=row.get("log_odds"),
                log_prize=row.get("log_prize"),
            )
            self.session.add(result)  # セッションにオブジェクトを追加

    def add2db(self):
        self._insert_raceinfo()
        logger.info(f"{self.race_id}のレース情報を格納しました.")
        self._insert_payback()
        logger.info(f"{self.race_id}の払い戻し情報を格納しました.")
        self._insert_result()
        logger.info(f"{self.race_id}の結果情報を格納しました.")

        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(
                f"{self.race_id}のデータのコミットに失敗しました.ロールバックします.\n{e}"
            )
        self.session.close()


# 一つのhorse_idからpedをscrapeしてdbに格納する
class Ped2DB:
    def __init__(self, horse_id):
        self.horse_id = horse_id
        self.session = get_session()
        p_scraper = PedScraper(horse_id)
        self.ped = p_scraper.scrape()

    def add2db(self):
        ped = Ped(
            horse_id=self.horse_id,
            f_id=self.ped["f_id"],  # 父ID
            m_id=self.ped["m_id"],  # 母ID
            ff_id=self.ped["ff_id"],  # 父父ID
            fm_id=self.ped["fm_id"],  # 父母ID
            mf_id=self.ped["mf_id"],  # 母父ID
            mm_id=self.ped["mm_id"],  # 母母ID
            fff_id=self.ped["fff_id"],  # 父父父ID
            ffm_id=self.ped["ffm_id"],  # 父父母ID
            fmf_id=self.ped["fmf_id"],  # 父母父ID
            fmm_id=self.ped["fmm_id"],  # 父母母ID
            mff_id=self.ped["mff_id"],  # 母父父ID
            mfm_id=self.ped["mfm_id"],  # 母父母ID
            mmf_id=self.ped["mmf_id"],  # 母母父ID
            mmm_id=self.ped["mmm_id"],  # 母母母ID
            ffff_id=self.ped["ffff_id"],  # 父父父父ID
            fffm_id=self.ped["fffm_id"],  # 父父父母ID
            ffmf_id=self.ped["ffmf_id"],  # 父父母父ID
            ffmm_id=self.ped["ffmm_id"],  # 父父母母ID
            fmff_id=self.ped["fmff_id"],  # 父母父父ID
            fmfm_id=self.ped["fmfm_id"],  # 父母父母ID
            fmmf_id=self.ped["fmmf_id"],  # 父母母父ID
            fmmm_id=self.ped["fmmm_id"],  # 父母母母ID
            mfff_id=self.ped["mfff_id"],  # 母父父父ID
            mffm_id=self.ped["mffm_id"],  # 母父父母ID
            mfmf_id=self.ped["mfmf_id"],  # 母父母父ID
            mfmm_id=self.ped["mfmm_id"],  # 母父母母ID
            mmff_id=self.ped["mmff_id"],  # 母母父父ID
            mmfm_id=self.ped["mmfm_id"],  # 母母父母ID
            mmmf_id=self.ped["mmmf_id"],  # 母母母父ID
            mmmm_id=self.ped["mmmm_id"],  # 母母母母ID
            fffff_id=self.ped["fffff_id"],  # 父父父父父ID
            ffffm_id=self.ped["ffffm_id"],  # 父父父父母ID
            fffmf_id=self.ped["fffmf_id"],  # 父父父母父ID
            fffmm_id=self.ped["fffmm_id"],  # 父父父母母ID
            ffmff_id=self.ped["ffmff_id"],  # 父父母父父ID
            ffmfm_id=self.ped["ffmfm_id"],  # 父父母父母ID
            ffmmf_id=self.ped["ffmmf_id"],  # 父父母母父ID
            ffmmm_id=self.ped["ffmmm_id"],  # 父父母母母ID
            fmfff_id=self.ped["fmfff_id"],  # 父母父父父ID
            fmffm_id=self.ped["fmffm_id"],  # 父母父父母ID
            fmfmf_id=self.ped["fmfmf_id"],  # 父母父母父ID
            fmfmm_id=self.ped["fmfmm_id"],  # 父母父母母ID
            fmmff_id=self.ped["fmmff_id"],  # 父母母父父ID
            fmmfm_id=self.ped["fmmfm_id"],  # 父母母父母ID
            fmmmf_id=self.ped["fmmmf_id"],  # 父母母母父ID
            fmmmm_id=self.ped["fmmmm_id"],  # 父母母母母ID
            mffff_id=self.ped["mffff_id"],  # 母父父父父ID
            mfffm_id=self.ped["mfffm_id"],  # 母父父父母ID
            mffmf_id=self.ped["mffmf_id"],  # 母父父母父ID
            mffmm_id=self.ped["mffmm_id"],  # 母父父母母ID
            mfmff_id=self.ped["mfmff_id"],  # 母父母父父ID
            mfmfm_id=self.ped["mfmfm_id"],  # 母父母父母ID
            mfmmf_id=self.ped["mfmmf_id"],  # 母父母母父ID
            mfmmm_id=self.ped["mfmmm_id"],  # 母父母母母ID
            mmfff_id=self.ped["mmfff_id"],  # 母母父父父ID
            mmffm_id=self.ped["mmffm_id"],  # 母母父父母ID
            mmfmf_id=self.ped["mmfmf_id"],  # 母母父母父ID
            mmfmm_id=self.ped["mmfmm_id"],  # 母母父母母ID
            mmmff_id=self.ped["mmmff_id"],  # 母母母父父ID
            mmmfm_id=self.ped["mmmfm_id"],  # 母母母父母ID
            mmmmf_id=self.ped["mmmmf_id"],  # 母母母母父ID
            mmmmm_id=self.ped["mmmmm_id"],  # 母母母母母ID
        )
        self.session.add(ped)
        try:
            self.session.commit()
            logger.info(f"{self.horse_id}の血統データを格納しました.")
        except Exception as e:
            self.session.rollback()
            logger.error(
                f"{self.horse_id}の血統データのコミットに失敗しました.ロールバックします.\n{e}"
            )
        self.session.close()


class MeteorologicalAgency2DB:
    def __init__(self, place, date):
        """
        Args:
            place (str): 場所の名前
            date (datetime.date): 日付
        """
        self.place = place
        self.date = date
        self.session = get_session()
        ma_scraper = MeteorologicalAgencyScraper(place, date)
        self.weather = ma_scraper.scrape()
        if len(self.weather) != 24:
            logger.error(f"{place}-{date}のデータが24時間分ありません.")
            raise PreprocessError(f"{place}-{date}のデータが24時間分ありません.")

    def _preprocess_weather(self):
        self.weather.columns = self.weather.columns.get_level_values(1)
        if "風速" in self.weather.columns:
            self.weather = self.weather.rename(
                columns={
                    "時": "時間",
                    "降水量 (mm)": "降水量",
                    "気温 (℃)": "気温",
                    "風速": "風速",
                    "風向": "風向",
                    "日照 時間 (h)": "日照時間",
                }
            )
        elif "平均風速 (m/s)" in self.weather.columns:
            self.weather = self.weather.rename(
                columns={
                    "時": "時間",
                    "降水量 (mm)": "降水量",
                    "気温 (℃)": "気温",
                    "平均風速 (m/s)": "風速",
                    "風向": "風向",
                    "日照 時間 (h)": "日照時間",
                }
            )
        self.weather = self.weather[
            ["時間", "降水量", "気温", "風速", "風向", "日照時間"]
        ]
        # ]や)を削除．これはデータに信頼性がないときにつく.
        for col in self.weather.columns:
            self.weather[col] = (
                self.weather[col].astype(str).str.replace(" ]", "", regex=False)
            )
            self.weather[col] = (
                self.weather[col].astype(str).str.replace(" )", "", regex=False)
            )

        # 降水量の--を0に置換．これは計測する事象が存在しないときにつく.
        self.weather["降水量"] = self.weather["降水量"].replace("--", "0")

        # 日照時間の--とnanを0に置換．これは計測する事象が存在しなかったり，夜になったときにつく.
        self.weather["日照時間"] = self.weather["日照時間"].replace(["--", "nan"], "0")

        for col in ["降水量", "気温", "風速", "日照時間"]:
            # {col}の×と///を同時に補完
            self.weather[col] = self.weather[col].replace(["×", "///"], [None, None])
            self.weather[col] = self.weather[col].astype(float)
            self.weather[col] = self.weather[col].interpolate(limit_direction="both")

        col = "風向"
        # {col}の×と///を最も近い向きで近似
        self.weather[col] = self.weather[col].replace(["×", "///"], [None, None])
        self.weather[col] = self.weather[col].fillna(method="ffill")

        # 時間をdatetime型に変換
        self.weather = self.weather.head(-1)
        self.weather["時間"] = self.weather["時間"].astype(str)
        self.weather["時間"] = self.weather["時間"] + ":00"
        self.weather["時間"] = pd.to_datetime(
            self.weather["時間"], format="%H:%M"
        ).dt.time

    def add2db(self):
        self._preprocess_weather()
        for index, row in self.weather.iterrows():
            weather = Weather(
                place=self.place,
                date=self.date,
                time=row["時間"],
                precipitation=row["降水量"],
                temperature=row["気温"],
                wind_speed=row["風速"],
                wind_angle=row["風向"],
                sunshine_hour=row["日照時間"],
            )
            self.session.add(weather)
        try:
            self.session.commit()
            logger.info(f"{self.place}-{self.date}の気象データを格納しました.")
        except Exception as e:
            self.session.rollback()
            logger.error(
                f"{self.place}-{self.date}の気象データのコミットに失敗しました.ロールバックします.\n{e}"
            )
        self.session.close()


if __name__ == "__main__":
    # race_id = 202406040307
    # race_id2db = RaceCard2DB(race_id)
    # race_id2db.add2db()

    race_id = 202406040308
    race_id2db = RaceCard2DB(race_id)
    race_id2db._insert_result()

    # horse_id = "2021100189"
    # ped2db = Ped2DB(horse_id)
    # ped2db.add2db()

    # place = "東京"
    # date = date(2021, 1, 1)
    # ma2db = MeteorologicalAgency2DB(place, date)
    # ma2db.add2db()

    pass
