# 馬の過去の戦績などの特徴エンジニアリングしたデータを作成する
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
from src.mysql.models.db3 import EngineeredFeature


def add_engineered_feature():
    """
    dummyとして適当な値を追加する
    """
    session = get_session()
    done_keys = session.query(
        EngineeredFeature.race_id, EngineeredFeature.horse_number
    ).all()
    todo_keys = session.query(Result.race_id, Result.horse_number).all()
    todo_keys = list(set(todo_keys) - set(done_keys))
    for key in todo_keys:
        engineered_feature = EngineeredFeature(
            race_id=key[0],
            horse_number=key[1],
            additional_feature=np.random.randint(0, 100),
        )
        session.add(engineered_feature)
    session.commit()
    session.close()


if __name__ == "__main__":
    add_engineered_feature()
