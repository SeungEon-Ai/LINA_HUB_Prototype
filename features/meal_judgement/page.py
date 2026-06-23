import json
import time
from html import escape

import requests
import streamlit as st
import streamlit.components.v1 as components

from features.local_secrets import get_openai_api_key
from features.shared_header import render_feature_banner, render_feature_intro_card
from .data import LOCAL_NUTRITION_DB, lookup_local_nutrition, normalize_to_meal_portion

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


SERVER_URL = "https://kfood-server.onrender.com"


def is_openai_api_key(value):
    return str(value or "").strip().startswith("sk-")


def render_css():
    st.markdown(
        """
        <style>
        .meal-card {
            border: 1px solid #e7ecf2;
            border-radius: 8px;
            background: #ffffff;
            padding: .9rem 1rem;
            margin: .75rem 0;
        }
        .meal-card-title {
            color: #111827;
            font-size: .96rem;
            font-weight: 900;
            line-height: 1.35;
            margin-bottom: .35rem;
        }
        .meal-card-copy {
            color: #64748b;
            font-size: .8rem;
            line-height: 1.5;
        }
        .meal-metric {
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            background: #f8fafc;
            padding: .56rem .82rem;
            min-height: 66px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        .meal-metric-feature {
            border-color: #f5b51b;
            background: #fff8e6;
            min-height: 76px;
        }
        .meal-metric-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .72rem .82rem;
            margin: .95rem 0 1.15rem;
        }
        .meal-metric-label {
            color: #64748b;
            font-size: .68rem;
            margin-bottom: .12rem;
            text-align: center;
        }
        .meal-metric-value {
            color: #111827;
            font-size: 1.02rem;
            font-weight: 900;
            line-height: 1.1;
            text-align: center;
        }
        .meal-metric-feature .meal-metric-value {
            font-size: 1.22rem;
        }
        @media (max-width: 540px) {
            .meal-metric-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        .meal-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: .42rem;
            margin-top: .65rem;
        }
        .meal-chip {
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            background: #fff;
            color: #475569;
            font-size: .74rem;
            padding: .28rem .55rem;
        }
        .meal-direct {
            border: 1px solid #e8edf3;
            border-radius: 8px;
            background: #fffdf7;
            padding: .85rem .95rem;
            margin-top: .75rem;
        }
        .meal-direct-title {
            color: #1f2937;
            font-size: .9rem;
            font-weight: 850;
            margin-bottom: .28rem;
        }
        .meal-direct-copy {
            color: #64748b;
            font-size: .78rem;
            line-height: 1.45;
            margin-bottom: .58rem;
        }
        .meal-direct a {
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
        .meal-ai-card {
            border: 1px solid #e8edf3;
            border-radius: 8px;
            background: #fff;
            padding: .9rem 1rem;
            margin: .9rem 0 .75rem;
        }
        .meal-ai-title {
            color: #111827;
            font-size: .92rem;
            font-weight: 900;
            margin-bottom: .35rem;
        }
        .meal-ai-copy {
            color: #475569;
            font-size: .8rem;
            line-height: 1.58;
            white-space: pre-line;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    defaults = {
        "meal_step": "upload",
        "meal_predictions": [],
        "meal_nutrition": None,
        "meal_food_name": "",
        "meal_error": "",
        "meal_show_result": False,
        "meal_ai_explanations": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_meal_flow():
    st.session_state.meal_step = "upload"
    st.session_state.meal_predictions = []
    st.session_state.meal_nutrition = None
    st.session_state.meal_food_name = ""
    st.session_state.meal_error = ""
    st.session_state.meal_show_result = False


def friendly_error(error):
    text = str(error)
    if "Read timed out" in text or "timed out" in text:
        return "분석 시간이 오래 걸리고 있어요. 잠시 후 다시 시도해주세요."
    if "NameResolutionError" in text or "Connection" in text:
        return "음식 분석 서버 연결이 불안정해요. 네트워크 상태를 확인한 뒤 다시 시도해주세요."
    return "사진 분석 중 문제가 발생했어요. 잠시 후 다시 시도해주세요."

def predict_food(uploaded_file):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "image/jpeg")}
    response = requests.post(f"{SERVER_URL}/predict", files=files, timeout=90)
    response.raise_for_status()
    data = response.json()
    return list(data.get("predictions", []))


def fetch_nutrition(food_name):
    local_result = lookup_local_nutrition(food_name)
    if local_result:
        return local_result

    response = requests.get(f"{SERVER_URL}/nutrition/{food_name}", timeout=60)
    response.raise_for_status()
    data = response.json()
    data.setdefault("name_ko", food_name)
    return normalize_to_meal_portion(data)


def nutrition_value(data, *names):
    candidates = [data]
    for container_name in ("nutrition", "nutrients", "data"):
        nested = data.get(container_name)
        if isinstance(nested, dict):
            candidates.append(nested)

    for name in names:
        for candidate in candidates:
            value = candidate.get(name)
            if value not in (None, ""):
                return value
    return "-"


def parse_number(value):
    try:
        return float(str(value).replace(",", "").split()[0])
    except Exception:
        return None


def judge_meal(nutrition):
    calories = parse_number(nutrition_value(nutrition, "calories", "kcal"))
    sodium = nutrition_value(nutrition, "sodium")
    protein = nutrition_value(nutrition, "protein")

    chips = ["한 끼 기록", "식습관 체크"]
    comment = "오늘 한 끼를 가볍게 기록해두면 식습관 패턴을 보기 쉬워집니다."

    if calories is not None:
        if calories >= 800:
            comment = "든든한 한 끼입니다. 이런 식사가 자주 반복된다면 활동량과 균형을 함께 맞춰보면 좋습니다."
            chips.append("든든한 한 끼")
        elif calories <= 350:
            comment = "가벼운 한 끼입니다. 다음 식사에서 단백질과 포만감을 조금 더 챙겨도 좋습니다."
            chips.append("가벼운 한 끼")
        else:
            comment = "부담이 크지 않은 한 끼입니다. 자주 먹는 음식이라면 영양 균형을 함께 확인해보세요."
            chips.append("보통 한 끼")

    if sodium != "-":
        chips.append("나트륨 확인")
    if protein != "-":
        chips.append("단백질 확인")

    return comment, chips

def food_health_message(nutrition):
    sodium = parse_number(nutrition_value(nutrition, "sodium"))
    sugar = parse_number(nutrition_value(nutrition, "sugar", "sugars"))
    fat = parse_number(nutrition_value(nutrition, "fat", "total_fat"))
    calories = parse_number(nutrition_value(nutrition, "calories", "kcal"))

    if sodium is not None and sodium >= 1000:
        return {
            "title": "짠 음식이 자주 반복된다면",
            "copy": "나트륨이 높은 식사는 혈압과 심혈관 건강에 부담을 줄 수 있고, 짠 식습관이 오래 반복되면 위 건강 리스크와도 연관될 수 있어요. 오늘 한 끼가 바로 문제가 된다는 뜻은 아니지만, 반복되는 식습관은 한 번쯤 점검해보면 좋습니다.",
            "link": "암·건강 보장 가볍게 보기",
            "show_direct": True,
        }
    if sugar is not None and sugar >= 20:
        return {
            "title": "단 음식이 자주 반복된다면",
            "copy": "당류가 높은 식사나 간식은 치아 건강과 혈당 관리에 영향을 줄 수 있어요. 특히 달달한 간식이나 음료가 잦다면 치아 관리 루틴도 같이 챙기면 좋습니다.",
            "link": "치아 관련 보장 가볍게 보기",
            "show_direct": True,
        }
    if fat is not None and fat >= 30:
        return {
            "title": "기름진 음식이 자주 반복된다면",
            "copy": "지방이 높은 식사는 체중 관리와 건강 수치에 부담을 줄 수 있어요. 한 번 먹는 한 끼보다 반복되는 식습관을 보는 것이 더 중요합니다.",
            "link": "",
            "show_direct": False,
        }
    if calories is not None and calories >= 800:
        return {
            "title": "고칼로리 한 끼가 자주 반복된다면",
            "copy": "칼로리가 높은 식사는 활동량과 균형이 중요해요. 먹는 즐거움은 살리되, 건강검진 수치와 몸의 변화를 한 번씩 확인하는 습관이 도움이 됩니다.",
            "link": "",
            "show_direct": False,
        }
    return {"title": "", "copy": "", "link": "", "show_direct": False}


def nutrient_band(value, high, medium, label_high="높은 편", label_medium="보통", label_low="낮은 편"):
    number = parse_number(value)
    if number is None:
        return "정보 없음"
    if number >= high:
        return label_high
    if number >= medium:
        return label_medium
    return label_low


def food_style_hint(food_name):
    name = str(food_name or "")
    if any(word in name for word in ("찌개", "국", "탕", "전골", "라면", "냉면", "국밥")):
        return "국물이나 장류 양념이 들어가는 음식은 나트륨이 높아지기 쉬워서 국물 섭취량이 전체 부담을 크게 바꿀 수 있습니다."
    if any(word in name for word in ("볶음", "제육", "불고기", "닭갈비", "주물럭")):
        return "볶음류는 양념장과 조리 과정에서 나트륨, 당류, 지방이 함께 올라갈 수 있어 함께 먹는 반찬과 양 조절이 중요합니다."
    if any(word in name for word in ("치킨", "튀김", "돈까스", "까스", "감자튀김")):
        return "튀김류는 조리유와 튀김옷 때문에 지방과 칼로리가 높아지기 쉬워 자주 반복될 때 부담이 커질 수 있습니다."
    if any(word in name for word in ("피자", "햄버거", "버거", "핫도그", "샌드위치")):
        return "치즈, 소스, 가공육이 들어가는 음식은 나트륨과 지방이 함께 높아질 수 있어 한 끼 전체 균형을 같이 보는 편이 좋습니다."
    if any(word in name for word in ("케이크", "빵", "도넛", "쿠키", "초콜릿", "아이스크림", "떡")):
        return "디저트류는 당류와 지방 비중이 높아질 수 있어 치아 건강과 혈당 관리 측면에서 섭취 빈도를 함께 보는 것이 좋습니다."
    if any(word in name for word in ("커피", "라떼", "주스", "음료", "에이드", "스무디")):
        return "음료류는 포만감은 낮지만 당류가 빠르게 늘 수 있어 달게 마시는 빈도를 확인하는 것이 좋습니다."
    return "이 음식은 한 가지 성분만 보기보다 칼로리, 나트륨, 당류, 단백질의 균형을 함께 보는 편이 좋습니다."


def fallback_nutrition_explanation(food_name, nutrition):
    serving = nutrition_value(nutrition, "display_serving", "serving")
    calories = nutrition_value(nutrition, "calories", "kcal")
    carbs = nutrition_value(nutrition, "carbohydrate", "carbohydrates", "carbs")
    protein = nutrition_value(nutrition, "protein")
    fat = nutrition_value(nutrition, "fat", "total_fat")
    sodium = nutrition_value(nutrition, "sodium")
    sugar = nutrition_value(nutrition, "sugar", "sugars")
    fiber = nutrition_value(nutrition, "dietary_fiber", "fiber")

    sodium_band = nutrient_band(sodium, 1500, 700)
    sugar_band = nutrient_band(sugar, 25, 10)
    fat_band = nutrient_band(fat, 25, 12)
    protein_band = nutrient_band(protein, 25, 12, "충분한 편", "보통", "적은 편")

    parts = [
        f"{food_name}은(는) {display_value(serving)} 기준으로 칼로리 {display_value(calories, 'kcal')}, 탄수화물 {display_value(carbs, 'g')}, 단백질 {display_value(protein, 'g')}, 지방 {display_value(fat, 'g')} 수준입니다.",
        f"나트륨은 {display_value(sodium, 'mg')}로 {sodium_band}이고, 당류는 {display_value(sugar, 'g')}로 {sugar_band}, 식이섬유는 {display_value(fiber, 'g')}입니다.",
        f"단백질은 {protein_band}, 지방은 {fat_band}으로 볼 수 있습니다. {food_style_hint(food_name)}",
        "오늘 한 끼만으로 건강 상태를 판단할 수는 없지만, 비슷한 식사가 자주 반복된다면 나트륨, 당류, 지방 중 어느 항목이 반복적으로 높은지 확인해보는 것이 좋습니다.",
    ]
    return "\n".join(parts)


def build_nutrition_payload(food_name, nutrition):
    keys = {
        "기준량": nutrition_value(nutrition, "display_serving", "serving"),
        "칼로리": display_value(nutrition_value(nutrition, "calories", "kcal"), "kcal"),
        "탄수화물": display_value(nutrition_value(nutrition, "carbohydrate", "carbohydrates", "carbs"), "g"),
        "단백질": display_value(nutrition_value(nutrition, "protein"), "g"),
        "지방": display_value(nutrition_value(nutrition, "fat", "total_fat"), "g"),
        "나트륨": display_value(nutrition_value(nutrition, "sodium"), "mg"),
        "당류": display_value(nutrition_value(nutrition, "sugar", "sugars"), "g"),
        "식이섬유": display_value(nutrition_value(nutrition, "dietary_fiber", "fiber"), "g"),
        "성격": food_style_hint(food_name),
    }
    return "\n".join(f"- {key}: {value}" for key, value in keys.items())


def generate_nutrition_explanation(food_name, nutrition):
    fallback = fallback_nutrition_explanation(food_name, nutrition)
    api_key = get_openai_api_key()
    if not is_openai_api_key(api_key) or OpenAI is None:
        return fallback

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 음식 영양정보를 사용자가 이해하기 쉽게 설명하는 한국어 AI입니다. "
                        "모든 문장은 존댓말로 작성합니다. 의학적 진단처럼 단정하지 않습니다. "
                        "숫자만 나열하지 말고 이 음식이 왜 나트륨, 당류, 지방, 단백질 측면에서 어떤 편인지 구체적으로 설명합니다. "
                        "보험 가입을 노골적으로 권유하지 않고, 반복되는 식습관이 건강 점검과 연결될 수 있다는 정도로만 자연스럽게 말합니다. "
                        "마크다운 굵게 표시용 별표(**)는 절대 쓰지 않습니다."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"음식명: {food_name}\n\n"
                        f"영양정보:\n{build_nutrition_payload(food_name, nutrition)}\n\n"
                        "아래 내용을 4~6문장으로 설명해 주세요.\n"
                        "1. 이 음식의 주요 성분 특징\n"
                        "2. 나트륨, 당류, 지방, 단백질 중 특히 볼 항목\n"
                        "3. 이런 성분이 왜 높거나 낮게 나올 수 있는지\n"
                        "4. 자주 먹는다면 어떤 식습관을 점검하면 좋은지\n"
                        "5. 과장 없이 건강 리스크와 연결되는 점"
                    ),
                },
            ],
            temperature=0.35,
            max_tokens=850,
        )
        text = response.choices[0].message.content or ""
        text = text.replace("**", "").strip()
        return text or fallback
    except Exception:
        return fallback


def get_cached_nutrition_explanation(food_name, nutrition):
    cache = st.session_state.get("meal_ai_explanations", {})
    cache_key = make_nutrition_explanation_cache_key(food_name, nutrition)
    if cache_key not in cache:
        cache[cache_key] = generate_nutrition_explanation(food_name, nutrition)
        st.session_state.meal_ai_explanations = cache
    return cache[cache_key]


def make_nutrition_explanation_cache_key(food_name, nutrition):
    api_key = get_openai_api_key()
    api_mode = "gpt" if is_openai_api_key(api_key) and OpenAI is not None else "fallback"
    return "|".join(
        [
            api_mode,
            str(food_name),
            str(nutrition_value(nutrition, "display_serving", "serving")),
            str(nutrition_value(nutrition, "calories", "kcal")),
            str(nutrition_value(nutrition, "sodium")),
            str(nutrition_value(nutrition, "sugar", "sugars")),
        ]
    )


def render_nutrition_explanation(food_name, nutrition):
    explanation = get_cached_nutrition_explanation(food_name, nutrition)
    with st.container(border=True):
        st.markdown("#### 성분 분석")
        st.markdown(explanation)

def render_upload():
    st.markdown(
        """
        <div class="meal-card">
            <div class="meal-card-title">음식 사진을 올리면 어떤 음식인지 판정해드릴게요.</div>
            <div class="meal-card-copy">음식을 분석하는데 시간이 걸릴 수 있어요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    upload_tab, camera_tab = st.tabs(["사진 업로드", "카메라로 바로 찍기"])
    with upload_tab:
        uploaded_file = st.file_uploader("음식 사진 업로드", type=["jpg", "jpeg", "png", "webp"])
    with camera_tab:
        camera_file = st.camera_input("휴대폰 카메라로 음식 사진 찍기")

    image_file = camera_file or uploaded_file
    if image_file:
        st.image(image_file, width=260)
        if st.button("오늘 한 끼 판정하기", use_container_width=True):
            st.session_state.meal_error = ""
            progress_text = st.empty()
            progress_bar = st.progress(0)
            try:
                for value in range(1, 71):
                    progress_text.markdown("음식을 분석중이에요. 최대 1분 정도 소요될 수 있어요.")
                    progress_bar.progress(value)
                    time.sleep(0.1)
                predictions = predict_food(image_file)
                for value in range(71, 101):
                    progress_text.markdown("판정 결과를 정리하는 중입니다.")
                    progress_bar.progress(value)
                    time.sleep(0.02)
                st.session_state.meal_predictions = predictions
                st.session_state.meal_food_name = ""
                st.session_state.meal_nutrition = None
                st.session_state.meal_show_result = False
                st.session_state.meal_step = "select"
            except Exception as error:
                st.session_state.meal_error = friendly_error(error)
            finally:
                progress_text.empty()
                progress_bar.empty()
            st.rerun()

def render_predictions():
    predictions = st.session_state.meal_predictions
    if not predictions:
        reset_meal_flow()
        st.rerun()

    st.markdown("### 음식 후보")
    labels = []
    food_by_label = {}
    for index, item in enumerate(predictions[:5]):
        food = str(item.get("food", "알 수 없는 음식"))
        confidence = item.get("confidence")
        label = f"{index + 1}. {food}"
        if isinstance(confidence, (int, float)):
            label = f"{label} ({confidence * 100:.1f}%)"
        labels.append(label)
        food_by_label[label] = food

    selected = st.radio("가장 비슷한 음식을 선택해주세요.", labels, horizontal=False)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("다른 음식 판정하기", use_container_width=True):
            reset_meal_flow()
            st.rerun()
    nutrition_progress_text = st.empty()
    nutrition_progress_bar = st.empty()
    with col2:
        if st.button("이 음식으로 영양 보기", use_container_width=True):
            food_name = food_by_label[selected]
            try:
                for value in range(1, 66):
                    nutrition_progress_text.markdown("영양정보를 분석 중이에요.")
                    nutrition_progress_bar.progress(value)
                    time.sleep(0.07)
                nutrition = fetch_nutrition(food_name)
                for value in range(66, 86):
                    nutrition_progress_text.markdown("영양성분 결과를 정리하고 있어요.")
                    nutrition_progress_bar.progress(value)
                    time.sleep(0.03)
                nutrition_progress_text.markdown("음식 성분 설명을 준비하고 있어요.")
                nutrition_progress_bar.progress(86)
                get_cached_nutrition_explanation(food_name, nutrition)
                for value in range(87, 101):
                    nutrition_progress_text.markdown("결과 화면을 준비하고 있어요.")
                    nutrition_progress_bar.progress(value)
                    time.sleep(0.02)
                st.session_state.meal_food_name = food_name
                st.session_state.meal_nutrition = nutrition
                st.session_state.meal_error = ""
                st.session_state.meal_show_result = True
                st.session_state.meal_step = "result"
            except Exception as error:
                st.session_state.meal_error = friendly_error(error)
            finally:
                nutrition_progress_text.empty()
                nutrition_progress_bar.empty()
            st.rerun()

def is_present_value(value):
    if value in (None, "", "-"):
        return False
    text = str(value).strip()
    return text not in ("", "-", "nan", "NaN", "None")


def display_value(value, unit=""):
    if not is_present_value(value):
        return "-"
    try:
        number = float(str(value).replace(",", ""))
        if number.is_integer():
            text = f"{int(number):,}"
        else:
            text = f"{number:,.2f}".rstrip("0").rstrip(".")
    except Exception:
        text = str(value)
    return f"{text}{unit}"


def render_metric_card(label, value, unit="", featured=False):
    class_name = "meal-metric meal-metric-feature" if featured else "meal-metric"
    return (
        f'<div class="{class_name}">'
        f'<div class="meal-metric-label">{escape(label)}</div>'
        f'<div class="meal-metric-value">{escape(display_value(value, unit))}</div>'
        f'</div>'
    )


def render_metric_grid(metrics):
    visible_metrics = [item for item in metrics if is_present_value(item[1])]
    if not visible_metrics:
        return
    metric_html = "".join(render_metric_card(label, value, unit) for label, value, unit in visible_metrics)
    st.markdown(f"<div class='meal-metric-grid'>{metric_html}</div>", unsafe_allow_html=True)

def build_share_text(food_name, nutrition):
    calories = display_value(nutrition_value(nutrition, "calories", "kcal"), "kcal")
    carbs = display_value(nutrition_value(nutrition, "carbs", "carbohydrate", "carbohydrates"), "g")
    protein = display_value(nutrition_value(nutrition, "protein"), "g")
    fat = display_value(nutrition_value(nutrition, "fat", "total_fat"), "g")
    sodium = display_value(nutrition_value(nutrition, "sodium"), "mg")
    sugar = display_value(nutrition_value(nutrition, "sugar", "sugars"), "g")
    return (
        "오늘 한 끼 판정단 결과\n"
        f"음식: {food_name}\n"
        f"칼로리: {calories}\n"
        f"탄수화물: {carbs} / 단백질: {protein} / 지방: {fat}\n"
        f"나트륨: {sodium} / 당류: {sugar}\n"
        "라이나생명 HUB에서 확인한 재미용 한 끼 기록입니다."
    )


def render_share_box(food_name, nutrition):
    share_text = build_share_text(food_name, nutrition)
    st.markdown("#### 결과 공유하기")
    st.text_area("카카오톡이나 인스타 스토리에 붙여넣을 공유 문구", share_text, height=145)
    share_text_json = json.dumps(share_text, ensure_ascii=False)
    components.html(
        f"""
        <button id="mealShareButton" style="width:100%; border:1px solid #f5b51b; border-radius:8px; background:#fff8e6; color:#111827; font-weight:800; padding:12px 14px; cursor:pointer;">
            휴대폰 공유창 열기 / 문구 복사하기
        </button>
        <div id="mealShareStatus" style="font-size:13px; color:#64748b; margin-top:8px;"></div>
        <script>
        const text = {share_text_json};
        const button = document.getElementById('mealShareButton');
        const status = document.getElementById('mealShareStatus');
        button.addEventListener('click', async () => {{
            try {{
                if (navigator.share) {{
                    await navigator.share({{ title: '오늘 한 끼 판정단', text }});
                    status.innerText = '공유창을 열었습니다.';
                }} else if (navigator.clipboard) {{
                    await navigator.clipboard.writeText(text);
                    status.innerText = '공유 문구를 복사했습니다.';
                }} else {{
                    status.innerText = '위 공유 문구를 직접 복사해서 사용해주세요.';
                }}
            }} catch (error) {{
                status.innerText = '공유가 취소되었거나 브라우저에서 지원하지 않습니다. 위 문구를 복사해서 사용해주세요.';
            }}
        }});
        </script>
        """,
        height=90,
    )


def render_nutrition():
    if not st.session_state.get("meal_show_result"):
        return

    food_name = st.session_state.meal_food_name
    nutrition = st.session_state.meal_nutrition or {}
    if not food_name or not nutrition:
        st.session_state.meal_step = "select"
        st.rerun()

    comment, chips = judge_meal(nutrition)
    health_message = food_health_message(nutrition)
    serving = nutrition_value(nutrition, "display_serving", "serving")
    serving_note = nutrition_value(nutrition, "serving_note")
    calorie_metric = ("칼로리", nutrition_value(nutrition, "calories", "kcal"), "kcal")
    main_metrics = [
        ("탄수화물", nutrition_value(nutrition, "carbohydrate", "carbohydrates", "carbs"), "g"),
        ("단백질", nutrition_value(nutrition, "protein"), "g"),
        ("지방", nutrition_value(nutrition, "fat", "total_fat"), "g"),
        ("나트륨", nutrition_value(nutrition, "sodium"), "mg"),
        ("당류", nutrition_value(nutrition, "sugar", "sugars"), "g"),
        ("식이섬유", nutrition_value(nutrition, "dietary_fiber", "fiber"), "g"),
    ]
    extra_metrics = [
        ("수분", nutrition_value(nutrition, "water"), "g"),
        ("회분", nutrition_value(nutrition, "ash"), "g"),
        ("칼슘", nutrition_value(nutrition, "calcium"), "mg"),
        ("철", nutrition_value(nutrition, "iron"), "mg"),
        ("인", nutrition_value(nutrition, "phosphorus"), "mg"),
        ("칼륨", nutrition_value(nutrition, "potassium"), "mg"),
        ("마그네슘", nutrition_value(nutrition, "magnesium"), "mg"),
        ("아연", nutrition_value(nutrition, "zinc"), "mg"),
        ("콜레스테롤", nutrition_value(nutrition, "cholesterol"), "mg"),
        ("포화지방산", nutrition_value(nutrition, "saturated_fat"), "g"),
        ("트랜스지방산", nutrition_value(nutrition, "trans_fat"), "g"),
        ("불포화지방산", nutrition_value(nutrition, "unsaturated_fat"), "g"),
        ("오메가3", nutrition_value(nutrition, "omega3"), "g"),
        ("오메가6", nutrition_value(nutrition, "omega6"), "g"),
        ("비타민 A", nutrition_value(nutrition, "vitamin_a"), "μg RAE"),
        ("레티놀", nutrition_value(nutrition, "retinol"), "μg"),
        ("베타카로틴", nutrition_value(nutrition, "beta_carotene"), "μg"),
        ("티아민", nutrition_value(nutrition, "thiamin"), "mg"),
        ("리보플라빈", nutrition_value(nutrition, "riboflavin"), "mg"),
        ("니아신", nutrition_value(nutrition, "niacin"), "mg"),
        ("비타민 C", nutrition_value(nutrition, "vitamin_c"), "mg"),
        ("비타민 D", nutrition_value(nutrition, "vitamin_d"), "μg"),
        ("카페인", nutrition_value(nutrition, "caffeine"), "mg"),
    ]

    with st.container(border=True):
        st.markdown(f"### {food_name} 판정 결과")
        st.markdown(f"<div class='meal-card-copy'>{escape(comment)}</div>", unsafe_allow_html=True)
        if is_present_value(serving):
            st.markdown(
                f"<div class='meal-card-copy' style='margin-top:.35rem; font-weight:850;'>기준량: {escape(display_value(serving))}</div>",
                unsafe_allow_html=True,
            )
        if is_present_value(serving_note):
            st.markdown(
                f"<div class='meal-card-copy' style='margin-top:.12rem;'>{escape(str(serving_note))}</div>",
                unsafe_allow_html=True,
            )
        if is_present_value(calorie_metric[1]):
            st.markdown(
                render_metric_card(calorie_metric[0], calorie_metric[1], calorie_metric[2], featured=True),
                unsafe_allow_html=True,
            )
        render_metric_grid(main_metrics)
        render_nutrition_explanation(food_name, nutrition)
        with st.expander("추가 영양성분 보기", expanded=False):
            with st.spinner("추가 영양성분을 불러오는 중입니다."):
                time.sleep(0.25)
                render_metric_grid(extra_metrics)
        st.markdown(
            "<div class='meal-chip-row'>"
            + "".join(f"<span class='meal-chip'>{escape(chip)}</span>" for chip in chips)
            + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='meal-card-copy' style='margin-top:.7rem;'>"
            "* 위 영양정보는 식약처 식품영양정보에 등록된 표준정보 입니다.<br>"
            "제공된 양과 조리법, 재료에 따라 달라질 수 있어요."
            "</div>",
            unsafe_allow_html=True,
        )

    if health_message.get("show_direct"):
        st.markdown(
            f"""
            <div class="meal-direct">
                <div class="meal-direct-title">{escape(health_message["title"])}</div>
                <div class="meal-direct-copy">{escape(health_message["copy"])}</div>
                <a href="https://direct.lina.co.kr/" target="_blank">{escape(health_message["link"])}</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_share_box(food_name, nutrition)
    if st.button("다른 음식 판정하기", use_container_width=True):
        reset_meal_flow()
        st.rerun()


def render():
    render_css()
    init_state()
    render_feature_banner("assets/feature_banners/meal_judgement.png", "오늘 한 끼 판정단")
    render_feature_intro_card(
        "음식 사진을 올리면 오늘 한 끼의 칼로리와 영양 흐름을 살펴봅니다. "
        "결과는 식단을 돌아보는 참고용이며, 다음 끼니를 조금 더 균형 있게 고르는 데 도움을 드립니다."
    )

    if st.session_state.meal_error:
        st.error(st.session_state.meal_error)

    if st.session_state.meal_step == "upload":
        render_upload()
    elif st.session_state.meal_step == "select":
        render_predictions()
    elif st.session_state.meal_step == "result":
        render_nutrition()
    else:
        reset_meal_flow()
        st.rerun()
