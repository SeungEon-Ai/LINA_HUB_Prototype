import streamlit as st

from .common import card, score_pill, tags


def render():
    st.markdown('<div class="kbo-section-title">3. 가족 직관 케어</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="kbo-intro-card">
            부모님, 아이, 연인과 함께 가는 직관 상황을 기준으로 이동 동선, 식사, 휴식, 건강 체크 포인트를 보여주는 기능입니다.
            가족 단위 관람자는 보험을 직접 묻지 않아도 자연스럽게 가족 생활보장, 건강검진, 치아관리 관심으로 이어질 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    companion = st.selectbox(
        "누구와 함께 직관하시나요?",
        ["부모님과 함께", "아이와 함께", "연인과 함께", "친구와 함께", "혼자 직관"],
        key="kbo_family_companion",
    )
    distance = st.slider("이동 시간", 10, 180, 60, step=10)
    meal_plan = st.radio("식사 계획", ["경기장 안에서 해결", "경기 전 식사", "경기 후 식사", "아직 미정"], horizontal=True)

    burden = min(100, 18 + distance // 4 + (18 if companion in ["부모님과 함께", "아이와 함께"] else 6))
    meal_signal = 62 if meal_plan == "경기장 안에서 해결" else 38

    tags([(companion, True), (f"이동 {distance}분", False), (meal_plan, False)])
    st.markdown(
        f"""
        <div class="kbo-score-grid">
            {score_pill("동선 부담", burden, "%")}
            {score_pill("식사 관리 신호", meal_signal, "%")}
            {score_pill("가족 케어", "ON", "")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="kbo-card-grid">
            {card("직관 전 체크", "티켓, 이동 동선, 계단 위치, 물, 간단한 간식, 귀가 교통편을 미리 정리하면 가족 관람 만족도가 올라갑니다.", True)}
            {card("자연스러운 연결", "부모님과 함께라면 건강 루틴, 아이와 함께라면 치아 간식 관리, 가족 단위라면 생활보장 공백 점검 콘텐츠로 이어가기 좋습니다.")}
        </div>
        """,
        unsafe_allow_html=True,
    )
