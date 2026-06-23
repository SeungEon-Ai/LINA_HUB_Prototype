import gzip
import json
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

import pandas as pd
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "features" / "policy_graph_rag" / "data"
GRAPH_PATH = DATA_DIR / "core_policy_graph.json.gz"
DOC_TYPE_LABELS = {"P": "상품약관", "B": "사업방법서", "S": "상품요약서"}

TOKEN_PATTERN = re.compile(r"[가-힣A-Za-z0-9]{2,}")

QUERY_TOPIC_KEYWORDS = {
    "치아": ["치아", "임플란트", "브릿지", "틀니", "충전", "크라운", "보철"],
    "암": ["암", "제자리암", "경계성종양", "악성신생물", "항암"],
    "치매간병": ["치매", "간병", "요양", "인지", "장기요양"],
    "종신": ["종신", "사망", "해약환급금", "납입"],
}


def _tokenize(text):
    tokens = TOKEN_PATTERN.findall(str(text or "").lower())
    expanded = list(tokens)
    for token in tokens:
        for suffix in ("은", "는", "이", "가", "을", "를", "에", "의", "와", "과", "도", "만"):
            if token.endswith(suffix) and len(token) > len(suffix) + 1:
                expanded.append(token[: -len(suffix)])
                break
    return expanded


def expand_policy_query(query):
    text = str(query or "")
    additions = []
    expansion_map = {
        "감액기간": ["감액기간", "감액", "보험금", "지급", "50", "퍼센트", "줄어", "계약일"],
        "면책기간": ["면책기간", "지급하지", "보험금", "90", "일", "보장개시", "계약일"],
        "임플란트": ["임플란트", "보철", "영구치", "발거", "치료", "보장", "보험금"],
        "특약": ["특약", "부가", "가입", "주계약", "보장"],
        "보험금": ["보험금", "지급", "지급사유", "보장", "한도"],
        "보장조건": ["보장", "조건", "보험금", "지급", "지급사유", "지급기준", "면책", "감액", "한도"],
        "보장 조건": ["보장", "조건", "보험금", "지급", "지급사유", "지급기준", "면책", "감액", "한도"],
        "보장내용": ["보장", "내용", "보험금", "지급", "지급사유", "지급기준", "면책", "감액", "한도"],
        "보장 내용": ["보장", "내용", "보험금", "지급", "지급사유", "지급기준", "면책", "감액", "한도"],
        "지급조건": ["지급", "조건", "보험금", "지급사유", "지급기준", "보장", "면책", "감액", "한도"],
        "지급 조건": ["지급", "조건", "보험금", "지급사유", "지급기준", "보장", "면책", "감액", "한도"],
    }
    for key, words in expansion_map.items():
        if key in text:
            additions.extend(words)
    if not additions:
        return text
    return text + " " + " ".join(dict.fromkeys(additions))


def detect_query_topics(query):
    text = str(query or "")
    topics = []
    for topic, keywords in QUERY_TOPIC_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            topics.append(topic)
    return topics


def detect_product_topics(product_name):
    text = str(product_name or "")
    topics = []
    for topic, keywords in QUERY_TOPIC_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            topics.append(topic)
    return topics


def is_related_rider_query(query):
    text = str(query or "")
    if "특약" not in text:
        return False
    intent_words = [
        "들",
        "가입",
        "추가",
        "붙",
        "연관",
        "관련",
        "같이",
        "함께",
        "가능",
        "추천",
        "있나",
        "있어",
        "뭐",
        "어떤",
    ]
    return any(word in text for word in intent_words)


def find_related_rider_products(graph, product_name=None, query=None, top_k=8):
    products = graph.get("products", [])
    product_topics = detect_product_topics(product_name)
    query_topics = detect_query_topics(query)
    topics = list(dict.fromkeys(product_topics + query_topics))
    query_tokens = set(_tokenize(query))
    product_tokens = {
        token
        for token in _tokenize(product_name)
        if token not in {"무배당", "갱신형", "보험", "보험ii", "ii"}
    }

    candidates = []
    for product in products:
        name = str(product.get("product_name") or "")
        if not name or name == product_name or "특약" not in name:
            continue

        score = 0
        rider_topics = detect_product_topics(name)
        if topics and not (set(rider_topics) & set(topics)):
            continue
        if topics and set(rider_topics) & set(topics):
            score += 20
        if query_tokens:
            name_tokens = set(_tokenize(name))
            score += len(query_tokens & name_tokens) * 3
        if product_tokens:
            name_tokens = set(_tokenize(name))
            score += len(product_tokens & name_tokens) * 8
        if "다이렉트" in str(product_name or "") and "다이렉트" in name:
            score += 18
        if "라이나" in str(product_name or "") and "라이나" in name:
            score += 10
        if product_topics and set(rider_topics) & set(product_topics):
            score += 10
        if not topics and not query_tokens:
            score += 1

        if score <= 0:
            continue
        enriched = dict(product)
        enriched["_score"] = score
        enriched["_topics"] = rider_topics
        candidates.append(enriched)

    candidates.sort(key=lambda item: (item.get("_score", 0), item.get("product_name", "")), reverse=True)
    return candidates[:top_k]


def load_graph():
    if not GRAPH_PATH.exists():
        return {"products": [], "nodes": [], "edges": [], "chunks": []}
    with gzip.open(GRAPH_PATH, "rt", encoding="utf-8") as file:
        return json.load(file)


def graph_stats(graph):
    return {
        "products": len(graph.get("products", [])),
        "nodes": len(graph.get("nodes", [])),
        "edges": len(graph.get("edges", [])),
        "chunks": len(graph.get("chunks", [])),
    }


def build_search_index(chunks):
    token_docs = []
    df = Counter()
    for chunk in chunks:
        tokens = _tokenize(chunk.get("search_text", "") + " " + chunk.get("text", ""))
        counts = Counter(tokens)
        token_docs.append(counts)
        for token in counts:
            df[token] += 1
    return token_docs, df


def filter_chunks_by_topic(chunks, query):
    topics = detect_query_topics(query)
    if not topics:
        return chunks, topics
    filtered = [c for c in chunks if set(c.get("tags", [])) & set(topics)]
    return filtered, topics


def search_chunks(graph, query, product_filter=None, top_k=8, require_topic_match=True):
    expanded_query = expand_policy_query(query)
    chunks = graph.get("chunks", [])
    query_topics = detect_query_topics(query)
    if product_filter and query_topics:
        product_topics = detect_product_topics(product_filter)
        if product_topics and not (set(product_topics) & set(query_topics)):
            return []

    if product_filter:
        chunks = [c for c in chunks if c.get("product_name") == product_filter]
    if not chunks:
        return []

    if require_topic_match:
        chunks, _topics = filter_chunks_by_topic(chunks, query)
        if not chunks:
            return []

    q_tokens = _tokenize(expanded_query)
    if not q_tokens:
        return []

    token_docs, df = build_search_index(chunks)
    total_docs = max(len(chunks), 1)
    q_counts = Counter(q_tokens)
    scored = []

    for idx, chunk in enumerate(chunks):
        score = 0.0
        doc_counts = token_docs[idx]
        for token, q_count in q_counts.items():
            if token not in doc_counts:
                continue
            idf = math.log((total_docs + 1) / (df[token] + 1)) + 1
            score += q_count * doc_counts[token] * idf
        if query_topics and set(chunk.get("tags", [])) & set(query_topics):
            score += 8.0
        if score:
            enriched = dict(chunk)
            enriched["_score"] = round(score, 4)
            scored.append((score, enriched))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


@lru_cache(maxsize=32)
def _extract_pdf_pages(local_file):
    path = ROOT / local_file
    if not path.exists():
        return []
    reader = PdfReader(str(path))
    pages = []
    for idx, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            pages.append((idx, text))
    return pages


def search_product_pdf_pages(graph, query, product_filter=None, top_k=5):
    if not product_filter:
        return []
    product = next(
        (item for item in graph.get("products", []) if item.get("product_name") == product_filter),
        None,
    )
    if not product:
        return []

    expanded_query = expand_policy_query(query)
    q_tokens = _tokenize(expanded_query)
    if not q_tokens:
        return []

    scored = []
    for doc in product.get("docs", []):
        doc_code = doc.get("doc_type_code")
        if doc_code != "P":
            continue
        for page_num, text in _extract_pdf_pages(doc.get("local_file", "")):
            page_tokens = _tokenize(text)
            if not page_tokens:
                continue
            counts = Counter(page_tokens)
            score = 0
            for token in q_tokens:
                if token in counts:
                    score += counts[token]
            if "감액기간" in str(query):
                if "감액" in text:
                    score += 60
                elif "50%" in text or "50％" in text:
                    score += 5
            if "면책기간" in str(query) and ("90" in text or "지급하지" in text):
                score += 15
            if score <= 0:
                continue
            scored.append(
                (
                    score,
                    {
                        "chunk_id": f"pdf:{doc.get('doc_id')}:{page_num}",
                        "product_name": product_filter,
                        "doc_type_name": DOC_TYPE_LABELS.get(doc_code, doc.get("doc_type_name", "")),
                        "page": page_num,
                        "tags": detect_query_topics(query),
                        "text": text[:2200],
                        "search_text": text,
                        "pdf_url": doc.get("pdf_url", ""),
                        "local_file": doc.get("local_file", ""),
                        "_score": round(score, 4),
                    },
                )
            )

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def get_related_graph(graph, chunks):
    chunk_ids = {c.get("chunk_id") for c in chunks}
    nodes_by_id = {n.get("id"): n for n in graph.get("nodes", [])}
    related_node_ids = set()
    for edge in graph.get("edges", []):
        if edge.get("source") in chunk_ids:
            related_node_ids.add(edge.get("target"))
        if edge.get("target") in chunk_ids:
            related_node_ids.add(edge.get("source"))

    product_names = {c.get("product_name") for c in chunks}
    product_nodes = [
        node
        for node in graph.get("nodes", [])
        if node.get("type") == "product" and node.get("label") in product_names
    ]
    related_nodes = [nodes_by_id[nid] for nid in related_node_ids if nid in nodes_by_id]
    return product_nodes + related_nodes


def products_dataframe(graph):
    return pd.DataFrame(graph.get("products", []))
