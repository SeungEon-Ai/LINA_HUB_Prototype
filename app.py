import base64
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from features.home.page import render as render_home
from features.insurance_dictionary.page import render as render_dictionary
from features.lina_faq_ai.page import render as render_lina_faq_ai
from features.lina_faq_ai.ai import answer_question as answer_mini_chat_question
from features.life_expectancy.page import render as render_life_expectancy
from features.future_worry_test.page import render as render_future_worry_test
from features.meal_judgement.page import render as render_meal_judgement
from features.policy_graph_rag.page import render as render_policy_graph_rag
from features.dental_score.page import render as render_dental_score
from features.dust_health_check.page import render as render_dust_health_check
from features.event_board.page import render as render_event_board
from features.insurance_news_summary.page import render as render_insurance_news_summary


ROOT = Path(__file__).parent
BRAND_LOGO = ROOT / "assets" / "lina_mark_color.png"
CHAT_ORB_ASSET = ROOT / "assets" / "home" / "chat-gunggeum-orb.png"
APP_ICON = ROOT / "assets" / "lina_hub_favicon.png"
MINI_CHAT_OPEN_KEY = "lina_hub_mini_chat_open_v1"
MINI_CHAT_MESSAGES_KEY = "lina_hub_mini_chat_messages_v1"
MINI_CHAT_TRIGGER_KEY = "lina_hub_mini_chat_trigger_v1"
MINI_CHAT_LAST_Q_KEY = "lina_hub_mini_chat_last_q_v1"


st.set_page_config(
    page_title="LINA HUB",
    page_icon=str(APP_ICON),
    layout="wide",
    initial_sidebar_state="expanded",
)


FEATURES = {
    "홈": {
        "key": "home",
        "description": "",
        "renderer": render_home,
    },
    "AI보험용어사전": {
        "key": "dictionary",
        "description": "",
        "renderer": render_dictionary,
    },
    "라이나 약관 AI": {
        "key": "policy_graph_rag",
        "description": "",
        "renderer": render_policy_graph_rag,
    },
    "라이나 궁금톡": {
        "key": "lina_faq_ai",
        "description": "",
        "renderer": render_lina_faq_ai,
    },
    "라이프타임 계산기": {
        "key": "life_expectancy",
        "description": "",
        "renderer": render_life_expectancy,
    },
    "미래 걱정 유형 테스트": {
        "key": "future_worry_test",
        "description": "",
        "renderer": render_future_worry_test,
    },
    "오늘 한 끼 판정단": {
        "key": "meal_judgement",
        "description": "",
        "renderer": render_meal_judgement,
    },
    "치아 건강점수": {
        "key": "dental_score",
        "description": "",
        "renderer": render_dental_score,
    },
    "오늘의 직관! 미세먼지는?": {
        "key": "dust_health_check",
        "description": "",
        "renderer": render_dust_health_check,
    },
    "보험뉴스 한입 AI": {
        "key": "insurance_news_summary",
        "description": "",
        "renderer": render_insurance_news_summary,
    },
    "이벤트": {
        "key": "event",
        "description": "",
        "renderer": render_event_board,
    },
}


FEATURE_KEYS = {meta["key"]: name for name, meta in FEATURES.items()}
FEATURE_KEY_ALIASES = {
    "event_board": "이벤트",
}

INTEREST_SECTIONS = [
    {
        "title": "보험이 궁금할 때",
        "items": [
            ("AI보험용어사전", "AI보험용어사전"),
            ("라이나 약관 AI", "라이나 약관 AI"),
            ("라이나 궁금톡", "라이나 궁금톡"),
        ],
    },
    {
        "title": "생활속 라이나",
        "items": [
            ("오늘의 직관! 미세먼지는?", "오늘의 직관! 미세먼지는?"),
            ("보험뉴스 한입 AI", "보험뉴스 한입 AI"),
        ],
    },
    {
        "title": "Fun Fun한 라이나",
        "items": [
            ("라이프타임 계산기", "라이프타임 계산기"),
            ("미래 걱정 유형 테스트", "미래 걱정 유형 테스트"),
            ("오늘 한 끼 판정단", "오늘 한 끼 판정단"),
            ("치아 건강점수", "치아 건강점수"),
        ],
    },
]


@st.cache_data(show_spinner=False)
def image_data_uri(path_text: str):
    path = Path(path_text)
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_base_css():
    st.markdown(
        """
        <style>
        :root {
            --lina-left-rail-x: clamp(76px, 4vw, 104px);
            --lina-left-rail-width: clamp(224px, 12.5vw, 260px);
            --lina-left-reserved: clamp(360px, 22vw, 460px);
            --lina-right-rail-x: clamp(26px, 2.2vw, 54px);
            --lina-right-rail-width: 176px;
            --lina-right-reserved: clamp(260px, 18vw, 380px);
            --lina-content-max: 1120px;
        }
        @media (min-resolution: 1.75dppx) and (min-width: 1200px) and (max-width: 1500px) and (max-height: 1000px) {
            html,
            body {
                overflow-x: hidden !important;
            }
            .stApp {
                width: 125vw;
                min-height: 125vh;
                transform: scale(.8);
                transform-origin: top left;
            }
        }
        .main .block-container,
        section.main > div,
        div[data-testid="stMainBlockContainer"] {
            width: 100%;
            max-width: 1320px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding-top: 1.15rem;
            padding-bottom: 4rem;
            position: relative !important;
            overflow: visible !important;
            left: 0;
        }
        div[data-testid="stMarkdownContainer"]:has(.brand-life-wrap),
        div[data-testid="stMarkdownContainer"]:has(.brand-life) {
            overflow: visible !important;
        }
        .brand-life-wrap {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 1rem;
            min-height: 2rem;
            width: 100vw;
            max-width: none;
            padding-top: 1.35rem;
            padding-left: clamp(86px, 4.7vw, 112px);
            padding-right: clamp(64px, 8vw, 132px);
            margin-bottom: .15rem;
            margin-top: 0;
            margin-left: calc(50% - 50vw);
            margin-right: calc(50% - 50vw);
            overflow: visible !important;
        }
        .brand-life {
            display: flex;
            align-items: center;
            gap: .35rem;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 1.28rem;
            font-weight: 800;
            line-height: 1.35;
            letter-spacing: .01em;
            margin: 0;
            padding: 0;
            min-height: 2rem;
            overflow: visible !important;
            text-decoration: none !important;
        }
        .brand-life span {
            display: block;
            line-height: 1.35;
            padding: 0;
            overflow: visible !important;
        }
        .brand-life .lina {
            color: #f5b51b;
        }
        .brand-life .life {
            color: #111827;
        }
        .hub-top-tabs {
            position: absolute;
            top: calc(1.35rem + .48rem);
            right: clamp(64px, 8vw, 132px);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: .95rem;
            min-width: 0;
            margin-right: 0;
        }
        .hub-top-tab {
            color: #1f2937 !important;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
            font-size: .82rem;
            font-weight: 800;
            line-height: 1;
            text-decoration: none !important;
            white-space: nowrap;
        }
        .hub-top-tab:hover {
            color: #f5b51b !important;
        }
        @media (min-width: 901px) {
            div[data-testid="stMarkdownContainer"]:has(.brand-life-wrap) {
                min-height: 3.2rem !important;
            }
            .brand-life-wrap {
                position: fixed;
                top: 2.15rem;
                left: 0;
                right: auto;
                z-index: 10050;
                margin-left: 0 !important;
                margin-right: 0 !important;
            }
        }
        .brand-row {
            display: flex;
            align-items: center;
            gap: .45rem;
            margin-bottom: .55rem;
            min-height: 42px;
            overflow: visible !important;
        }
        .brand-mark {
            width: 58px;
            height: 58px;
            display: block;
            flex: 0 0 58px;
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
            border-radius: 4px;
            opacity: 1 !important;
            visibility: visible !important;
        }
        .brand-name {
            display: inline-flex;
            align-items: center;
            gap: .42rem;
            color: #0f172a;
            font-size: 1.7rem;
            line-height: 1;
            font-weight: 900;
            white-space: nowrap;
            text-decoration: none !important;
            letter-spacing: .01em;
            font-family: Arial, Helvetica, sans-serif;
        }
        .brand-name-mark {
            width: 26px;
            height: 26px;
            flex: 0 0 26px;
            display: block;
            object-fit: contain;
            border-radius: 6px;
        }
        .brand-name .lina {
            color: #f5b51b;
        }
        .brand-name .hub {
            color: #0f172a;
        }
        .brand-text {
            height: 42px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: .28rem;
        }
        .brand-links {
            display: flex;
            flex-direction: column;
            gap: .12rem;
        }
        .brand-links a {
            color: #64748b;
            font-size: .68rem;
            line-height: 1;
            text-decoration: none;
            white-space: nowrap;
        }
        .brand-links a:hover {
            color: #111827;
            text-decoration: underline;
        }

        .mobile-hub-menu,
        .mobile-feature-menu {
            display: none;
        }
        .mobile-hub-menu summary,
        .mobile-feature-menu summary {
            list-style: none;
            cursor: pointer;
        }
        .mobile-hub-menu summary::-webkit-details-marker,
        .mobile-feature-menu summary::-webkit-details-marker {
            display: none;
        }
        .hub-nav-label {
            color: #64748b;
            font-size: .78rem;
            margin-top: 4.45rem;
            margin-bottom: .18rem;
            text-align: center;
        }
        .hub-divider {
            border-bottom: 1px solid #e2e8f0;
            margin: .28rem 0 0;
        }
        .today-rec-row {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: nowrap;
            gap: .48rem;
            width: 100%;
            overflow: hidden;
            margin-bottom: .05rem;
        }
        .today-rec-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 28px;
            padding: .22rem .62rem;
            border: 1px solid #dbe3ef;
            border-radius: 999px;
            color: #475569 !important;
            background: #fff;
            font-size: .76rem;
            font-weight: 700;
            line-height: 1.1;
            text-decoration: none !important;
            white-space: nowrap;
            box-shadow: 0 1px 0 rgba(15, 23, 42, .02);
        }
        .today-rec-pill:hover {
            border-color: #f2c14e;
            background: #fffaf0;
            color: #111827 !important;
        }
        .today-rec-pill.active {
            border-color: #f5b51b;
            background: #fff7df;
            color: #111827 !important;
        }
        .st-key-today_recommendation_nav {
            margin-bottom: .05rem;
        }
        .st-key-today_recommendation_nav div[data-testid="stPills"] {
            display: flex;
            justify-content: center;
            width: 100%;
        }
        .st-key-today_recommendation_nav div[data-testid="stPills"] > div {
            width: 100%;
            display: flex;
            justify-content: center;
        }
        .st-key-today_recommendation_nav div[data-baseweb="button-group"] {
            display: flex;
            justify-content: center;
            gap: .48rem;
            flex-wrap: nowrap;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
        }
        .st-key-today_recommendation_nav div[role="group"] {
            display: flex;
            justify-content: center;
            gap: .48rem;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
        }
        .st-key-today_recommendation_nav div[data-testid="stHorizontalBlock"] {
            align-items: center;
            justify-content: center;
            gap: .48rem;
        }
        .st-key-today_recommendation_nav div[data-testid="stButton"] {
            display: flex;
            justify-content: center;
        }
        .st-key-today_recommendation_nav button {
            width: auto !important;
            min-height: 28px !important;
            padding: .22rem .62rem !important;
            border-radius: 999px !important;
            font-size: .76rem !important;
            font-weight: 700 !important;
            line-height: 1.1 !important;
            white-space: nowrap !important;
            box-shadow: 0 1px 0 rgba(15, 23, 42, .02) !important;
        }
        .st-key-today_recommendation_nav button[kind="primary"] {
            border-color: #f5b51b !important;
            background: #fff7df !important;
            color: #111827 !important;
        }
        @media (max-width: 900px) {
            html,
            body,
            .stApp,
            .stAppViewContainer,
            .appview-container {
                background: #fff !important;
            }
            .main .block-container,
            section.main > div,
            div[data-testid="stMainBlockContainer"] {
                left: 0;
                max-width: none !important;
                padding-left: .9rem !important;
                padding-right: .9rem !important;
                padding-top: .7rem !important;
            }
            .brand-life-wrap {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                width: 100vw;
                padding: 1.32rem .9rem .2rem;
                margin-bottom: .18rem;
            }
            .brand-row {
                margin-bottom: .2rem;
            }
            .brand-name {
                font-size: clamp(1.38rem, 8vw, 1.72rem);
                gap: .36rem;
            }
            .brand-name-mark {
                width: 27px;
                height: 27px;
                flex-basis: 27px;
            }
            .hub-top-tabs {
                display: none;
            }
            .mobile-hub-menu {
                display: block;
                width: min(100%, 360px);
                margin-top: .45rem;
                font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
            }
            .mobile-hub-menu summary {
                min-height: 38px;
                border: 1px solid #dbe5f0;
                border-radius: 999px;
                background: #fff;
                color: #111827;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: .92rem;
                font-weight: 900;
                box-shadow: 0 8px 18px rgba(15, 23, 42, .05);
            }
            .mobile-hub-menu summary::after,
            .mobile-feature-menu summary::after {
                content: ">";
                margin-left: .5rem;
                color: #f5b51b;
                font-weight: 950;
                transform: rotate(90deg);
            }
            .mobile-hub-menu[open] summary::after,
            .mobile-feature-menu[open] summary::after {
                transform: rotate(-90deg);
            }
            .mobile-hub-menu-panel,
            .mobile-feature-menu-panel {
                margin-top: .5rem;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                background: rgba(255, 255, 255, .98);
                box-shadow: 0 14px 30px rgba(15, 23, 42, .08);
                padding: .55rem;
            }
            .mobile-hub-menu-panel {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: .42rem;
            }
            .mobile-hub-menu-panel a,
            .mobile-feature-menu-link {
                min-height: 38px;
                border-radius: 12px;
                background: #f8fafc;
                color: #334155 !important;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: .45rem .5rem;
                font-size: .82rem;
                font-weight: 850;
                line-height: 1.2;
                text-align: center;
                text-decoration: none !important;
            }
            .mobile-hub-menu-panel a:hover,
            .mobile-feature-menu-link:hover,
            .mobile-feature-menu-link.active {
                background: #fff7df;
                color: #111827 !important;
            }
            .today-rec-row {
                justify-content: flex-start;
                overflow-x: auto;
                padding-bottom: .12rem;
            }
            .mobile-feature-menu {
                display: block;
                width: 100%;
                max-width: 720px;
                margin: .12rem auto 0;
                font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
            }
            .mobile-feature-menu summary {
                min-height: 42px;
                border: 1px solid #dbe5f0;
                border-radius: 14px;
                background: #fff;
                color: #111827;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: .92rem;
                font-weight: 950;
                box-shadow: 0 8px 18px rgba(15, 23, 42, .05);
            }
            .mobile-feature-section + .mobile-feature-section {
                margin-top: .72rem;
            }
            .mobile-feature-section-title {
                color: #94a3b8;
                font-size: .76rem;
                font-weight: 900;
                margin: .1rem .18rem .34rem;
            }
            .mobile-feature-links {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: .42rem;
            }
            div[data-testid="stElementContainer"]:has(.interest-rail),
            div[data-testid="stLayoutWrapper"]:has(.st-key-interest_rail),
            div[data-testid="stElementContainer"]:has(.event-rail) {
                display: none !important;
                height: 0 !important;
                min-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            div[data-testid="stElementContainer"]:has(.home-grid) {
                margin-top: -64px !important;
            }
            div[data-testid="stElementContainer"]:has(.feature-visual-banner) {
                margin-top: -32px !important;
            }
        }
        @media (max-width: 430px) {
            .mobile-feature-links,
            .mobile-hub-menu-panel {
                grid-template-columns: 1fr;
            }
        }
        .interest-rail {
            position: absolute;
            top: 7.85rem;
            left: var(--lina-left-rail-x);
            width: var(--lina-left-rail-width);
            box-sizing: border-box;
            z-index: 3;
            color: #1f2937;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .interest-rail-title {
            color: #111827;
            font-size: .7rem;
            font-weight: 900;
            margin-bottom: .28rem;
            white-space: nowrap;
        }
        .interest-rail-card {
            border: 1px solid #e2e8f0;
            border-radius: 11px;
            background: rgba(255, 255, 255, .92);
            box-shadow: 0 8px 24px rgba(15, 23, 42, .05);
            padding: .8rem .62rem .84rem;
            margin-bottom: 0;
            overflow: hidden;
        }
        .interest-section-name {
            color: #94a3b8;
            font-size: .72rem;
            font-weight: 800;
            margin-bottom: .2rem;
        }
        .interest-link {
            display: block;
            border-radius: 999px;
            padding: .32rem .42rem;
            margin-top: .16rem;
            color: #334155 !important;
            font-size: .76rem;
            font-weight: 700;
            line-height: 1.15;
            text-decoration: none !important;
            border: 1px solid transparent;
            background: transparent;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .interest-link:hover {
            background: #fff7e6;
            border-color: #f2c14e;
            color: #111827 !important;
        }
        .interest-link.active {
            background: #fff6db;
            border-color: #f5b51b;
            color: #111827 !important;
        }
        .st-key-interest_rail {
            position: fixed;
            top: 7.85rem;
            left: var(--lina-left-rail-x);
            width: var(--lina-left-rail-width);
            box-sizing: border-box;
            z-index: 10010;
            max-height: calc(100vh - 9.1rem);
            gap: .58rem !important;
            row-gap: .58rem !important;
            color: #1f2937;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .st-key-interest_rail > div[data-testid="stVerticalBlock"],
        .st-key-interest_rail div[data-testid="stVerticalBlock"] {
            gap: 0 !important;
            row-gap: 0 !important;
        }
        .st-key-interest_rail .interest-rail-title {
            color: #111827;
            font-size: .7rem;
            font-weight: 900;
            margin-bottom: .28rem;
            white-space: nowrap;
        }
        .st-key-interest_rail div[data-testid="stMarkdownContainer"]:has(.interest-section-name) {
            padding-bottom: .32rem !important;
            margin-bottom: 0 !important;
        }
        .st-key-interest_rail .interest-section-name {
            display: block !important;
            margin-bottom: 0 !important;
            position: relative !important;
            z-index: 2 !important;
        }
        .st-key-interest_section_0,
        .st-key-interest_section_1,
        .st-key-interest_section_2,
        .st-key-interest_section_3,
        .st-key-interest_search_card {
            box-sizing: border-box;
            border: 1px solid #e2e8f0;
            border-radius: 11px;
            background: rgba(255, 255, 255, .92);
            box-shadow: 0 8px 24px rgba(15, 23, 42, .05);
            padding: .8rem .62rem .84rem;
            margin-bottom: 0;
            overflow: hidden;
        }
        .st-key-interest_rail div[data-testid="stVerticalBlockBorderWrapper"],
        .st-key-interest_rail div[data-testid="stElementContainer"] {
            margin-bottom: 0 !important;
        }
        .st-key-interest_rail div[data-testid="stElementContainer"]:has(.interest-section-name)
            + div[data-testid="stElementContainer"] {
            margin-top: 0 !important;
        }
        .st-key-interest_rail div[data-testid="stButton"] {
            margin: 0;
        }
        .st-key-interest_rail button {
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            text-align: left !important;
            width: 100% !important;
            min-height: 30px !important;
            border-radius: 999px !important;
            padding: .32rem .42rem !important;
            margin-top: .16rem !important;
            font-size: .76rem !important;
            font-weight: 700 !important;
            line-height: 1.15 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            box-shadow: none !important;
        }
        .st-key-interest_rail button > div,
        .st-key-interest_rail button span,
        .st-key-interest_rail button [data-testid="stMarkdownContainer"] {
            display: block !important;
            width: 100% !important;
            text-align: left !important;
            justify-content: flex-start !important;
            margin-left: 0 !important;
            margin-right: auto !important;
        }
        .st-key-interest_rail button * {
            text-align: left !important;
            justify-content: flex-start !important;
        }
        .st-key-interest_rail button div[data-testid="stMarkdownContainer"],
        .st-key-interest_rail button p {
            width: 100%;
            text-align: left !important;
            margin-left: 0 !important;
            margin-right: auto !important;
            font-size: .76rem !important;
            line-height: 1.15 !important;
        }
        .st-key-interest_rail button[kind="secondary"] {
            border-color: transparent !important;
            background: transparent !important;
            color: #334155 !important;
        }
        .st-key-interest_rail button[kind="primary"] {
            border-color: #f5b51b !important;
            background: #fff6db !important;
            color: #111827 !important;
        }
        .st-key-interest_search_card {
            padding: .78rem .62rem .78rem;
            position: relative;
        }
        .st-key-interest_search_card div[data-baseweb="input"] {
            min-height: 42px !important;
            border-radius: 999px !important;
            border-color: #e2e8f0 !important;
            background: #fff !important;
        }
        .st-key-interest_search_card input {
            min-height: 42px !important;
            padding: .15rem 2.05rem .15rem .46rem !important;
            font-size: .74rem !important;
            font-weight: 700 !important;
        }
        .st-key-interest_search_card div[data-testid="stTextInput"] {
            margin-bottom: 0 !important;
        }
        .st-key-interest_feature_search_button {
            position: absolute !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            right: 1.16rem !important;
            width: 30px !important;
            height: 30px !important;
            z-index: 20;
        }
        .st-key-interest_rail .st-key-interest_feature_search_button button,
        .st-key-interest_rail .st-key-interest_feature_search_button button[kind="secondary"],
        .st-key-interest_rail .st-key-interest_feature_search_button button[kind="primary"] {
            position: relative !important;
            min-height: 30px !important;
            width: 30px !important;
            height: 30px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 999px !important;
            border: 0 !important;
            background-color: #ffb71b !important;
            background-image: none !important;
            color: #111827 !important;
            margin-top: 0 !important;
            opacity: 1 !important;
            box-shadow: 0 4px 10px rgba(245, 181, 27, .28) !important;
        }
        .st-key-interest_feature_search_button button:before {
            content: "" !important;
            position: absolute !important;
            left: 50% !important;
            top: 50% !important;
            width: 15px !important;
            height: 15px !important;
            border: 2px solid #fff !important;
            border-radius: 999px !important;
            box-sizing: border-box !important;
            transform: translate(-58%, -58%) !important;
        }
        .st-key-interest_feature_search_button button:after {
            content: "" !important;
            position: absolute !important;
            left: 19px !important;
            top: 21px !important;
            width: 7px !important;
            height: 2px !important;
            border-radius: 999px !important;
            background: #fff !important;
            transform: rotate(45deg) !important;
            transform-origin: left center !important;
        }
        .st-key-interest_rail .st-key-interest_feature_search_button button:hover,
        .st-key-interest_rail .st-key-interest_feature_search_button button[kind="secondary"]:hover,
        .st-key-interest_rail .st-key-interest_feature_search_button button[kind="primary"]:hover {
            background-color: #f5a800 !important;
            background-image: none !important;
        }
        .st-key-interest_feature_search_button button p {
            color: transparent !important;
            font-size: 0 !important;
            line-height: 0 !important;
        }
        .interest-search-empty {
            color: #94a3b8;
            font-size: .64rem;
            font-weight: 750;
            line-height: 1.3;
            padding: .18rem .34rem;
        }
        .event-rail {
            position: fixed;
            top: 50%;
            right: var(--lina-right-rail-x);
            left: auto;
            width: var(--lina-right-rail-width);
            z-index: 10020;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
            transform: translateY(-50%);
        }
        .event-rail-card {
            display: block;
            width: var(--lina-right-rail-width);
            color: #111827 !important;
            text-decoration: none !important;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            background: #fff;
            box-shadow: -8px 12px 30px rgba(15, 23, 42, .08);
            overflow: hidden;
            transition: width .22s ease, transform .22s ease;
        }
        .event-rail-card:hover {
            width: min(288px, calc((100vw - 1040px) / 2 - 36px));
            transform: translateX(calc(var(--lina-right-rail-width) - min(288px, calc((100vw - 1040px) / 2 - 36px))));
        }
        .customer-rail-card {
            display: block;
            width: var(--lina-right-rail-width);
            margin-top: .34rem;
            padding: .82rem .86rem;
            color: #111827 !important;
            text-decoration: none !important;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            background: #fff;
            box-shadow: -8px 12px 30px rgba(15, 23, 42, .07);
            overflow: hidden;
            transition: width .22s ease, transform .22s ease;
        }
        .customer-rail-card:hover {
            width: min(288px, calc((100vw - 1040px) / 2 - 36px));
            transform: translateX(calc(var(--lina-right-rail-width) - min(288px, calc((100vw - 1040px) / 2 - 36px))));
        }
        .customer-rail-top {
            display: flex;
            align-items: center;
            gap: .5rem;
            min-width: 0;
        }
        .customer-rail-icon {
            width: 34px;
            height: 34px;
            border-radius: 999px;
            background: #ffb71b;
            color: #111827;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: .88rem;
            font-weight: 900;
            flex: 0 0 34px;
        }
        .customer-rail-kicker {
            color: #64748b;
            font-size: .52rem;
            font-weight: 900;
            line-height: 1;
            white-space: nowrap;
        }
        .customer-rail-title {
            margin-top: .18rem;
            color: #111827;
            font-size: .78rem;
            font-weight: 900;
            line-height: 1.2;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .customer-rail-desc,
        .customer-rail-more {
            opacity: 0;
            max-height: 0;
            overflow: hidden;
            transition: opacity .18s ease, max-height .18s ease, margin .18s ease;
        }
        .customer-rail-card:hover .customer-rail-desc {
            opacity: 1;
            max-height: 38px;
            margin-top: .46rem;
            color: #64748b;
            font-size: .54rem;
            font-weight: 700;
            line-height: 1.35;
        }
        .customer-rail-card:hover .customer-rail-more {
            opacity: 1;
            max-height: 30px;
            margin-top: .56rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 28px;
            width: 100%;
            border-radius: 999px;
            background: #24138d;
            color: #fff;
            font-size: .56rem;
            font-weight: 900;
            white-space: nowrap;
        }
        .chatbot-rail-card {
            display: block;
            width: var(--lina-right-rail-width);
            margin-top: .34rem;
            padding: .8rem .86rem;
            color: #111827 !important;
            text-decoration: none !important;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            background: #fff;
            box-shadow: -8px 12px 30px rgba(15, 23, 42, .07);
            overflow: hidden;
            transition: width .22s ease, transform .22s ease;
        }
        .chatbot-rail-card:hover {
            width: min(288px, calc((100vw - 1040px) / 2 - 36px));
            transform: translateX(calc(var(--lina-right-rail-width) - min(288px, calc((100vw - 1040px) / 2 - 36px))));
        }
        .chatbot-rail-icon {
            width: 34px;
            height: 34px;
            border-radius: 999px;
            background: #24138d;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 34px;
            overflow: hidden;
            box-shadow: 0 7px 16px rgba(37, 18, 160, .18);
        }
        .chatbot-rail-icon img {
            width: 100%;
            height: 100%;
            display: block;
            object-fit: cover;
            transform: scale(1.18);
        }
        .chatbot-rail-card:hover .customer-rail-desc {
            opacity: 1;
            max-height: 38px;
            margin-top: .46rem;
            color: #64748b;
            font-size: .54rem;
            font-weight: 700;
            line-height: 1.35;
        }
        .chatbot-rail-card:hover .customer-rail-more {
            opacity: 1;
            max-height: 30px;
            margin-top: .56rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 28px;
            width: 100%;
            border-radius: 999px;
            background: #ffb71b;
            color: #111827;
            font-size: .56rem;
            font-weight: 900;
            white-space: nowrap;
        }
        .event-rail-head {
            min-height: 126px;
            padding: .92rem .86rem;
            background: #24138d;
            color: #fff;
            position: relative;
        }
        .event-rail-kicker {
            display: inline-flex;
            align-items: center;
            height: 28px;
            padding: 0 .66rem;
            border-radius: 999px;
            background: #fff;
            color: #24138d;
            font-size: .62rem;
            font-weight: 900;
            white-space: nowrap;
        }
        .event-rail-title {
            margin-top: .62rem;
            color: #fff;
            font-size: .78rem;
            font-weight: 900;
            line-height: 1.22;
            letter-spacing: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .event-rail-gift {
            position: absolute;
            right: .38rem;
            bottom: .42rem;
            width: 28px;
            height: 22px;
            border-radius: 7px;
            background: #ffc62e;
            color: #24138d;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: .44rem;
            font-weight: 900;
            box-shadow: 0 5px 12px rgba(0, 0, 0, .18);
        }
        .event-rail-body {
            padding: .84rem .86rem .92rem;
        }
        .event-rail-status {
            display: inline-flex;
            align-items: center;
            height: 30px;
            padding: 0 .68rem;
            border: 1px solid #24138d;
            border-radius: 999px;
            color: #24138d;
            font-size: .66rem;
            font-weight: 900;
            white-space: nowrap;
        }
        .event-rail-name {
            margin-top: .58rem;
            color: #111827;
            font-size: .72rem;
            font-weight: 900;
            line-height: 1.25;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .event-rail-desc,
        .event-rail-more {
            opacity: 0;
            max-height: 0;
            overflow: hidden;
            transition: opacity .18s ease, max-height .18s ease, margin .18s ease;
        }
        .event-rail-card:hover .event-rail-desc {
            opacity: 1;
            max-height: 36px;
            margin-top: .28rem;
            color: #64748b;
            font-size: .52rem;
            font-weight: 700;
            line-height: 1.35;
        }
        .event-rail-card:hover .event-rail-more {
            opacity: 1;
            max-height: 30px;
            margin-top: .56rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 28px;
            width: 100%;
            border-radius: 999px;
            background: #ffb71b;
            color: #111827;
            font-size: .56rem;
            font-weight: 900;
            white-space: nowrap;
        }
@media (max-width: 1380px) {
            .interest-rail,
            .st-key-interest_rail,
            .event-rail {
                display: none;
            }
        }
        .lina-footer {
            border-top: 0;
            position: relative;
            z-index: 10;
            width: 100vw;
            margin-top: 30rem;
            margin-left: calc(50% - 50vw);
            margin-right: calc(50% - 50vw);
            padding: 2.2rem max(5rem, calc((100vw - 1320px) / 2)) 0;
            background: #fff;
            color: #1f2937;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .lina-footer:before {
            content: "";
            position: absolute;
            top: 0;
            left: max(5rem, calc((100vw - 1320px) / 2));
            right: max(5rem, calc((100vw - 1320px) / 2));
            border-top: 1px solid #e5e7eb;
        }
        .lina-footer-main {
            display: grid;
            grid-template-columns: 170px minmax(0, 1fr) 130px;
            gap: 2.4rem;
            align-items: start;
            max-width: 1320px;
            margin-left: auto;
            margin-right: auto;
        }
        .lina-footer-brand {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: .85rem;
            padding-top: 1.15rem;
        }
        .lina-footer-logo {
            display: flex;
            align-items: center;
            gap: .5rem;
            color: #737373;
            font-size: 1.16rem;
            font-weight: 900;
            line-height: 1;
            white-space: nowrap;
        }
        .lina-footer-logo-mark {
            width: 30px;
            height: 30px;
            border-radius: 2px;
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
            filter: grayscale(1);
            opacity: .72;
        }
        .lina-footer-logo-sub {
            color: #9ca3af;
            font-size: .5rem;
            font-weight: 700;
            text-align: center;
            margin-top: .24rem;
        }
        .lina-footer-ci {
            min-width: 122px;
            min-height: 34px;
            border: 1px solid #e5e7eb;
            border-radius: 3px;
            background: #fff;
            color: #737373;
            font-size: .82rem;
            font-weight: 900;
        }
        .lina-footer-section {
            margin-bottom: 1.05rem;
        }
        .lina-footer-heading {
            color: #111827;
            font-size: .86rem;
            font-weight: 900;
            margin-bottom: .5rem;
        }
        .lina-footer-links {
            display: flex;
            flex-wrap: wrap;
            gap: .38rem 0;
            color: #374151;
            font-size: .62rem;
            font-weight: 700;
            line-height: 1.6;
        }
        .lina-footer-links span {
            white-space: nowrap;
        }
        .lina-footer-links span + span::before {
            content: "";
            display: inline-block;
            width: 1px;
            height: .62rem;
            margin: 0 .48rem;
            background: #d1d5db;
            vertical-align: -.08rem;
        }
        .lina-footer-links .accent {
            color: #1d4ed8;
            font-weight: 900;
        }
        .lina-footer-badge {
            border: 1px solid #e5e7eb;
            min-height: 108px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #374151;
            font-size: .62rem;
            font-weight: 800;
            text-align: center;
            gap: .42rem;
        }
        .lina-footer-badge-icon {
            border: 2px solid #1f9a49;
            color: #1f9a49;
            width: 58px;
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: .82rem;
            font-weight: 900;
            background: #f7fff9;
        }
        .lina-footer-bottom {
            border-top: 1px solid #e5e7eb;
            margin-top: 1.6rem;
            padding: 1.25rem 0 .4rem;
            display: grid;
            grid-template-columns: 420px minmax(0, 1fr);
            gap: 2rem;
            align-items: center;
            color: #6b7280;
            font-size: .66rem;
            line-height: 1.6;
            max-width: 1320px;
            margin-left: auto;
            margin-right: auto;
        }
        .lina-footer-awards {
            display: flex;
            justify-content: flex-end;
            gap: .9rem;
            min-width: 0;
        }
        .lina-footer-award {
            display: flex;
            align-items: center;
            gap: .38rem;
            color: #6b7280;
            font-size: .54rem;
            font-weight: 800;
            line-height: 1.25;
            min-width: 0;
            white-space: nowrap;
        }
        .lina-footer-award-icon {
            flex: 0 0 34px;
            width: 34px;
            height: 24px;
            border: 1px solid #d1d5db;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9ca3af;
            font-size: .48rem;
            font-weight: 900;
            background: #fff;
        }
        @media (max-width: 900px) {
            .lina-footer-main,
            .lina-footer-bottom {
                grid-template-columns: 1fr;
            }
            .lina-footer-brand {
                align-items: flex-start;
            }
            .lina-footer-badge {
                max-width: 150px;
            }
            .lina-footer-awards {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def feature_url(feature_name):
    return f"?feature={quote(FEATURES[feature_name]['key'])}"


def get_today_recommendations(feature_names, limit=5):
    if not feature_names:
        return []
    start = date.today().toordinal() % len(feature_names)
    rotated = feature_names[start:] + feature_names[:start]
    return rotated[: min(limit, len(rotated))]


def set_active_feature(feature_name):
    st.session_state.active_feature = feature_name
    st.session_state.feature_changed_by_click = True


def sync_feature_from_query(feature_names):
    query_feature = st.query_params.get("feature")
    query_feature_name = FEATURE_KEYS.get(query_feature) or FEATURE_KEY_ALIASES.get(query_feature)
    if st.session_state.get("feature_changed_by_click"):
        active_feature = st.session_state.get("active_feature", feature_names[0])
        if active_feature in FEATURES:
            st.query_params["feature"] = FEATURES[active_feature]["key"]
        st.session_state.feature_changed_by_click = False
        return

    if query_feature_name:
        st.session_state.active_feature = query_feature_name
    elif "active_feature" not in st.session_state:
        st.session_state.active_feature = feature_names[0]


def render_interest_rail(active_feature):
    render_mobile_feature_menu(active_feature)
    rail_top = "11.9rem" if active_feature == FEATURE_KEYS["home"] else "11.3rem"
    feature_page_width_css = ""
    if active_feature != FEATURE_KEYS["home"]:
        feature_page_width_css = """
        @media (min-width: 1381px) {
            .main .block-container,
            section.main > div,
            div[data-testid="stMainBlockContainer"] {
                width: 100vw !important;
                max-width: none !important;
                margin-left: calc(50% - 50vw) !important;
                margin-right: calc(50% - 50vw) !important;
                padding-left: var(--lina-left-reserved) !important;
                padding-right: var(--lina-right-reserved) !important;
                box-sizing: border-box !important;
                left: 0 !important;
            }
        }        .feature-visual-banner,
        .feature-intro-card,
        .step-row,
        .saved-box,
        .result-grid,
        .insight-box,
        .source-note,
        .direct-cta,
        .worry-step-row,
        .worry-question-card,
        .worry-result,
        .worry-direct,
        .st-key-dictionary_chat_surface,
        .st-key-policy_chat_surface,
        .st-key-lina_faq_ai_chat_surface,
        .stFileUploader,
        div[data-testid="stHorizontalBlock"],
        div[data-testid="stTabs"],
        div[data-testid="stForm"]:not(.st-key-dictionary_chat_surface div[data-testid="stForm"]):not(.st-key-policy_chat_surface div[data-testid="stForm"]):not(.st-key-lina_faq_ai_chat_surface div[data-testid="stForm"]),
        div[data-testid="stRadio"],
        div[data-testid="stVerticalBlockBorderWrapper"] {
            max-width: var(--lina-content-max) !important;
            margin-left: auto !important;
            margin-right: auto !important;
            box-sizing: border-box !important;
        }
        .feature-visual-banner,
        .st-key-dictionary_chat_surface,
        .st-key-policy_chat_surface,
        .st-key-lina_faq_ai_chat_surface {
            transform: none !important;
        }
        """
    st.markdown(
        f"""
        <style>
        {feature_page_width_css}
        .interest-rail,
        .st-key-interest_rail {{
            top: {rail_top} !important;
            max-height: calc(100vh - {rail_top} - 1rem) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="interest_rail"):
        for section_index, section in enumerate(INTEREST_SECTIONS):
            with st.container(key=f"interest_section_{section_index}"):
                st.markdown(
                    f'<div class="interest-section-name">{section["title"]}</div>',
                    unsafe_allow_html=True,
                )
                for feature_name, label in section["items"]:
                    button_type = "primary" if feature_name == active_feature else "secondary"
                    st.button(
                        label,
                        key=f"interest_nav_{FEATURES[feature_name]['key']}",
                        type=button_type,
                        use_container_width=True,
                        on_click=set_active_feature,
                        args=(feature_name,),
                    )
        with st.container(key="interest_search_card"):
            search_query = st.text_input(
                "기능 검색",
                key="interest_feature_search",
                placeholder="",
                label_visibility="collapsed",
            ).strip()
            st.button(
                "검색",
                key="interest_feature_search_button",
                help="기능 검색",
            )
            if search_query:
                searchable_features = [name for name in FEATURES if name != FEATURE_KEYS["home"]]
                matches = [name for name in searchable_features if search_query.lower() in name.lower()]
                if matches:
                    for feature_name in matches[:5]:
                        button_type = "primary" if feature_name == active_feature else "secondary"
                        st.button(
                            feature_name,
                            key=f"interest_search_{FEATURES[feature_name]['key']}",
                            type=button_type,
                            use_container_width=True,
                            on_click=set_active_feature,
                            args=(feature_name,),
                        )
                else:
                    st.markdown(
                        '<div class="interest-search-empty">검색 결과가 없습니다.</div>',
                        unsafe_allow_html=True,
                    )


def render_mobile_feature_menu(active_feature):
    sections_html = []
    for section in INTEREST_SECTIONS:
        links_html = []
        for feature_name, label in section["items"]:
            active_class = " active" if feature_name == active_feature else ""
            links_html.append(
                f'<a class="mobile-feature-menu-link{active_class}" href="{feature_url(feature_name)}" target="_self">{label}</a>'
            )
        sections_html.append(
            "".join(
                [
                    '<div class="mobile-feature-section">',
                    f'<div class="mobile-feature-section-title">{section["title"]}</div>',
                    '<div class="mobile-feature-links">',
                    "".join(links_html),
                    "</div>",
                    "</div>",
                ]
            )
        )
    st.markdown(
        f"""
        <details class="mobile-feature-menu">
            <summary>기능 메뉴</summary>
            <div class="mobile-feature-menu-panel">{"".join(sections_html)}</div>
        </details>
        """,
        unsafe_allow_html=True,
    )


def render_event_rail(active_feature):
    mini_chat_href = "?feature=lina_faq_ai&chat=1#lina-gunggeumtalk-chat"
    chat_orb_uri = image_data_uri(str(CHAT_ORB_ASSET))
    st.markdown(
        f"""
        <aside class="event-rail" aria-label="라이나 다이렉트 이벤트">
            <a class="event-rail-card" href="https://direct.lina.co.kr/event/detail?evtSeq=2421" target="_blank" rel="noopener noreferrer">
                <div class="event-rail-head">
                    <div class="event-rail-kicker">EVENT</div>
                    <div class="event-rail-title">다이렉트 보험 가입 시<br>신세계 상품권 증정</div>
                    <div class="event-rail-gift">100%</div>
                </div>
                <div class="event-rail-body">
                    <div class="event-rail-status">진행중</div>
                    <div class="event-rail-name">2026년 6월 가입감사 이벤트</div>
                    <div class="event-rail-desc">라이나생명 다이렉트에서 진행 중인 이벤트를 확인해보세요.</div>
                    <div class="event-rail-more">이벤트 보러가기</div>
                </div>
            </a>
            <a class="customer-rail-card" href="https://www.lina.co.kr/customer/consult" target="_blank" rel="noopener noreferrer">
                <div class="customer-rail-top">
                    <div class="customer-rail-icon">☎</div>
                    <div>
                        <div class="customer-rail-kicker">CUSTOMER</div>
                        <div class="customer-rail-title">고객센터</div>
                    </div>
                </div>
                <div class="customer-rail-desc">보험 상담과 문의가 필요할 때 라이나 고객센터로 연결됩니다.</div>
                <div class="customer-rail-more">상담 바로가기</div>
            </a>
            <a class="chatbot-rail-card" href="{mini_chat_href}" target="_self" aria-label="라이나 궁금톡 바로가기">
                <div class="customer-rail-top">
                    <div class="chatbot-rail-icon"><img src="{chat_orb_uri}" alt=""></div>
                    <div>
                        <div class="customer-rail-kicker">CHATBOT</div>
                        <div class="customer-rail-title">챗봇</div>
                    </div>
                </div>
                <div class="customer-rail-desc">궁금톡 AI 상담 기능으로 이동합니다.</div>
                <div class="customer-rail-more">챗봇 열기</div>
            </a>
        </aside>
        """,
        unsafe_allow_html=True,
    )


def render_top_nav():
    feature_names = list(FEATURES.keys())
    sync_feature_from_query(feature_names)
    is_home = st.session_state.active_feature == FEATURE_KEYS["home"]

    home_href = feature_url("홈")
    brand_logo_uri = image_data_uri(str(BRAND_LOGO))
    brand_logo_html = f'<img class="brand-name-mark" src="{brand_logo_uri}" alt="LINA">' if brand_logo_uri else ""
    st.markdown(
        f"""
        <div class="brand-life-wrap">
            <div class="brand-row">
                <div class="brand-text">
                    <a class="brand-name" href="{home_href}" target="_self">{brand_logo_html}<span class="lina">LINA</span> <span class="hub">HUB</span></a>
                </div>
            </div>
            <nav class="hub-top-tabs" aria-label="LINA HUB categories">
                <a class="hub-top-tab" href="{feature_url('AI보험용어사전')}" target="_self">보험이 궁금할때</a>
                <a class="hub-top-tab" href="{feature_url('라이프타임 계산기')}" target="_self">Fun Fun한 라이나</a>
                <a class="hub-top-tab" href="{feature_url('오늘의 직관! 미세먼지는?')}" target="_self">생활속 라이나</a>
                <a class="hub-top-tab" href="{feature_url('이벤트')}" target="_self">이벤트</a>
                <a class="hub-top-tab" href="https://www.lina.co.kr/customer/consult" target="_blank">고객센터</a>
            </nav>
            <details class="mobile-hub-menu">
                <summary>메뉴</summary>
                <div class="mobile-hub-menu-panel">
                    <a href="{feature_url('AI보험용어사전')}" target="_self">보험이 궁금할때</a>
                    <a href="{feature_url('라이프타임 계산기')}" target="_self">Fun Fun한 라이나</a>
                    <a href="{feature_url('오늘의 직관! 미세먼지는?')}" target="_self">생활속 라이나</a>
                    <a href="{feature_url('이벤트')}" target="_self">이벤트</a>
                    <a href="https://www.lina.co.kr/customer/consult" target="_blank">고객센터</a>
                </div>
            </details>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_home:
        return st.session_state.active_feature

    return st.session_state.active_feature



def render_mini_chat(active_feature):
    if not st.query_params.get("mini_chat"):
        return

    feature_key = FEATURES[active_feature]["key"]
    close_href = f"?feature={quote(feature_key)}"
    iframe_src = "http://127.0.0.1:8501/?feature=lina_faq_ai&mini_embed=1&chat=1"

    st.markdown(
        f"""
        <style>
        .lina-mini-chat-panel {{
            position: fixed;
            right: 42px;
            bottom: 34px;
            width: min(420px, calc(100vw - 34px));
            height: min(640px, calc(100vh - 72px));
            z-index: 10020;
            border: 1px solid #dfe7f1;
            border-radius: 22px;
            background: #fff;
            box-shadow: 0 18px 50px rgba(15,23,42,.18);
            overflow: hidden;
            font-family: inherit;
        }}
        .lina-mini-chat-head {{
            height: 72px;
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:.8rem;
            padding:0 .95rem 0 1rem;
            background:#24138d;
            color:#fff;
        }}
        .lina-mini-chat-title {{ font-size:.95rem; font-weight:950; line-height:1.2; }}
        .lina-mini-chat-close {{
            display:flex; align-items:center; justify-content:center;
            width:2rem; height:2rem; border-radius:999px;
            background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.28);
            color:#fff !important; text-decoration:none !important; font-size:1.15rem; font-weight:900;
            flex:0 0 auto;
        }}
        .lina-mini-chat-frame {{
            display:block;
            width:100%;
            height:calc(100% - 72px);
            border:0;
            background:#fff;
        }}
        @media (max-width: 980px) {{
            .lina-mini-chat-panel {{ right: 16px; bottom: 18px; }}
        }}
        </style>
        <section class="lina-mini-chat-panel" aria-label="라이나 궁금톡 미니 상담창">
            <div class="lina-mini-chat-head">
                <div class="lina-mini-chat-title">라이나 궁금톡</div>
                <a class="lina-mini-chat-close" href="{close_href}" target="_self" aria-label="상담창 닫기">×</a>
            </div>
            <iframe class="lina-mini-chat-frame" src="{iframe_src}" title="라이나 궁금톡"></iframe>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    logo_uri = image_data_uri(str(BRAND_LOGO))
    logo_mark_html = (
        f'<div class="lina-footer-logo-mark" style="background-image:url({logo_uri});"></div>'
        if logo_uri
        else '<div class="lina-footer-logo-mark"></div>'
    )
    st.markdown(
        f"""
        <footer class="lina-footer">
            <div class="lina-footer-main">
                <div class="lina-footer-brand">
                    <div>
                        <div class="lina-footer-logo">{logo_mark_html}<span>라이나생명</span></div>
                        <div class="lina-footer-logo-sub">A Chubb Company</div>
                    </div>
                    <button class="lina-footer-ci" type="button">브랜드/CI</button>
                </div>
                <div>
                    <div class="lina-footer-section">
                        <div class="lina-footer-heading">개인정보보호/상품 관련 안내</div>
                        <div class="lina-footer-links">
                            <span class="accent">개인정보처리방침</span><span>신용정보활용체제</span><span>전자금융거래약관</span><span>전자금융서비스약관</span><span>본인정보 이용·제공 조회</span><span>본인정보 이용·제공 철회</span><span>개인(신용)정보 열람·정정 청구</span><span>개인(신용)정보 삭제 청구</span><span>보호금융상품등록부</span><span>개인신용정보 전송요구·철회</span><span>법금융권고객정보보호캠페인</span>
                        </div>
                    </div>
                    <div class="lina-footer-section">
                        <div class="lina-footer-heading">접수/신고 안내</div>
                        <div class="lina-footer-links">
                            <span>전자민원접수</span><span>보험가입자발신고센터</span><span>보험모집질서위반신고</span><span>서민금융119</span><span>TV보험광고제공요청</span>
                        </div>
                    </div>
                    <div class="lina-footer-section">
                        <div class="lina-footer-heading">협력사 안내</div>
                        <div class="lina-footer-links">
                            <span>전자구매시스템</span>
                        </div>
                    </div>
                </div>
                <div class="lina-footer-badge">
                    <div class="lina-footer-badge-icon">파인</div>
                    <div>금융소비자 정보포털<br>‘파인’</div>
                </div>
            </div>
            <div class="lina-footer-bottom">
                <div>
                    서울특별시 종로구 삼봉로 48 (청진동 188) 라이나타워 라이나생명(주)<br>
                    대표이사 조지은&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;사업자등록번호 104-81-85673<br><br>
                    ©LINA Life Insurance Co., Ltd. All rights reserved. For more information, Contact linaweb@linakorea.com
                </div>
                <div class="lina-footer-awards">
                    <div class="lina-footer-award"><span class="lina-footer-award-icon">WA</span><span>정보통신접근성<br>품질인증 획득</span></div>
                    <div class="lina-footer-award"><span class="lina-footer-award-icon">KSQI</span><span>2013년 KMAC 선정<br>KSQI 한국의 우수 콜센터</span></div>
                    <div class="lina-footer-award"><span class="lina-footer-award-icon">R</span><span>KMAC 선정 2021년 소비자가 가장<br>추천하는 브랜드 생명보험 부문 1위</span></div>
                    <div class="lina-footer-award"><span class="lina-footer-award-icon">CCM</span><span>공정거래위원회 주관<br>소비자중심경영 CCM 인증 획득</span></div>
                </div>
            </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def main():
    render_base_css()
    feature_names = list(FEATURES.keys())
    if st.query_params.get("mini_embed") == "1" or st.query_params.get("embed") == "1":
        for feature in FEATURES.values():
            if feature.get("key") == "lina_faq_ai":
                feature["renderer"]()
                return

    sync_feature_from_query(feature_names)
    active_feature = st.session_state.active_feature
    active_feature = render_top_nav()
    render_interest_rail(active_feature)
    if active_feature != FEATURE_KEYS["home"]:
        render_event_rail(active_feature)
    FEATURES[active_feature]["renderer"]()
    render_mini_chat(active_feature)
    render_footer()


if __name__ == "__main__":
    main()



