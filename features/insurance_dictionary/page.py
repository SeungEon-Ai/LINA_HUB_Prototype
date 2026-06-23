import base64
import html
import re

import streamlit as st

from .ai import answer, get_api_key
from .config import LOGO_MARK
from .data import load_terms, search_terms
from features.shared_header import render_feature_banner, render_feature_intro_card


MESSAGE_KEY = "dictionary_chat_messages_v17"
PENDING_KEY = "pending_dictionary_prompt_v15"
QUERY_PROMPT_KEY = "processed_dictionary_query_prompt_v1"

EXAMPLE_QUESTIONS = [
    "보험료와 보험금의 차이가 뭐야?",
    "보험계약자가 무슨 뜻이야?",
    "자동갱신계약이 무슨 뜻이야?",
    "면책기간이 무슨뜻이야?",
]

def assistant_avatar():
    return str(LOGO_MARK) if LOGO_MARK.exists() else None


def logo_data_uri():
    if not LOGO_MARK.exists():
        return ""
    encoded = base64.b64encode(LOGO_MARK.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def clean_answer_text(text):
    text = str(text or "")
    text = re.sub(r"</?div[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?p[^>]*>", "", text, flags=re.IGNORECASE)
    text = text.replace("**", "")
    text = re.sub(r"^-?\s*쉬운 설명\s*:\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^-?\s*분류\s*:\s*.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n*\s*참고\s*출처\s*:.*$", "", text, flags=re.MULTILINE)
    return text.strip()


def html_text(text):
    return html.escape(clean_answer_text(text)).replace("\n", "<br>")


def render_chat_css():
    st.markdown(
        """
        <style>
        .dictionary-title-row {
            display: flex;
            align-items: center;
            gap: .5rem;
            height: 32px;
            margin-bottom: .8rem;
        }
        .dictionary-title-logo {
            width: 30px;
            height: 30px;
            object-fit: contain;
            display: block;
            flex: 0 0 30px;
        }
        .dictionary-title {
            color: #15202b;
            font-size: 1.42rem;
            font-weight: 900;
            line-height: 32px;
            height: 32px;
            margin: 0;
            letter-spacing: 0;
            white-space: nowrap;
        }
        div[data-testid="stSegmentedControl"] label {
            font-size: .68rem !important;
            min-height: 1.25rem !important;
            padding: .1rem .5rem !important;
            white-space: nowrap !important;
        }
        .st-key-dictionary_example_question_v17_0 button,
        .st-key-dictionary_example_question_v17_1 button,
        .st-key-dictionary_example_question_v17_2 button,
        .st-key-dictionary_example_question_v17_3 button {
            min-height: 2.15rem !important;
            padding: .25rem .42rem !important;
        }
        .st-key-dictionary_example_question_v17_0 button p,
        .st-key-dictionary_example_question_v17_1 button p,
        .st-key-dictionary_example_question_v17_2 button p,
        .st-key-dictionary_example_question_v17_3 button p {
            font-size: .72rem !important;
            line-height: 1.05 !important;
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }
        .chat-row {
            display: flex;
            align-items: flex-start;
            width: 100%;
            margin: .6rem 0;
            gap: .72rem;
        }
        .st-key-dictionary_chat_surface {
            min-height: 560px;
            position: relative;
            border: 1px solid #ded7f4;
            border-radius: 20px;
            background: #f7f3ff;
            padding: 1.3rem 1rem 5.9rem;
            margin: .9rem 0 1rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, .05);
        }
        .st-key-dictionary_chat_surface > div[data-testid="stVerticalBlock"] {
            min-height: 526px;
            display: flex;
            flex-direction: column;
        }
        .st-key-dictionary_chat_surface div[data-testid="stElementContainer"]:has(div[data-testid="stForm"]) {
            position: absolute !important;
            left: 1rem !important;
            right: 1rem !important;
            bottom: -7.45rem !important;
            width: auto !important;
            margin-top: 0 !important;
            z-index: 3 !important;
        }
        .st-key-dictionary_chat_surface > div[data-testid="stLayoutWrapper"]:has(div[data-testid="stForm"]) {
            position: absolute !important;
            left: 1rem !important;
            right: 1rem !important;
            bottom: .9rem !important;
            width: auto !important;
            margin: 0 !important;
            z-index: 4 !important;
        }
        .st-key-dictionary_chat_surface div[data-testid="stForm"] {
            padding: .45rem !important;
        }
        .chat-row.assistant {
            justify-content: flex-start;
        }
        .chat-row.user {
            justify-content: flex-end;
        }
        .chat-avatar {
            width: 28px;
            height: 28px;
            object-fit: contain;
            flex: 0 0 28px;
            border-radius: 7px;
        }
        .chat-bubble {
            max-width: 74%;
            border-radius: 8px;
            border: 1px solid #d8e4f2;
            padding: .12rem .35rem .35rem;
            font-size: .98rem;
            line-height: 1.45;
            color: #252b36;
            word-break: keep-all;
            overflow-wrap: anywhere;
            background: #f8fbff;
        }
        .chat-row.user .chat-bubble {
            max-width: 52%;
            padding: .48rem .72rem;
        }
        .chat-row.assistant .chat-bubble {
            background: #fff;
            box-shadow: 0 6px 18px rgba(15, 23, 42, .05);
        }
        .chat-row.user .chat-bubble {
            background: #fff8e6;
            border-color: #f4d38b;
        }
        div[data-testid="stForm"] {
            position: relative !important;
            border: 1px solid #d8e4f2 !important;
            border-radius: 18px !important;
            padding: .45rem !important;
            background: #f7faff !important;
            box-shadow: 0 8px 24px rgba(15, 23, 42, .04) !important;
        }
        .st-key-dictionary_chat_input input {
            min-height: 3rem !important;
            border-radius: 999px !important;
            border: 0 !important;
            background: #e8eef6 !important;
            padding: 0 3.7rem 0 1.15rem !important;
            font-size: .9rem !important;
        }
        .st-key-dictionary_send {
            position: absolute !important;
            right: .38rem !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            z-index: 5 !important;
            width: 2.35rem !important;
        }
        .st-key-dictionary_send button {
            width: 2.35rem !important;
            height: 2.35rem !important;
            min-height: 2.35rem !important;
            padding: 0 !important;
            border-radius: 999px !important;
            font-size: 1.25rem !important;
            line-height: 1 !important;
            font-weight: 900 !important;
            background: #ffb71b !important;
            color: #fff !important;
            border: 3px solid #fff !important;
            box-shadow: 0 8px 18px rgba(255,183,27,.32) !important;
        }
        .st-key-dictionary_send button p { font-size: 1.25rem !important; line-height: 1 !important; }
        .dictionary-chat-input-spacer {
            height: 18rem;
        }
        .dictionary-loading-inline {
            display: flex;
            align-items: center;
            gap: .55rem;
            flex-wrap: nowrap;
            white-space: nowrap;
        }
        .dictionary-loading-bubble {
            padding: .48rem .72rem !important;
        }
        .dictionary-loading-spinner {
            width: 20px;
            height: 20px;
            border: 3px solid #e5e7eb;
            border-top-color: #5b83df;
            border-radius: 999px;
            flex: 0 0 20px;
            animation: dictionary-loading-spin .75s linear infinite;
        }
        @keyframes dictionary-loading-spin {
            to { transform: rotate(360deg); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_messages():
    for key in list(st.session_state.keys()):
        if key.startswith("dictionary_chat_messages") and key != MESSAGE_KEY:
            del st.session_state[key]

    if MESSAGE_KEY not in st.session_state:
        st.session_state[MESSAGE_KEY] = [
            {
                "role": "assistant",
                "content": "보험용어에 대해 궁금한 점을 물어보세요!  ",
            }
        ]

    for msg in st.session_state[MESSAGE_KEY]:
        if msg["role"] == "assistant":
            msg["content"] = clean_answer_text(msg.get("content", "")) or "보험용어에 대해 궁금한 점을 물어보세요!  "


def messages():
    return st.session_state[MESSAGE_KEY]


def render_header():
    render_feature_banner("assets/feature_banners/insurance_dictionary.png", "AI보험용어사전")
    render_feature_intro_card(
        "보험료, 보험금, 면책기간처럼 비슷해 보이는 말도 뜻은 다릅니다. "
        "헷갈리는 보험용어를 짧게 물어보면 쉬운 말로 풀어드립니다."
    )


def render_status(df):
    return


def queue_prompt(prompt):
    messages().append({"role": "user", "content": prompt})
    st.session_state[PENDING_KEY] = prompt


def queue_query_prompt_from_url():
    query_prompt = st.query_params.get("dictionary_q", "")
    if isinstance(query_prompt, list):
        query_prompt = query_prompt[0] if query_prompt else ""
    query_prompt = str(query_prompt).strip()
    if not query_prompt:
        return
    if st.session_state.get(QUERY_PROMPT_KEY) == query_prompt:
        return
    queue_prompt(query_prompt)
    st.session_state[QUERY_PROMPT_KEY] = query_prompt


def render_quick_examples():
    st.markdown("예시 질문")
    cols = st.columns(len(EXAMPLE_QUESTIONS), gap="small")
    for index, question in enumerate(EXAMPLE_QUESTIONS):
        with cols[index]:
            if st.button(
                question,
                key=f"dictionary_example_question_v17_{index}",
                use_container_width=True,
            ):
                queue_prompt(question)
                st.rerun()


def render_message(msg):
    role = msg["role"]
    content = html_text(msg["content"])
    if role == "assistant":
        avatar = logo_data_uri()
        avatar_html = f'<img class="chat-avatar" src="{avatar}" alt="LINA">' if avatar else ""
        st.markdown(
            f"""
            <div class="chat-row assistant">
                {avatar_html}
                <div class="chat-bubble">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="chat-row user">
                <div class="chat-bubble">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_messages():
    for msg in messages():
        render_message(msg)


def complete_pending_prompt(df):
    prompt = st.session_state.get(PENDING_KEY, "")
    if not prompt:
        return

    loading_slot = st.empty()
    avatar = logo_data_uri()
    avatar_html = f'<img class="chat-avatar" src="{avatar}" alt="LINA">' if avatar else ""
    loading_slot.markdown(
        f"""
        <div class="chat-row assistant">
            {avatar_html}
            <div class="chat-bubble dictionary-loading-bubble">
                <div class="dictionary-loading-inline">
                    <div class="dictionary-loading-spinner"></div>
                    <div>보험용어를 찾아 정리하고 있어요.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    results = search_terms(df, prompt)
    response = clean_answer_text(answer(prompt, results))

    messages().append(
        {
            "role": "assistant",
            "content": response,
        }
    )
    st.session_state[PENDING_KEY] = ""
    st.rerun()


def render():
    render_chat_css()
    df = load_terms()
    init_messages()
    queue_query_prompt_from_url()
    render_header()
    render_status(df)
    with st.container(key="dictionary_chat_surface"):
        render_quick_examples()
        render_messages()
        complete_pending_prompt(df)
    
        st.markdown('<div class="dictionary-chat-input-spacer"></div>', unsafe_allow_html=True)
        with st.form("dictionary_inline_chat_form", clear_on_submit=True):
            prompt = st.text_input(
                "보험용어 질문 입력",
                placeholder="예: 보험계약자가 무슨 뜻이야?",
                label_visibility="collapsed",
                key="dictionary_chat_input",
            )
            submitted = st.form_submit_button("↑", key="dictionary_send", use_container_width=False)
    
    if submitted and prompt.strip():
        queue_prompt(prompt)
        st.rerun()
