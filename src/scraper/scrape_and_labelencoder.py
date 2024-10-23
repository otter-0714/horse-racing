# 複数のrace_id，horse_idなどから連続してDBに追加
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
from sqlalchemy import distinct

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.scraper.race_card_scraper import RaceCardScraper
from src.scraper.ped_scraper import PedScraper
from src.scraper.race_id_list_scraper import RaceIdListScraper
from src.scraper.xxxx_id_scraper import (
    HorseIdScraper,
    JockyIdScraper,
    TrainerIdScraper,
    OwnerIdScraper,
)
from src.scraper.meteorological_agency_scraper import MeteorologicalAgencyScraper
from src.mysql.initialize_db import get_session
from src.utils.my_error import LessRaceinfoError, PreprocessError
from src.utils._variables import KIND_OF_TICKET
from src.mysql.models.db1 import RaceInfo, Result, Ped, Weather, Payback
from src.scraper.scrape2db import RaceCard2DB, Ped2DB, MeteorologicalAgency2DB
from src.mysql.models.db2 import (
    LabelEncoderTrack,
    LabelEncoderDirection,
    LabelEncoderTrackCondition,
    LabelEncoderWeather,
    LabelEncoderDetailCourse,
    LabelEncoderPlace,
    LabelEncoderHorseId,
    LabelEncoderJockyId,
    LabelEncoderTrainerId,
    LabelEncoderOwnerId,
    LabelEncoderSex,
    LabelEncoderSireId,
    LabelEncoderDamId,
)


# ログの設定
logger = getLogger("project").getChild(__name__)
log_config_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "log_config.json"
)
with open(log_config_path, "r") as file:
    log_conf = json.load(file)
config.dictConfig(log_conf)


def scrape_all_race_id(start_year, end_year):
    """
    年度を指定してDBにない情報をスクレイピングしてDBに追加する
    """
    session = get_session()
    done_race_ids = session.query(RaceInfo.race_id).all()
    done_race_ids = [race_id[0] for race_id in done_race_ids]

    for year in range(start_year, end_year + 1):
        scraper = RaceIdListScraper(year, year)
        todo_race_ids = scraper.scrape_raceid_list()
        todo_race_ids = list(set(todo_race_ids) - set(done_race_ids))
        for race_id in todo_race_ids:
            if race_id[4:6] in ["63", "64", "65", "66"]:
                # ばんえいのためスキップ
                continue
            try:
                race_card2db = RaceCard2DB(race_id)
                race_card2db.add2db()
            except Exception as e:
                logger.error(f"予想外のエラーが発生しました\n{e}")


def scrape_all_horse_id():
    """
    resultからhorse_idを取得してDBにない情報をスクレイピングしてDBに追加する
    """
    session = get_session()
    done_horse_ids = session.query(Ped.horse_id).all()
    done_horse_ids = [horse_id[0] for horse_id in done_horse_ids]
    todo_horse_ids = session.query(Result.horse_id).all()
    todo_horse_ids = [horse_id[0] for horse_id in todo_horse_ids]
    todo_horse_ids = list(set(todo_horse_ids) - set(done_horse_ids))
    for horse_id in todo_horse_ids:
        ped2db = Ped2DB(horse_id)
        ped2db.add2db()


def scrape_all_weather():
    """
    race_infoからplaceとdateを取得してDBにない情報をスクレイピングしてDBに追加する
    """
    session = get_session()
    done_keys = session.query(Weather.place, Weather.date).all()
    todo_keys = session.query(RaceInfo.place, RaceInfo.date).all()
    todo_keys = list(set(todo_keys) - set(done_keys))
    for key in todo_keys:
        meteorological_agency2db = MeteorologicalAgency2DB(key[0], key[1])
        meteorological_agency2db.add2db()


def label_encode1():
    """
    必要な情報を取得してラベルエンコーディングを行う
    ほとんど更新する必要がない群
    """
    session = get_session()
    # track
    todo_track_list = session.query(distinct(RaceInfo.track)).all()
    todo_track_list = [track[0] for track in todo_track_list]
    done_track_list = session.query(LabelEncoderTrack.track).all()
    done_track_list = [track[0] for track in done_track_list]
    todo_track_list = list(set(todo_track_list) - set(done_track_list))
    for track in todo_track_list:
        label_encoder_track = LabelEncoderTrack(track=track)
        session.add(label_encoder_track)
    logger.info("trackのラベルエンコーディング完了")
    session.commit()

    # direction
    todo_direction_list = session.query(distinct(RaceInfo.direction)).all()
    todo_direction_list = [direction[0] for direction in todo_direction_list]
    done_direction_list = session.query(LabelEncoderDirection.direction).all()
    done_direction_list = [direction[0] for direction in done_direction_list]
    todo_direction_list = list(set(todo_direction_list) - set(done_direction_list))
    for direction in todo_direction_list:
        label_encoder_direction = LabelEncoderDirection(direction=direction)
        session.add(label_encoder_direction)
    logger.info("directionのラベルエンコーディング完了")
    session.commit()

    # track_condition
    todo_track_condition_list = session.query(distinct(RaceInfo.track_condition)).all()
    todo_track_condition_list = [
        track_condition[0] for track_condition in todo_track_condition_list
    ]
    done_track_condition_list = session.query(
        LabelEncoderTrackCondition.track_condition
    ).all()
    done_track_condition_list = [
        track_condition[0] for track_condition in done_track_condition_list
    ]
    todo_track_condition_list = list(
        set(todo_track_condition_list) - set(done_track_condition_list)
    )
    for track_condition in todo_track_condition_list:
        label_encoder_track_condition = LabelEncoderTrackCondition(
            track_condition=track_condition
        )
        session.add(label_encoder_track_condition)
    logger.info("track_conditionのラベルエンコーディング完了")
    session.commit()

    # weather
    todo_weather_list = session.query(distinct(RaceInfo.weather)).all()
    todo_weather_list = [weather[0] for weather in todo_weather_list]
    done_weather_list = session.query(LabelEncoderWeather.weather).all()
    done_weather_list = [weather[0] for weather in done_weather_list]
    todo_weather_list = list(set(todo_weather_list) - set(done_weather_list))
    for weather in todo_weather_list:
        label_encoder_weather = LabelEncoderWeather(weather=weather)
        session.add(label_encoder_weather)
    logger.info("weatherのラベルエンコーディング完了")
    session.commit()

    # detail_course
    todo_detail_course_list = session.query(distinct(RaceInfo.detail_course)).all()
    todo_detail_course_list = [
        detail_course[0] for detail_course in todo_detail_course_list
    ]
    done_detail_course_list = session.query(
        LabelEncoderDetailCourse.detail_course
    ).all()
    done_detail_course_list = [
        detail_course[0] for detail_course in done_detail_course_list
    ]
    todo_detail_course_list = list(
        set(todo_detail_course_list) - set(done_detail_course_list)
    )
    for detail_course in todo_detail_course_list:
        label_encoder_detail_course = LabelEncoderDetailCourse(
            detail_course=detail_course
        )
        session.add(label_encoder_detail_course)
    logger.info("detail_courseのラベルエンコーディング完了")
    session.commit()

    # place
    todo_place_list = session.query(distinct(RaceInfo.place)).all()
    todo_place_list = [place[0] for place in todo_place_list]
    done_place_list = session.query(LabelEncoderPlace.place).all()
    done_place_list = [place[0] for place in done_place_list]
    todo_place_list = list(set(todo_place_list) - set(done_place_list))
    for place in todo_place_list:
        label_encoder_place = LabelEncoderPlace(place=place)
        session.add(label_encoder_place)
    logger.info("placeのラベルエンコーディング完了")
    session.commit()

    # sex
    todo_sex_list = session.query(distinct(Result.sex)).all()
    todo_sex_list = [sex[0] for sex in todo_sex_list]
    done_sex_list = session.query(LabelEncoderSex.sex).all()
    done_sex_list = [sex[0] for sex in done_sex_list]
    todo_sex_list = list(set(todo_sex_list) - set(done_sex_list))
    for sex in todo_sex_list:
        label_encoder_sex = LabelEncoderSex(sex=sex)
        session.add(label_encoder_sex)
    logger.info("sexのラベルエンコーディング完了")
    session.commit()

    session.close()


def label_encode2():
    """
    必要な情報を取得してラベルエンコーディングを行う
    頻繁に更新する群
    """
    session = get_session()

    # horse
    todo_horse_list = session.query(distinct(Result.horse_id)).all()
    todo_horse_list = [horse[0] for horse in todo_horse_list]
    done_horse_list = session.query(LabelEncoderHorseId.horse_id).all()
    done_horse_list = [horse[0] for horse in done_horse_list]
    todo_horse_list = list(set(todo_horse_list) - set(done_horse_list))
    for horse in todo_horse_list:
        horse_id_scraper = HorseIdScraper(horse)
        name = horse_id_scraper.scrape()
        label_encoder_horse_id = LabelEncoderHorseId(horse_id=horse, name=name)
        session.add(label_encoder_horse_id)
    logger.info("horseのラベルエンコーディング完了")
    session.commit()

    # trainer
    todo_trainer_list = session.query(distinct(Result.trainer_id)).all()
    todo_trainer_list = [trainer[0] for trainer in todo_trainer_list]
    done_trainer_list = session.query(LabelEncoderTrainerId.trainer_id).all()
    done_trainer_list = [trainer[0] for trainer in done_trainer_list]
    todo_trainer_list = list(set(todo_trainer_list) - set(done_trainer_list))
    for trainer in todo_trainer_list:
        trainer_id_scraper = TrainerIdScraper(trainer)
        name = trainer_id_scraper.scrape()
        label_encoder_trainer_id = LabelEncoderTrainerId(trainer_id=trainer, name=name)
        session.add(label_encoder_trainer_id)
    logger.info("trainerのラベルエンコーディング完了")
    session.commit()

    # jocky
    todo_jocky_list = session.query(distinct(Result.jockey_id)).all()
    todo_jocky_list = [jocky[0] for jocky in todo_jocky_list]
    done_jocky_list = session.query(LabelEncoderJockyId.jockey_id).all()
    done_jocky_list = [jocky[0] for jocky in done_jocky_list]
    todo_jocky_list = list(set(todo_jocky_list) - set(done_jocky_list))
    for jocky in todo_jocky_list:
        jockey_id_scraper = JockyIdScraper(jocky)
        name = jockey_id_scraper.scrape()
        label_encoder_jockey_id = LabelEncoderJockyId(jockey_id=jocky, name=name)
        session.add(label_encoder_jockey_id)
    logger.info("jockyのラベルエンコーディング完了")
    session.commit()

    # owner
    todo_owner_list = session.query(distinct(Result.owner_id)).all()
    todo_owner_list = [owner[0] for owner in todo_owner_list]
    done_owner_list = session.query(LabelEncoderOwnerId.owner_id).all()
    done_owner_list = [owner[0] for owner in done_owner_list]
    todo_owner_list = list(set(todo_owner_list) - set(done_owner_list))
    for owner in todo_owner_list:
        owner_id_scraper = OwnerIdScraper(owner)
        name = owner_id_scraper.scrape()
        label_encoder_owner_id = LabelEncoderOwnerId(owner_id=owner, name=name)
        session.add(label_encoder_owner_id)
    logger.info("ownerのラベルエンコーディング完了")
    session.commit()

    session.close()


def label_encode3():
    """
    必要な情報を取得してラベルエンコーディングを行う
    頻繁に更新する群
    血統
    """
    session = get_session()

    # 雄系列
    todo_f_list = session.query(distinct(Ped.f_id)).all()
    todo_f_list = [f[0] for f in todo_f_list]
    todo_ff_list = session.query(distinct(Ped.ff_id)).all()
    todo_ff_list = [ff[0] for ff in todo_ff_list]
    todo_mf_list = session.query(distinct(Ped.mf_id)).all()
    todo_mf_list = [mf[0] for mf in todo_mf_list]
    done_sire_list = session.query(LabelEncoderSireId.sire_id).all()
    done_sire_list = [f[0] for f in done_sire_list]
    todo_sire_list = list(
        set(todo_f_list + todo_ff_list + todo_mf_list) - set(done_sire_list)
    )
    for sire in todo_sire_list:
        label_encoder_sire_id = LabelEncoderSireId(sire_id=sire)
        session.add(label_encoder_sire_id)
    logger.info("sireのラベルエンコーディング完了")
    session.commit()

    # 雄系列
    todo_m_list = session.query(distinct(Ped.m_id)).all()
    todo_m_list = [m[0] for m in todo_m_list]
    todo_fm_list = session.query(distinct(Ped.fm_id)).all()
    todo_fm_list = [fm[0] for fm in todo_fm_list]
    todo_mm_list = session.query(distinct(Ped.mm_id)).all()
    todo_mm_list = [mm[0] for mm in todo_mm_list]
    done_dam_list = session.query(LabelEncoderDamId.dam_id).all()
    done_dam_list = [m[0] for m in done_dam_list]
    todo_dam_list = list(
        set(todo_m_list + todo_fm_list + todo_mm_list) - set(done_dam_list)
    )
    for dam in todo_dam_list:
        label_encoder_dam_id = LabelEncoderDamId(dam_id=dam)
        session.add(label_encoder_dam_id)
    logger.info("damのラベルエンコーディング完了")
    session.commit()


if __name__ == "__main__":
    scrape_all_race_id(2023, 2023)

    scrape_all_horse_id()

    scrape_all_weather()

    label_encode1()

    label_encode2()

    label_encode3()
