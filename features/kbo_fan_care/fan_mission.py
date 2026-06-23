import streamlit as st

from .common import TEAMS, card, stable_index, tags


MISSIONS = [
    ("응원 후 물 한 병", "응원 열기가 올라간 날, 물 한 병 인증으로 가볍게 참여합니다."),
    ("야구장 단짠 줄이기", "오늘은 단 음식 또는 짠 음식을 하나만 줄여보는 미션입니다."),
    ("스케일링 리마인드", "최근 치과 방문을 미뤘다면 캘린더에 체크해보는 미션입니다."),
    ("가족 직관 체크리스트", "부모님 또는 아이와 함께 갈 때 이동, 식사, 휴식 포인트를 체크합니다."),
    ("9회 말 심호흡", "끝까지 몰입한 날, 경기 후 심호흡과 귀가 루틴을 챙겨보는 미션입니다."),
]


def render():
    st.markdown('<div class="kbo-section-title">4. 구단별 팬 챌린지</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="kbo-intro-card">
            구단별 팬덤 참여형 챌린지입니다. 광고처럼 보이기보다 팬들이 인증하고 공유할 수 있는 가벼운 이벤트 구조로 설계합니다.
            KBO MOU가 있다면 구단명, 경기 일정, 직관 인증과 연결해 더 자연스러운 참여형 콘텐츠가 됩니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    team = st.selectbox("응원 구단", TEAMS, key="kbo_mission_team")
    mission_count = st.slider("오늘 받을 미션 수", 1, 3, 2)

    start = stable_index(team, len(MISSIONS))
    selected = [MISSIONS[(start + i) % len(MISSIONS)] for i in range(mission_count)]

    tags([(team, True), ("인스타 공유형", False), ("팬 참여 이벤트", False)])
    cards = ""
    for index, (title, body) in enumerate(selected, 1):
        cards += card(f"{index}. {title}", body, gold=index == 1)

    st.markdown(f'<div class="kbo-card-grid">{cards}</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="kbo-report">
            공유 문구 예시<br>
            오늘의 KBO 팬 케어 미션 완료. 응원도 좋지만 내 루틴도 챙기는 팬이 진짜 오래 갑니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
