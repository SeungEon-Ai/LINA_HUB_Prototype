import re

import pandas as pd
import streamlit as st

from .config import DATA_PATH


TEXT_COLUMNS = [
    "term_title",
    "term_ko",
    "term_hanja",
    "term_en",
    "plain_definition",
    "source_definition",
    "source_summary",
    "source_full_text",
    "category",
    "domain_main",
    "include_hits",
]


@st.cache_data(show_spinner=False)
def load_terms() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH).fillna("")
    for col in TEXT_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df["best_definition"] = df.apply(best_definition, axis=1)
    df["search_blob"] = df[TEXT_COLUMNS].astype(str).agg(" ".join, axis=1).str.lower()
    return df


def best_definition(row: pd.Series) -> str:
    for col in ["plain_definition", "source_definition", "source_summary"]:
        value = str(row.get(col, "")).strip()
        if value:
            return value
    full_text = str(row.get("source_full_text", "")).strip()
    return full_text[:700] + ("..." if len(full_text) > 700 else "")


def normalize_query(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def search_terms(df: pd.DataFrame, query: str, limit: int = 6) -> pd.DataFrame:
    q = normalize_query(query)
    if not q:
        return df[df["record_type"] == "dictionary_term"].head(limit)

    parts = [part for part in q.split(" ") if part]
    candidates = df.copy()
    mask = candidates["search_blob"].apply(lambda blob: all(part in blob for part in parts))
    results = candidates[mask].copy()
    if results.empty:
        mask = candidates["search_blob"].apply(lambda blob: any(part in blob for part in parts))
        results = candidates[mask].copy()

    def score(row: pd.Series) -> int:
        title = f"{row.get('term_title', '')} {row.get('term_ko', '')}".lower()
        blob = row.get("search_blob", "")
        exact = 20 if q in title else 0
        title_hits = sum(6 for part in parts if part in title)
        body_hits = sum(1 for part in parts if part in blob)
        term_bonus = 5 if row.get("record_type") == "dictionary_term" else 0
        return exact + title_hits + body_hits + term_bonus

    if not results.empty:
        results["score"] = results.apply(score, axis=1)
        results = results.sort_values("score", ascending=False)
    return results.head(limit)


def build_context(rows: pd.DataFrame) -> str:
    chunks = []
    for _, row in rows.head(6).iterrows():
        source_name = str(row.get("source_name", "") or "")
        source_basis = str(row.get("source_basis", "") or "")
        domain = str(row.get("domain_main", "") or "")
        combined = f"{source_name} {source_basis} {domain}"
        if "생명보험협회" in combined or ("ABL" in combined and "생명보험" in combined):
            source = "생명보험협회"
        else:
            source = source_name or source_basis
        chunks.append(
            "\n".join(
                [
                    f"용어/자료명: {row.get('term_title', '')}",
                    f"표제어: {row.get('term_ko', '')}",
                    f"도메인: {row.get('domain_main', '')}",
                    f"분류: {row.get('category', '')}",
                    f"정의/근거: {row.get('best_definition', '')}",
                    f"출처: {source} {row.get('source_url', '')}",
                ]
            )
        )
    return "\n\n---\n\n".join(chunks)
