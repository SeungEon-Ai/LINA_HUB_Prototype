from .config import MODEL_NAME
from .data import build_context
from features.local_secrets import get_openai_api_key

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


def get_api_key() -> str:
    return get_openai_api_key()


def fallback_answer(question: str, context_rows) -> str:
    if context_rows.empty:
        return "바로 설명할 수 있는 보험용어를 찾지 못했습니다. 핵심 용어만 짧게 입력해 주세요."

    row = context_rows.iloc[0]
    term = row.get("term_title", "") or row.get("term_ko", "")
    definition = row.get("best_definition", "")

    if definition:
        return f"{term}은(는) {definition}"

    return (
        f"{term}은(는) 보험계약이나 보장 내용을 이해할 때 참고하는 용어입니다. "
        "아직 자세한 설명이 준비되지 않았습니다."
    )


def answer(question: str, context_rows) -> str:
    api_key = get_api_key()
    if not api_key:
        return fallback_answer(question, context_rows)
    if OpenAI is None:
        return "openai 패키지가 설치되어 있지 않습니다. pip install openai 후 다시 실행해 주세요."

    client = OpenAI(api_key=api_key)
    context = build_context(context_rows)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 한국 보험 용어를 쉽게 설명하는 챗봇입니다. 모든 답변은 반드시 존댓말로 작성합니다. "
                        "반말 어미인 '~해', '~야', '~돼'를 쓰지 말고 '~합니다', '~입니다', '~됩니다', '~할 수 있습니다'처럼 작성합니다. "
                        "DB 근거를 우선 사용하되, 부족한 부분은 일반 보험 지식으로 보완합니다. "
                        "마크다운 굵게 표시(**), '쉬운 설명:', '분류:', '참고 출처:' 같은 라벨은 쓰지 않습니다. "
                        "출처 문장이나 참고한 DB 근거는 답변에 포함하지 않습니다. "
                        "사용자가 바로 이해할 수 있도록 자연스러운 문장 2~4개로 설명합니다."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"질문: {question}\n\n"
                        f"DB 검색 결과:\n{context}\n\n"
                        "위 근거를 바탕으로 존댓말 문장형으로 답변해 주세요. "
                        "굵게 표시, 쉬운 설명 라벨, 분류 라벨, 참고 출처는 쓰지 마세요."
                    ),
                },
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
    except Exception:
        return "설명을 불러오는 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."
