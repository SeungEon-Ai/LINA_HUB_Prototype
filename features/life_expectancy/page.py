import base64
import time
from pathlib import Path

import streamlit as st

from .data import get_health_life_years, get_remaining_life_years
from features.shared_header import render_feature_banner, render_feature_intro_card


ROOT = Path(__file__).resolve().parents[2]
LOGO_MARK = ROOT / "assets" / "lina_mark_color.png"


def image_data_uri(path):
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_css():
    st.markdown(
        """
        <style>
        .lifetime-title-row {
            display: flex;
            align-items: center;
            gap: .5rem;
            height: 32px;
            margin-bottom: .8rem;
        }
        .lifetime-title-row img {
            width: 30px;
            height: 30px;
            object-fit: contain;
            display: block;
        }
        .lifetime-title {
            color: #15202b;
            font-size: 1.42rem;
            line-height: 32px;
            font-weight: 900;
            letter-spacing: 0;
            white-space: nowrap;
        }
        .lifetime-subcopy {
            color: #64748b;
            font-size: .88rem;
            line-height: 1.45;
            margin-bottom: 1rem;
        }
        .result-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .7rem;
            margin: .8rem 0 1rem;
        }
        .result-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: .85rem;
            background: #ffffff;
        }
        .result-label {
            color: #64748b;
            font-size: .74rem;
            margin-bottom: .25rem;
        }
        .result-value {
            color: #111827;
            font-size: 1.45rem;
            line-height: 1.1;
            font-weight: 900;
            letter-spacing: 0;
        }
        .result-note {
            color: #64748b;
            font-size: .72rem;
            line-height: 1.4;
            margin-top: .35rem;
        }
        .insight-box {
            border-radius: 8px;
            background: #f8fafc;
            padding: .9rem 1rem;
            margin-top: .75rem;
            color: #1f2937;
            font-size: .9rem;
            line-height: 1.55;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .signal-row {
            display: flex;
            flex-wrap: wrap;
            gap: .45rem;
            margin-top: .65rem;
        }
        .signal-chip {
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            padding: .28rem .55rem;
            color: #475569;
            font-size: .74rem;
            background: #fff;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .source-note {
            color: #8a8f98;
            font-size: .78rem;
            line-height: 1.55;
            margin-top: .55rem;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .direct-cta {
            border: 1px solid #e8edf3;
            border-radius: 8px;
            background: #ffffff;
            padding: .85rem .95rem;
            margin-top: .75rem;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
        }
        .direct-cta-title {
            color: #1f2937;
            font-size: .92rem;
            font-weight: 800;
            line-height: 1.35;
            margin-bottom: .28rem;
        }
        .direct-cta-copy {
            color: #64748b;
            font-size: .78rem;
            line-height: 1.45;
            margin-bottom: .62rem;
        }
        .direct-cta-actions {
            display: flex;
            gap: .45rem;
            flex-wrap: wrap;
        }
        .direct-cta-actions a {
            border: 1px solid #d8dee8;
            border-radius: 999px;
            color: #1f2937;
            background: #fff;
            padding: .34rem .68rem;
            font-size: .76rem;
            line-height: 1;
            text-decoration: none;
        }
        .direct-cta-actions a.primary {
            border-color: #f5b51b;
            background: #fff8e6;
            font-weight: 800;
        }
        .direct-cta-actions a:hover {
            border-color: #f5b51b;
            color: #111827;
        }
        .step-row {
            display: flex;
            gap: .45rem;
            flex-wrap: wrap;
            margin: .5rem 0 1rem;
        }
        .step-chip {
            border-radius: 999px;
            padding: .28rem .62rem;
            font-size: .76rem;
            line-height: 1;
            border: 1px solid #e2e8f0;
            color: #64748b;
            background: #fff;
        }
        .step-chip.active {
            border-color: #f5b51b;
            color: #111827;
            background: #fff8e6;
            font-weight: 800;
        }
        .step-chip.done {
            color: #334155;
            background: #f1f5f9;
        }
        .saved-box {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: .65rem .8rem;
            background: #f8fafc;
            color: #475569;
            font-size: .8rem;
            line-height: 1.45;
            margin-bottom: .8rem;
        }
        @media (max-width: 760px) {
            .result-grid {
                grid-template-columns: 1fr;
            }
            .lifetime-title {
                font-size: 1.25rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def lifestyle_adjustment(inputs):
    adjustment = 0.0
    signals = []

    bmi = inputs["weight"] / ((inputs["height"] / 100) ** 2)
    if 18.5 <= bmi < 25:
        adjustment += 0.4
        signals.append("BMI 안정")
    elif bmi >= 30:
        adjustment -= 1.2
        signals.append("체중 관리 필요")
    elif bmi >= 25:
        adjustment -= 0.6
        signals.append("BMI 주의")
    else:
        adjustment -= 0.5
        signals.append("저체중 주의")

    if inputs["smoking"] == "현재 흡연":
        adjustment -= 2.0
        signals.append("흡연 리스크")
    elif inputs["smoking"] == "과거 흡연":
        adjustment -= 0.6
        signals.append("과거 흡연")
    else:
        adjustment += 0.4
        signals.append("비흡연")

    if inputs["exercise"] == "주 4회 이상":
        adjustment += 1.0
        signals.append("운동 습관 좋음")
    elif inputs["exercise"] == "주 1~3회":
        adjustment += 0.4
        signals.append("운동 보통")
    else:
        adjustment -= 0.8
        signals.append("운동 부족")

    if inputs["sleep"] < 6:
        adjustment -= 0.7
        signals.append("수면 부족")
    elif inputs["sleep"] <= 8:
        adjustment += 0.3
        signals.append("수면 안정")
    else:
        signals.append("수면 확인")

    if inputs["drinking"] == "주 4회 이상":
        adjustment -= 1.0
        signals.append("음주 빈도 높음")
    elif inputs["drinking"] == "거의 안 함":
        adjustment += 0.2
        signals.append("음주 낮음")

    if inputs["chronic"] == "있음":
        adjustment -= 1.4
        signals.append("만성질환 관리")
    if inputs["family_history"] == "있음":
        adjustment -= 0.6
        signals.append("가족력 확인")

    return max(min(adjustment, 3.0), -5.0), signals, bmi


def calculate(inputs):
    base_remaining_years = get_remaining_life_years(inputs["gender"], inputs["age"])
    health_years = get_health_life_years(inputs["gender"], inputs["age"])
    adjustment, signals, bmi = lifestyle_adjustment(inputs)
    estimated_age = max(inputs["age"] + 1, inputs["age"] + base_remaining_years + adjustment)
    remaining_years = max(estimated_age - inputs["age"], 0)

    monthly_gap = max(inputs["monthly_cost"] - inputs["monthly_income_cover"], 0)
    reserve_months = 999 if monthly_gap == 0 else inputs["reserve"] / monthly_gap
    family_need_years = max(inputs["family_years"], 0)
    needed_amount = monthly_gap * 12 * family_need_years
    shortage = max(needed_amount - inputs["reserve"], 0)

    return {
        "base_remaining_years": base_remaining_years,
        "base_target": inputs["age"] + base_remaining_years,
        "estimated_age": estimated_age,
        "remaining_years": remaining_years,
        "disease_free_years": health_years["disease_free_years"],
        "self_rated_healthy_years": health_years["self_rated_healthy_years"],
        "health_reference_age": health_years["nearest_age"],
        "adjustment": adjustment,
        "signals": signals,
        "bmi": bmi,
        "monthly_gap": monthly_gap,
        "reserve_months": reserve_months,
        "needed_amount": needed_amount,
        "shortage": shortage,
    }


def format_money(value):
    if value >= 10000:
        return f"{value / 10000:,.1f}억원"
    return f"{value:,.0f}만원"


def render_header():
    render_feature_banner("assets/feature_banners/life_expectancy.png", "라이프타임 계산기")
    render_feature_intro_card(
        "현재 나이와 생활 습관을 바탕으로 앞으로의 시간을 가볍게 계산해봅니다. "
        "결과는 정답이 아니라 오래 살아갈 시간을 준비해보는 참고용 안내입니다."
    )


def default_inputs():
    return {
        "gender": "남성",
        "age": 40,
        "family_years": 15,
        "height": 170,
        "weight": 68,
        "smoking": "비흡연",
        "drinking": "거의 안 함",
        "exercise": "주 1~3회",
        "sleep": 7.0,
        "chronic": "없음",
        "family_history": "없음",
        "monthly_cost": 350,
        "monthly_income_cover": 80,
        "reserve": 3000,
    }


def init_step_state():
    if "lifetime_step" not in st.session_state:
        st.session_state.lifetime_step = 1
    if "lifetime_inputs" not in st.session_state:
        st.session_state.lifetime_inputs = default_inputs()


def render_step_status():
    step = st.session_state.lifetime_step
    labels = [("기본 정보", 1), ("건강 습관", 2), ("생활보장 공백", 3), ("결과", 4)]
    chips = []
    for label, index in labels:
        class_name = "active" if step == index else "done" if step > index else ""
        chips.append(f'<span class="step-chip {class_name}">{label}</span>')
    st.markdown(f'<div class="step-row">{"".join(chips)}</div>', unsafe_allow_html=True)


def render_saved_summary():
    inputs = st.session_state.lifetime_inputs
    if st.session_state.lifetime_step >= 2:
        st.markdown(
            f"""
            <div class="saved-box">
                기본 정보: {inputs["gender"]}, {inputs["age"]}세, 가족 책임 기간 {inputs["family_years"]}년
            </div>
            """,
            unsafe_allow_html=True,
        )
    if st.session_state.lifetime_step >= 3:
        st.markdown(
            f"""
            <div class="saved-box">
                건강 습관: 키 {inputs["height"]}cm, 몸무게 {inputs["weight"]}kg,
                {inputs["smoking"]}, 운동 {inputs["exercise"]}, 수면 {inputs["sleep"]:.1f}시간
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_basic_form():
    inputs = st.session_state.lifetime_inputs
    with st.form("lifetime_basic_form"):
        st.markdown("#### 기본 정보")
        col1, col2, col3 = st.columns(3)
        with col1:
            gender = st.selectbox("성별", ["남성", "여성"], index=["남성", "여성"].index(inputs["gender"]))
        with col2:
            age = st.number_input("현재 나이", min_value=19, max_value=90, value=int(inputs["age"]), step=1)
        with col3:
            family_years = st.number_input("가족 책임 기간", min_value=0, max_value=40, value=int(inputs["family_years"]), step=1, help="자녀 독립, 배우자 생활비, 대출 상환 등 가족에게 필요한 기간입니다.")

        submitted = st.form_submit_button("다음: 건강 습관 입력", use_container_width=True)
        if submitted:
            st.session_state.lifetime_inputs.update(
                {
                    "gender": gender,
                    "age": age,
                    "family_years": family_years,
                }
            )
            st.session_state.lifetime_step = 2
            st.rerun()


def render_health_form():
    inputs = st.session_state.lifetime_inputs
    with st.form("lifetime_health_form"):
        st.markdown("#### 건강 습관")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            height = st.number_input("키(cm)", min_value=130, max_value=220, value=int(inputs["height"]), step=1)
        with col2:
            weight = st.number_input("몸무게(kg)", min_value=35, max_value=160, value=int(inputs["weight"]), step=1)
        with col3:
            smoking_options = ["비흡연", "과거 흡연", "현재 흡연"]
            smoking = st.selectbox("흡연", smoking_options, index=smoking_options.index(inputs["smoking"]))
        with col4:
            drinking_options = ["거의 안 함", "주 1~3회", "주 4회 이상"]
            drinking = st.selectbox("음주", drinking_options, index=drinking_options.index(inputs["drinking"]))

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            exercise_options = ["거의 안 함", "주 1~3회", "주 4회 이상"]
            exercise = st.selectbox("운동", exercise_options, index=exercise_options.index(inputs["exercise"]))
        with col2:
            sleep = st.number_input("평균 수면", min_value=3.0, max_value=11.0, value=float(inputs["sleep"]), step=0.5)
        with col3:
            chronic_options = ["없음", "있음"]
            chronic = st.selectbox("만성질환", chronic_options, index=chronic_options.index(inputs["chronic"]))
        with col4:
            family_history_options = ["없음", "있음"]
            family_history = st.selectbox("주요 가족력", family_history_options, index=family_history_options.index(inputs["family_history"]))

        col1, col2 = st.columns([1, 2])
        with col1:
            back = st.form_submit_button("이전", use_container_width=True)
        with col2:
            submitted = st.form_submit_button("다음: 생활보장 공백 입력", use_container_width=True)

        if back:
            st.session_state.lifetime_step = 1
            st.rerun()
        if submitted:
            st.session_state.lifetime_inputs.update(
                {
                    "height": height,
                    "weight": weight,
                    "smoking": smoking,
                    "drinking": drinking,
                    "exercise": exercise,
                    "sleep": sleep,
                    "chronic": chronic,
                    "family_history": family_history,
                }
            )
            st.session_state.lifetime_step = 3
            st.rerun()


def render_gap_form():
    inputs = st.session_state.lifetime_inputs
    with st.form("lifetime_gap_form"):
        st.markdown("#### 생활보장 공백")
        col1, col2, col3 = st.columns(3)
        with col1:
            monthly_cost = st.number_input("가족 월 생활비(만원)", min_value=0, max_value=3000, value=int(inputs["monthly_cost"]), step=10)
        with col2:
            monthly_income_cover = st.number_input("이미 확보된 월 소득(만원)", min_value=0, max_value=3000, value=int(inputs["monthly_income_cover"]), step=10, help="연금, 임대소득, 배우자 소득 등 이미 확보된 금액입니다.")
        with col3:
            reserve = st.number_input("비상/보장 준비금(만원)", min_value=0, max_value=100000, value=int(inputs["reserve"]), step=100)

        col1, col2 = st.columns([1, 2])
        with col1:
            back = st.form_submit_button("이전", use_container_width=True)
        with col2:
            submitted = st.form_submit_button("라이프타임 계산하기", use_container_width=True)

        if back:
            st.session_state.lifetime_step = 2
            st.rerun()
        if submitted:
            st.session_state.lifetime_inputs.update(
                {
                    "monthly_cost": monthly_cost,
                    "monthly_income_cover": monthly_income_cover,
                    "reserve": reserve,
                }
            )
            progress_text = st.empty()
            progress_bar = st.progress(0)
            for value in range(1, 101):
                progress_text.markdown("라이프타임 결과를 계산하는 중입니다.")
                progress_bar.progress(value)
                time.sleep(0.07)
            progress_text.empty()
            progress_bar.empty()
            st.session_state.lifetime_result_inputs = dict(st.session_state.lifetime_inputs)
            st.session_state.lifetime_result = calculate(st.session_state.lifetime_result_inputs)
            st.session_state.lifetime_step = 4
            st.rerun()


def render_step_forms():
    render_step_status()
    render_saved_summary()

    if st.session_state.lifetime_step == 1:
        render_basic_form()
    elif st.session_state.lifetime_step == 2:
        render_health_form()
    elif st.session_state.lifetime_step == 3:
        render_gap_form()
    else:
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("다시 계산", use_container_width=True):
                st.session_state.lifetime_step = 1
                st.session_state.lifetime_result = None
                st.rerun()


def render_results(inputs, result):
    reserve_months = "충분" if result["reserve_months"] >= 999 else f"{result['reserve_months']:.1f}개월"
    st.markdown(
        f"""
        <div class="result-grid">
            <div class="result-card">
                <div class="result-label">KOSIS 기준 기대수명</div>
                <div class="result-value">{result["base_target"]:.1f}세</div>
                <div class="result-note">KOSIS 통계청 완전생명표의 성별/현재 나이별 기대여명 기준입니다.</div>
            </div>
            <div class="result-card">
                <div class="result-label">생활습관 반영 예상</div>
                <div class="result-value">{result["estimated_age"]:.1f}세</div>
                <div class="result-note">공식 기대여명에 입력하신 생활습관 보정값을 더한 참고값입니다.</div>
            </div>
            <div class="result-card">
                <div class="result-label">유병기간 제외 기대여명</div>
                <div class="result-value">{result["disease_free_years"]:.1f}년</div>
                <div class="result-note">건강수준별 기대여명 표의 {result["health_reference_age"]}세 기준값입니다.</div>
            </div>
            <div class="result-card">
                <div class="result-label">현재 준비금 지속 기간</div>
                <div class="result-value">{reserve_months}</div>
                <div class="result-note">월 생활비에서 이미 확보된 월 소득을 뺀 금액 기준입니다.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="insight-box">
            현재 입력값 기준 BMI는 <b>{result["bmi"]:.1f}</b>이고, 생활습관 보정은 <b>{result["adjustment"]:+.1f}년</b>입니다.
            KOSIS 완전생명표 기준으로는 앞으로 약 <b>{result["base_remaining_years"]:.1f}년</b>의 기대여명이 있으며,
            건강수준별 기대여명 기준으로는 유병기간을 제외한 기간이 약 <b>{result["disease_free_years"]:.1f}년</b>입니다.
            가족 책임 기간을 {inputs["family_years"]}년으로 보면, 생활비 공백을 줄이기 위해 점검할 필요 금액은
            <b>{format_money(result["needed_amount"])}</b> 수준입니다.
            현재 준비금 반영 후 남는 공백은 <b>{format_money(result["shortage"])}</b>입니다.
            <br><br>
            생명보험은 이 공백 전체를 대신하는 상품이 아니라, 예상보다 이른 소득 단절이 생겼을 때 가족의 생활비와 주거비가 갑자기 끊기지 않도록 보완하는 수단으로 볼 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="direct-cta">
            <div class="direct-cta-title">계산 결과를 보고 필요한 보장을 가볍게 확인해보세요.</div>
            <div class="direct-cta-copy">
                라이나생명 다이렉트에서 암보험, 치아보험 등 주요 보장을 직접 비교해볼 수 있습니다.
            </div>
            <div class="direct-cta-actions">
                <a class="primary" href="https://direct.lina.co.kr/" target="_blank">라이나생명 다이렉트 바로가기</a>
                <a href="https://direct.lina.co.kr/" target="_blank">암보험 확인하기</a>
                <a href="https://direct.lina.co.kr/" target="_blank">치아보험 확인하기</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chips = "".join(f'<span class="signal-chip">{signal}</span>' for signal in result["signals"])
    st.markdown(f'<div class="signal-row">{chips}</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="source-note">
            ※ 출처: KOSIS 통계청 완전생명표, 건강수준별 기대여명에서 가져왔습니다.<br>
            본 계산기는 의학적 진단, 보험 가입 심사, 실제 수명 예측을 의미하지 않습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render():
    render_css()
    render_header()
    init_step_state()
    render_step_forms()

    if st.session_state.get("lifetime_result"):
        render_results(st.session_state.lifetime_result_inputs, st.session_state.lifetime_result)
