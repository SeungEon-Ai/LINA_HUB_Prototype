import base64
import html
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from features.shared_header import render_feature_banner, render_feature_intro_card
from .ai import answer_question
from .config import CONSULT_URL, FAQ_SOURCE_URL
from .data import load_faq_data, search_faq

MESSAGE_KEY = "lina_faq_ai_messages_v4"
PENDING_KEY = "lina_faq_ai_pending_v1"
QUERY_KEY = "lina_faq_ai_query_processed_v1"
CHAT_OPEN_KEY = "lina_faq_ai_chat_open_processed_v1"
FAQ_PAGE_KEY = "lina_faq_ai_faq_page_v1"
FAQ_SEARCH_KEY = "lina_faq_ai_faq_search_prev_v1"
FAQ_PAGE_SIZE = 10
MINI_HERO_BG = Path(__file__).resolve().parents[2] / "assets" / "home" / "gunggeumtalk-mini-bg-v2.png"
LOGO_MARK = Path(__file__).resolve().parents[2] / "assets" / "lina_mark_color.png"
DEFAULT_ASSISTANT_MESSAGE = "보험금 청구, 계약 조회, 납입, 고객센터 이용까지 궁금한 내용을 편하게 물어보세요!  "

EXAMPLES = [
    "치아보험금 청구시 필요한 서류는 무엇이 있나요?",
    "온라인으로 보험금 청구하는 방법은?",
    "보험료를 얼마나 미납하면 실효가 되나요?",
    "보험료 납입 카드를 변경하고 싶어요",
    "보험금은 언제 받을 수 있나요?",
    "계약 조회는 어디서 확인하나요?",
]



def _image_data_uri(path):
    path = Path(path)
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def _escape(text):
    return html.escape(str(text or "")).replace("\n", "<br>")


def render_css():
    st.markdown(
        """
        <style>
        .faq-ai-actions { display:flex; gap:.5rem; flex-wrap:wrap; margin:.4rem 0 1rem; }
        .faq-ai-link { display:inline-flex; align-items:center; justify-content:center; min-height:30px; padding:0 .8rem; border:1px solid #dfe7f1; border-radius:999px; color:#334155 !important; background:#fff; font-size:.72rem; font-weight:800; text-decoration:none !important; }
        .st-key-lina_faq_ai_chat_surface { min-height:560px; position:relative; border:1px solid #ded7f4; border-radius:22px; background:#f7f3ff; padding:1.3rem 1rem 5.9rem; margin:.9rem 0 1.1rem; box-shadow:0 10px 28px rgba(15,23,42,.05); }
        .st-key-lina_faq_ai_chat_surface > div[data-testid="stVerticalBlock"] { min-height:526px; display:flex; flex-direction:column; }
        .st-key-lina_faq_ai_chat_surface div[data-testid="stElementContainer"]:has(div[data-testid="stForm"]) { position:absolute !important; left:1rem !important; right:1rem !important; bottom:-7.45rem !important; width:auto !important; margin-top:0 !important; z-index:3 !important; }
        .st-key-lina_faq_ai_chat_surface > div[data-testid="stLayoutWrapper"]:has(div[data-testid="stForm"]) { position:absolute !important; left:1rem !important; right:1rem !important; bottom:.9rem !important; width:auto !important; margin:0 !important; z-index:4 !important; }
        .st-key-lina_faq_ai_chat_surface div[data-testid="stForm"] { padding:.45rem !important; }
        .faq-ai-chat-card { border:0; border-radius:16px; background:transparent; padding:0 0 1rem; margin:.12rem 0 1rem; box-shadow:none; }
        .faq-ai-input-spacer { height:18rem; }
        .faq-ai-ready { margin:.35rem 0 .65rem; padding:.56rem .75rem; border:1px solid #f5c24b; border-radius:14px; background:#fff8e6; color:#334155; font-size:.76rem; font-weight:850; }
        .faq-ai-msg { display:flex; align-items:flex-start; gap:.72rem; margin:.55rem 0; }
        .faq-ai-msg.user { justify-content:flex-end; }
        .faq-ai-avatar { width:28px; height:28px; object-fit:contain; flex:0 0 28px; border-radius:7px; }
        .faq-ai-bubble { max-width:78%; border:1px solid #d8e4f2; border-radius:12px; padding:.58rem .72rem; color:#1f2937; font-size:.82rem; line-height:1.5; word-break:keep-all; overflow-wrap:anywhere; background:#f8fbff; }
        .faq-ai-msg.user .faq-ai-bubble { background:#fff8e6; border-color:#f4d38b; }
        .faq-ai-msg.assistant .faq-ai-bubble { background:#fff; box-shadow:0 5px 14px rgba(15,23,42,.04); }
        .faq-ai-evidence-title { color:#334155; font-size:.8rem; font-weight:900; margin:.9rem 0 .35rem; }
        .faq-answer-text { white-space:pre-line; color:#1f2937; font-size:.9rem; line-height:1.72; word-break:keep-all; overflow-wrap:anywhere; }
        .faq-list-count { color:#64748b; font-size:.72rem; font-weight:800; margin:.35rem 0 .55rem; }
        .faq-page-caption { color:#64748b; font-size:.68rem; font-weight:800; text-align:center; margin:.45rem 0 .2rem; }
        .st-key-faq_page_first button,
        .st-key-faq_page_prev button,
        .st-key-faq_page_next button,
        .st-key-faq_page_last button,
        div[class*="st-key-faq_page_num_"] button { min-height:2rem !important; padding:.15rem .25rem !important; border-radius:999px !important; font-size:.72rem !important; font-weight:900 !important; }
        div[data-testid="stForm"] { position:relative !important; border:1px solid #d8e4f2 !important; border-radius:18px !important; padding:.45rem !important; background:#f7faff !important; box-shadow:0 8px 24px rgba(15,23,42,.04) !important; }
        .st-key-lina_faq_ai_input input { min-height:3rem !important; border-radius:999px !important; border:0 !important; background:#e8eef6 !important; padding:0 3.7rem 0 1.15rem !important; font-size:.9rem !important; }
        .st-key-lina_faq_ai_submit { position:absolute !important; right:.38rem !important; top:50% !important; transform:translateY(-50%) !important; z-index:5 !important; width:2.35rem !important; }
        .st-key-lina_faq_ai_submit button { width:2.35rem !important; height:2.35rem !important; min-height:2.35rem !important; padding:0 !important; border-radius:999px !important; font-size:1.25rem !important; line-height:1 !important; font-weight:900 !important; background:#ffb71b !important; color:#fff !important; border:3px solid #fff !important; box-shadow:0 8px 18px rgba(255,183,27,.32) !important; }
        .st-key-lina_faq_ai_submit button p { font-size:1.25rem !important; line-height:1 !important; }
        .st-key-lina_faq_ai_example_0 button,
        .st-key-lina_faq_ai_example_1 button,
        .st-key-lina_faq_ai_example_2 button,
        .st-key-lina_faq_ai_example_3 button,
        .st-key-lina_faq_ai_example_4 button,
        .st-key-lina_faq_ai_example_5 button { min-height:2.15rem !important; padding:.25rem .45rem !important; border-radius:10px !important; }
        .st-key-lina_faq_ai_example_0 button p,
        .st-key-lina_faq_ai_example_1 button p,
        .st-key-lina_faq_ai_example_2 button p,
        .st-key-lina_faq_ai_example_3 button p,
        .st-key-lina_faq_ai_example_4 button p,
        .st-key-lina_faq_ai_example_5 button p { font-size:.72rem !important; line-height:1.15 !important; }
        div[data-testid="stHorizontalBlock"]:has(.st-key-lina_faq_ai_example_0),
        div[data-testid="stHorizontalBlock"]:has(.st-key-lina_faq_ai_example_3) {
            margin-bottom: .12rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_messages():
    if MESSAGE_KEY not in st.session_state:
        st.session_state[MESSAGE_KEY] = [
            {
                "role": "assistant",
                "content": DEFAULT_ASSISTANT_MESSAGE,
            }
        ]


def queue_question(question):
    question = str(question or "").strip()
    if not question:
        return
    st.session_state[MESSAGE_KEY].append({"role": "user", "content": question})
    st.session_state[PENDING_KEY] = question


def process_query_param():
    chat_open = st.query_params.get("chat") or st.query_params.get("chat_open")
    if chat_open and st.session_state.get(CHAT_OPEN_KEY) != chat_open:
        st.session_state[CHAT_OPEN_KEY] = chat_open
        st.session_state[MESSAGE_KEY].append(
            {
                "role": "assistant",
                "content": "상담챗봇을 바로 열었어요. 보험금 청구, 계약 조회, 납입, 고객센터 이용처럼 궁금한 내용을 아래 입력창에 편하게 적어주세요!  ",
            }
        )

    query = st.query_params.get("faq_q") or st.query_params.get("qna_q")
    if query and st.session_state.get(QUERY_KEY) != query:
        st.session_state[QUERY_KEY] = query
        queue_question(query)


def render_messages():
    avatar = _image_data_uri(LOGO_MARK)
    avatar_html = f'<img class="faq-ai-avatar" src="{avatar}" alt="LINA">' if avatar else ""
    st.markdown('<div class="faq-ai-chat-card">', unsafe_allow_html=True)
    for msg in st.session_state[MESSAGE_KEY]:
        role = "user" if msg.get("role") == "user" else "assistant"
        assistant_avatar_html = avatar_html if role == "assistant" else ""
        st.markdown(
            f'<div class="faq-ai-msg {role}">{assistant_avatar_html}<div class="faq-ai-bubble">{_escape(msg.get("content", ""))}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)


def render_evidence(matches):
    if not matches:
        return
    st.markdown('<div class="faq-ai-evidence-title">답변에 참고한 자주 묻는 질문</div>', unsafe_allow_html=True)
    for item in matches[:3]:
        with st.expander(item["question"]):
            st.markdown(f'<div class="faq-answer-text">{_escape(item["answer"])}</div>', unsafe_allow_html=True)



def render_embed_chat():
    render_css()
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"], .stApp { background:#fff !important; min-height:100vh !important; }
        header, footer, #MainMenu, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton, [data-testid="stStatusWidget"], .viewerBadge_container__1QSob { display:none !important; }
        [data-testid="stAppViewContainer"] > .main { padding-top:0 !important; }
        .block-container { min-height:100vh !important; padding: .55rem .85rem 4.8rem !important; max-width: 100% !important; }
        .mini-chat-hero {
            height: 144px;
            margin: .05rem 0 .45rem;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            background: #f6f4ff center center / cover no-repeat;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 24px rgba(15,23,42,.05);
        }
        .mini-chat-hero-copy {
            position:absolute;
            left: 38%;
            top: 2.05rem;
            z-index: 2;
            color:#111827;
            text-shadow: 0 1px 0 rgba(255,255,255,.72);
        }
        .mini-chat-hero-title {
            font-size: 1.34rem;
            font-weight: 950;
            line-height: 1.05;
            letter-spacing: 0;
        }
        .mini-chat-hero-sub {
            margin-top: .36rem;
            color:#64748b;
            font-size: .84rem;
            font-weight: 800;
            line-height: 1.25;
        }
        .element-container { margin-top:0 !important; margin-bottom:.18rem !important; }
        div[data-testid="stVerticalBlock"] { gap:.32rem !important; }
        div[data-testid="stHorizontalBlock"]:has(.st-key-mini_chat_badge_0) {
            width: calc(100% - 2.4rem) !important;
            max-width: calc(100% - 2.4rem) !important;
            margin: -2.36rem auto .85rem !important;
            position: relative;
            z-index: 4;
            gap: .18rem !important;
            display: grid !important;
            grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.st-key-mini_chat_badge_0) > div {
            width: auto !important;
            min-width: 0 !important;
            flex: none !important;
        }
        div[class*="st-key-mini_chat_badge_"] button {
            min-height: 1.68rem !important;
            height: 1.68rem !important;
            border: 1px solid rgba(124,111,214,.34) !important;
            border-radius: 999px !important;
            background: rgba(255,255,255,.92) !important;
            color: #24138d !important;
            box-shadow: 0 8px 18px rgba(15,23,42,.06) !important;
            padding: 0 .06rem !important;
        }
        div[class*="st-key-mini_chat_badge_"] button:hover {
            background: #fff8e6 !important;
            border-color: #ffb71b !important;
        }
        div[class*="st-key-mini_chat_badge_"] button p {
            color: #24138d !important;
            font-size: .5rem !important;
            font-weight: 900 !important;
            line-height: 1 !important;
            white-space: nowrap !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] { margin-top:0 !important; }
        .faq-ai-chat-card { margin: 0 0 .55rem !important; padding: .55rem !important; border:0 !important; box-shadow:none !important; }
        .faq-ai-msg { margin:.38rem 0 !important; }
        .faq-ai-bubble { max-width: 94% !important; font-size: .74rem !important; line-height: 1.45 !important; }
        .faq-ai-evidence-title, .faq-list-count, .faq-page-caption { display:none !important; }
        div[data-testid="stExpander"], div[data-testid="stExpanderDetails"] { display:none !important; }
        .st-key-lina_faq_ai_input input { min-height:2.55rem !important; padding:0 3.1rem 0 .9rem !important; font-size:.78rem !important; }
        .st-key-lina_faq_ai_submit { right:.28rem !important; width:2.05rem !important; }
        .st-key-lina_faq_ai_submit button { width:2.05rem !important; height:2.05rem !important; min-height:2.05rem !important; font-size:1.05rem !important; }
        .st-key-lina_faq_ai_submit button p { font-size:1.05rem !important; }
        div[data-testid="stElementContainer"]:has(div[data-testid="stForm"]),
        div[data-testid="stLayoutWrapper"]:has(div[data-testid="stForm"]) {
            position: fixed !important;
            left: .85rem !important;
            right: .85rem !important;
            bottom: .85rem !important;
            width: auto !important;
            margin: 0 !important;
            z-index: 20 !important;
        }
        div[data-testid="stForm"] {
            position: relative !important;
            width: 100% !important;
            margin: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    hero_uri = _image_data_uri(MINI_HERO_BG)
    badge_questions = [
        ("보험금 청구", "보험금 청구서류는 뭐가 필요해?"),
        ("계약조회", "내 계약은 어디서 확인하나요?"),
        ("보장내용", "내 보험 보장내용은 어디서 확인해?"),
        ("자주 묻는 질문", "자주 묻는 질문을 보여줘"),
    ]
    st.markdown(
        f'<section class="mini-chat-hero" style="background-image:url({hero_uri});">'
        '<div class="mini-chat-hero-copy">'
        '<div class="mini-chat-hero-title">라이나 궁금톡</div>'
        '<div class="mini-chat-hero-sub">무엇을 도와드릴까요?</div>'
        '</div>'
        '</section>',
        unsafe_allow_html=True,
    )

    init_messages()
    cols = st.columns(4)
    for badge_idx, (label, question) in enumerate(badge_questions):
        if cols[badge_idx].button(label, key=f"mini_chat_badge_{badge_idx}", use_container_width=True):
            queue_question(question)
            st.rerun()

    query = st.query_params.get("faq_q") or st.query_params.get("qna_q")
    if query and st.session_state.get(QUERY_KEY) != query:
        st.session_state[QUERY_KEY] = query
        queue_question(query)
    render_messages()

    last_matches = []
    pending = st.session_state.pop(PENDING_KEY, "")
    if pending:
        with st.spinner("답변을 정리하고 있습니다..."):
            reply, last_matches = answer_question(pending)
        st.session_state[MESSAGE_KEY].append({"role": "assistant", "content": reply})
        st.session_state["lina_faq_ai_last_matches_v1"] = last_matches
        st.rerun()

    with st.form("lina_faq_ai_form", clear_on_submit=True):
        question = st.text_input(
            "질문 입력",
            placeholder="예: 보험금 청구서류는 뭐가 필요해?",
            label_visibility="collapsed",
            key="lina_faq_ai_input",
        )
        submitted = st.form_submit_button("↑", key="lina_faq_ai_submit", use_container_width=False, type="primary")
        if submitted and question.strip():
            queue_question(question)
            st.rerun()

def set_faq_page(page, total_pages):
    st.session_state[FAQ_PAGE_KEY] = max(1, min(int(page), int(total_pages)))


def render_faq_browser(data):
    keyword = st.text_input(
        "키워드",
        placeholder="예: 보험료 납입, 해약환급금, 증명서",
        key="lina_faq_ai_search",
    )
    keyword = str(keyword or "").strip()
    if st.session_state.get(FAQ_SEARCH_KEY) != keyword:
        st.session_state[FAQ_SEARCH_KEY] = keyword
        st.session_state[FAQ_PAGE_KEY] = 1

    items = search_faq(keyword, limit=300) if keyword else data.get("items", [])
    total = len(items)
    if total == 0:
        st.write("검색 결과가 없습니다.")
        return

    total_pages = max(1, (total + FAQ_PAGE_SIZE - 1) // FAQ_PAGE_SIZE)
    page = max(1, min(int(st.session_state.get(FAQ_PAGE_KEY, 1)), total_pages))
    st.session_state[FAQ_PAGE_KEY] = page
    start = (page - 1) * FAQ_PAGE_SIZE
    page_items = items[start : start + FAQ_PAGE_SIZE]

    label = f"검색 결과 {total}건" if keyword else "자주 묻는 질문 참고자료"
    st.markdown(f'<div class="faq-list-count">{label} · {page}/{total_pages}페이지</div>', unsafe_allow_html=True)

    for index, item in enumerate(page_items, start + 1):
        with st.expander(f"{index}. {item['question']}"):
            st.markdown(f'<div class="faq-answer-text">{_escape(item["answer"])}</div>', unsafe_allow_html=True)
            if st.button("이 질문으로 상담하기", key=f"faq_ask_{page}_{index}"):
                queue_question(item["question"])
                st.rerun()

    st.markdown(f'<div class="faq-page-caption">{page} / {total_pages}</div>', unsafe_allow_html=True)
    max_buttons = 7
    half = max_buttons // 2
    left = max(1, min(page - half, total_pages - max_buttons + 1))
    right = min(total_pages, left + max_buttons - 1)
    page_numbers = list(range(left, right + 1))

    cols = st.columns([0.8, 0.8] + [1] * len(page_numbers) + [0.8, 0.8])
    if cols[0].button("≪", key="faq_page_first", use_container_width=True, disabled=page == 1):
        set_faq_page(1, total_pages)
        st.rerun()
    if cols[1].button("‹", key="faq_page_prev", use_container_width=True, disabled=page == 1):
        set_faq_page(page - 1, total_pages)
        st.rerun()
    for offset, number in enumerate(page_numbers, 2):
        button_type = "primary" if number == page else "secondary"
        if cols[offset].button(str(number), key=f"faq_page_num_{number}", use_container_width=True, type=button_type):
            set_faq_page(number, total_pages)
            st.rerun()
    if cols[-2].button("›", key="faq_page_next", use_container_width=True, disabled=page == total_pages):
        set_faq_page(page + 1, total_pages)
        st.rerun()
    if cols[-1].button("≫", key="faq_page_last", use_container_width=True, disabled=page == total_pages):
        set_faq_page(total_pages, total_pages)
        st.rerun()


def render():
    if st.query_params.get("mini_embed") == "1" or st.query_params.get("embed") == "1":
        render_embed_chat()
        return

    render_css()
    init_messages()
    process_query_param()

    data = load_faq_data()
    render_feature_banner("assets/feature_banners/lina_faq_ai.png", "라이나 궁금톡")
    render_feature_intro_card("보험 상담 전 궁금한 점을 먼저 물어보고 자주 묻는 질문을 쉽게 확인해보세요.")
    st.markdown(
        f'<div class="faq-ai-actions"><a class="faq-ai-link" href="{FAQ_SOURCE_URL}" target="_blank">자주 묻는 질문 보기</a><a class="faq-ai-link" href="{CONSULT_URL}" target="_blank">고객센터 연결</a></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div id="lina-gunggeumtalk-chat"></div>', unsafe_allow_html=True)

    with st.container(key="lina_faq_ai_chat_surface"):
        cols = st.columns(3)
        for idx, example in enumerate(EXAMPLES[:3]):
            if cols[idx].button(example, key=f"lina_faq_ai_example_{idx}", use_container_width=True):
                queue_question(example)
                st.rerun()
        cols = st.columns(3)
        for idx, example in enumerate(EXAMPLES[3:], 3):
            if cols[idx - 3].button(example, key=f"lina_faq_ai_example_{idx}", use_container_width=True):
                queue_question(example)
                st.rerun()

        if st.query_params.get("chat") or st.query_params.get("chat_open"):
            st.markdown('<div class="faq-ai-ready">상담챗봇이 열렸습니다. 아래 입력창에 질문을 바로 남겨보세요.</div>', unsafe_allow_html=True)

        render_messages()

        last_matches = []
        pending = st.session_state.pop(PENDING_KEY, "")
        if pending:
            with st.spinner("궁금한 내용을 정리하고 있습니다..."):
                reply, last_matches = answer_question(pending)
            st.session_state[MESSAGE_KEY].append({"role": "assistant", "content": reply})
            st.session_state["lina_faq_ai_last_matches_v1"] = last_matches
            st.rerun()

        st.markdown('<div class="faq-ai-input-spacer"></div>', unsafe_allow_html=True)
        with st.form("lina_faq_ai_form", clear_on_submit=True):
            question = st.text_input(
                "질문 입력",
                placeholder="예: 보험금 청구서류는 뭐가 필요해?",
                label_visibility="collapsed",
                key="lina_faq_ai_input",
            )
            submitted = st.form_submit_button("↑", key="lina_faq_ai_submit", use_container_width=False, type="primary")
            if submitted and question.strip():
                queue_question(question)
                st.rerun()

    render_evidence(st.session_state.get("lina_faq_ai_last_matches_v1", []))

    with st.expander("자주 묻는 질문 참고자료"):
        render_faq_browser(data)







