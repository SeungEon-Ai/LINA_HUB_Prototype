import base64
import time
from pathlib import Path

import streamlit as st

from features.shared_header import render_feature_banner, render_feature_intro_card


ROOT = Path(__file__).resolve().parents[2]
LOGO_MARK = ROOT / "assets" / "lina_mark_color.png"


QUESTIONS = [
    {
        "text": "갑자기 쉬어야 한다면 제일 먼저 드는 생각은?",
        "options": [
            ("생활비가 바로 걱정돼요", "family"),
            ("병원비가 얼마나 나올지 무서워요", "health"),
            ("카드값과 고정비부터 떠올라요", "money"),
            ("일단 어떻게든 버틸 것 같아요", "present"),
            ("가족에게 부담이 될까 걱정돼요", "family"),
        ],
    },
    {
        "text": "미래 걱정이 가장 크게 올라오는 순간은?",
        "options": [
            ("가족에게 돈 이야기를 꺼낼 때", "family"),
            ("건강검진 결과를 기다릴 때", "health"),
            ("월말 카드값을 볼 때", "money"),
            ("뉴스에서 큰 질병 이야기를 볼 때", "health"),
            ("아직은 잘 모르겠고 미루고 싶을 때", "present"),
        ],
    },
    {
        "text": "치과 예약을 미루는 편인가요?",
        "options": [
            ("네, 비용 생각하면 미루게 돼요", "money"),
            ("아프면 바로 가는 편이에요", "health"),
            ("예약 자체를 자주 까먹어요", "present"),
            ("가족 치료비가 더 신경 쓰여요", "family"),
            ("치과비는 늘 갑자기 커지는 느낌이에요", "money"),
        ],
    },
    {
        "text": "가족에게 가장 남기고 싶은 건?",
        "options": [
            ("갑자기 흔들리지 않는 생활", "family"),
            ("건강하게 오래 함께 있는 시간", "health"),
            ("지금 즐거운 추억", "present"),
            ("돈 때문에 선택지가 줄지 않는 상황", "money"),
            ("내가 없어도 버틸 수 있는 여유", "family"),
        ],
    },
    {
        "text": "보험 이야기를 들으면 먼저 드는 생각은?",
        "options": [
            ("뭐가 필요한지 잘 모르겠어요", "present"),
            ("큰 병이 생기면 어쩌지 싶어요", "health"),
            ("매달 내는 돈이 부담돼요", "money"),
            ("가족에게 도움이 될 수 있을까 생각해요", "family"),
            ("너무 복잡해서 나중에 보고 싶어요", "present"),
        ],
    },
    {
        "text": "미래의 나에게 가장 먼저 챙겨주고 싶은 건?",
        "options": [
            ("아프더라도 치료비 걱정을 줄이는 것", "health"),
            ("가족 생활이 갑자기 흔들리지 않는 것", "family"),
            ("예상 못 한 큰 지출을 막는 것", "money"),
            ("너무 복잡하지 않게 시작하는 것", "present"),
            ("지금의 생활도 너무 희생하지 않는 것", "present"),
        ],
    },
    {
        "text": "갑작스러운 일이 생겼을 때 가장 피하고 싶은 상황은?",
        "options": [
            ("가족이 생활비 때문에 불안해지는 것", "family"),
            ("병원비 때문에 치료 선택이 좁아지는 것", "health"),
            ("모아둔 돈이 한 번에 사라지는 것", "money"),
            ("뭘 해야 할지 몰라 계속 미루는 것", "present"),
            ("고정비를 감당하지 못하는 것", "money"),
        ],
    },
]


RESULTS = {
    "family": {
        "title": "가족 안전벨트형",
        "tagline": "내 걱정보다 가족의 생활 리듬을 먼저 떠올리는 타입입니다.",
        "copy": "평소엔 담담해 보여도, 갑작스러운 소득 공백이나 가족 생활비 문제에는 예민하게 반응하는 편입니다. 이런 유형은 큰 보장보다도 가족이 당장 흔들리지 않을 최소 안전선을 먼저 생각해보면 좋습니다.",
        "chips": ["생활비 공백", "가족 책임", "소득 단절"],
    },
    "health": {
        "title": "건강 알림등형",
        "tagline": "미래 걱정의 버튼이 건강 쪽에서 켜지는 타입입니다.",
        "copy": "건강검진, 병원비, 치료 기간처럼 몸과 연결된 이슈에 민감합니다. 이런 유형은 갑자기 큰 비용이 생기는 상황과 치료 중 생활 리듬이 무너지는 상황을 함께 떠올려보면 좋습니다.",
        "chips": ["건강검진", "큰 병원비", "치료 기간"],
    },
    "money": {
        "title": "지갑 방어형",
        "tagline": "큰돈이 한 번에 나가는 상황을 가장 싫어하는 타입입니다.",
        "copy": "평소 소비는 잘 조절하지만, 예상 못 한 병원비나 치과비처럼 한 번에 나가는 비용에는 부담을 크게 느낄 수 있습니다. 이런 유형은 자주 미루는 비용부터 가볍게 체크해보면 좋습니다.",
        "chips": ["치과비", "월 지출", "갑작스러운 비용"],
    },
    "present": {
        "title": "오늘 우선형",
        "tagline": "걱정은 있지만 너무 멀리 있는 일은 잠시 접어두는 타입입니다.",
        "copy": "복잡한 준비보다 지금의 생활감이 더 중요합니다. 이런 유형은 긴 설명보다 간단한 테스트나 계산기로 내 상황을 한 번씩 확인하는 방식이 잘 맞습니다.",
        "chips": ["간단한 점검", "가벼운 시작", "미루기 방지"],
    },
}


SECONDARY_RESULTS = {
    "family": {
        "name": "가족 보호 본능",
        "copy": "결정의 기준에 가족의 생활 안정이 자주 들어옵니다.",
    },
    "health": {
        "name": "건강 경보 센서",
        "copy": "건강 이슈가 생겼을 때의 비용과 시간을 꽤 현실적으로 상상하는 편입니다.",
    },
    "money": {
        "name": "지출 방어 감각",
        "copy": "갑자기 커지는 비용이나 고정비 부담에 민감하게 반응합니다.",
    },
    "present": {
        "name": "가벼운 시작 선호",
        "copy": "너무 먼 미래보다 지금 바로 이해하고 실행할 수 있는 방식이 잘 맞습니다.",
    },
}


def image_data_uri(path):
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_css():
    st.markdown(
        """
        <style>
        .worry-title-row {
            display: flex;
            align-items: center;
            gap: .5rem;
            height: 32px;
            margin-bottom: .8rem;
        }
        .worry-title-row img {
            width: 30px;
            height: 30px;
            object-fit: contain;
            display: block;
        }
        .worry-title {
            color: #15202b;
            font-size: 1.42rem;
            line-height: 32px;
            font-weight: 900;
            letter-spacing: 0;
            white-space: nowrap;
        }
        .worry-subcopy {
            color: #64748b;
            font-size: .88rem;
            line-height: 1.45;
            margin-bottom: .8rem;
        }
        .worry-step-row {
            display: flex;
            flex-wrap: wrap;
            gap: .4rem;
            margin: .45rem 0 .95rem;
        }
        .worry-step-chip {
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            background: #fff;
            color: #64748b;
            font-size: .72rem;
            line-height: 1;
            padding: .26rem .52rem;
        }
        .worry-step-chip.active {
            border-color: #f5b51b;
            background: #fff8e6;
            color: #111827;
            font-weight: 850;
        }
        .worry-step-chip.done {
            background: #f1f5f9;
            color: #334155;
        }
        .worry-question-card {
            border: 1px solid #e7ecf2;
            border-radius: 8px;
            background: #ffffff;
            padding: .95rem 1rem;
            margin-bottom: .85rem;
        }
        .worry-question-number {
            color: #d99a08;
            font-size: .76rem;
            font-weight: 900;
            margin-bottom: .25rem;
        }
        .worry-question-title {
            color: #111827;
            font-size: 1.04rem;
            font-weight: 900;
            line-height: 1.35;
        }
        .worry-result {
            border: 1px solid #e8edf3;
            border-radius: 8px;
            background: #fffdf7;
            padding: 1rem;
            margin-top: .7rem;
        }
        .worry-result-label {
            color: #d99a08;
            font-size: .76rem;
            font-weight: 900;
            margin-bottom: .25rem;
        }
        .worry-result-title {
            color: #111827;
            font-size: 1.45rem;
            font-weight: 950;
            line-height: 1.15;
            margin-bottom: .35rem;
        }
        .worry-result-tagline {
            color: #334155;
            font-size: .95rem;
            font-weight: 800;
            line-height: 1.45;
            margin-bottom: .5rem;
        }
        .worry-result-copy {
            color: #475569;
            font-size: .88rem;
            line-height: 1.6;
        }
        .worry-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: .42rem;
            margin-top: .7rem;
        }
        .worry-chip {
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            background: #fff;
            color: #475569;
            font-size: .74rem;
            padding: .28rem .55rem;
        }
        .worry-direct {
            border: 1px solid #e8edf3;
            border-radius: 8px;
            background: #ffffff;
            padding: .82rem .95rem;
            margin-top: .75rem;
        }
        .worry-direct-title {
            color: #1f2937;
            font-size: .9rem;
            font-weight: 850;
            margin-bottom: .28rem;
        }
        .worry-direct-copy {
            color: #64748b;
            font-size: .78rem;
            line-height: 1.45;
            margin-bottom: .58rem;
        }
        .worry-direct a {
            border: 1px solid #f5b51b;
            border-radius: 999px;
            background: #fff8e6;
            color: #111827;
            display: inline-block;
            font-size: .76rem;
            font-weight: 850;
            line-height: 1;
            padding: .35rem .7rem;
            text-decoration: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    if "future_worry_answers" not in st.session_state:
        st.session_state.future_worry_answers = {}
    if "future_worry_step" not in st.session_state:
        st.session_state.future_worry_step = 0
    if "future_worry_result" not in st.session_state:
        st.session_state.future_worry_result = None


def render_header():
    render_feature_banner("assets/feature_banners/future_worry_test.png", "미래 걱정 유형 테스트")
    render_feature_intro_card(
        "간단한 질문으로 내가 어떤 미래 걱정에 더 민감한지 살펴봅니다. "
        "걱정을 없애기보다 먼저 알아차리고, 필요한 준비를 생각해보는 테스트입니다."
    )


def score_answers(answers):
    scores = {"family": 0, "health": 0, "money": 0, "present": 0}
    for value in answers.values():
        scores[value] += 1
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    primary = ranked[0][0]
    secondary = ranked[1][0] if ranked[1][1] > 0 else primary
    return {
        "primary": primary,
        "secondary": secondary,
        "scores": scores,
    }


def render_step_status():
    current = st.session_state.future_worry_step
    chips = []
    for index in range(len(QUESTIONS)):
        class_name = "active" if current == index else "done" if current > index else ""
        chips.append(f'<span class="worry-step-chip {class_name}">{index + 1}번</span>')
    if current >= len(QUESTIONS):
        chips.append('<span class="worry-step-chip active">결과</span>')
    st.markdown(f'<div class="worry-step-row">{"".join(chips)}</div>', unsafe_allow_html=True)


def render_question_step():
    step = st.session_state.future_worry_step
    question = QUESTIONS[step]
    st.markdown(
        f"""
        <div class="worry-question-card">
            <div class="worry-question-number">{step + 1} / {len(QUESTIONS)}</div>
            <div class="worry-question-title">{question["text"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form(f"future_worry_step_form_{step}"):
        labels = [f"{index + 1}. {option[0]}" for index, option in enumerate(question["options"])]
        label_to_type = {label: option[1] for label, option in zip(labels, question["options"])}
        selected = st.radio("보기", labels, label_visibility="collapsed")
        col1, col2 = st.columns([1, 2])
        with col1:
            back = st.form_submit_button("이전", use_container_width=True, disabled=step == 0)
        with col2:
            is_last = step == len(QUESTIONS) - 1
            next_label = "내 걱정 유형 보기" if is_last else "다음"
            submitted = st.form_submit_button(next_label, use_container_width=True)

    if back:
        st.session_state.future_worry_step = max(step - 1, 0)
        st.rerun()

    if submitted:
        st.session_state.future_worry_answers[step] = label_to_type[selected]
        if step == len(QUESTIONS) - 1:
            progress_text = st.empty()
            progress_bar = st.progress(0)
            for value in range(1, 101):
                progress_text.markdown("나의 미래 걱정 유형을 찾는 중입니다.")
                progress_bar.progress(value)
                time.sleep(0.05)
            progress_text.empty()
            progress_bar.empty()
            st.session_state.future_worry_result = score_answers(st.session_state.future_worry_answers)
            st.session_state.future_worry_step = len(QUESTIONS)
        else:
            st.session_state.future_worry_step = step + 1
        st.rerun()


def render_result_step():
    result_data = st.session_state.future_worry_result
    if not result_data:
        st.session_state.future_worry_step = 0
        st.rerun()

    primary_key = result_data["primary"]
    secondary_key = result_data["secondary"]
    result = RESULTS[primary_key]
    secondary = SECONDARY_RESULTS[secondary_key]
    score_text = " · ".join(
        [
            f"가족 {result_data['scores']['family']}",
            f"건강 {result_data['scores']['health']}",
            f"지출 {result_data['scores']['money']}",
            f"현재 {result_data['scores']['present']}",
        ]
    )
    combo_title = result["title"]
    if primary_key != secondary_key:
        combo_title = f"{result['title']} + {secondary['name']}"

    chips = "".join(f'<span class="worry-chip">{chip}</span>' for chip in result["chips"])
    st.markdown(
        f"""
        <div class="worry-result">
            <div class="worry-result-label">나의 미래 걱정 유형</div>
            <div class="worry-result-title">{combo_title}</div>
            <div class="worry-result-tagline">{result["tagline"]}</div>
            <div class="worry-result-copy">
                {result["copy"]}<br><br>
                보조 성향은 <b>{secondary["name"]}</b>입니다. {secondary["copy"]}<br>
                <span style="color:#8a8f98;font-size:.78rem;">점수: {score_text}</span>
            </div>
            <div class="worry-chip-row">{chips}<span class="worry-chip">{secondary["name"]}</span></div>
        </div>
        <div class="worry-direct">
            <div class="worry-direct-title">결과를 보고 궁금해진 보장이 있다면</div>
            <div class="worry-direct-copy">
                라이나생명 다이렉트에서 암보험, 치아보험 등 주요 보장을 가볍게 확인해볼 수 있습니다.
            </div>
            <a href="https://direct.lina.co.kr/" target="_blank">라이나생명 다이렉트로 이동</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("다시 테스트하기", use_container_width=True):
        st.session_state.future_worry_answers = {}
        st.session_state.future_worry_result = None
        st.session_state.future_worry_step = 0
        st.rerun()


def render():
    render_css()
    init_state()
    render_header()
    render_step_status()
    if st.session_state.future_worry_step < len(QUESTIONS):
        render_question_step()
    else:
        render_result_step()
