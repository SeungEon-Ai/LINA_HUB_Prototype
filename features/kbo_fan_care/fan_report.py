import streamlit as st

from .common import TEAMS, card, level_label, score_pill, stable_index, tags


def render():
    st.markdown('<div class="kbo-section-title">1. KBO 팬 컨디션 리포트</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="kbo-intro-card">
            직관 스타일, 응원 몰입도, 수면, 음주/흡연 습관을 바탕으로 오늘의 팬 컨디션을 가볍게 보여주는 기능입니다.
            야구를 즐기는 방식에서 건강 루틴 점검으로 자연스럽게 이어지도록 만든 콘텐츠입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("kbo_fan_report_form"):
        col1, col2 = st.columns(2)
        with col1:
            team = st.selectbox("응원 구단", TEAMS, key="kbo_report_team")
            mode = st.radio("관람 방식", ["집관", "직관", "원정 직관"], horizontal=True)
            stress = st.slider("응원 몰입도", 1, 5, 3)
        with col2:
            sleep = st.slider("어젯밤 수면 시간", 3, 9, 6)
            alcohol = st.slider("최근 음주 빈도", 0, 5, 2)
            smoking = st.slider("흡연/전자담배 빈도", 0, 5, 0)

        submitted = st.form_submit_button("팬 컨디션 보기", use_container_width=True)

    if not submitted and "kbo_fan_report" not in st.session_state:
        st.info("응원 스타일을 입력하면 오늘의 팬 컨디션과 건강 루틴 신호를 보여줍니다.")
        return

    if submitted:
        condition = 20 + max(0, stress - 3) * 9 + max(0, 6 - sleep) * 7 + alcohol * 5 + smoking * 8
        condition += 8 if mode == "직관" else 4 if mode == "원정 직관" else 0
        condition = min(100, condition)
        fan_score = max(35, min(99, 84 - condition // 3 + stable_index(team + mode, 12)))
        st.session_state.kbo_fan_report = {
            "team": team,
            "mode": mode,
            "condition": condition,
            "fan_score": fan_score,
            "stress": stress,
            "sleep": sleep,
        }

    result = st.session_state.kbo_fan_report
    tags([(result["team"], False), (result["mode"], False), (f"컨디션 부담 {level_label(result['condition'])}", True)])

    st.markdown(
        f"""
        <div class="kbo-score-grid">
            {score_pill("팬 컨디션 점수", result["fan_score"])}
            {score_pill("직관 피로 신호", result["condition"], "%")}
            {score_pill("응원 몰입도", result["stress"], "단계")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="kbo-card-grid">
            {card("오늘의 팬 타입", f"{result['team']} 팬 기준으로 보면, 오늘은 응원 몰입과 컨디션 관리가 함께 필요한 날입니다.", True)}
            {card("건강 루틴 연결", f"수면이 짧거나 응원 몰입도가 높은 날은 피로감이 쌓이기 쉽습니다. 직관 전후로 물, 휴식, 이동 동선을 챙기는 식으로 부담을 줄일 수 있습니다.")}
        </div>
        """,
        unsafe_allow_html=True,
    )
