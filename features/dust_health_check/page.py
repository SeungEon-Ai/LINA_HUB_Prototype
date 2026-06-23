import requests
import streamlit as st
import streamlit.components.v1 as components

from features.local_secrets import get_secret_value
from features.shared_header import render_feature_banner, render_feature_intro_card


API_URL = (
    "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/"
    "getCtprvnRltmMesureDnsty"
)

REGIONS = [
    "서울",
    "부산",
    "대구",
    "인천",
    "광주",
    "대전",
    "울산",
    "세종",
    "경기",
    "강원",
    "충북",
    "충남",
    "전북",
    "전남",
    "경북",
    "경남",
    "제주",
]

REFRESH_INTERVAL_MS = 5 * 60 * 1000

METRIC_SPECS = [
    ("khaiValue", "통합대기지수", "", True),
    ("pm10Value", "미세먼지 PM10", "㎍/㎥", False),
    ("pm25Value", "초미세먼지 PM2.5", "㎍/㎥", False),
    ("o3Value", "오존 O3", "ppm", False),
    ("no2Value", "이산화질소 NO2", "ppm", False),
    ("coValue", "일산화탄소 CO", "ppm", False),
    ("so2Value", "아황산가스 SO2", "ppm", False),
]

GRADE_SPECS = [
    ("khaiGrade", "통합 등급"),
    ("pm10Grade", "PM10 등급"),
    ("pm10Grade1h", "PM10 등급"),
    ("pm25Grade", "PM2.5 등급"),
    ("pm25Grade1h", "PM2.5 등급"),
    ("o3Grade", "오존 등급"),
    ("no2Grade", "이산화질소 등급"),
    ("coGrade", "일산화탄소 등급"),
    ("so2Grade", "아황산가스 등급"),
]


def _schedule_refresh():
    components.html(
        f"""
        <script>
        window.setTimeout(function () {{
            window.parent.location.reload();
        }}, {REFRESH_INTERVAL_MS});
        </script>
        """,
        height=0,
    )


def _safe_number(value):
    text = str(value).strip()
    if not text or text in {"-", "통신장애", "점검중"}:
        return None
    try:
        number = float(text)
        if number.is_integer():
            return int(number)
        return number
    except Exception:
        return None


def _format_number(value):
    if value is None:
        return ""
    if isinstance(value, int):
        return f"{value:,}"
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _grade_label(value):
    mapping = {
        "1": "좋음",
        "2": "보통",
        "3": "나쁨",
        "4": "매우 나쁨",
    }
    return mapping.get(str(value).strip())


def _sanitize_error_message(error):
    message = str(error)
    for token in ["serviceKey=", "AIRKOREA_SERVICE_KEY=", "PUBLIC_DATA_SERVICE_KEY="]:
        if token not in message:
            continue
        head, tail = message.split(token, 1)
        masked_tail = tail
        for sep in ["&", " ", '"', "'"]:
            if sep in tail:
                _, rest = tail.split(sep, 1)
                masked_tail = "****" + sep + rest
                break
        else:
            masked_tail = "****"
        message = head + token + masked_tail
    return message


def _grade_text(grade_value):
    mapping = {
        "1": ("좋음", "#16a34a"),
        "2": ("보통", "#f59e0b"),
        "3": ("나쁨", "#f97316"),
        "4": ("매우 나쁨", "#dc2626"),
    }
    return mapping.get(str(grade_value).strip(), ("확인 필요", "#64748b"))


def _message_for_grade(grade_label):
    messages = {
        "좋음": "오늘 공기는 비교적 편안한 편이에요. 가볍게 외출하거나 걷기 좋은 흐름입니다.",
        "보통": "오늘 공기는 무난한 편이지만 오래 야외에 있으면 목이나 코가 먼저 반응할 수도 있어요.",
        "나쁨": "오늘은 공기가 조금 거슬릴 수 있어요. 오래 걷기보다는 이동 시간을 줄이고 실내 휴식을 섞는 편이 좋습니다.",
        "매우 나쁨": "오늘은 공기 자체가 꽤 무거운 날이에요. 장시간 야외 활동보다는 실내 위주로 움직이는 편이 몸이 덜 피곤합니다.",
    }
    return messages.get(
        grade_label,
        "지금 공기 흐름을 기준으로 몸이 먼저 반응할 만한지 가볍게 확인해보는 용도로 봐주세요.",
    )


def _parse_items(payload):
    body = payload.get("response", {}).get("body", {})
    return body.get("items", []) or []


def _request_air_data(params, service_key):
    response = requests.get(API_URL, params={**params, "serviceKey": service_key}, timeout=20)
    response.raise_for_status()
    payload = response.json()
    items = _parse_items(payload)
    if items:
        return payload

    if "%" not in service_key:
        return payload

    query = "&".join(f"{key}={value}" for key, value in params.items())
    response = requests.get(f"{API_URL}?serviceKey={service_key}&{query}", timeout=20)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_air_quality(region, service_key):
    params = {
        "returnType": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "sidoName": region,
        "ver": "1.0",
    }
    payload = _request_air_data(params, service_key)
    items = _parse_items(payload)
    valid_items = [
        item
        for item in items
        if any(_safe_number(item.get(field)) is not None for field, *_ in METRIC_SPECS)
    ]
    if not valid_items:
        raise ValueError("현재 표시할 수 있는 대기 측정값이 없습니다.")

    ranked_items = sorted(
        valid_items,
        key=lambda item: (
            sum(_safe_number(item.get(field)) is not None for field, *_ in METRIC_SPECS),
            _safe_number(item.get("khaiValue")) or -1,
            _safe_number(item.get("pm25Value")) or -1,
            _safe_number(item.get("pm10Value")) or -1,
        ),
        reverse=True,
    )
    return ranked_items[0]


def _render_metric_card(label, value, unit, accent=False):
    card_class = "dust-metric-card accent" if accent else "dust-metric-card"
    return f"""
        <div class="{card_class}">
            <div class="dust-metric-label">{label}</div>
            <div class="dust-metric-value">{_format_number(value)}{unit}</div>
        </div>
    """


def _render_metric_grid(metrics):
    if not metrics:
        return

    hero_label, hero_value, hero_unit, hero_accent = metrics[0]
    sub_metrics = metrics[1:]
    st.markdown(
        f'<div class="dust-metric-wrap">{_render_metric_card(hero_label, hero_value, hero_unit, accent=hero_accent)}</div>',
        unsafe_allow_html=True,
    )

    rows = [sub_metrics[i : i + 3] for i in range(0, len(sub_metrics), 3)]
    for row_index, row in enumerate(rows):
        columns = st.columns(3, gap="small")
        for col_index, column in enumerate(columns):
            with column:
                if col_index < len(row):
                    label, value, unit, accent = row[col_index]
                    st.markdown(
                        _render_metric_card(label, value, unit, accent=accent),
                        unsafe_allow_html=True,
                    )
        if row_index < len(rows) - 1:
            st.markdown('<div class="dust-metric-row-gap"></div>', unsafe_allow_html=True)


def _aqi_band(value):
    number = _safe_number(value)
    if number is None:
        return None
    if number <= 50:
        return "good"
    if number <= 100:
        return "normal"
    if number <= 250:
        return "bad"
    return "very_bad"


def _render_aqi_guide(value):
    number = _safe_number(value)
    active_band = _aqi_band(number)
    current = _format_number(number) if number is not None else "-"
    bands = [
        ("good", "좋음", "0-50"),
        ("normal", "보통", "51-100"),
        ("bad", "나쁨", "101-250"),
        ("very_bad", "매우 나쁨", "251+"),
    ]
    band_html = "".join(
        f"""
        <div class="dust-aqi-band{' active' if key == active_band else ''}">
            <div class="dust-aqi-band-range">{range_text}</div>
            <div class="dust-aqi-band-name">{label}</div>
        </div>
        """
        for key, label, range_text in bands
    )
    st.markdown(
        f"""
        <div class="dust-aqi-guide">
            <div class="dust-aqi-guide-head">
                <div>
                    <div class="dust-aqi-kicker">통합대기지수 한눈에 보기</div>
                    <div class="dust-aqi-title">숫자가 높을수록 공기 부담이 커져요.</div>
                </div>
                <div class="dust-aqi-now">현재 {current}</div>
            </div>
            <div class="dust-aqi-scale">{band_html}</div>
            <div class="dust-aqi-note">
                미세먼지, 초미세먼지, 오존, 이산화질소, 일산화탄소, 아황산가스를 한 번에 묶어 본 지표입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_grade_chips(data):
    chips = []
    seen_labels = set()
    for field, label in GRADE_SPECS:
        if label in seen_labels:
            continue
        grade = _grade_label(data.get(field))
        if grade:
            chips.append(f'<span class="dust-grade-pill">{label} {grade}</span>')
            seen_labels.add(label)

    if not chips:
        return

    st.markdown(
        f'<div class="dust-grade-pill-row">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def _render_insurance_bridge():
    st.markdown(
        """
        <div class="dust-insurance-bridge">
            <div class="dust-bridge-title">공기질이 자주 신경 쓰인다면</div>
            <div class="dust-bridge-copy">
                미세먼지와 초미세먼지가 높은 날이 반복되면 목·코 같은 호흡기 불편뿐 아니라
                심혈관 부담도 함께 커질 수 있습니다. 오늘 수치 하나로 질병을 예측할 수는 없지만,
                이런 날이 자주 반복된다면 호흡기 질환, 심뇌혈관 질환, 질병 입원·간병 공백처럼
                건강보험에서 자주 확인하는 보장 흐름도 함께 점검해볼 수 있습니다.
            </div>
            <div class="dust-bridge-pills">
                <span>호흡기 부담</span>
                <span>심뇌혈관 부담</span>
                <span>질병 입원</span>
                <span>간병 공백</span>
                <span>수술비 점검</span>
            </div>
            <div class="dust-bridge-note">
                라이나생명 일반보험에는 상품별로 질병 입원, 간병, 수술, 심뇌혈관 관련 특약이 있을 수 있습니다.
                다만 실제 보장 여부와 조건은 상품별 약관 기준으로 확인하는 것이 가장 정확합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("라이나 약관 AI에서 관련 보장 물어보기", key="dust_policy_bridge"):
        st.query_params["feature"] = "policy_graph_rag"
        st.session_state["active_feature"] = "라이나 약관 AI"
        st.rerun()


def _render_styles():
    st.markdown(
        """
        <style>
        .dust-region-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .8rem;
            margin: .35rem 0 1.05rem;
        }
        .dust-updated {
            color: #64748b;
            font-size: .85rem;
            text-align: right;
            line-height: 1.55;
        }
        .dust-grade-card {
            border: 1px solid #e2e8f0;
            border-radius: 22px;
            padding: .95rem 1.1rem;
            margin: .25rem 0 .42rem;
            background: linear-gradient(180deg, #fffdf7 0%, #ffffff 100%);
        }
        .dust-grade-chip {
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: .24rem .7rem;
            border-radius: 999px;
            font-size: .82rem;
            font-weight: 800;
            color: #fff;
            margin-bottom: .72rem;
        }
        .dust-grade-copy {
            color: #1f2937;
            font-size: .98rem;
            line-height: 1.58;
            margin: 0;
        }
        .dust-metric-wrap {
            margin: .2rem 0 1rem;
        }
        .dust-metric-row-gap {
            height: .52rem;
        }
        .dust-metric-card {
            border: 1px solid #dbe3ef;
            border-radius: 999px;
            background: #f8fafc;
            padding: .95rem 2.6rem;
            text-align: center;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            width: 100%;
            box-sizing: border-box;
        }
        .dust-metric-card.accent {
            background: #fff8e8;
            border-color: #f5b51b;
            min-height: 96px;
            padding-top: .7rem;
            padding-bottom: .7rem;
            margin-bottom: 0;
        }
        .dust-metric-label {
            color: #64748b;
            font-size: .82rem;
            margin-bottom: .32rem;
        }
        .dust-metric-value {
            color: #111827;
            font-size: 1.04rem;
            font-weight: 900;
            line-height: 1.2;
            word-break: keep-all;
        }
        .dust-grade-pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: .46rem;
            margin: .95rem 0 1rem;
        }
        .dust-grade-pill {
            display: inline-flex;
            align-items: center;
            min-height: 30px;
            padding: .22rem .72rem;
            border-radius: 999px;
            border: 1px solid #dbe3ef;
            background: #fff;
            color: #475569;
            font-size: .8rem;
            font-weight: 700;
        }
        .dust-insurance-bridge {
            border: 1px solid #f3d58a;
            border-radius: 18px;
            background: #fffaf0;
            padding: 1rem 1.1rem;
            margin: 1.05rem 0 1rem;
            color: #1f2937;
        }
        .dust-bridge-title {
            font-size: 1rem;
            font-weight: 900;
            margin-bottom: .45rem;
        }
        .dust-bridge-copy {
            color: #475569;
            font-size: .9rem;
            line-height: 1.7;
        }
        .dust-bridge-pills {
            display: flex;
            flex-wrap: wrap;
            gap: .42rem;
            margin-top: .75rem;
        }
        .dust-bridge-pills span {
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: .18rem .66rem;
            border: 1px solid #f2c24b;
            border-radius: 999px;
            background: #fff;
            color: #334155;
            font-size: .78rem;
            font-weight: 800;
        }
        .dust-bridge-note {
            margin-top: .72rem;
            color: #64748b;
            font-size: .82rem;
            line-height: 1.65;
        }
        .dust-aqi-guide {
            border: 1px solid #e2e8f0;
            border-radius: 22px;
            background: #ffffff;
            padding: .95rem 1rem;
            margin: .72rem 0 .95rem;
        }
        .dust-aqi-guide-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .9rem;
        }
        .dust-aqi-kicker {
            color: #64748b;
            font-size: .82rem;
            font-weight: 800;
            line-height: 1.2;
        }
        .dust-aqi-title {
            color: #111827;
            font-size: 1rem;
            font-weight: 900;
            line-height: 1.35;
            margin-top: .2rem;
        }
        .dust-aqi-now {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            min-height: 32px;
            padding: .25rem .78rem;
            border: 1px solid #f5b51b;
            border-radius: 999px;
            background: #fff8e8;
            color: #111827;
            font-size: .86rem;
            font-weight: 900;
        }
        .dust-aqi-scale {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: .45rem;
            margin-top: .78rem;
        }
        .dust-aqi-band {
            border: 1px solid #dbe3ef;
            border-radius: 999px;
            background: #f8fafc;
            padding: .38rem .55rem;
            text-align: center;
        }
        .dust-aqi-band.active {
            border-color: #f5b51b;
            background: #fff8e8;
            box-shadow: inset 0 0 0 1px #f5b51b;
        }
        .dust-aqi-band-range {
            color: #64748b;
            font-size: .72rem;
            line-height: 1.1;
        }
        .dust-aqi-band-name {
            color: #111827;
            font-size: .84rem;
            font-weight: 900;
            line-height: 1.2;
            margin-top: .14rem;
        }
        .dust-aqi-note {
            color: #64748b;
            font-size: .82rem;
            line-height: 1.55;
            margin-top: .7rem;
        }
        .dust-notice {
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 1.05rem 1.1rem;
            background: #ffffff;
            color: #475569;
            font-size: .92rem;
            line-height: 1.75;
            margin-top: 1rem;
        }
        @media (max-width: 900px) {
            .dust-region-row {
                display: block;
            }
            .dust-updated {
                margin-top: .4rem;
                text-align: left;
            }
        }
        @media (max-width: 640px) {
            .dust-metric-card,
            .dust-metric-card.accent {
                min-height: 102px;
                padding: .9rem 1.4rem;
            }
            .dust-aqi-guide-head {
                align-items: flex-start;
                flex-direction: column;
            }
            .dust-aqi-scale {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render():
    _render_styles()
    render_feature_banner("assets/feature_banners/dust_health_check.png", "오늘의 직관! 미세먼지는?")
    render_feature_intro_card(
        "지역을 선택하면 오늘의 미세먼지, 초미세먼지, 오존 등 공기 상태를 한눈에 보여드립니다. "
        "외출, 환기, 산책처럼 오늘의 작은 선택을 할 때 참고해보세요."
    )

    service_key = get_secret_value(
        "AIRKOREA_SERVICE_KEY",
        "DATA_GO_KR_SERVICE_KEY",
        "PUBLIC_DATA_SERVICE_KEY",
    )

    region = st.selectbox("지역 선택", REGIONS, index=0, key="dust_region")

    if not service_key:
        st.markdown(
            """
            <div class="feature-intro-card">
                <b>미세먼지 정보를 불러올 수 없습니다.</b><br>
                잠시 후 다시 확인해 주세요.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    with st.spinner("최신 미세먼지 데이터를 불러오고 있어요."):
        try:
            data = fetch_air_quality(region, service_key)
        except Exception as exc:
            st.error(
                "미세먼지 데이터를 불러오지 못했습니다. "
                "잠시 후 다시 시도해 주세요."
            )
            return

    station_name = str(data.get("stationName", "") or "-")
    data_time = str(data.get("dataTime", "") or "-")
    grade_label, grade_color = _grade_text(
        data.get("khaiGrade") or data.get("pm25Grade1h") or data.get("pm10Grade1h")
    )

    st.markdown(
        f"""
        <div class="dust-region-row">
            <div><b>{region}</b> · {station_name}</div>
            <div class="dust-updated">측정소 측정 시간: {data_time}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="dust-grade-card">
            <div class="dust-grade-chip" style="background:{grade_color};">{grade_label}</div>
            <p class="dust-grade-copy">{_message_for_grade(grade_label)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    visible_metrics = []
    for field, label, unit, accent in METRIC_SPECS:
        value = _safe_number(data.get(field))
        if value is None:
            continue
        visible_metrics.append((label, value, unit, accent))

    if visible_metrics:
        _render_metric_grid(visible_metrics)

    _render_aqi_guide(data.get("khaiValue"))

    _render_grade_chips(data)
    _render_insurance_bridge()

    st.markdown(
        """
        <div class="dust-notice">
            한국환경공단 실시간 대기정보를 기준으로 가까운 측정소의 대기 측정값을 불러옵니다.<br>
            목이 칼칼하거나 눈이 따갑게 느껴지는 날에는 실내 환기 시간과 야외 체류 시간을 조금 조절해보는 편이 좋습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
