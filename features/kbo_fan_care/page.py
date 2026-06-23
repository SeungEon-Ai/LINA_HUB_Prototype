from pathlib import Path

import streamlit as st

from features.shared_header import render_feature_header

from . import ballpark_food, family_care, fan_mission, fan_report, ticket_goods
from .common import render_kbo_css


ROOT = Path(__file__).resolve().parents[2]
KBO_LOGO = ROOT / "assets" / "kbo_logo_square.png"

KBO_FEATURES = {
    "팬 컨디션": fan_report.render,
    "먹거리 케어": ballpark_food.render,
    "가족 직관": family_care.render,
    "팬 챌린지": fan_mission.render,
    "티켓/굿즈": ticket_goods.render,
}


def render():
    render_kbo_css()
    render_feature_header(
        "KBO 팬 케어",
        "KBO 팬의 직관, 응원, 먹거리, 가족 관람을 나눠서 보는 KBO X LINA 콘텐츠입니다.",
        logo_path=KBO_LOGO,
        logo_alt="KBO",
        logo_size=36,
    )

    st.markdown(
        """
        <div class="kbo-intro-card">
            KBO X LINA는 하나의 큰 이벤트 카테고리로 두고, 실제 경험은 기능별로 나눠 보여줍니다.
            팬 컨디션, 야구장 먹거리, 가족 직관, 팬 챌린지, 티켓/굿즈 관심을 각각 다른 콘텐츠로 분리해
            사용자가 원하는 주제만 가볍게 눌러볼 수 있게 구성했습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected = st.segmented_control(
        "KBO X LINA 기능",
        list(KBO_FEATURES.keys()),
        default="팬 컨디션",
        label_visibility="collapsed",
        key="kbo_subfeature",
    )

    KBO_FEATURES[selected]()
