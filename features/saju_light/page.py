import streamlit as st

from features.shared_header import render_feature_header


def render():
    render_feature_header(
        "사주",
        "가볍게 즐기는 오늘의 운세 콘텐츠 탭입니다.",
    )

    st.markdown(
        """
        <div class="feature-intro-card">
            <b>준비 중인 기능입니다.</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
