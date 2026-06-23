import streamlit as st

from .common import BALLPARK_FOODS, card, level_label, score_pill, tags


SALTY = {"치킨", "떡볶이", "라면", "오징어", "나초", "맥주"}
SWEET = {"탄산음료", "아이스크림", "떡볶이"}
HARD = {"오징어", "핫도그", "나초"}


def render():
    st.markdown('<div class="kbo-section-title">2. 야구장 먹거리 케어</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="kbo-intro-card">
            야구장에서 자주 먹는 메뉴를 고르면 짠맛, 단맛, 딱딱한 간식 신호를 나눠 보여줍니다.
            치아보험은 단 음식과 딱딱한 음식, 암보험은 반복되는 짠 식습관과 건강 루틴 점검 흐름으로 자연스럽게 연결할 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    foods = st.multiselect(
        "자주 먹는 야구장 메뉴",
        BALLPARK_FOODS,
        default=["치킨", "맥주"],
        key="kbo_food_menu",
    )

    salty_count = len(set(foods) & SALTY)
    sweet_count = len(set(foods) & SWEET)
    hard_count = len(set(foods) & HARD)
    sodium_signal = min(100, 20 + salty_count * 18)
    dental_signal = min(100, 18 + sweet_count * 18 + hard_count * 14)

    tags(
        [
            (f"짠맛 신호 {level_label(sodium_signal)}", sodium_signal >= 48),
            (f"치아 부담 {level_label(dental_signal)}", dental_signal >= 48),
            ("한 끼 기록용 콘텐츠", False),
        ]
    )

    st.markdown(
        f"""
        <div class="kbo-score-grid">
            {score_pill("짠맛 신호", sodium_signal, "%")}
            {score_pill("치아 부담 신호", dental_signal, "%")}
            {score_pill("선택 메뉴", len(foods), "개")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected = ", ".join(foods) if foods else "선택한 메뉴 없음"
    st.markdown(
        f"""
        <div class="kbo-card-grid">
            {card("오늘 고른 메뉴", selected, True)}
            {card("보험 연결 포인트", "딱딱하거나 단 음식은 치아 관리 콘텐츠와 잘 이어지고, 짠 음식이 반복되는 패턴은 건강 루틴 점검 콘텐츠와 자연스럽게 이어집니다. 단, 특정 음식 하나가 바로 질병을 만든다는 식으로 과장하지 않습니다.")}
        </div>
        """,
        unsafe_allow_html=True,
    )
