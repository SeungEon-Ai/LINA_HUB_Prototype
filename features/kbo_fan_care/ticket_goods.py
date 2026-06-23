import streamlit as st

from .common import card, score_pill, tags


def render():
    st.markdown('<div class="kbo-section-title">5. 티켓/굿즈 케어</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="kbo-intro-card">
            티켓, 유니폼, 굿즈 구매 흐름을 팬의 관심 데이터로 보고, 다음에 어떤 콘텐츠를 보여줄지 정리하는 기능입니다.
            당장 판매 전환보다 팬의 관심사를 이해하고 다음 콘텐츠 추천으로 이어가는 목적입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    ticket_type = st.radio("관심 있는 항목", ["홈경기 티켓", "원정경기 티켓", "유니폼", "응원 굿즈", "가족석"], horizontal=True)
    budget = st.slider("이번 달 야구 예산", 0, 300000, 70000, step=10000)
    frequency = st.slider("한 달 관람/응원 소비 빈도", 0, 8, 2)

    fan_heat = min(100, frequency * 12 + budget // 5000)
    routine_match = 78 if ticket_type in ["가족석", "원정경기 티켓"] else 54

    tags([(ticket_type, True), (f"예산 {budget:,}원", False), ("다음 콘텐츠 추천", False)])
    st.markdown(
        f"""
        <div class="kbo-score-grid">
            {score_pill("팬 열정도", fan_heat, "%")}
            {score_pill("루틴 콘텐츠 적합도", routine_match, "%")}
            {score_pill("추천 흐름", "콘텐츠", "")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="kbo-card-grid">
            {card("다음에 보여줄 콘텐츠", "가족석이나 원정경기에 관심이 있으면 가족 직관 케어, 굿즈와 간식 관심이 높으면 야구장 먹거리 케어로 이어갈 수 있습니다.", True)}
            {card("MOU 확장 포인트", "티켓 예매 완료 화면, 구단 앱, 경기 알림 메시지 안에 팬 케어 카드가 들어가면 광고보다 자연스러운 접점이 됩니다.")}
        </div>
        """,
        unsafe_allow_html=True,
    )
