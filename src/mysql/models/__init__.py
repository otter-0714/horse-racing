import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from src.mysql.models.db1 import (
    RaceInfo,
    Result,
    Ped,
    Weather,
)
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
    LabelEncoderDamId
)
