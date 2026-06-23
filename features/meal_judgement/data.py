from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).parent / "data"
LOCAL_NUTRITION_DB = DATA_DIR / "food_nutrition.csv.gz"

STANDARD_COLUMNS = [
    "name_ko",
    "serving",
    "category",
    "source",
    "calories",
    "carbs",
    "protein",
    "fat",
    "sodium",
    "sugar",
    "water",
    "ash",
    "dietary_fiber",
    "calcium",
    "iron",
    "phosphorus",
    "potassium",
    "vitamin_a",
    "retinol",
    "beta_carotene",
    "thiamin",
    "riboflavin",
    "niacin",
    "vitamin_c",
    "vitamin_d",
    "cholesterol",
    "saturated_fat",
    "trans_fat",
    "unsaturated_fat",
    "omega3",
    "omega6",
    "magnesium",
    "zinc",
    "caffeine",
]

NUMERIC_COLUMNS = [
    column
    for column in STANDARD_COLUMNS
    if column not in ("name_ko", "serving", "category", "source")
]


def _parse_number(value):
    try:
        return float(str(value).replace(",", "").split()[0])
    except Exception:
        return None


def _serving_unit(serving):
    text = str(serving).strip().lower()
    if "ml" in text:
        return "ml"
    if "g" in text:
        return "g"
    return ""


def _serving_amount(serving):
    text = str(serving).strip().lower().replace(",", "")
    number = ""
    for char in text:
        if char.isdigit() or char == ".":
            number += char
        elif number:
            break
    return _parse_number(number)


def _estimated_portion(name, unit):
    compact = str(name).replace(" ", "")

    portion_rules = [
        (("찌개", "국", "탕", "전골", "스튜", "죽"), 400),
        (("라면", "우동", "국수", "냉면", "칼국수", "짬뽕", "짜장면"), 500),
        (("덮밥", "비빔밥", "볶음밥", "카레", "오므라이스"), 400),
        (("제육", "불고기", "닭갈비", "오징어볶음", "돼지고기볶음", "볶음"), 250),
        (("구이", "스테이크", "삼겹살", "목살", "갈비", "수육", "보쌈"), 250),
        (("조림", "찜", "찜닭", "갈비찜"), 300),
        (("전", "부침개", "파전", "김치전"), 180),
        (("만두", "교자"), 200),
        (("샐러드",), 180),
        (("떡볶이", "순대", "튀김"), 300),
        (("김밥", "샌드위치", "버거", "햄버거"), 250),
        (("피자",), 150),
        (("치킨", "닭강정"), 200),
        (("아이스크림", "빙수"), 150),
        (("케이크", "빵", "도넛", "쿠키"), 100),
        (("커피", "라떼", "주스", "음료", "스무디", "차"), 250),
    ]

    for keywords, amount in portion_rules:
        if any(keyword in compact for keyword in keywords):
            return amount

    return 250 if unit == "ml" else 200


def normalize_to_meal_portion(result):
    serving = result.get("serving", "")
    amount = _serving_amount(serving)
    unit = _serving_unit(serving)

    if amount is None or unit not in ("g", "ml"):
        result["display_serving"] = serving or "1인분"
        result["serving_note"] = ""
        return result

    portion_amount = _estimated_portion(result.get("name_ko", ""), unit)
    scale = portion_amount / amount

    for column in NUMERIC_COLUMNS:
        value = _parse_number(result.get(column))
        if value is not None:
            result[column] = round(value * scale, 2)

    display_unit = "ml" if unit == "ml" else "g"
    result["display_serving"] = f"1인분 추정 {int(portion_amount)}{display_unit}"
    result["serving_note"] = f"DB {serving} 기준을 1인분 추정량으로 환산"
    result["original_serving"] = serving
    result["portion_scale"] = scale
    return result


def _rank_matches(match, query):
    ranked = match.copy()
    ranked["match_rank"] = 50
    ranked.loc[ranked["search_name"] == query, "match_rank"] = 0
    ranked.loc[ranked["search_name"].str.contains(query, regex=False, na=False), "match_rank"] = ranked[
        "match_rank"
    ].clip(upper=10)
    beverage_query = any(
        keyword in query
        for keyword in ("커피", "라떼", "주스", "음료", "스무디", "차", "밀크티", "버블티", "에이드")
    )
    preferred_unit = "100ml" if beverage_query else "100g"
    ranked["unit_rank"] = ranked["serving"].astype(str).str.contains(preferred_unit, regex=False, na=False).map(
        {True: 0, False: 1}
    )
    ranked["name_len"] = ranked["search_name"].str.len()
    return ranked.sort_values(["match_rank", "unit_rank", "name_len"])


@st.cache_data(show_spinner=False)
def load_local_nutrition_db():
    if not LOCAL_NUTRITION_DB.exists():
        return pd.DataFrame()

    df = pd.read_csv(LOCAL_NUTRITION_DB, encoding="utf-8-sig", low_memory=False)

    for column in STANDARD_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    mapped = df[STANDARD_COLUMNS].copy()
    mapped["name_ko"] = mapped["name_ko"].fillna("").astype(str).str.strip()
    mapped = mapped[mapped["name_ko"].ne("")]
    mapped["search_name"] = (
        mapped["name_ko"].str.replace(" ", "", regex=False).str.lower()
    )
    return mapped


def lookup_local_nutrition(food_name):
    df = load_local_nutrition_db()
    if df.empty:
        return None

    query = str(food_name).replace(" ", "").lower().strip()
    if not query:
        return None

    match = df.loc[df["search_name"] == query]
    if match.empty:
        match = df.loc[df["search_name"].str.contains(query, regex=False, na=False)]
    if match.empty and len(query) >= 2:
        compact_names = df["search_name"]
        match = df.loc[compact_names.apply(lambda value: bool(value) and value in query)]
    if match.empty:
        return None

    row = _rank_matches(match, query).iloc[0].to_dict()
    result = {
        "name_ko": row.get("name_ko") or food_name,
        "calories": row.get("calories", "-"),
        "carbs": row.get("carbs", "-"),
        "protein": row.get("protein", "-"),
        "fat": row.get("fat", "-"),
        "sodium": row.get("sodium", "-"),
        "sugar": row.get("sugar", "-"),
        "serving": row.get("serving", "1 serving"),
        "source": row.get("source", "local"),
    }
    for column in STANDARD_COLUMNS:
        if column not in result:
            result[column] = row.get(column, "-")
    return normalize_to_meal_portion(result)
