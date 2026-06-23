import re
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).parent / "data"
COMPLETE_LIFE_TABLE = DATA_DIR / "complete_life_table_2024.csv"
HEALTH_LIFE_TABLE = DATA_DIR / "health_life_expectancy_2024.csv"


def _age_to_int(value):
    text = str(value).strip()
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


@st.cache_data(show_spinner=False)
def load_complete_life_table():
    raw = pd.read_csv(COMPLETE_LIFE_TABLE, header=[0, 1])
    frame = pd.DataFrame(
        {
            "age": raw[("연령별", "연령별")].map(_age_to_int),
            "남성": raw[("2024", "기대여명(남자) (년)")],
            "여성": raw[("2024", "기대여명(여자) (년)")],
            "전체": raw[("2024", "기대여명(전체) (년)")],
        }
    )
    return frame.dropna(subset=["age"]).astype({"age": int})


@st.cache_data(show_spinner=False)
def load_health_life_table():
    raw = pd.read_csv(HEALTH_LIFE_TABLE, header=[0, 1])
    frame = pd.DataFrame(
        {
            "gender": raw[("성별", "성별")].replace({"남자": "남성", "여자": "여성", "남녀전체": "전체"}),
            "age": raw[("연령별", "연령별")].map(_age_to_int),
            "disease_free_years": raw[("2024", "유병기간 제외 기대여명 (년)")],
            "self_rated_healthy_years": raw[("2024", "주관적 건강평가 기대여명 (년)")],
        }
    )
    return frame.dropna(subset=["age"]).astype({"age": int})


def get_remaining_life_years(gender, age):
    table = load_complete_life_table()
    age = min(max(int(age), int(table["age"].min())), int(table["age"].max()))
    matched = table.loc[table["age"] == age]
    if matched.empty:
        matched = table.iloc[[(table["age"] - age).abs().idxmin()]]
    return float(matched.iloc[0][gender])


def get_health_life_years(gender, age):
    table = load_health_life_table()
    gender_table = table.loc[table["gender"] == gender]
    if gender_table.empty:
        gender_table = table.loc[table["gender"] == "전체"]

    nearest_index = (gender_table["age"] - int(age)).abs().idxmin()
    row = gender_table.loc[nearest_index]
    return {
        "nearest_age": int(row["age"]),
        "disease_free_years": float(row["disease_free_years"]),
        "self_rated_healthy_years": float(row["self_rated_healthy_years"]),
    }
