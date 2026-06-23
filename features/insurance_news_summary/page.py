import base64
import html
import json
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
import streamlit as st
from openai import OpenAI

from features.local_secrets import get_openai_api_key
from features.shared_header import render_feature_intro_card

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"
NAVER_NEWS_SEARCH = "https://search.naver.com/search.naver"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

NEWS_LIMIT = 5
FETCH_POOL_SIZE = 20
DEFAULT_QUERY = "\ubcf4\ud5d8"
SOURCE_ALL = "\uc804\uccb4"
SORT_TITLE = "\uc81c\ubaa9\uc21c"
SOURCE_OPTIONS = [SOURCE_ALL, "Google", "Naver"]
SORT_OPTIONS = ["\ucd5c\uc2e0\uc21c", SORT_TITLE]
SUMMARY_MODEL = "gpt-4o-mini"
SUMMARY_CHUNK_SIZE = 5
SUMMARY_WORKERS = 3
ITEM_SUMMARY_WORKERS = 5
NEWS_LOGIC_VERSION = "importance_v6"
PERSIST_CACHE_PATH = Path.home() / "Documents" / "\ub77c\uc774\ub098\uc0dd\uba85" / "insurance_news_summary_cache.json"
BANNER_IMAGE_PATH = Path(__file__).resolve().parents[2] / "assets" / "insurance_news_summary_banner.png"
PRIORITY_QUERIES = [
    "\ubcf4\ud5d8 \uc190\ud574\uc728",
    "\uc190\ud574\ubcf4\ud5d8 \uc190\ud574\uc728",
    "\uc2e4\uc190\ubcf4\ud5d8",
    "\ubcf4\ud5d8\uc0ac\uae30",
    "\uae08\uac10\uc6d0 \ubcf4\ud5d8",
    "\uc0dd\uba85\ubcf4\ud5d8",
    "\ubcf4\ud5d8 \uc18c\ube44\uc790",
]
IMPORTANT_KEYWORDS = {
    "\uc190\ud574\uc728": 16,
    "\uc801\uc790": 13,
    "\uc2e4\uc190": 12,
    "\uc2e4\uc190\ubcf4\ud5d8": 14,
    "\ubcf4\ud5d8\uc0ac\uae30": 14,
    "\uae08\uac10\uc6d0": 11,
    "\ubd84\uc7c1": 10,
    "\ubbfc\uc6d0": 10,
    "\ubcf4\ud5d8\uae08": 9,
    "\uccad\uad6c": 9,
    "\uc790\ub3d9\ucc28\ubcf4\ud5d8": 9,
    "\uc190\ud574\ubcf4\ud5d8": 8,
    "\uc0dd\uba85\ubcf4\ud5d8": 7,
    "\uac74\uc804\uc131": 7,
    "\uaddc\uc81c": 7,
    "\uac1c\uc120": 6,
    "\uc778\uc0c1": 6,
    "\ub9cc\uae30": 6,
}
LOW_VALUE_KEYWORDS = {
    "\ucd9c\uc2dc": 8,
    "\ud504\ub85c\ubaa8\uc158": 8,
    "\uc774\ubca4\ud2b8": 8,
    "\ud611\uc57d": 5,
    "\ucea0\ud398\uc778": 5,
    "\uccad\ub144": 4,
}
TITLE_STOP_WORDS = {
    "\ubcf4\ud5d8",
    "\ub274\uc2a4",
    "\uae30\uc0ac",
    "\ucd9c\uc2dc",
    "\uad00\ub828",
    "\uc9c0\uc18d",
    "\ub300\ube44",
    "\uae08\uc735",
    "\uc18c\ube44\uc790",
    "\ub3d9\uc591\uc0dd\uba85",
    "\uc6b0\ub9ac",
    "won",
    "\uccad\ub144",
    "\ubbf8\ub798",
    "\uc9c0\uc6d0",
    "\ubcf4\uc7a5",
}


def _strip_tags(value):
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def _image_data_url(path):
    try:
        data = Path(path).read_bytes()
    except Exception:
        return ""
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def _format_date(value):
    if not value:
        return ""
    try:
        parsed = parsedate_to_datetime(value)
    except Exception:
        return str(value)[:16]
    return parsed.strftime("%Y-%m-%d %H:%M")


def _google_actual_link(link):
    parsed = urlparse(str(link or ""))
    query = parse_qs(parsed.query)
    for key in ("url", "q"):
        if query.get(key):
            return query[key][0]
    return str(link or "")


@st.cache_data(ttl=600, show_spinner=False)
def _fetch_google_news(query, limit):
    params = {
        "q": f"{query} \ubcf4\ud5d8 OR \uc0dd\uba85\ubcf4\ud5d8 OR \uc190\ud574\ubcf4\ud5d8",
        "hl": "ko",
        "gl": "KR",
        "ceid": "KR:ko",
    }
    response = requests.get(
        GOOGLE_NEWS_RSS,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=12,
    )
    response.raise_for_status()
    root = ET.fromstring(response.content)
    items = []
    for item in root.findall("./channel/item")[:limit]:
        source_node = item.find("source")
        items.append(
            {
                "platform": "Google",
                "source": _strip_tags(source_node.text if source_node is not None else "Google News"),
                "title": _strip_tags(item.findtext("title")),
                "summary": _strip_tags(item.findtext("description")),
                "link": _google_actual_link(item.findtext("link")),
                "published": _format_date(item.findtext("pubDate")),
            }
        )
    return items


@st.cache_data(ttl=600, show_spinner=False)
def _fetch_naver_news(query, limit):
    params = {"where": "news", "query": query, "sm": "tab_opt", "sort": "1"}
    response = requests.get(
        NAVER_NEWS_SEARCH,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=12,
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    text = response.text

    if BeautifulSoup is not None:
        soup = BeautifulSoup(text, "html.parser")
        items = []
        for anchor in soup.select("a.news_tit")[:limit]:
            title = _strip_tags(anchor.get("title") or anchor.get_text(" ", strip=True))
            link = html.unescape(anchor.get("href") or "")
            parent = anchor
            for _ in range(5):
                if parent and parent.select_one("a.info.press, span.info.press, a.press"):
                    break
                parent = parent.parent if parent else None
            press_node = parent.select_one("a.info.press, span.info.press, a.press") if parent else None
            desc_node = parent.select_one("a.api_txt_lines, div.news_dsc, div.dsc_wrap") if parent else None
            items.append(
                {
                    "platform": "Naver",
                    "source": _strip_tags(press_node.get_text(" ", strip=True)) if press_node else "Naver News",
                    "title": title,
                    "summary": _strip_tags(desc_node.get_text(" ", strip=True)) if desc_node else "",
                    "link": link,
                    "published": "",
                }
            )
        if items:
            return items

    card_pattern = re.compile(
        r'<a[^>]+class="[^"]*news_tit[^"]*"[^>]+href="([^"]+)"[^>]*title="([^"]+)"[^>]*>.*?</a>',
        re.S,
    )
    info_pattern = re.compile(r'<a[^>]+class="[^"]*info press[^"]*"[^>]*>(.*?)</a>', re.S)
    desc_pattern = re.compile(r'<a[^>]+class="[^"]*api_txt_lines[^"]*"[^>]*>(.*?)</a>', re.S)
    cards = card_pattern.findall(text)
    presses = info_pattern.findall(text)
    descs = desc_pattern.findall(text)

    items = []
    for idx, (link, title) in enumerate(cards[:limit]):
        items.append(
            {
                "platform": "Naver",
                "source": _strip_tags(presses[idx]) if idx < len(presses) else "Naver News",
                "title": _strip_tags(title),
                "summary": _strip_tags(descs[idx]) if idx < len(descs) else "",
                "link": html.unescape(link),
                "published": "",
            }
        )
    return items


def _dedupe(items):
    unique = []
    for item in items:
        key = _item_key(item)
        if not key:
            continue
        if any(_is_duplicate_topic(item, existing) for existing in unique):
            continue
        unique.append(item)
    return unique


def _interleave(first, second):
    mixed = []
    max_len = max(len(first), len(second))
    for index in range(max_len):
        if index < len(first):
            mixed.append(first[index])
        if index < len(second):
            mixed.append(second[index])
    return mixed


def _item_key(item):
    link = str(item.get("link") or "").strip()
    title = re.sub(r"\W+", "", _normalize_title(item.get("title", "")))[:110]
    return title or link


def _normalize_title(title):
    text = _strip_tags(title).lower()
    text = re.sub(r"\s+-\s+[^-]+$", "", text)
    text = text.replace("\u8eca", "\uc790\ub3d9\ucc28")
    text = text.replace("\ucc28\ubcf4\ud5d8", "\uc790\ub3d9\ucc28\ubcf4\ud5d8")
    text = text.replace("\ucc28\ubcf4", "\uc790\ub3d9\ucc28\ubcf4\ud5d8")
    text = text.replace("\uc790\ubcf4", "\uc790\ub3d9\ucc28\ubcf4\ud5d8")
    text = text.replace("\uc190\ubcf4", "\uc190\ud574\ubcf4\ud5d8")
    text = text.replace("\uc0dd\ubcf4", "\uc0dd\uba85\ubcf4\ud5d8")
    text = re.sub(r"[^\w\uac00-\ud7a3]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _combined_text(item):
    return _normalize_title(f"{item.get('title', '')} {item.get('summary', '')}")


def _issue_family(text):
    families = []
    if any(keyword in text for keyword in ("\uc790\ub3d9\ucc28\ubcf4\ud5d8", "\uc790\ub3d9\ucc28")) and "\uc190\ud574\uc728" in text:
        families.append("auto_loss_ratio")
    if "\uc2e4\uc190" in text and any(keyword in text for keyword in ("\uc190\ud574\uc728", "\uc801\uc790", "\uc778\uc0c1")):
        families.append("medical_indemnity")
    if "\ubcf4\ud5d8\uc0ac\uae30" in text:
        families.append("insurance_fraud")
    if "\uc694\uc591\ubcd1\uc6d0" in text and any(
        keyword in text
        for keyword in ("\uc2e4\uc190", "\ud398\uc774\ubc31", "\uc9c4\ub8cc\uae30\ub85d", "\uc870\uc791", "\ubd88\ubc95", "\ubcf4\ud5d8\uc0ac\uae30")
    ):
        families.append("nursing_hospital_fraud")
    if "\uae08\uac10\uc6d0" in text or "\ubd84\uc7c1" in text or "\ubbfc\uc6d0" in text:
        families.append("regulator_consumer")
    if "\ubcf4\ud5d8\uae08" in text and "\uccad\uad6c" in text:
        families.append("claim_payment")
    return set(families)


def _number_buckets(text):
    buckets = set()
    for raw in re.findall(r"\d+(?:\.\d+)?", text):
        try:
            value = float(raw)
        except ValueError:
            continue
        if 50 <= value <= 150:
            buckets.add(("percent", round(value / 5) * 5))
        elif 1000 <= value <= 9999:
            buckets.add(("year", int(value)))
    return buckets


def _topic_signature(text):
    family = _issue_family(text)
    if "auto_loss_ratio" in family:
        return "auto_loss_ratio"
    if "medical_indemnity" in family:
        return "medical_indemnity"
    if "insurance_fraud" in family:
        return "insurance_fraud"
    if "nursing_hospital_fraud" in family:
        return "nursing_hospital_fraud"
    if "regulator_consumer" in family:
        return "regulator_consumer"
    if "claim_payment" in family:
        return "claim_payment"
    return ""


def _title_tokens(title):
    text = _normalize_title(title)
    tokens = set()
    for token in text.split():
        if len(token) < 2 or token in TITLE_STOP_WORDS:
            continue
        tokens.add(token)
    return tokens


def _is_duplicate_topic(first, second):
    first_link = str(first.get("link") or "").strip()
    second_link = str(second.get("link") or "").strip()
    if first_link and second_link and first_link == second_link:
        return True

    first_text = _combined_text(first)
    second_text = _combined_text(second)
    first_signature = _topic_signature(first_text)
    second_signature = _topic_signature(second_text)
    if first_signature and first_signature == second_signature:
        return True

    first_family = _issue_family(first_text)
    second_family = _issue_family(second_text)
    if first_family and second_family and first_family & second_family:
        first_numbers = _number_buckets(first_text)
        second_numbers = _number_buckets(second_text)
        if not first_numbers or not second_numbers or first_numbers & second_numbers:
            return True

    first_tokens = _title_tokens(first.get("title", ""))
    second_tokens = _title_tokens(second.get("title", ""))
    if not first_tokens or not second_tokens:
        return False
    common = first_tokens & second_tokens
    overlap = len(common) / max(1, min(len(first_tokens), len(second_tokens)))
    if len(common) >= 2 and overlap >= 0.46:
        return True

    first_core = {token for token in first_tokens if token not in TITLE_STOP_WORDS}
    second_core = {token for token in second_tokens if token not in TITLE_STOP_WORDS}
    core_common = first_core & second_core
    return len(core_common) >= 2 and bool(first_family & second_family)


def _news_importance_score(item):
    combined = _combined_text(item)
    score = 0
    for keyword, weight in IMPORTANT_KEYWORDS.items():
        if keyword in combined:
            score += weight
    for keyword, penalty in LOW_VALUE_KEYWORDS.items():
        if keyword in combined:
            score -= penalty
    if item.get("platform") == "Naver":
        score += 2
    if item.get("priority") in ("\ubcf4\ud5d8 \uc190\ud574\uc728", "\uc190\ud574\ubcf4\ud5d8 \uc190\ud574\uc728"):
        score += 6
    if item.get("priority") == "\uc0dd\uba85\ubcf4\ud5d8":
        score += 1
    return score


def _select_important_news(items, limit):
    ranked = sorted(items, key=_news_importance_score, reverse=True)
    selected = []
    for item in ranked:
        if any(_is_duplicate_topic(item, existing) for existing in selected):
            continue
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected


def _select_balanced_news(naver_items, google_items, limit):
    selected = []
    for item in _select_important_news(naver_items, min(2, limit)):
        selected.append(item)

    for item in _select_important_news(_dedupe(google_items + naver_items), limit * 2):
        if any(_is_duplicate_topic(item, existing) for existing in selected):
            continue
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected[:limit]


def _filter_unseen(items, seen_keys):
    filtered = []
    for item in items:
        key = _item_key(item)
        if not key or key in seen_keys:
            continue
        if any(_is_duplicate_topic(item, existing) for existing in filtered):
            continue
        filtered.append(item)
    return filtered


def _priority_query(base_query, priority):
    base = (base_query or DEFAULT_QUERY).strip()
    if not base or base == DEFAULT_QUERY:
        return priority
    return f"{base} {priority}"


def _fetch_priority_source(fetcher, base_query):
    items = []
    for priority in PRIORITY_QUERIES:
        try:
            for item in fetcher(_priority_query(base_query, priority), FETCH_POOL_SIZE):
                item["priority"] = priority
                items.append(item)
        except Exception:
            raise
    return _dedupe(items)


def _fetch_news(query, source, seen_keys=None):
    errors = []
    google_items = []
    naver_items = []
    seen_keys = seen_keys or set()

    if source in (SOURCE_ALL, "Google"):
        try:
            google_items = _fetch_priority_source(_fetch_google_news, query)
        except Exception as error:
            errors.append(f"Google \ub274\uc2a4 \uc218\uc9d1 \uc2e4\ud328: {error}")

    if source in (SOURCE_ALL, "Naver"):
        try:
            naver_items = _fetch_priority_source(_fetch_naver_news, query)
        except Exception as error:
            errors.append(f"Naver \ub274\uc2a4 \uc218\uc9d1 \uc2e4\ud328: {error}")

    google_items = _filter_unseen(_dedupe(google_items), seen_keys)
    naver_items = _filter_unseen(_dedupe(naver_items), seen_keys)

    if source == SOURCE_ALL:
        return _select_balanced_news(naver_items, google_items, NEWS_LIMIT), errors

    return _select_important_news(_dedupe(google_items or naver_items), NEWS_LIMIT), errors


def _fallback_summary(news_items, query):
    if not news_items:
        return "\uc218\uc9d1\ub41c \ub274\uc2a4\uac00 \uc5c6\uc5b4 \uc694\uc57d\ud560 \ub0b4\uc6a9\uc774 \uc5c6\uc2b5\ub2c8\ub2e4."

    titles = [item["title"] for item in news_items[:5]]
    sources = sorted({item["source"] for item in news_items[:6] if item.get("source")})
    return (
        f"'{query}' \uad00\ub828 \ubcf4\ud5d8 \ub274\uc2a4 {len(news_items)}\uac74\uc744 \ud655\uc778\ud588\uc2b5\ub2c8\ub2e4. "
        f"\uc8fc\uc694 \ud750\ub984\uc740 {', '.join(titles[:3])} \uac19\uc740 \uc774\uc288\ub85c \ubcf4\uc785\ub2c8\ub2e4. "
        f"\ud655\uc778\ub41c \ucd9c\ucc98\ub294 {', '.join(sources[:4]) or '\ub274\uc2a4 \uac80\uc0c9 \uacb0\uacfc'}\uc785\ub2c8\ub2e4. "
        "\uc0c1\uc138 \ud310\ub2e8\uc774 \ud544\uc694\ud55c \ub0b4\uc6a9\uc740 \uc6d0\ubb38 \uae30\uc0ac\uc5d0\uc11c \ub0a0\uc9dc\uc640 \ub9e5\ub77d\uc744 \ud568\uaed8 \ud655\uc778\ud574 \uc8fc\uc138\uc694."
    )


def _load_persisted_news(cache_key):
    try:
        if not PERSIST_CACHE_PATH.exists():
            return None
        data = json.loads(PERSIST_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None

    if data.get("logic_version") != NEWS_LOGIC_VERSION:
        return None
    if tuple(data.get("cache_key", [])) != tuple(cache_key):
        return None

    item_summaries = {}
    for key, value in (data.get("item_summaries") or {}).items():
        try:
            item_summaries[int(key)] = value
        except (TypeError, ValueError):
            continue

    return {
        "items": data.get("items") or [],
        "errors": data.get("errors") or [],
        "total_summary": data.get("total_summary") or "",
        "item_summaries": item_summaries,
        "seen_keys": set(data.get("seen_keys") or []),
    }


def _save_persisted_news(cache_key, news_items, errors, total_summary, item_summaries, seen_keys):
    try:
        PERSIST_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "logic_version": NEWS_LOGIC_VERSION,
            "cache_key": list(cache_key),
            "items": news_items,
            "errors": errors,
            "total_summary": total_summary,
            "item_summaries": {str(key): value for key, value in (item_summaries or {}).items()},
            "seen_keys": sorted(seen_keys),
        }
        PERSIST_CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _format_ai_text(text):
    if not text:
        return ""
    escaped = html.escape(str(text).strip())
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?m)^#{1,4}\s*(.+)$", r"<strong>\1</strong>", escaped)
    blocks = [block.strip() for block in re.split(r"\n\s*\n", escaped) if block.strip()]
    if not blocks:
        return escaped.replace("\n", "<br>")
    return "".join(f"<p>{block.replace(chr(10), '<br>')}</p>" for block in blocks)


def _chunk_items(items, size):
    return [items[index : index + size] for index in range(0, len(items), size)]


def _compact_news(items):
    return "\n".join(
        f"- [{item['platform']}/{item['source']}] {item['title']} / {item.get('summary', '')[:260]}"
        for item in items
    )


def _call_summary_model(api_key, messages, max_tokens):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=SUMMARY_MODEL,
        messages=messages,
        temperature=0.25,
        max_tokens=max_tokens,
    )
    return (response.choices[0].message.content or "").strip()


def _summarize_chunk(api_key, query, chunk, chunk_number):
    return _call_summary_model(
        api_key,
        [
            {
                "role": "system",
                "content": (
                    "Summarize only the provided Korean insurance-news batch in Korean. "
                    "Always use polite Korean honorific style ending with '-합니다', '-입니다', or '-주세요'. "
                    "Never use casual or plain endings. "
                    "Write a detailed batch summary, not a short one. "
                    "Use Markdown-style bold with **important words**. "
                    "Use clear line breaks and this structure: "
                    "**주요 이슈**, **소비자 영향**, **확인할 점**. "
                    "Ignore any malformed section labels above. "
                    "Use the exact Korean section labels **주요 이슈**, **소비자 영향**, **확인할 점**. "
                    "Do not add financial advice or unsupported claims."
                ),
            },
            {
                "role": "user",
                "content": f"Search query: {query}\nBatch: {chunk_number}\nNews:\n{_compact_news(chunk)}",
            },
        ],
        max_tokens=520,
    )


def _merge_summaries(api_key, query, partial_summaries):
    joined = "\n\n".join(
        f"[Summary {index + 1}]\n{summary}" for index, summary in enumerate(partial_summaries) if summary
    )
    if not joined:
        return ""
    return _call_summary_model(
        api_key,
        [
            {
                "role": "system",
                "content": (
                    "Merge the batch summaries into one Korean insurance-news briefing. "
                    "Always use polite Korean honorific style ending with '-합니다', '-입니다', or '-주세요'. "
                    "Never use casual or plain endings. "
                    "Make it much more detailed and readable. "
                    "Use Markdown-style bold with **important phrases**. "
                    "Use blank lines between sections. "
                    "Use this structure exactly: "
                    "**전체 흐름** / **주요 이슈** / **소비자가 확인할 점** / **기사별로 눈에 띄는 포인트**. "
                    "Ignore any malformed section labels above. "
                    "Use the exact Korean section labels **전체 흐름**, **주요 이슈**, **소비자가 확인할 점**, **기사별로 눈에 띄는 포인트**. "
                    "Override any malformed section instructions above. "
                    "Use exactly three sections only: **\uc804\uccb4 \ud750\ub984**, **\uc8fc\uc694 \uc774\uc288**, **\uae30\uc0ac\ubcc4 \ud3ec\uc778\ud2b8**. "
                    "Do not include any section named **\uc18c\ube44\uc790\uac00 \ud655\uc778\ud560 \uc810** or **\ud655\uc778\ud560 \uc810** in the total summary. "
                    "Do not mention years unless the year is explicitly included in the provided news title, date, or description. "
                    "Remove duplicated points, but do not over-compress the summary."
                ),
            },
            {"role": "user", "content": f"Search query: {query}\nBatch summaries:\n{joined}"},
        ],
        max_tokens=980,
    )


def _summarize_one_item(api_key, item):
    section_format = (
        "**\ub0b4\uc6a9**\n"
        "- 4~5\uc904\ub85c \uae30\uc0ac\uc758 \ud575\uc2ec \ub0b4\uc6a9\uc744 \uc790\uc138\ud558\uac8c \uc124\uba85\ud558\uc138\uc694.\n"
        "- \uae30\uc0ac \uc81c\ubaa9\uacfc \uc694\uc57d\ubb38\uc5d0\uc11c \ud655\uc778\ub418\ub294 \ub0b4\uc6a9\ub9cc \ub2e4\ub8e8\uc138\uc694.\n\n"
        "**\uc911\uc694 \ud3ec\uc778\ud2b8**\n"
        "- 2~3\uc904\ub85c \ubcf4\ud5d8 \uc2dc\uc7a5, \ubcf4\ud5d8\uc0ac, \uac00\uc785\uc790\uc5d0\uac8c \uc911\uc694\ud55c \uc774\uc720\ub97c \uc815\ub9ac\ud558\uc138\uc694.\n\n"
        "**\uc18c\ube44\uc790\uac00 \ud655\uc778\ud560 \uc810**\n"
        "- 2~3\uc904\ub85c \uc18c\ube44\uc790\uac00 \uc57d\uad00, \ubcf4\uc7a5, \uccad\uad6c, \ube44\uc6a9 \uce21\uba74\uc5d0\uc11c \ud655\uc778\ud560 \ub0b4\uc6a9\uc744 \uc815\ub9ac\ud558\uc138\uc694."
    )
    return _call_summary_model(
        api_key,
        [
            {
                "role": "system",
                "content": (
                    "Summarize this single Korean insurance-news item in Korean. "
                    "Always use polite Korean honorific style ending with '-합니다', '-입니다', or '-주세요'. "
                    "Never use casual or plain endings. "
                    "Write a much more detailed explanation than a normal short summary. "
                    "Use Markdown-style bold with **important phrases**. "
                    "Use clear line breaks and this structure exactly: "
                    "**무슨 내용인지** / **왜 중요한지** / **소비자가 확인할 점**. "
                    "Use 5 to 7 sentences total. Mention only confirmed content from the title and description. "
                    "Ignore any malformed section labels above. "
                    "Use the exact Korean section labels **무슨 내용인지**, **왜 중요한지**, **소비자가 확인할 점**. "
                    "Override any previous malformed labels. "
                    "Use exactly three sections with these exact Korean labels: "
                    "**\ub0b4\uc6a9**, **\uc911\uc694 \ud3ec\uc778\ud2b8**, **\uc18c\ube44\uc790\uac00 \ud655\uc778\ud560 \uc810**. "
                    "**\ub0b4\uc6a9** must be 4 to 5 lines, "
                    "**\uc911\uc694 \ud3ec\uc778\ud2b8** must be 2 to 3 lines, "
                    "and **\uc18c\ube44\uc790\uac00 \ud655\uc778\ud560 \uc810** must be 2 to 3 lines. "
                    "Do not use external knowledge. Do not mention years unless the year is explicitly included in the title, source date, or description. "
                    "If the title says only '\u0037\uc6d4\ubd80\ud130' without a year, write '\uae30\uc0ac\uc5d0\uc11c \uc5b8\uae09\ud55c 7\uc6d4\ubd80\ud130' and do not infer 2023 or any other year. "
                    "Avoid advice, predictions, or exaggeration."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Required output format:\n{section_format}\n\n"
                    f"Title: {item.get('title', '')}\n"
                    f"Source: {item.get('source', '')}\n"
                    f"Published date shown in card: {item.get('published', '') or 'not provided'}\n"
                    f"Description: {item.get('summary', '')[:720]}"
                ),
            },
        ],
        max_tokens=860,
    )


def _ai_summaries(news_items, query):
    api_key = get_openai_api_key()
    if not api_key or not news_items:
        return _fallback_summary(news_items, query), {}

    try:
        chunks = _chunk_items(news_items[:NEWS_LIMIT], SUMMARY_CHUNK_SIZE)
        partials = [None] * len(chunks)
        with ThreadPoolExecutor(max_workers=min(SUMMARY_WORKERS, len(chunks))) as executor:
            futures = {
                executor.submit(_summarize_chunk, api_key, query, chunk, index + 1): index
                for index, chunk in enumerate(chunks)
            }
            for future in as_completed(futures):
                partials[futures[future]] = future.result()
        total_summary = _merge_summaries(api_key, query, [summary for summary in partials if summary])
    except Exception:
        total_summary = _fallback_summary(news_items, query)

    item_summaries = {}
    try:
        with ThreadPoolExecutor(max_workers=min(ITEM_SUMMARY_WORKERS, len(news_items))) as executor:
            futures = {
                executor.submit(_summarize_one_item, api_key, item): index
                for index, item in enumerate(news_items[:NEWS_LIMIT])
            }
            for future in as_completed(futures):
                item_summaries[futures[future]] = future.result()
    except Exception:
        item_summaries = {}

    return total_summary or _fallback_summary(news_items, query), item_summaries


def _render_css():
    banner_url = _image_data_url(BANNER_IMAGE_PATH)
    st.markdown(
        """
        <style>
        .news-hero {
            width: 100%;
            max-width: 1160px;
            aspect-ratio: 2172 / 724;
            min-height: 0;
            margin: 0 auto 8px;
            border: 1px solid #ded7f4;
            border-radius: 24px;
            background: #ffffff url("__BANNER_URL__") center / contain no-repeat;
            box-shadow: 0 14px 34px rgba(15, 23, 42, .06);
            padding: 0;
            box-sizing: border-box;
            overflow: hidden;
            position: relative;
        }
        .news-hero h1,
        .news-hero p,
        .news-hero-badge {
            display: none;
        }
        .news-hero h1 {
            margin: 0 0 .65rem;
            color: #111827;
            font-size: 2.2rem;
            line-height: 1.16;
            letter-spacing: 0;
            font-weight: 950;
        }
        .news-hero h1 strong { color: #7468ec; font-weight: 950; }
        .news-hero p {
            max-width: 620px;
            margin: 0;
            color: #536276;
            font-size: .98rem;
            line-height: 1.55;
            font-weight: 700;
            word-break: keep-all;
        }
        .news-hero-badge {
            position: absolute;
            right: 2.2rem;
            bottom: 1.8rem;
            display: none;
            grid-template-columns: repeat(3, 58px);
            gap: .65rem;
        }
        .news-hero-badge span {
            width: 58px;
            height: 58px;
            border-radius: 18px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #ffffff;
            color: #7468ec;
            box-shadow: 0 12px 24px rgba(116, 104, 236, .15);
            font-size: 1.2rem;
            font-weight: 950;
        }
        .st-key-news_control_card,
        .news-summary-card,
        .news-list {
            width: 100%;
            max-width: 1160px;
            margin-left: auto;
            margin-right: auto;
            box-sizing: border-box;
        }
        .st-key-news_control_card {
            border: 1px solid #dfe7f1;
            border-radius: 18px;
            padding: 1rem;
            background: #fff;
            box-shadow: 0 10px 24px rgba(15, 23, 42, .04);
            margin-bottom: 16px;
        }
        .news-summary-card {
            border: 1px solid #ded7f4;
            border-radius: 20px;
            background: #f7f3ff;
            padding: 1.05rem 1.15rem;
            margin-bottom: 18px;
            color: #1f2937;
        }
        .news-summary-card h3 {
            margin: 0 0 .55rem;
            color: #111827;
            font-size: 1.05rem;
            font-weight: 950;
        }
        .news-summary-card p {
            margin: 0;
            color: #334155;
            line-height: 1.65;
            font-size: .9rem;
            white-space: pre-wrap;
            word-break: keep-all;
        }
        .news-list {
            display: grid;
            gap: 1.1rem;
        }
        .news-card-shell {
            border: 1px solid #dfe7f1;
            border-radius: 16px;
            background: #fff;
            padding: .95rem 1rem;
            box-shadow: 0 8px 20px rgba(15, 23, 42, .035);
            min-height: 178px;
        }
        .news-item-top {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: .45rem;
            margin-bottom: .45rem;
            color: #738095;
            font-size: .72rem;
            font-weight: 850;
        }
        .news-platform {
            border-radius: 999px;
            background: #fff8e6;
            color: #8a5a00;
            padding: .16rem .5rem;
        }
        .news-title-link {
            color: #111827 !important;
            text-decoration: none !important;
            font-size: .98rem;
            line-height: 1.35;
            font-weight: 950;
        }
        .news-desc {
            margin: .45rem 0 .55rem;
            color: #52637a;
            font-size: .82rem;
            line-height: 1.48;
            word-break: keep-all;
        }
        .news-ai-summary {
            color: #334155;
            font-size: .82rem;
            line-height: 1.58;
            word-break: keep-all;
        }
        .news-ai-formatted p,
        .news-ai-summary p {
            margin: 0 0 .62rem;
        }
        .news-ai-formatted p:last-child,
        .news-ai-summary p:last-child {
            margin-bottom: 0;
        }
        .news-ai-formatted strong,
        .news-ai-summary strong {
            color: #111827;
            font-weight: 950;
        }
        .st-key-news_list_container [data-testid="stVerticalBlock"] {
            gap: 1.1rem;
        }
        </style>
        """.replace("__BANNER_URL__", banner_url),
        unsafe_allow_html=True,
    )


def _render_news_card(item, item_summary):
    title = html.escape(item["title"])
    source = html.escape(item.get("source", "\ub274\uc2a4"))
    platform = html.escape(item.get("platform", ""))
    link = html.escape(item.get("link", ""), quote=True)
    summary = html.escape(item.get("summary", ""))
    published = html.escape(item.get("published", ""))
    date_html = f"<span>{published}</span>" if published else ""
    summary_html = f'<p class="news-desc">{summary}</p>' if summary else ""

    with st.container(border=True):
        st.markdown(
            f'<div class="news-item-top"><span class="news-platform">{platform}</span><span>{source}</span>{date_html}</div><a class="news-title-link" href="{link}" target="_blank" rel="noopener noreferrer">{title}</a>{summary_html}',
            unsafe_allow_html=True,
        )
        with st.expander("\ub274\uc2a4\ubcc4 AI \uc694\uc57d"):
            st.markdown(
                f'<div class="news-ai-summary">{_format_ai_text(item_summary or "\uc694\uc57d\uc744 \ubd88\ub7ec\uc624\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4.")}</div>',
                unsafe_allow_html=True,
            )


def _render_news_list(items, item_summaries):
    if not items:
        st.markdown(
            '<div class="news-list"><div class="news-card-shell">\uc218\uc9d1\ub41c \ub274\uc2a4\uac00 \uc5c6\uc2b5\ub2c8\ub2e4.</div></div>',
            unsafe_allow_html=True,
        )
        return

    with st.container(key="news_list_container"):
        for index, item in enumerate(items):
            _render_news_card(item, item_summaries.get(index, ""))


def render():
    _render_css()
    st.markdown(
        """
        <section class="news-hero">
            <h1>\ubcf4\ud5d8\uc774\uc288<br><strong>\ud55c\uc785 AI</strong></h1>
            <p>\ub124\uc774\ubc84\uc640 \uad6c\uae00\uc5d0\uc11c \ubcf4\ud5d8 \uad00\ub828 \ub274\uc2a4\ub97c \ubaa8\uc544 \ud575\uc2ec \ud750\ub984\uc744 \uc9e7\uac8c \uc815\ub9ac\ud569\ub2c8\ub2e4. \ub274\uc2a4\ub294 \ud56d\uc0c1 5\uac1c\ub97c \ubcf4\uc5ec\uc8fc\uace0, \uc804\uccb4 \uc694\uc57d\uacfc \ub274\uc2a4\ubcc4 \uc694\uc57d\uc744 \ud568\uaed8 \uc81c\uacf5\ud569\ub2c8\ub2e4.</p>
            <div class="news-hero-badge"><span>\uc774\uc288</span><span>\ud55c\uc785</span><span>AI</span></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    render_feature_intro_card("보험 관련 뉴스를 짧고 쉽게 살펴보세요.")

    with st.container(key="news_control_card"):
        col1, col2, col3, col4 = st.columns([2.2, 1, 1, 0.8])
        with col1:
            query = st.text_input(
                "\uac80\uc0c9\uc5b4",
                value=DEFAULT_QUERY,
                placeholder="\uc608: \ubcf4\ud5d8\uae08 \uccad\uad6c, \uc2e4\uc190\ubcf4\ud5d8, \uce58\uc544\ubcf4\ud5d8",
            )
        with col2:
            source = st.selectbox("\ub274\uc2a4 \ucd9c\ucc98", SOURCE_OPTIONS, index=0)
        with col3:
            sort_label = st.selectbox("\uc815\ub82c", SORT_OPTIONS, index=0)
        with col4:
            st.markdown("<div style='height: 1.82rem'></div>", unsafe_allow_html=True)
            run = st.button("\ub274\uc2a4 \uac00\uc838\uc624\uae30", use_container_width=True)

    cache_key = (query.strip() or DEFAULT_QUERY, source, sort_label)
    if run and "insurance_news_last_items" not in st.session_state:
        persisted = _load_persisted_news(cache_key)
        if persisted:
            st.session_state.insurance_news_last_key = cache_key
            st.session_state.insurance_news_last_items = persisted["items"]
            st.session_state.insurance_news_last_errors = persisted["errors"]
            st.session_state.insurance_news_last_summary = persisted["total_summary"]
            st.session_state.insurance_news_item_summaries = persisted["item_summaries"]
            st.session_state.insurance_news_seen_keys = sorted(persisted["seen_keys"])
            st.session_state.insurance_news_logic_version = NEWS_LOGIC_VERSION

    has_current_results = (
        "insurance_news_last_items" in st.session_state
        and st.session_state.get("insurance_news_last_key") == cache_key
        and st.session_state.get("insurance_news_logic_version") == NEWS_LOGIC_VERSION
    )
    should_fetch = run

    if not should_fetch and has_current_results:
        news_items = st.session_state.insurance_news_last_items
        errors = st.session_state.get("insurance_news_last_errors", [])
        total_summary = st.session_state.get("insurance_news_last_summary", "")
        item_summaries = st.session_state.get("insurance_news_item_summaries", {})
    elif should_fetch:
        with st.spinner("\ubcf4\ud5d8 \ub274\uc2a4\ub97c \uc218\uc9d1\ud558\uace0 \uc694\uc57d\ud558\uace0 \uc788\uc5b4\uc694."):
            seen_keys = set(st.session_state.get("insurance_news_seen_keys", [])) if run else set()
            news_items, errors = _fetch_news(query.strip() or DEFAULT_QUERY, source, seen_keys)
            if sort_label == SORT_TITLE:
                news_items = sorted(news_items, key=lambda item: item["title"])
            total_summary, item_summaries = _ai_summaries(news_items, query.strip() or DEFAULT_QUERY)
            seen_keys.update(_item_key(item) for item in news_items if _item_key(item))
            st.session_state.insurance_news_last_key = cache_key
            st.session_state.insurance_news_last_items = news_items
            st.session_state.insurance_news_last_errors = errors
            st.session_state.insurance_news_last_summary = total_summary
            st.session_state.insurance_news_item_summaries = item_summaries
            st.session_state.insurance_news_seen_keys = sorted(seen_keys)
            st.session_state.insurance_news_logic_version = NEWS_LOGIC_VERSION
            _save_persisted_news(cache_key, news_items, errors, total_summary, item_summaries, seen_keys)
    else:
        news_items = []
        errors = []
        total_summary = ""
        item_summaries = {}

    if errors:
        st.warning(" / ".join(errors))

    if news_items:
        st.markdown(
            f"""
            <section class="news-summary-card">
                <h3>AI \uc804\uccb4 \uc694\uc57d</h3>
                <div class="news-ai-formatted">{_format_ai_text(total_summary)}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        _render_news_list(news_items, item_summaries)
