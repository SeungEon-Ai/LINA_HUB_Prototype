import base64
import html
from pathlib import Path

import streamlit as st

from features.local_secrets import get_openai_api_key
from features.shared_header import render_feature_banner, render_feature_intro_card

from .ai import answer_with_gpt, fallback_answer
from .data import (
    detect_product_topics,
    detect_query_topics,
    find_related_rider_products,
    get_related_graph,
    graph_stats,
    is_related_rider_query,
    load_graph,
    products_dataframe,
    search_chunks,
    search_product_pdf_pages,
)


ROOT = Path(__file__).resolve().parents[2]
LOGO_MARK = ROOT / "assets" / "lina_mark_color.png"
MESSAGE_VERSION = "policy_graph_messages_v7"
DEFAULT_ASSISTANT_MESSAGE = "약관이나 보장 조건에 대해 궁금한 점을 물어보세요!  "


def _image_data_uri(path):
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_css():
    st.markdown(
        """
        <style>
        .policy-chat-intro {
            display: flex;
            align-items: flex-start;
            gap: .55rem;
            margin: .7rem 0 1rem;
            color: #1f2937;
            font-size: .92rem;
            line-height: 1.45;
        }
        .policy-chat-intro img {
            width: 28px;
            height: 28px;
            border-radius: 8px;
            object-fit: contain;
        }
        .policy-stat-row {
            display: none;
            flex-wrap: wrap;
            gap: .45rem;
            margin: .55rem 0 .8rem;
        }
        .policy-pill {
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            padding: .22rem .55rem;
            color: #64748b;
            background: #fff;
            font-size: .72rem;
            line-height: 1.15;
            white-space: nowrap;
        }
        .policy-evidence {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: .7rem .85rem;
            margin: .55rem 0;
            background: #f8fafc;
        }
        .policy-evidence-title {
            color: #111827;
            font-size: .78rem;
            font-weight: 800;
            margin-bottom: .3rem;
        }
        .policy-evidence-link {
            display: inline-flex;
            align-items: center;
            min-height: 24px;
            margin: .12rem 0 .45rem;
            padding: 0 .62rem;
            border: 1px solid #d7def0;
            border-radius: 999px;
            background: #ffffff;
            color: #2512a0 !important;
            font-size: .72rem;
            font-weight: 850;
            text-decoration: none !important;
        }
        .policy-evidence-link:hover {
            border-color: #2512a0;
            background: #f5f3ff;
        }
        .policy-evidence-body {
            color: #475569;
            font-size: .72rem;
            line-height: 1.55;
            white-space: normal;
            overflow-wrap: anywhere;
            word-break: keep-all;
        }
        .policy-node-row {
            display: flex;
            flex-wrap: wrap;
            gap: .35rem;
            margin-top: .4rem;
        }
        .policy-node {
            border-radius: 999px;
            background: #fff7df;
            border: 1px solid #f1bd2b;
            color: #374151;
            font-size: .68rem;
            padding: .14rem .45rem;
        }
        .st-key-policy_example_0 button,
        .st-key-policy_example_1 button,
        .st-key-policy_example_2 button,
        .st-key-policy_example_3 button {
            min-height: 42px !important;
            padding: .28rem .4rem !important;
            white-space: nowrap !important;
            overflow: hidden !important;
        }
        .st-key-policy_example_0 button p,
        .st-key-policy_example_1 button p,
        .st-key-policy_example_2 button p,
        .st-key-policy_example_3 button p {
            font-size: .72rem !important;
            line-height: 1.1 !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            word-break: keep-all !important;
        }
        .policy-chat-row {
            display: flex;
            align-items: flex-start;
            width: 100%;
            margin: .6rem 0;
            gap: .72rem;
        }
        .st-key-policy_chat_surface {
            min-height: 560px;
            position: relative;
            border: 1px solid #ded7f4;
            border-radius: 22px;
            background: #f7f3ff;
            padding: 1.3rem 1rem 5.9rem;
            margin: 1rem 0 1.1rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, .05);
        }
        .st-key-policy_chat_surface > div[data-testid="stVerticalBlock"] {
            min-height: 526px;
            display: flex;
            flex-direction: column;
        }
        .st-key-policy_chat_surface div[data-testid="stElementContainer"]:has(div[data-testid="stForm"]) {
            position: absolute !important;
            left: 1rem !important;
            right: 1rem !important;
            bottom: -7.45rem !important;
            width: auto !important;
            margin-top: 0 !important;
            z-index: 3 !important;
        }
        .st-key-policy_chat_surface > div[data-testid="stLayoutWrapper"]:has(div[data-testid="stForm"]) {
            position: absolute !important;
            left: 1rem !important;
            right: 1rem !important;
            bottom: .9rem !important;
            width: auto !important;
            margin: 0 !important;
            z-index: 4 !important;
        }
        .st-key-policy_chat_surface div[data-testid="stForm"] {
            padding: .45rem !important;
        }
        .policy-chat-row.assistant {
            justify-content: flex-start;
        }
        .policy-chat-row.user {
            justify-content: flex-end;
        }
        .policy-chat-avatar {
            width: 28px;
            height: 28px;
            object-fit: contain;
            flex: 0 0 28px;
            border-radius: 7px;
        }
        .policy-chat-bubble {
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
        .policy-chat-row.assistant .policy-chat-bubble {
            background: #fff;
            box-shadow: 0 6px 18px rgba(15, 23, 42, .05);
        }
        .policy-chat-row.user .policy-chat-bubble {
            max-width: 52%;
            padding: .48rem .72rem;
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
        .st-key-policy_graph_chat_input input {
            min-height: 3rem !important;
            border-radius: 999px !important;
            border: 0 !important;
            background: #e8eef6 !important;
            padding: 0 3.7rem 0 1.15rem !important;
            font-size: .9rem !important;
        }
        .st-key-policy_graph_send {
            position: absolute !important;
            right: .38rem !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            z-index: 5 !important;
            width: 2.35rem !important;
        }
        .st-key-policy_graph_send button {
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
        .st-key-policy_graph_send button p { font-size: 1.25rem !important; line-height: 1 !important; }
        .policy-chat-input-spacer {
            height: 18rem;
        }
        .policy-loading-panel {
            display: flex;
            align-items: center;
            gap: .6rem;
            flex-wrap: nowrap;
            white-space: nowrap;
            margin: .85rem 0 .75rem;
            color: #1f2937;
            font-size: .96rem;
            line-height: 1.35;
        }
        .policy-loading-spinner {
            width: 22px;
            height: 22px;
            border: 3px solid #e5e7eb;
            border-top-color: #5b83df;
            border-radius: 999px;
            flex: 0 0 22px;
            animation: policy-loading-spin .75s linear infinite;
        }
        @keyframes policy-loading-spin {
            to { transform: rotate(360deg); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _html_text(text):
    cleaned = str(text or "").replace("**", "")
    for marker in (
        '<div class="policy-evidence-body">',
        "<div class='policy-evidence-body'>",
        "</div>",
    ):
        cleaned = cleaned.replace(marker, "")
    return html.escape(cleaned).replace("\n", "<br>")


def _strip_basis_lines(text):
    lines = []
    for line in str(text or "").splitlines():
        normalized = line.strip()
        if "참고한 약관 근거" in normalized:
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _product_category(product_name):
    topics = detect_product_topics(product_name) or []
    if topics:
        return " / ".join(topics)
    name = str(product_name or "")
    if "치아" in name:
        return "치아보험"
    if "암" in name:
        return "암보험"
    if "치매" in name or "간병" in name or "LTC" in name:
        return "치매/간병보험"
    if "종신" in name:
        return "종신보험"
    return "기타 보장성 상품"


def _topic_mismatch(product_name, query):
    if not product_name or product_name == "전체 상품":
        return False, [], []
    product_topics = detect_product_topics(product_name)
    query_topics = detect_query_topics(query)
    if not product_topics or not query_topics:
        return False, product_topics, query_topics
    return not (set(product_topics) & set(query_topics)), product_topics, query_topics


def _render_product_notice(product_name):
    if not product_name or product_name == "전체 상품":
        return
    _render_chat_message(
        "assistant",
        f"선택한 상품명: {product_name}\n카테고리: {_product_category(product_name)}",
    )


def _related_rider_answer(product_filter, candidates):
    if not candidates:
        return (
            f"현재 선택한 상품은 `{product_filter}`입니다.\n\n"
            "현재 판매중인 상품 목록에서 바로 연결해 볼 수 있는 특약 후보를 찾지 못했습니다. "
            "이 경우 상품 범위를 `전체 상품`으로 바꾸거나, 원하는 보장명을 함께 넣어 다시 물어보시면 더 넓게 찾아볼 수 있습니다.\n\n"
            "예: 치아 보철치료 관련 특약이 있어요? / 암 진단 후 생활비 관련 특약이 있어요?"
        )

    lines = [
        f"현재 선택한 상품은 `{product_filter}`입니다.",
        "",
        "현재 판매중인 상품 목록에서 같은 보장 주제로 함께 검토해볼 수 있는 특약 후보를 찾았습니다.",
        "다만 실제로 이 상품에 부가 가능한지는 주계약, 가입나이, 판매채널, 인수기준에 따라 달라질 수 있으므로 최종 확인이 필요합니다.",
        "",
    ]
    for idx, product in enumerate(candidates[:6], start=1):
        name = product.get("product_name", "")
        category = _product_category(name)
        lines.append(f"{idx}. {name}")
        lines.append(f"   - 연결 이유: 선택 상품과 같은 `{category}` 주제의 특약 후보입니다.")
    lines.extend(
        [
            "",
            "다음으로 확인하면 좋은 질문:",
            "- 이 특약은 어떤 치료를 보장해?",
            "- 이 특약의 면책기간이나 감액기간은 있어?",
            "- 이 특약의 보장 한도는 어떻게 돼?",
        ]
    )
    return "\n".join(lines)


def _related_rider_nodes(candidates):
    return [
        {
            "type": "product",
            "label": product.get("product_name", ""),
            "id": f"product:{product.get('inscd', '')}",
        }
        for product in candidates[:10]
    ]


def _is_openai_api_key(value):
    value = str(value or "").strip()
    return value.startswith("sk-") and len(value) >= 30


def _evidence_text_key(text):
    return " ".join(str(text or "").split())[:520]


def _truncate_evidence_text(text, limit=900):
    cleaned = " ".join(str(text or "").split())
    if len(cleaned) <= limit:
        return cleaned
    window = cleaned[:limit]
    cut = max(window.rfind(mark) for mark in ("다.", "요.", ".", "!", "?", "。"))
    if cut < int(limit * 0.55):
        cut = max(window.rfind(mark) for mark in (" ", ",", "，", "·", "ㆍ"))
    if cut < int(limit * 0.45):
        cut = limit
    else:
        cut += 1
    return cleaned[:cut].rstrip(" ,，·ㆍ") + " ..."


def _dedupe_evidence_chunks(chunks, limit=5):
    deduped = []
    seen = set()
    for chunk in chunks:
        text_key = _evidence_text_key(chunk.get("text", ""))
        meta_key = (
            str(chunk.get("product_name") or ""),
            str(chunk.get("doc_type_name") or ""),
            str(chunk.get("page") or ""),
        )
        key = text_key or "|".join(meta_key)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(chunk)
        if len(deduped) >= limit:
            break
    return deduped


def _render_evidence(chunks):
    if not chunks:
        return
    with st.expander("참고한 약관 근거 보기", expanded=False):
        for chunk in _dedupe_evidence_chunks(chunks):
            evidence_text = _truncate_evidence_text(chunk.get("text", ""))
            pdf_url = str(chunk.get("pdf_url") or "").strip()
            pdf_href = html.escape(pdf_url, quote=True)
            pdf_link = (
                f'<a class="policy-evidence-link" href="{pdf_href}" target="_blank" rel="noopener noreferrer">원문 PDF 열기</a>'
                if pdf_href
                else ""
            )
            evidence_body = _html_text(evidence_text)
            st.markdown(
                f"""
                <div class="policy-evidence">
                    <div class="policy-evidence-title">
                        {html.escape(chunk.get("product_name", ""))} · {html.escape(chunk.get("doc_type_name", ""))} · p.{chunk.get("page")}
                    </div>
                    {pdf_link}
                    <div class="policy-evidence-body">{evidence_body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_nodes(nodes):
    return


def _render_chat_message(role, content):
    content_html = _html_text(content)
    if role == "assistant":
        avatar = _image_data_uri(LOGO_MARK)
        avatar_html = f'<img class="policy-chat-avatar" src="{avatar}" alt="LINA">' if avatar else ""
        st.markdown(
            f"""
            <div class="policy-chat-row assistant">
                {avatar_html}
                <div class="policy-chat-bubble">{content_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="policy-chat-row user">
                <div class="policy-chat-bubble">{content_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_loading_panel(text):
    st.markdown(
        f"""
        <div class="policy-loading-panel">
            <div class="policy-loading-spinner"></div>
            <div>{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _make_answer(api_key, question, chunks, related_nodes, history, product_filter):
    if api_key and _is_openai_api_key(api_key):
        try:
            answer = answer_with_gpt(
                api_key,
                question,
                chunks,
                related_nodes,
                history=history,
                product_filter=product_filter,
            )
            if answer:
                cleaned_answer = _strip_basis_lines(answer)
                if chunks:
                    return f"{cleaned_answer}\n\n참고한 약관 근거는 아래의 `참고한 약관 근거 보기`에서 확인해 주세요."
                return cleaned_answer
        except Exception:
            return (
                "답변을 정리하는 중 문제가 있어 약관 근거 중심으로 보여드립니다.\n\n"
                + fallback_answer(question, chunks, product_filter=product_filter)
            )
    if api_key and not _is_openai_api_key(api_key):
        return fallback_answer(question, chunks, product_filter=product_filter)
    return fallback_answer(question, chunks, product_filter=product_filter)


def _basis_summary(chunks):
    if not chunks:
        return ""
    seen = []
    for chunk in chunks[:3]:
        item = (
            str(chunk.get("product_name") or ""),
            str(chunk.get("doc_type_name") or ""),
            str(chunk.get("page") or ""),
        )
        if item not in seen:
            seen.append(item)
    parts = [f"`{name}`의 `{doc}` p.{page}" for name, doc, page in seen if name and doc and page]
    if not parts:
        return ""
    return "참고한 약관 근거: " + ", ".join(parts) + "을 참고했습니다."


def _chunks_look_like_toc(chunks):
    if not chunks:
        return True
    toc_like = 0
    for chunk in chunks:
        text = str(chunk.get("text") or "")
        if "........" in text and "제 " in text and "조" in text:
            toc_like += 1
    return toc_like >= max(1, len(chunks) - 1)


def render():
    render_css()
    render_feature_banner("assets/feature_banners/policy_graph_rag.png", "라이나 약관 AI")
    render_feature_intro_card(
        "라이나생명 핵심 상품 약관에서 보장 조건, 면책기간, 감액기간, 제외사항을 찾아 설명합니다."
    )

    graph = load_graph()
    stats = graph_stats(graph)
    products_count = stats["products"]
    st.markdown(
        f"""
        <style>
        .st-key-policy_product_scope label::after {{
            content: "상품 {products_count}개";
            display: inline-flex;
            align-items: center;
            min-height: 22px;
            margin-left: .45rem;
            padding: 0 .55rem;
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            background: #fff;
            color: #64748b;
            font-size: .72rem;
            font-weight: 800;
            line-height: 1;
            vertical-align: .05rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="policy-stat-row">
            <span class="policy-pill">상품 {stats['products']}개</span>
            <span class="policy-pill">그래프 노드 {stats['nodes']}개</span>
            <span class="policy-pill">관계 {stats['edges']}개</span>
            <span class="policy-pill">약관 근거 {stats['chunks']}개</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    api_key = get_openai_api_key()

    products_df = products_dataframe(graph)
    product_names = ["전체 상품"]
    if not products_df.empty:
        product_names.extend(products_df["product_name"].dropna().drop_duplicates().tolist())

    select_col, search_col = st.columns([2.2, 1])
    selected_product = select_col.selectbox("상품 범위", product_names, index=0, key="policy_product_scope")
    search_selected_product = search_col.selectbox(
        "상품 검색",
        product_names[1:],
        index=None,
        key="policy_product_search_result",
        placeholder="상품명 검색",
        help="목록을 열고 상품명을 입력하면 후보가 바로 좁혀집니다.",
    )
    active_product = search_selected_product or selected_product
    product_filter = None if active_product == "전체 상품" else active_product

    if st.session_state.get("policy_graph_message_version") != MESSAGE_VERSION:
        st.session_state.policy_graph_messages = [
            {"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}
        ]
        st.session_state.policy_graph_message_version = MESSAGE_VERSION

    if "policy_graph_messages" not in st.session_state:
        st.session_state.policy_graph_messages = [
            {"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}
        ]
    elif not st.session_state.policy_graph_messages:
        st.session_state.policy_graph_messages = [
            {"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}
        ]

    if product_filter and st.session_state.get("policy_graph_active_product_notice") != product_filter:
        st.session_state.policy_graph_messages.append(
            {
                "role": "assistant",
                "content": f"선택한 상품명: {product_filter}\n카테고리: {_product_category(product_filter)}",
            }
        )
        st.session_state.policy_graph_active_product_notice = product_filter

    examples = [
        "암보험 면책기간은 어떻게 적용돼?",
        "치아보험 임플란트 보장은 어떤 조건이 있어?",
        "감액기간에는 보험금이 줄어들어?",
        "치매 간병 보장은 어떤 상태일 때 확인해야 해?",
    ]

    pending_question = st.session_state.pop("policy_graph_pending_question", None)
    if pending_question:
        with st.container(key="policy_chat_surface"):
            cols = st.columns(4)
            for idx, example in enumerate(examples):
                if cols[idx].button(example, key=f"policy_example_pending_{idx}", use_container_width=True):
                    st.session_state.policy_graph_pending_question = example
                    st.rerun()

            for message in st.session_state.policy_graph_messages:
                _render_chat_message(message["role"], message["content"])
                if message["role"] == "assistant":
                    _render_evidence(message.get("chunks", []))
                    _render_nodes(message.get("nodes", []))

            st.session_state.policy_graph_messages.append({"role": "user", "content": pending_question})
            _render_chat_message("user", pending_question)
            loading_slot = st.empty()

        query_topics = detect_query_topics(pending_question)
        related_rider_mode = is_related_rider_query(pending_question)
        mismatch, product_topics, query_topics_for_block = _topic_mismatch(product_filter, pending_question)
        if related_rider_mode:
            with loading_slot.container():
                _render_loading_panel("현재 판매중인 상품 목록에서 연관 특약 후보를 찾고 있어요.")
            rider_candidates = find_related_rider_products(
                graph,
                product_name=product_filter,
                query=pending_question,
                top_k=8,
            )
            chunks = []
            related_nodes = _related_rider_nodes(rider_candidates)
            answer = _related_rider_answer(product_filter or "전체 상품", rider_candidates)
        elif mismatch:
            topic_text = ", ".join(query_topics_for_block)
            answer = (
                f"선택한 상품명: {product_filter}\n"
                f"카테고리: {_product_category(product_filter)}\n"
                f"질문 주제: {topic_text}\n\n"
                "선택한 상품과 질문 주제가 맞지 않아 약관 설명을 이어가지 않았습니다. "
                "질문과 맞는 상품을 선택하거나 상품 범위를 `전체 상품`으로 바꿔 주세요."
            )
            chunks = []
            related_nodes = []
        else:
            with loading_slot.container():
                _render_loading_panel("약관 내용을 확인하고 있어요.")
            chunks = search_chunks(
                graph,
                pending_question,
                product_filter=product_filter,
                top_k=7,
                require_topic_match=True,
            )
            if product_filter and (not chunks or _chunks_look_like_toc(chunks)):
                pdf_chunks = search_product_pdf_pages(
                    graph,
                    pending_question,
                    product_filter=product_filter,
                    top_k=7,
                )
                if pdf_chunks:
                    chunks = pdf_chunks
            related_nodes = get_related_graph(graph, chunks)
            answer = _make_answer(
                api_key,
                pending_question,
                chunks,
                related_nodes,
                st.session_state.policy_graph_messages,
                product_filter,
            )

        if not related_rider_mode and not mismatch and product_filter and query_topics and not chunks:
            topic_text = ", ".join(query_topics)
            answer = (
                f"선택한 상품명: {product_filter}\n"
                f"카테고리: {_product_category(product_filter)}\n"
                f"질문 주제: {topic_text}\n\n"
                "선택한 상품과 질문 주제가 맞지 않아 약관 설명을 이어가지 않았습니다. "
                "질문과 맞는 상품을 선택하거나 상품 범위를 `전체 상품`으로 바꿔 주세요."
            )

        st.session_state.policy_graph_messages.append(
            {
                "role": "assistant",
                "content": answer,
                "chunks": chunks,
                "nodes": related_nodes,
            }
        )
        st.rerun()

    with st.container(key="policy_chat_surface"):
        cols = st.columns(4)
        for idx, example in enumerate(examples):
            if cols[idx].button(example, key=f"policy_example_{idx}", use_container_width=True):
                st.session_state.policy_graph_pending_question = example
                st.rerun()

        for message in st.session_state.policy_graph_messages:
            _render_chat_message(message["role"], message["content"])
            if message["role"] == "assistant":
                _render_evidence(message.get("chunks", []))
                _render_nodes(message.get("nodes", []))

        st.markdown('<div class="policy-chat-input-spacer"></div>', unsafe_allow_html=True)
        with st.form("policy_graph_inline_chat_form", clear_on_submit=True):
            typed_question = st.text_input(
                "약관 질문 입력",
                placeholder="약관이나 보장 조건에 대해 궁금한 점을 물어보세요.",
                label_visibility="collapsed",
                key="policy_graph_chat_input",
            )
            submitted = st.form_submit_button("↑", key="policy_graph_send", use_container_width=False)
    if submitted and typed_question.strip():
        st.session_state.policy_graph_pending_question = typed_question.strip()
        st.rerun()

