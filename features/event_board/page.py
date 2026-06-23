import base64
import json
from datetime import date
from html import escape
from pathlib import Path

import streamlit as st


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "user_events.json"

DEFAULT_EVENTS = [
    {
        "title": "다이렉트 보험 신규 가입 이벤트",
        "status": "진행중",
        "date": "2026-06-01",
        "body": "",
        "image": "",
    }
]


def _load_events():
    if not DATA_PATH.exists():
        return DEFAULT_EVENTS.copy()
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_EVENTS.copy()
    if not isinstance(data, list):
        return DEFAULT_EVENTS.copy()
    return data


def _save_events(events):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")


def _uploaded_image_data_uri(uploaded_file):
    if not uploaded_file:
        return ""
    mime_type = uploaded_file.type or "image/png"
    encoded = base64.b64encode(uploaded_file.getvalue()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _clean_body(value):
    text = str(value or "").strip()
    if text == "홈 화면에 보여줄 이벤트 내용을 직접 작성해보세요.":
        return ""
    if '<div class="event-user-card-top"' in text or "<article" in text or "</span>" in text:
        return ""
    return text


def render():
    st.markdown(
        """
<style>
.event-editor-hero,
.st-key-event_writer,
.event-list-heading,
.event-card-list {
    width: 100% !important;
    max-width: 1160px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    box-sizing: border-box !important;
}
.event-editor-hero {
    padding: 28px 32px;
    border: 1px solid #dfe7f1;
    border-radius: 24px;
    background: linear-gradient(135deg, #fff8dc 0%, #ffffff 54%, #f3f0ff 100%);
    box-shadow: 0 18px 42px rgba(17, 24, 39, 0.06);
    margin-top: 1.8rem;
    margin-bottom: 22px;
}
.event-editor-hero h1 {
    margin: 0;
    font-size: 34px;
    letter-spacing: 0;
    color: #101828;
}
.event-content-field {
    margin: .35rem 0 .45rem;
    color: #111827;
    font-size: 1rem;
    font-weight: 800;
}
.st-key-event_writer .event-content-field + div[data-testid="stElementContainer"] {
    background: #eef1f5 !important;
    border-radius: 10px 10px 0 0 !important;
    padding: .95rem .95rem .25rem !important;
    margin-bottom: 0 !important;
}
.st-key-event_writer .event-content-field + div[data-testid="stElementContainer"] + div[data-testid="stElementContainer"] {
    background: #eef1f5 !important;
    border-radius: 0 !important;
    padding: .25rem .95rem .35rem !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}
.st-key-event_writer div[data-testid="stFileUploader"] {
    margin-bottom: 0 !important;
}
.st-key-event_writer div[data-testid="stFileUploaderDropzone"] {
    border: 0 !important;
    background: transparent !important;
    padding: 0 !important;
    min-height: 54px !important;
}
.event-upload-preview {
    display: block;
    width: 100%;
    max-height: 320px;
    object-fit: contain;
    border-radius: 12px;
    border: 1px solid #dde6f0;
    background: #fff;
    margin: .35rem 0 .65rem;
}
.st-key-event_writer div[data-testid="stElementContainer"]:has(.event-upload-preview) {
    background: #eef1f5 !important;
    padding: .25rem .95rem .8rem !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}
.st-key-event_writer div[data-testid="stTextArea"] {
    margin-top: 0 !important;
    background: #eef1f5 !important;
    border-radius: 0 0 10px 10px !important;
    padding: .25rem .95rem .95rem !important;
}
.st-key-event_writer div[data-testid="stTextArea"] textarea {
    border: 1px solid #d8e2ef !important;
    box-shadow: none !important;
    background: #eef1f5 !important;
    border-radius: 10px !important;
    padding: .9rem 1rem !important;
}
.st-key-event_writer div[data-testid="stTextArea"] textarea:focus {
    border: 0 !important;
    box-shadow: none !important;
}
.event-card-list {
    display: grid;
    gap: 14px;
    margin-top: 18px;
}
.event-user-card {
    border: 1px solid #dfe7f1;
    border-radius: 18px;
    padding: 18px 20px;
    background: #fff;
    box-shadow: 0 10px 26px rgba(17, 24, 39, 0.05);
    overflow: hidden;
}
.event-user-image {
    width: 100%;
    max-height: 260px;
    object-fit: cover;
    border-radius: 14px;
    border: 1px solid #e5edf7;
    margin-bottom: 14px;
    display: block;
}
.event-user-card-top {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.event-user-status {
    padding: 7px 14px;
    border-radius: 999px;
    background: #fff2c7;
    color: #2f1f00;
    font-weight: 800;
    font-size: 14px;
}
.event-user-date {
    color: #8a97aa;
    font-weight: 700;
    margin-left: auto;
}
.event-user-card h3 {
    margin: 0 0 8px;
    font-size: 21px;
    color: #101828;
}
.event-user-card p {
    margin: 0;
    color: #52637a;
    line-height: 1.6;
    font-size: 16px;
    white-space: pre-wrap;
}
</style>
<section class="event-editor-hero"><h1>이벤트</h1></section>
        """,
        unsafe_allow_html=True,
    )

    events = _load_events()

    with st.container(key="event_writer"):
        st.subheader("이벤트 글쓰기")
        title = st.text_input("제목", placeholder="예: 7월 건강 체크 이벤트")
        status = st.text_input("상태", value="진행중", placeholder="예: 진행중, 예정, 종료")
        event_date = st.date_input("표시 날짜", value=date.today())
        st.markdown('<div class="event-content-field">내용</div>', unsafe_allow_html=True)
        image_file = st.file_uploader(
            "내용 이미지 등록",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )
        image_preview_uri = _uploaded_image_data_uri(image_file)
        if image_preview_uri:
            st.markdown(
                f'<img class="event-upload-preview" src="{escape(image_preview_uri, quote=True)}" alt="이벤트 이미지 미리보기">',
                unsafe_allow_html=True,
            )
        body = st.text_area(
            "내용 글 작성",
            placeholder="이미지 아래에 들어갈 이벤트 안내 문구를 입력하세요.",
            height=140,
            label_visibility="collapsed",
        )
        submitted = st.button("내용 등록하기", use_container_width=True)

    if submitted:
        clean_title = title.strip()
        clean_body = body.strip()
        if not clean_title or (not clean_body and not image_preview_uri):
            st.warning("제목과 이미지 또는 내용을 입력해주세요.")
        else:
            events.insert(
                0,
                {
                    "title": clean_title,
                    "status": status.strip() or "진행중",
                    "date": event_date.isoformat(),
                    "body": clean_body,
                    "image": image_preview_uri,
                },
            )
            _save_events(events)
            st.success("이벤트가 등록되었습니다.")
            st.rerun()

    st.markdown('<h3 class="event-list-heading">등록된 이벤트</h3>', unsafe_allow_html=True)
    if not events:
        st.info("아직 등록된 이벤트가 없습니다.")
        return

    for idx, item in enumerate(events):
        title_html = escape(str(item.get("title", "")))
        status_html = escape(str(item.get("status", "진행중")))
        date_html = escape(str(item.get("date", "")))
        body_html = escape(_clean_body(item.get("body", "")))
        image_uri = str(item.get("image", ""))
        image_html = (
            f'<img class="event-user-image" src="{escape(image_uri, quote=True)}" alt="{title_html}">'
            if image_uri.startswith("data:image/")
            else ""
        )
        body_block = f"<p>{body_html}</p>" if body_html else ""
        card_html = (
            '<div class="event-card-list">'
            '<article class="event-user-card">'
            f"{image_html}"
            '<div class="event-user-card-top">'
            f'<span class="event-user-status">{status_html}</span>'
            f'<span class="event-user-date">{date_html}</span>'
            "</div>"
            f"<h3>{title_html}</h3>"
            f"{body_block}"
            "</article>"
            "</div>"
        )
        st.markdown(card_html, unsafe_allow_html=True)
        if st.button("삭제", key=f"delete_event_{idx}"):
            del events[idx]
            _save_events(events)
            st.rerun()
