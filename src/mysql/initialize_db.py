from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.mysql.base import Base
from src.utils._variables import (
    AWS_RDS_USER_NAME,
    AWS_RDS_PASSWORD,
    AWS_RDS_DB_NAME,
    AWS_RDS_DB_HOST,
)
from src.mysql.models.db1 import RaceInfo, Result, Ped, Weather, Payback
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


def get_session():
    engine = create_engine(
        f"mysql+pymysql://{AWS_RDS_USER_NAME}:{AWS_RDS_PASSWORD}@{AWS_RDS_DB_HOST}:3306/{AWS_RDS_DB_NAME}",
        connect_args={"ssl": {"ssl_ca": "global-bundle.pem"}},
    )

    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成
    session = SessionClass()

    return session


def create_database():
    inputinput = input(
        "DBを初期化しますか?本当に初期化する場合はyesと入力してください:"
    )
    if inputinput != "yes":
        print("DBの初期化を中止しました")
        return

    engine = create_engine(
        f"mysql+pymysql://{AWS_RDS_USER_NAME}:{AWS_RDS_PASSWORD}@{AWS_RDS_DB_HOST}:3306/{AWS_RDS_DB_NAME}",
        connect_args={"ssl": {"ssl_ca": "global-bundle.pem"}},
    )

    Base.metadata.drop_all(engine)  # すべてのテーブルを削除
    Base.metadata.create_all(engine)  # テーブルを作成

    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成
    session = SessionClass()

    # race_info = RaceInfo(
    #     race_id=1,
    #     track="ダート",
    #     direction="右",
    #     distance=1200,
    #     detail_course="ダ1200",
    #     weather="晴",
    #     track_condition="良",
    #     starting_time="13:00:00",
    #     date="2021-01-01",
    #     inning=1,
    #     place="中山",
    #     round=1,
    #     day=1,
    #     sum_prize=1000,
    #     log_sum_prize=3.0,
    # )
    # session.add(race_info)

    # payback = Payback(race_id=1, win=1999)
    # session.add(payback)

    session.commit()
    session.close()


if __name__ == "__main__":
    print("AAAAAAAAAAAAAAAAAA")
    create_database()
    print("BBBBBBBBBBBBBBBBBB")
