# er.dioの緑色のテーブルを定義
# 馬の過去の戦績などの特徴エンジニアリングしたテーブルを定義

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


# なんか適当にテーブルを作成
class EngineeredFeature(Base):
    __tablename__ = "engineered_feature"
    race_id = Column(String(15), primary_key=True)  # レースID
    horse_number = Column(Integer, primary_key=True)  # 馬番

    additional_feature = Column(Integer, nullable=True)  # 追加した特徴量
