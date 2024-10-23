# er.dioの赤色のテーブルを定義
# netkeibaから取得したデータに関するもの
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


# race_infoテーブルを定義
class RaceInfo(Base):
    __tablename__ = "race_info"

    race_id = Column(String(15), primary_key=True)  # レースID
    track = Column(String(10), nullable=False, index=True)  # 馬場
    direction = Column(String(10), nullable=False, index=True)  # レースの方向
    distance = Column(Integer, nullable=True)  # 距離
    detail_course = Column(String(32), nullable=False, index=True)  # コース詳細
    weather = Column(String(10), nullable=False, index=True)  # 天気
    track_condition = Column(String(10), nullable=False, index=True)  # 馬場状態
    starting_time = Column(Time, nullable=True)  # 出走時刻
    date = Column(Date, nullable=True)  # レース日
    inning = Column(Integer, nullable=True)  # 回
    day = Column(Integer, nullable=True)  # 日目
    place = Column(String(10), nullable=False, index=True)  # 場所
    round = Column(Integer, nullable=True)  # ラウンド
    cos_starting_time = Column(Float, nullable=True)  # 出走時刻_cos
    sin_starting_time = Column(Float, nullable=True)  # 出走時刻_sin
    cos_date = Column(Float, nullable=True)  # 日付_cos
    sin_date = Column(Float, nullable=True)  # 日付_sin
    other_info = Column(String(256), nullable=True)  # その他の情報
    sum_prize = Column(Float, nullable=True)  # レース合計賞金
    log_sum_prize = Column(Float, nullable=True)  # レース合計賞金の対数
    num_horse = Column(Integer, nullable=True)  # 馬数

    # relationshipを定義
    payback = relationship("Payback", back_populates="race_info", uselist=False)
    result = relationship("Result", back_populates="race_info", uselist=False)


# paybackテーブルを定義
class Payback(Base):
    __tablename__ = "payback"

    race_id = Column(
        String(15), ForeignKey("race_info.race_id"), primary_key=True
    )  # 外部キー (race_infoのrace_id)
    win = Column(Integer, nullable=True)  # 単勝
    show1 = Column(Integer, nullable=True)  # 複勝1着
    show2 = Column(Integer, nullable=True)  # 複勝2着
    show3 = Column(Integer, nullable=True)  # 複勝3着
    quinella = Column(Integer, nullable=True)  # 馬連
    exacta = Column(Integer, nullable=True)  # 馬単
    trio = Column(Integer, nullable=True)  # 三連複
    trifecta = Column(Integer, nullable=True)  # 三連単

    # relationshipを定義
    race_info = relationship("RaceInfo", back_populates="payback")


# weatherテーブルを定義
class Weather(Base):
    __tablename__ = "weather"

    place = Column(String(10), primary_key=True)  # 場所
    date = Column(Date, primary_key=True)  # 日付
    time = Column(Time, primary_key=True)  # 時間

    precipitation = Column(Float, nullable=True)  # 降水量
    temperature = Column(Float, nullable=True)  # 気温
    wind_speed = Column(Float, nullable=True)  # 風速
    wind_angle = Column(String(10), nullable=False, index=True)  # 風向
    sunshine_hour = Column(Float, nullable=True)  # 日照時間


# resultテーブルを定義
class Result(Base):
    __tablename__ = "result"

    race_id = Column(String(15), ForeignKey("race_info.race_id"), primary_key=True)
    horse_number = Column(Integer, primary_key=True)

    time = Column(Float, nullable=True)  # タイム
    prize = Column(Integer, nullable=True)  # 賞金
    passing_order = Column(String(50), nullable=True)  # 通過順
    second_half_time = Column(Float, nullable=True)  # 後半タイム
    rank = Column(Integer, nullable=True)  # 着順
    barrier_number = Column(Integer, nullable=True)  # 枠番
    horse_id = Column(String(32), nullable=True)  # 馬ID
    jockey_id = Column(String(12), nullable=True)  # 騎手ID
    trainer_id = Column(String(12), nullable=True)  # 調教師ID
    owner_id = Column(String(12), nullable=True)  # 馬主ID
    sex = Column(String(10), nullable=False)  # 性別
    age = Column(Integer, nullable=True)  # 年齢
    handicap = Column(Float, nullable=True)  # 斤量
    time_difference = Column(Float, nullable=True)  # タイム差
    odds = Column(Float, nullable=True)  # オッズ
    popularity = Column(Integer, nullable=True)  # 人気
    weight = Column(Float, nullable=True)  # 体重
    weight_difference = Column(Float, nullable=True)  # 体重差
    corner_1 = Column(Integer, nullable=True)  # コーナー1
    corner_2 = Column(Integer, nullable=True)  # コーナー2
    corner_3 = Column(Integer, nullable=True)  # コーナー3
    corner_4 = Column(Integer, nullable=True)  # コーナー4
    relative_corner_1 = Column(Float, nullable=True)  # コーナー1の相対位置
    relative_corner_2 = Column(Float, nullable=True)  # コーナー2の相対位置
    relative_corner_3 = Column(Float, nullable=True)  # コーナー3の相対位置
    relative_corner_4 = Column(Float, nullable=True)  # コーナー4の相対位置
    diff_corner_1_2 = Column(Float, nullable=True)  # 相対コーナー1とコーナー2の差
    diff_corner_1_3 = Column(Float, nullable=True)  # 相対コーナー1とコーナー3の差
    diff_corner_1_4 = Column(Float, nullable=True)  # 相対コーナー1とコーナー4の差
    diff_corner_2_3 = Column(Float, nullable=True)  # 相対コーナー2とコーナー3の差
    diff_corner_2_4 = Column(Float, nullable=True)  # 相対コーナー2とコーナー4の差
    diff_corner_3_4 = Column(Float, nullable=True)  # 相対コーナー3とコーナー4の差
    relative_rank = Column(Float, nullable=True)  # 相対順位
    relative_popularity = Column(Float, nullable=True)  # 相対人気
    inverse_odds = Column(Float, nullable=True)  # 逆オッズ
    log_odds = Column(Float, nullable=True)  # オッズの対数
    log_prize = Column(Float, nullable=True)  # 賞金の対数

    # relationshipを定義
    race_info = relationship("RaceInfo", back_populates="result")


# pedテーブルを定義
class Ped(Base):
    __tablename__ = "ped"

    horse_id = Column(String(32), primary_key=True)  # 馬ID
    f_id = Column(String(32), nullable=True)  # 父ID
    m_id = Column(String(32), nullable=True)  # 母ID
    ff_id = Column(String(32), nullable=True)  # 父父ID
    fm_id = Column(String(32), nullable=True)  # 父母ID
    mf_id = Column(String(32), nullable=True)  # 母父ID
    mm_id = Column(String(32), nullable=True)  # 母母ID
    fff_id = Column(String(32), nullable=True)  # 父父父ID
    ffm_id = Column(String(32), nullable=True)  # 父父母ID
    fmf_id = Column(String(32), nullable=True)  # 父母父ID
    fmm_id = Column(String(32), nullable=True)  # 父母母ID
    mff_id = Column(String(32), nullable=True)  # 母父父ID
    mfm_id = Column(String(32), nullable=True)  # 母父母ID
    mmf_id = Column(String(32), nullable=True)  # 母母父ID
    mmm_id = Column(String(32), nullable=True)  # 母母母ID
    ffff_id = Column(String(32), nullable=True)  # 父父父父ID
    fffm_id = Column(String(32), nullable=True)  # 父父父母ID
    ffmf_id = Column(String(32), nullable=True)  # 父父母父ID
    ffmm_id = Column(String(32), nullable=True)  # 父父母母ID
    fmff_id = Column(String(32), nullable=True)  # 父母父父ID
    fmfm_id = Column(String(32), nullable=True)  # 父母父母ID
    fmmf_id = Column(String(32), nullable=True)  # 父母母父ID
    fmmm_id = Column(String(32), nullable=True)  # 父母母母ID
    mfff_id = Column(String(32), nullable=True)  # 母父父父ID
    mffm_id = Column(String(32), nullable=True)  # 母父父母ID
    mfmf_id = Column(String(32), nullable=True)  # 母父母父ID
    mfmm_id = Column(String(32), nullable=True)  # 母父母母ID
    mmff_id = Column(String(32), nullable=True)  # 母母父父ID
    mmfm_id = Column(String(32), nullable=True)  # 母母父母ID
    mmmf_id = Column(String(32), nullable=True)  # 母母母父ID
    mmmm_id = Column(String(32), nullable=True)  # 母母母母ID
    fffff_id = Column(String(32), nullable=True)  # 父父父父父ID
    ffffm_id = Column(String(32), nullable=True)  # 父父父父母ID
    fffmf_id = Column(String(32), nullable=True)  # 父父父母父ID
    fffmm_id = Column(String(32), nullable=True)  # 父父父母母ID
    ffmff_id = Column(String(32), nullable=True)  # 父父母父父ID
    ffmfm_id = Column(String(32), nullable=True)  # 父父母父母ID
    ffmmf_id = Column(String(32), nullable=True)  # 父父母母父ID
    ffmmm_id = Column(String(32), nullable=True)  # 父父母母母ID
    fmfff_id = Column(String(32), nullable=True)  # 父母父父父ID
    fmffm_id = Column(String(32), nullable=True)  # 父母父父母ID
    fmfmf_id = Column(String(32), nullable=True)  # 父母父母父ID
    fmfmm_id = Column(String(32), nullable=True)  # 父母父母母ID
    fmmff_id = Column(String(32), nullable=True)  # 父母母父父ID
    fmmfm_id = Column(String(32), nullable=True)  # 父母母父母ID
    fmmmf_id = Column(String(32), nullable=True)  # 父母母母父ID
    fmmmm_id = Column(String(32), nullable=True)  # 父母母母母ID
    mffff_id = Column(String(32), nullable=True)  # 母父父父父ID
    mfffm_id = Column(String(32), nullable=True)  # 母父父父母ID
    mffmf_id = Column(String(32), nullable=True)  # 母父父母父ID
    mffmm_id = Column(String(32), nullable=True)  # 母父父母母ID
    mfmff_id = Column(String(32), nullable=True)  # 母父母父父ID
    mfmfm_id = Column(String(32), nullable=True)  # 母父母父母ID
    mfmmf_id = Column(String(32), nullable=True)  # 母父母母父ID
    mfmmm_id = Column(String(32), nullable=True)  # 母父母母母ID
    mmfff_id = Column(String(32), nullable=True)  # 母母父父父ID
    mmffm_id = Column(String(32), nullable=True)  # 母母父父母ID
    mmfmf_id = Column(String(32), nullable=True)  # 母母父母父ID
    mmfmm_id = Column(String(32), nullable=True)  # 母母父母母ID
    mmmff_id = Column(String(32), nullable=True)  # 母母母父父ID
    mmmfm_id = Column(String(32), nullable=True)  # 母母母父母ID
    mmmmf_id = Column(String(32), nullable=True)  # 母母母母父ID
    mmmmm_id = Column(String(32), nullable=True)  # 母母母母母ID
