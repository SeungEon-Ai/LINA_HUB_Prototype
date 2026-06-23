import re

from openai import OpenAI


SYSTEM_PROMPT = """
당신은 라이나생명 보험상품 약관을 쉬운 말로 설명하는 약관 설명 AI입니다.
모든 답변은 존댓말로 작성합니다.

가장 중요한 원칙:
사용자는 "조건이 있다"는 말을 들으려고 질문하는 것이 아니라, 그 조건이 정확히 무엇인지 알고 싶어서 질문합니다.
따라서 "특정 조건", "특정 원인", "약관에서 정한 조건", "조건을 충족해야 합니다"처럼 모호한 말로 끝내면 안 됩니다.
조건이라는 말을 쓰는 순간, 바로 뒤에 그 조건의 실제 내용을 풀어서 써야 합니다.

예를 들어 나쁜 답변은 다음과 같습니다.
"특정 원인에 의해 발생해야 합니다."
"약관에서 정한 조건에 부합해야 합니다."
"특정 조건을 충족해야 보장됩니다."

좋은 답변은 다음과 같습니다.
"이 약관 근거에서는 임플란트가 모든 경우에 보장되는 것이 아니라, 영구치 발거치료와 관련된 경우를 중심으로 설명됩니다. 즉 단순 교체나 미용 목적이 아니라, 약관에서 보장 대상으로 보는 치아 치료 사유가 먼저 있어야 합니다."

규칙:
1. 약관 근거 안에 있는 숫자, 기간, 비율, 원인, 진단명, 치료명, 보장 한도, 제외사항은 가능한 한 그대로 가져와 설명합니다.
2. 약관 근거 안에 정확한 조건이 있으면 절대 "특정 조건"이라고 뭉뚱그리지 말고, 조건 내용을 이름 붙여 설명합니다.
3. 약관 근거 안에서 조건이 충분히 보이지 않으면 "조건을 알 수 없습니다"라고만 하지 말고, 확인된 근거와 확인이 필요한 항목을 분리해서 말합니다.
4. 보험 가입을 권유하지 않습니다.
5. Markdown 굵게 표시용 별표(**)를 사용하지 않습니다.
6. 참고한 약관 근거 문장은 답변 첫 줄에 쓰지 않습니다. 필요한 경우 마지막에 "아래 참고한 약관 근거 보기에서 확인해 주세요."라고만 말합니다.
""".strip()


FORBIDDEN_VAGUE_PATTERNS = [
    "특정 조건",
    "특정 원인",
    "약관에서 정한 조건",
    "약관상 조건",
    "조건에 부합",
    "조건을 충족",
]


def _format_history(history):
    if not history:
        return "이전 대화 없음"
    lines = []
    for item in history[-6:]:
        role = "사용자" if item.get("role") == "user" else "AI"
        content = re.sub(r"\s+", " ", str(item.get("content", ""))).strip()
        lines.append(f"{role}: {content[:500]}")
    return "\n".join(lines)


def _trim_text(text, limit=1500):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _compact_terms_from_chunks(chunks):
    terms = []
    keywords = [
        "면책기간",
        "감액기간",
        "보장개시일",
        "보험금",
        "지급",
        "지급하지",
        "제외",
        "한도",
        "임플란트",
        "영구치",
        "발거",
        "충전",
        "크라운",
        "암",
        "진단",
        "수술",
        "입원",
        "간병",
        "치매",
    ]
    for chunk in chunks[:7]:
        text = str(chunk.get("text", ""))
        for keyword in keywords:
            if keyword in text and keyword not in terms:
                terms.append(keyword)
    return ", ".join(terms[:16]) or "없음"


def _build_context_blocks(chunks):
    context_blocks = []
    for i, chunk in enumerate(chunks[:8], start=1):
        context_blocks.append(
            f"[약관 근거 {i}]\n"
            f"상품명: {chunk.get('product_name')}\n"
            f"문서: {chunk.get('doc_type_name')} / p.{chunk.get('page')}\n"
            f"분류 태그: {', '.join(chunk.get('tags', []))}\n"
            f"근거 내용:\n{_trim_text(chunk.get('text'), 1800)}"
        )
    return "\n\n".join(context_blocks)


def answer_with_gpt(api_key, question, chunks, related_nodes, history=None, product_filter=None):
    if not api_key or not chunks:
        return None

    graph_lines = []
    for node in related_nodes[:25]:
        graph_lines.append(f"- {node.get('type')}: {node.get('label')}")

    user_prompt = f"""
현재 선택 상품:
{product_filter or "전체 상품"}

이전 대화:
{_format_history(history)}

사용자 질문:
{question}

관련 그래프 노드:
{chr(10).join(graph_lines) if graph_lines else "관련 노드 없음"}

근거에서 보이는 핵심 단어:
{_compact_terms_from_chunks(chunks)}

약관 근거:
{_build_context_blocks(chunks)}

답변 작성 지시:
1. 사용자가 물은 핵심 질문에 먼저 답하세요.
2. "특정 조건", "특정 원인", "약관에서 정한 조건", "조건에 부합" 같은 표현은 쓰지 마세요.
3. 만약 조건을 설명해야 한다면 아래처럼 반드시 실제 조건명과 내용을 같이 쓰세요.
   - 보장되는 치료/상황:
   - 보장되지 않을 수 있는 경우:
   - 기간/비율/한도:
   - 사용자가 확인해야 할 것:
4. 약관 근거에 임플란트, 영구치, 발거, 충전, 크라운, 암 진단, 면책기간, 감액기간 같은 단어가 있으면 그 단어를 쉬운 말로 풀어 설명하세요.
5. "특정 원인"이라고 말하지 말고, 근거에 보이는 원인이 있으면 "예: 치아우식증, 치주질환, 재해, 영구치 발거처럼 약관 근거에 나온 원인"처럼 구체화하세요.
6. 근거에 없는 내용을 만들어내지 마세요. 다만 근거가 불완전하면 "이 근거에서 확인되는 부분"과 "추가로 확인해야 하는 부분"을 나눠 말하세요.
7. 답변은 너무 짧게 축약하지 말고, 사용자가 다음 행동을 판단할 수 있을 정도로 자세히 설명하세요.
8. 별표(**)를 쓰지 마세요.

권장 답변 형식:
1. 결론
질문에 대한 답을 바로 설명합니다. 단, "조건이 필요하다"로 끝내지 말고 어떤 조건인지 풀어 씁니다.

2. 약관 근거에서 확인되는 내용
기간, 비율, 보장 대상, 보장 제외, 한도, 치료명, 진단명 등을 항목별로 정리합니다.

3. 쉽게 말하면
사용자가 실제 상황에 대입해서 이해할 수 있게 예시형 문장으로 설명합니다.

4. 확인할 점
청구 전 확인할 서류, 치료 시점, 진단명, 보장 한도, 면책/감액기간 등을 정리합니다.
""".strip()

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=3200,
    )
    answer = response.choices[0].message.content.strip().replace("**", "")
    return _soften_vague_phrases(answer)


def _soften_vague_phrases(text):
    cleaned = str(text or "").replace("**", "")
    for phrase in FORBIDDEN_VAGUE_PATTERNS:
        cleaned = cleaned.replace(phrase, "구체적인 약관 요건")
    return cleaned


def fallback_answer(question, chunks, product_filter=None):
    if not chunks:
        if product_filter:
            return (
                f"현재 선택한 상품은 `{product_filter}`입니다.\n\n"
                "선택한 상품 안에서는 질문과 직접 연결되는 약관 근거가 충분히 검색되지 않았습니다. "
                "이 경우 답을 억지로 만들기보다, 상품 범위를 `전체 상품`으로 바꾸거나 질문에 상품명·보장명·치료명을 조금 더 구체적으로 넣어 다시 묻는 편이 안전합니다."
            )
        return (
            "질문과 바로 연결되는 약관 내용을 찾지 못했습니다.\n\n"
            "상품명, 보장명, 질병명, 치료명처럼 핵심 단어를 조금 더 구체적으로 입력해 주세요."
        )

    top = chunks[0]
    tags = ", ".join(top.get("tags", [])) or "관련 조항"
    preview = _trim_text(top.get("text", ""), 1100)

    return (
        f"`{tags}` 관련 약관 내용을 찾았습니다.\n\n"
        f"가장 가까운 근거는 `{top.get('product_name')}`의 `{top.get('doc_type_name')}` p.{top.get('page')}입니다.\n\n"
        "이 근거에서 확인되는 핵심 내용은 아래와 같습니다.\n"
        f"{preview}\n\n"
        "현재는 약관 근거 문장을 중심으로 보여드렸습니다. "
        "관련 상품명, 보장명, 치료명을 더 구체적으로 입력하면 조건과 예외를 더 좁혀서 확인할 수 있습니다."
    )
