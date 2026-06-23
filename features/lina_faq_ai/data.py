import json
import re
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "faq_qna.json"

_LINK_PATTERNS = [
    r"[▶▷>]\s*(?:PC|모바일)[^▶▷>。\n]*(?:클릭|바로가기|청구하러가기|신청하기|조회/?신청하기|변경하기)[^▶▷>。\n]*",
    r"아래(?:의)?\s*(?:링크|버튼)[^。\.\n]*(?:클릭|누르)[^。\.\n]*(?:있습니다|보세요|됩니다)?\.?",
    r"아래 링크를 클릭[^。\.\n]*(?:있습니다|보세요|됩니다)?\.?",
    r"링크를 클릭[^。\.\n]*(?:있습니다|보세요|됩니다)?\.?",
    r"바로가기\s*>?",
]



def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def strip_link_prompts(text: str) -> str:
    cleaned = str(text or "")
    # 원문 FAQ의 실제 링크는 크롤링 과정에서 사라지므로, 본문은 보존하고 바로가기 안내 조각만 제거합니다.
    for pattern in _LINK_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(
        r"\s*\[\d+\]\s*(?:홈페이지|모바일|PC)\s*채널?\s*[:：][^\[①②③④⑤⑥⑦⑧⑨⑩。\.\n]*",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s*\(\s*클릭\s*\)", "", cleaned)
    cleaned = re.sub(r"\s*\(?클릭\)?", "", cleaned)
    cleaned = re.sub(r"\s*▶\s*", " ", cleaned)
    cleaned = re.sub(r"\s*※\s*$", "", cleaned)
    return normalize(cleaned)


def format_answer(text: str) -> str:
    text = strip_link_prompts(text)
    text = re.sub(r"\s*([①②③④⑤⑥⑦⑧⑨⑩])\s*", r"\n\n\1 ", text)
    text = re.sub(r"\s*\[(\d+)\]\s*", r"\n\n[\1] ", text)
    text = re.sub(r"\s+(\d+)\.\s+", r"\n\n\1. ", text)
    text = re.sub(r"\s+-\s+", r"\n- ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


@lru_cache(maxsize=1)
def load_faq_data():
    if not DATA_PATH.exists():
        return {"source": "", "count": 0, "items": []}
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"source": "", "count": 0, "items": []}
    items = []
    for item in data.get("items", []):
        question = normalize(item.get("question"))
        answer = format_answer(item.get("answer"))
        if question and answer:
            items.append({"question": question, "answer": answer, "source_url": item.get("source_url", data.get("source", ""))})
    return {"source": data.get("source", ""), "count": len(items), "items": items}


def tokenize(text: str):
    text = normalize(text).lower()
    tokens = re.findall(r"[가-힣a-zA-Z0-9]{2,}", text)
    expanded = []
    for token in tokens:
        expanded.append(token)
        if len(token) >= 4 and re.search(r"[가-힣]", token):
            expanded.extend(token[i : i + 2] for i in range(len(token) - 1))
    return expanded


def search_faq(query: str, limit: int = 5):
    query = normalize(query)
    if not query:
        return []
    q_tokens = tokenize(query)
    q_set = set(q_tokens)
    scored = []
    for item in load_faq_data()["items"]:
        haystack = f"{item['question']} {item['answer']}"
        h_tokens = tokenize(haystack)
        h_set = set(h_tokens)
        overlap = len(q_set & h_set)
        exact_bonus = 6 if query in item["question"] else 0
        title_bonus = sum(2 for token in q_set if token in item["question"].lower())
        answer_bonus = sum(1 for token in q_set if token in item["answer"].lower())
        score = overlap * 3 + exact_bonus + title_bonus + answer_bonus
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item | {"score": score} for score, item in scored[:limit]]


def build_context(matches):
    if not matches:
        return "관련 FAQ를 찾지 못했습니다."
    blocks = []
    for index, item in enumerate(matches, 1):
        blocks.append(f"[{index}] 질문: {item['question']}\n답변: {item['answer']}")
    return "\n\n".join(blocks)
