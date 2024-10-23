# er.dioの青色のテーブルを定義
# label_enocderやbinningなどの処理を行う際に使用するテーブルを定義
from sqlalchemy import create_engine, Column, Integer, ForeignKey, Index
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from src.utils._variables import (
    AWS_RDS_USER_NAME,
    AWS_RDS_PASSWORD,
    AWS_RDS_DB_NAME,
    AWS_RDS_DB_HOST,
)
from src.mysql.base import Base


# label_encoder用のテーブルを定義
class LabelEncoderTrack(Base):
    __tablename__ = "label_encoder_track"
    track = Column(String(10))  # 馬場
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル


class LabelEncoderDirection(Base):
    __tablename__ = "label_encoder_direction"
    direction = Column(String(10))  # レースの方向
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル


class LabelEncoderTrackCondition(Base):
    __tablename__ = "label_encoder_track_condition"
    track_condition = Column(String(10))  # 馬場状態
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル


class LabelEncoderWeather(Base):
    __tablename__ = "label_encoder_weather"
    weather = Column(String(10))  # 天気
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル


class LabelEncoderDetailCourse(Base):
    __tablename__ = "label_encoder_detail_course"
    detail_course = Column(String(32))  # コース詳細
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル


class LabelEncoderPlace(Base):
    __tablename__ = "label_encoder_place"
    place = Column(String(10))  # 場所
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル


class LabelEncoderSex(Base):
    __tablename__ = "label_encoder_sex"
    sex = Column(String(10))  # 性別
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル


class LabelEncoderHorseId(Base):
    __tablename__ = "label_encoder_horse_id"
    horse_id = Column(String(32))  # 馬ID
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル
    name = Column(String(32), nullable=True)  # 馬名


class LabelEncoderJockyId(Base):
    __tablename__ = "label_encoder_jockey_id"
    jockey_id = Column(String(12))  # 騎手ID
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル
    name = Column(String(32), nullable=True)  # 騎手名


class LabelEncoderTrainerId(Base):
    __tablename__ = "label_encoder_trainer_id"
    trainer_id = Column(String(12))  # 調教師ID
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル
    name = Column(String(32), nullable=True)  # 調教師名


class LabelEncoderOwnerId(Base):
    __tablename__ = "label_encoder_owner_id"
    owner_id = Column(String(12))  # 馬主ID
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル
    name = Column(String(32), nullable=True)  # 馬主名


class LabelEncoderSireId(Base):
    __tablename__ = "label_encoder_sire_id"
    sire_id = Column(String(32))  # 父馬ID
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル


class LabelEncoderDamId(Base):
    __tablename__ = "label_encoder_dam_id"
    dam_id = Column(String(32))  # 母馬ID
    label = Column(Integer, primary_key=True, autoincrement=True)  # ラベル
