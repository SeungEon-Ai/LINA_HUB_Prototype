from __future__ import annotations

import time
import re
from html import escape

import streamlit as st

from features.local_secrets import get_openai_api_key
from features.shared_header import render_feature_banner, render_feature_intro_card

from .ai import generate_dental_commentary
from .data import calculate_dental_score


QUESTION_STEPS = [
    {
        "field": "age_group",
        "title": "현재 연령대는 어디에 가까우신가요?",
        "kind": "choice",
        "options": ["10대 후반", "20대", "30대", "40대", "50대 이상"],
    },
    {
        "field": "brushing",
        "title": "하루에 양치는 보통 몇 번 하세요?",
        "kind": "choice",
        "options": ["매 식후 3회 이상", "하루 2회", "하루 1회", "가끔 하루를 넘김", "며칠씩 놓칠 때 있음"],
    },
    {
        "field": "brushing_time",
        "title": "한 번 양치할 때 시간은 어느 정도인가요?",
        "kind": "choice",
        "options": ["3분 이상 꼼꼼히", "2분 정도", "1분 안팎", "대충 빠르게", "기억 안 날 정도로 짧음"],
    },
    {
        "field": "night_brushing",
        "title": "자기 전 양치는 얼마나 잘 지키세요?",
        "kind": "choice",
        "options": ["거의 매일 지킴", "일주일 1~2회 놓침", "절반 정도 놓침", "자주 놓침", "거의 안 함"],
    },
    {
        "field": "floss",
        "title": "치실이나 치간칫솔을 사용하시나요?",
        "kind": "choice",
        "options": ["매일 사용", "주 3~4회", "가끔 사용", "거의 안 씀", "사용해본 적 거의 없음"],
    },
    {
        "field": "sweet_snack",
        "title": "단 간식이나 단 음료는 얼마나 자주 드세요?",
        "kind": "choice",
        "options": ["거의 안 먹음", "주 1~2회", "주 3~5회", "하루 1회", "하루 2회 이상"],
    },
    {
        "field": "coffee_soda",
        "title": "커피, 탄산, 산성 음료는 얼마나 자주 마시나요?",
        "kind": "choice",
        "options": ["거의 안 마심", "주 1~2회", "주 3~5회", "하루 1회", "하루 2회 이상"],
    },
    {
        "field": "after_drink",
        "title": "단 음료나 커피를 마신 뒤 입안을 헹구는 편인가요?",
        "kind": "choice",
        "options": ["대부분 물로 헹굼", "가끔 헹굼", "잘 안 헹굼", "바로 양치하는 편", "신경 써본 적 없음"],
    },
    {
        "field": "smoking",
        "title": "흡연 여부를 알려주세요.",
        "kind": "choice",
        "options": ["비흡연", "과거 흡연", "가끔 흡연", "현재 흡연", "전자담배 포함 자주 흡연"],
    },
    {
        "field": "scaling",
        "title": "마지막 스케일링은 언제 받으셨나요?",
        "kind": "choice",
        "options": ["6개월 이내", "1년 이내", "1~2년 전", "2년 이상 안 함", "기억 안 남"],
    },
    {
        "field": "checkup",
        "title": "마지막 치과 검진은 언제였나요?",
        "kind": "choice",
        "options": ["6개월 이내", "1년 이내", "1~2년 전", "2년 이상 안 함", "기억 안 남"],
    },
    {
        "field": "bleeding",
        "title": "양치할 때 피가 나는 편인가요?",
        "kind": "choice",
        "options": ["거의 없음", "한 달에 가끔", "주 1~2회", "자주 있음", "거의 매번 있음"],
    },
    {
        "field": "pain",
        "title": "욱신거리는 치아 통증이 있나요?",
        "kind": "choice",
        "options": ["거의 없음", "아주 가끔", "월 1~2회", "주 1회 이상", "자주 아픔"],
    },
    {
        "field": "cold",
        "title": "찬물이나 뜨거운 음식에 치아가 시린가요?",
        "kind": "choice",
        "options": ["거의 없음", "아주 가끔", "특정 치아만 가끔", "자주 시림", "일상적으로 불편함"],
    },
    {
        "field": "chewing",
        "title": "씹을 때 불편하거나 아픈 느낌이 있나요?",
        "kind": "choice",
        "options": ["거의 없음", "딱딱한 음식만 가끔", "특정 부위만 불편", "자주 불편", "씹기 힘들 정도"],
    },
    {
        "field": "bad_breath",
        "title": "입냄새나 입안 텁텁함이 자주 느껴지나요?",
        "kind": "choice",
        "options": ["거의 없음", "아침에만 가끔", "피곤할 때 가끔", "자주 느낌", "거의 매일 신경 쓰임"],
    },
    {
        "field": "gum_swelling",
        "title": "잇몸이 붓거나 내려앉은 느낌이 있나요?",
        "kind": "choice",
        "options": ["전혀 없음", "가끔 붓는 느낌", "특정 부위만 불편", "자주 붓거나 내려앉음", "치아가 흔들리는 느낌도 있음"],
    },
    {
        "field": "visit_delay",
        "title": "치과 방문은 보통 어떤 편인가요?",
        "kind": "choice",
        "options": ["정기적으로 감", "불편하면 바로 감", "조금 미룸", "아파도 꽤 미룸", "참을 수 있을 때까지 미룸"],
    },
    {
        "field": "past_treatment",
        "title": "과거에 받은 큰 치과치료가 있나요?",
        "kind": "choice",
        "options": ["큰 치료 없음", "충전치료 경험", "크라운/신경치료 경험", "임플란트/브릿지 경험", "여러 치료가 반복됨"],
    },
    {
        "field": "cost_worry",
        "title": "치과비 때문에 치료를 망설인 적이 있나요?",
        "kind": "choice",
        "options": ["거의 없음", "한두 번 있음", "가끔 망설임", "자주 미룸", "비용 때문에 치료를 포기한 적 있음"],
    },
]


def render_css():
    st.markdown(
        """
        <style>
        .dental-step-row {
            display: flex;
            flex-wrap: wrap;
            gap: .42rem;
            margin: .45rem 0 .95rem;
        }
        .dental-step-chip {
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            background: #fff;
            color: #64748b;
            font-size: .72rem;
            line-height: 1;
            padding: .27rem .56rem;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .dental-step-chip.active {
            border-color: #f5b51b;
            background: #fff8e6;
            color: #111827;
            font-weight: 850;
        }
        .dental-step-chip.done {
            background: #f1f5f9;
            color: #334155;
        }
        .dental-intro {
            border: 1px solid #e8edf3;
            border-radius: 12px;
            background: #ffffff;
            padding: .85rem .95rem;
            margin: .3rem 0 .8rem;
            color: #475569;
            font-size: .84rem;
            line-height: 1.55;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .dental-question-card {
            border: 1px solid #e8edf3;
            border-radius: 16px;
            background: #ffffff;
            padding: 1rem 1rem;
            margin: .45rem 0 .85rem;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .dental-question-count {
            color: #d99a08;
            font-size: .76rem;
            font-weight: 900;
            line-height: 1;
            margin-bottom: .4rem;
        }
        .dental-question-title {
            color: #111827;
            font-size: 1.06rem;
            font-weight: 900;
            line-height: 1.35;
            letter-spacing: 0;
        }
        .dental-mini-progress {
            height: 8px;
            border-radius: 999px;
            background: #e8edf3;
            overflow: hidden;
            margin: .5rem 0 1rem;
        }
        .dental-mini-progress-fill {
            height: 8px;
            border-radius: 999px;
            background: #f5b51b;
        }
        .dental-score-card {
            border: 1px solid #e8edf3;
            border-radius: 18px;
            background: linear-gradient(180deg, #fffdf5 0%, #ffffff 100%);
            padding: 1.05rem 1rem;
            margin: .8rem 0;
        }
        .dental-score-top {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: .65rem;
            margin-bottom: .9rem;
        }
        .dental-score-pill {
            border: 1px solid #e5ebf3;
            border-radius: 999px;
            padding: .75rem .85rem;
            text-align: center;
            background: #fff;
        }
        .dental-score-pill.primary {
            border-color: #f5b51b;
            background: #fff8e6;
        }
        .dental-score-label {
            color: #64748b;
            font-size: .72rem;
            line-height: 1.1;
            margin-bottom: .25rem;
        }
        .dental-score-value {
            color: #111827;
            font-size: 1.5rem;
            font-weight: 950;
            line-height: 1.05;
            letter-spacing: 0;
        }
        .dental-type-title {
            color: #111827;
            font-size: 1.18rem;
            font-weight: 950;
            line-height: 1.25;
            margin-bottom: .3rem;
        }
        .dental-type-copy {
            color: #475569;
            font-size: .85rem;
            line-height: 1.55;
        }
        .dental-risk-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: .55rem;
            margin: .75rem 0;
        }
        .dental-risk-card {
            border: 1px solid #e5ebf3;
            border-radius: 14px;
            background: #f8fafc;
            padding: .65rem .7rem;
        }
        .dental-risk-label {
            color: #64748b;
            font-size: .72rem;
            margin-bottom: .25rem;
        }
        .dental-risk-bar {
            height: 8px;
            background: #e2e8f0;
            border-radius: 999px;
            overflow: hidden;
        }
        .dental-risk-fill {
            height: 8px;
            border-radius: 999px;
            background: #f5b51b;
        }
        .dental-list-box {
            border: 1px solid #e8edf3;
            border-radius: 12px;
            padding: .8rem .9rem;
            background: #ffffff;
            margin: .65rem 0;
            color: #334155;
            font-size: .84rem;
            line-height: 1.55;
        }
        .dental-list-title {
            color: #111827;
            font-weight: 900;
            margin-bottom: .35rem;
        }
        .dental-list-box ul {
            margin: .25rem 0 0 1rem;
            padding: 0;
        }
        .dental-ai-box {
            border: 1px solid #e8edf3;
            border-radius: 12px;
            background: #f8fafc;
            padding: .85rem .95rem;
            color: #1f2937;
            font-size: .86rem;
            line-height: 1.62;
            margin: .75rem 0;
            white-space: pre-wrap;
        }
        .dental-direct {
            border: 1px solid #f2d98b;
            border-radius: 14px;
            background: #fffaf0;
            padding: .85rem .95rem;
            margin: .75rem 0;
            color: #334155;
            font-size: .83rem;
            line-height: 1.55;
        }
        .dental-direct-title {
            color: #111827;
            font-weight: 950;
            margin-bottom: .3rem;
        }
        .dental-direct a {
            display: inline-block;
            margin-top: .55rem;
            border: 1px solid #f5b51b;
            border-radius: 999px;
            background: #ffffff;
            color: #111827;
            font-size: .76rem;
            font-weight: 850;
            line-height: 1;
            padding: .38rem .72rem;
            text-decoration: none;
        }
        @media (max-width: 760px) {
            .dental-score-top,
            .dental-risk-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def default_inputs() -> dict:
    return {
        "age_group": "20대",
        "brushing": "하루 2회",
        "brushing_time": "2분 정도",
        "night_brushing": "일주일 1~2회 놓침",
        "floss": "가끔 사용",
        "sweet_snack": "주 3~5회",
        "coffee_soda": "주 3~5회",
        "after_drink": "가끔 헹굼",
        "smoking": "비흡연",
        "scaling": "1년 이내",
        "checkup": "1년 이내",
        "bleeding": "한 달에 가끔",
        "pain": "거의 없음",
        "cold": "아주 가끔",
        "chewing": "거의 없음",
        "bad_breath": "아침에만 가끔",
        "gum_swelling": "전혀 없음",
        "visit_delay": "조금 미룸",
        "past_treatment": "충전치료 경험",
        "cost_worry": "한두 번 있음",
    }


def init_state():
    if st.session_state.get("dental_score_version") != 3:
        st.session_state.dental_score_step = 0
        st.session_state.dental_score_inputs = default_inputs()
        st.session_state.dental_score_result = None
        st.session_state.dental_score_ai_commentary = ""
        st.session_state.dental_score_version = 3
    if "dental_score_step" not in st.session_state:
        st.session_state.dental_score_step = 0
    if "dental_score_inputs" not in st.session_state:
        st.session_state.dental_score_inputs = default_inputs()
    if "dental_score_result" not in st.session_state:
        st.session_state.dental_score_result = None
    if "dental_score_ai_commentary" not in st.session_state:
        st.session_state.dental_score_ai_commentary = ""


def render_step_status():
    step = st.session_state.dental_score_step
    if step < len(QUESTION_STEPS):
        progress = int((step / len(QUESTION_STEPS)) * 100)
        label = f"{step + 1} / {len(QUESTION_STEPS)}"
    else:
        progress = 100
        label = "결과"
    st.markdown(
        f"""
        <div class="dental-step-row">
            <span class="dental-step-chip active">{label}</span>
            <span class="dental-step-chip">한 문항씩 진행</span>
        </div>
        <div class="dental-mini-progress"><div class="dental-mini-progress-fill" style="width:{progress}%;"></div></div>
        """,
        unsafe_allow_html=True,
    )


def render_intro():
    render_feature_intro_card(
        "치아 건강점수는 생활습관, 스케일링/검진 공백, 현재 증상, 치과 방문 미루기 성향을 함께 반영한 셀프체크입니다.\n"
        "결과는 진단이 아니라 재미와 점검용이며, 통증·출혈·흔들림·붓기가 반복되면 치과 진료가 우선입니다."
    )


def render_question_step():
    step = st.session_state.dental_score_step
    inputs = st.session_state.dental_score_inputs
    question = QUESTION_STEPS[step]
    field = question["field"]
    st.markdown(
        f"""
        <div class="dental-question-card">
            <div class="dental-question-count">{step + 1}번째 질문</div>
            <div class="dental-question-title">{question["title"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form(f"dental_question_form_{step}"):
        if question["kind"] == "number":
            value = st.number_input(
                "답변",
                min_value=question["min"],
                max_value=question["max"],
                value=int(inputs[field]),
                step=question["step"],
                label_visibility="collapsed",
            )
        else:
            options = question["options"]
            value = st.radio(
                "답변",
                options,
                index=options.index(inputs[field]),
                label_visibility="collapsed",
            )
        col1, col2 = st.columns([1, 2])
        with col1:
            back = st.form_submit_button("이전", use_container_width=True, disabled=step == 0)
        with col2:
            label = "내 치아 건강점수 보기" if step == len(QUESTION_STEPS) - 1 else "다음"
            submitted = st.form_submit_button(label, use_container_width=True)

        if back:
            st.session_state.dental_score_step = max(0, step - 1)
            st.rerun()
        if submitted:
            st.session_state.dental_score_inputs[field] = value
            if step == len(QUESTION_STEPS) - 1:
                progress_text = st.empty()
                progress_bar = st.progress(0)
                for progress_value in range(1, 91):
                    progress_text.markdown("치아 건강 신호를 분석하고 있어요.")
                    progress_bar.progress(progress_value)
                    time.sleep(0.07)

                progress_text.markdown("치아 건강점수와 결과 문구를 정리하고 있어요.")
                progress_bar.progress(94)
                result = calculate_dental_score(st.session_state.dental_score_inputs)
                st.session_state.dental_score_result = result
                api_key = get_openai_api_key()
                try:
                    if api_key:
                        progress_text.markdown("치아 건강점수 설명을 작성하고 있어요.")
                        progress_bar.progress(97)
                    st.session_state.dental_score_ai_commentary = generate_dental_commentary(
                        api_key,
                        st.session_state.dental_score_inputs,
                        result,
                    ) or ""
                except Exception as exc:
                    st.session_state.dental_score_ai_commentary = f"결과 설명을 불러오지 못해 기본 분석 결과로 표시합니다. ({exc})"
                progress_text.markdown("결과 화면을 준비하고 있어요.")
                progress_bar.progress(100)
                time.sleep(0.3)
                progress_text.empty()
                progress_bar.empty()
                st.session_state.dental_score_step = len(QUESTION_STEPS)
            else:
                st.session_state.dental_score_step = step + 1
            st.rerun()


def render_risk_cards(result: dict):
    labels = {
        "cavity": "충치 리스크",
        "gum": "잇몸 리스크",
        "sensitive": "시림/통증 리스크",
        "delay": "치과 미루기 리스크",
        "cost": "치료비 공백 리스크",
    }
    cards = []
    for key, label in labels.items():
        percent = result["risk_percent"][key]
        cards.append(
            f'<div class="dental-risk-card"><div class="dental-risk-label">{label} {percent}%</div>'
            f'<div class="dental-risk-bar"><div class="dental-risk-fill" style="width:{percent}%;"></div></div></div>'
        )
    st.markdown(f'<div class="dental-risk-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_detail_list(title: str, items: list[str]):
    if not items:
        return
    safe_items = "".join(f"<li>{escape(str(item))}</li>" for item in items)
    st.markdown(
        f"""
        <div class="dental-list-box">
            <div class="dental-list-title">{escape(title)}</div>
            <ul>{safe_items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def normalize_ai_commentary(text: str) -> str:
    text = str(text or "").replace("**", "").strip()
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"(?m)^(\s*\d+)\.\s*\n+\s*", r"\1. ", text)
    text = re.sub(r"(?m)^(\s*[-•])\s*\n+\s*", r"\1 ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def render_result():
    result = st.session_state.dental_score_result
    if not result:
        st.session_state.dental_score_step = 0
        st.rerun()

    st.markdown(
        f"""
        <div class="dental-score-card">
            <div class="dental-score-top">
                <div class="dental-score-pill primary">
                    <div class="dental-score-label">치아 건강점수</div>
                    <div class="dental-score-value">{result["score"]}점</div>
                </div>
                <div class="dental-score-pill">
                    <div class="dental-score-label">치아 나이 느낌</div>
                    <div class="dental-score-value">{result["dental_age"]}세</div>
                </div>
                <div class="dental-score-pill">
                    <div class="dental-score-label">현재 등급</div>
                    <div class="dental-score-value">{result["grade"]}</div>
                </div>
            </div>
            <div class="dental-type-title">{result["type"]["title"]}</div>
            <div class="dental-type-copy">{result["type"]["copy"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_risk_cards(result)

    render_detail_list("좋게 반영된 부분", result.get("strengths") or result["positives"])
    render_detail_list("점수가 낮아진 주요 이유", result.get("top_factors") or result["warnings"])
    render_detail_list("바로 바꿔볼 7일 루틴", result.get("routine_plan", []))

    if st.session_state.get("dental_score_ai_commentary"):
        safe_commentary = escape(normalize_ai_commentary(st.session_state.dental_score_ai_commentary))
        st.markdown(
            f'<div class="dental-ai-box">{safe_commentary}</div>',
            unsafe_allow_html=True,
        )

    hooks = "<br>".join(f"- {hook}" for hook in result["insurance_hooks"])
    st.markdown(
        f"""
        <div class="dental-direct">
            <div class="dental-direct-title">치아보장으로 자연스럽게 연결해보면</div>
            {hooks}<br>
            치아보험은 상품마다 면책기간, 감액기간, 보장되는 치료명이 다를 수 있으니 약관 기준으로 확인하는 편이 좋습니다.
            <br>
            <a href="https://direct.lina.co.kr/" target="_blank">라이나생명 다이렉트 치아보험 확인하기</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("본 점수는 재미와 셀프점검용이며, 치과 진단이나 치료 필요 여부를 대신하지 않습니다.")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("다시 체크하기", use_container_width=True):
            st.session_state.dental_score_step = 0
            st.session_state.dental_score_inputs = default_inputs()
            st.session_state.dental_score_result = None
            st.session_state.dental_score_ai_commentary = ""
            st.rerun()
    with col2:
        if st.button("라이나 약관 AI에서 치아보장 물어보기", use_container_width=True):
            st.session_state.active_feature = "라이나 약관 AI"
            st.rerun()


def render():
    render_css()
    init_state()
    render_feature_banner("assets/feature_banners/dental_score.png", "내 치아 건강점수는 몇점?")
    render_intro()
    render_step_status()

    if st.session_state.dental_score_step < len(QUESTION_STEPS):
        render_question_step()
    else:
        render_result()
