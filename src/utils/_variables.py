import os
import pandas as pd
import pickle
import sys
import re
import json

KIND_OF_TICKET = [
    "単勝",
    "複勝1着",
    "複勝2着",
    "複勝3着",
    "馬連",
    "馬単",
    "三連複",
    "三連単",
]

path2secret = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "credentials", "secret.json"
)
with open(path2secret, "r") as f:
    data = json.load(f)
    AWS_RDS_USER_NAME = data["AWS_RDS_USER_NAME"]
    AWS_RDS_PASSWORD = data["AWS_RDS_PASSWORD"]
    AWS_RDS_DB_NAME = data["AWS_RDS_DB_NAME"]
    AWS_RDS_DB_HOST = data["AWS_RDS_DB_HOST"]


class _variables:
    def __init__(self):
        pass


if __name__ == "__main__":
    variables = _variables()
