from .config import CONSULT_URL, FAQ_SOURCE_URL, MAX_CONTEXT_ITEMS, MODEL_NAME
from .data import build_context, search_faq
from features.local_secrets import get_openai_api_key

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


GENERAL_CONSULT_INFO = """
라이나생명 기본 상담 정보:
- 본사 주소: 서울특별시 종로구 삼봉로 48 (청진동 188) 라이나타워 라이나생명(주)
- 고객센터: 1588-0058, 평일 09:00~18:00
- 라이나생명 공식 홈페이지: www.lina.co.kr
- 라이나생명 다이렉트 공식 홈페이지: direct.lina.co.kr
- 개인 계약 조회, 보험금 지급 여부 확정, 서류 접수 상태 확인은 본인 확인이 필요하므로 공식 홈페이지 또는 고객센터에서 확인해야 합니다.
"""


def get_api_key() -> str:
    return get_openai_api_key()


def fallback_answer(question: str, matches):
    normalized = str(question or "")
    if not matches:
        if any(word in normalized for word in ["본사", "주소", "위치", "어디"]):
            return "라이나생명 본사는 서울특별시 종로구 삼봉로 48, 라이나타워에 있습니다. 방문이나 서류 접수처럼 정확한 안내가 필요한 경우에는 고객센터(1588-0058)로 한 번 더 확인해 주세요."
        if any(word in normalized for word in ["전화", "고객센터", "상담", "연락"]):
            return "라이나생명 고객센터는 1588-0058이며, 상담 시간은 평일 09:00~18:00입니다. 계약 조회나 접수 상태처럼 본인 확인이 필요한 내용은 고객센터 또는 공식 홈페이지에서 확인해 주세요."
        if any(word in normalized for word in ["홈페이지", "사이트", "다이렉트"]):
            return "라이나생명 공식 홈페이지는 www.lina.co.kr, 다이렉트 공식 홈페이지는 direct.lina.co.kr입니다. 보험금 청구, 계약 조회, 증명서 발급 같은 메뉴는 공식 홈페이지에서 확인하실 수 있습니다."

        return (
            "자주 묻는 질문에서 딱 맞는 항목은 찾지 못했지만, 일반 상담 기준으로 안내드릴게요. "
            "보험금 청구, 계약 조회, 납입, 해지/환급처럼 업무 유형을 알려주시면 필요한 경로와 준비사항을 더 구체적으로 정리해드릴 수 있습니다. "
            f"개인 계약 정보 확인이나 접수가 필요한 내용은 라이나생명 고객센터({CONSULT_URL})에서 확인해 주세요."
        )
    top = matches[0]
    answer = top["answer"]
    if len(answer) > 520:
        answer = answer[:520].rstrip() + "..."
    return (
        f"상담에 참고한 자주 묻는 질문은 '{top['question']}'입니다.\n\n"
        f"{answer}\n\n"
        "더 자세한 확인이나 개인 계약 정보가 필요한 내용은 라이나생명 고객센터로 이어서 확인하시면 좋습니다."
    )


def answer_question(question: str):
    matches = search_faq(question, limit=MAX_CONTEXT_ITEMS)
    api_key = get_api_key()
    if not api_key or OpenAI is None:
        return fallback_answer(question, matches), matches

    client = OpenAI(api_key=api_key)
    context = build_context(matches)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 라이나생명 고객을 돕는 친절한 상담 AI입니다. "
                        "제공된 FAQ 근거가 있으면 가장 먼저 활용하고, FAQ에 없는 일반 상담 질문도 고객이 다음 행동을 알 수 있게 답합니다. "
                        "다만 개인 계약 조회, 보험금 지급 가능 여부 확정, 회사 주소/연락처처럼 최신성이나 본인 확인이 필요한 내용은 공식 홈페이지 또는 고객센터 확인을 안내합니다. "
                        "답변은 존댓말로, 고객이 바로 이해할 수 있게 짧은 문단과 필요 시 번호 목록으로 정리합니다. "
                        "근거가 부족하더라도 무조건 거절하지 말고 일반적인 안내와 확인 경로를 함께 제시합니다. "
                        "마크다운 표, 출처 라벨, 과한 기술 설명은 쓰지 않습니다."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"사용자 질문: {question}\n\n"
                        f"라이나생명 FAQ 근거:\n{context}\n\n"
                        f"기본 상담 정보:\n{GENERAL_CONSULT_INFO}\n\n"
                        f"자주 묻는 질문 바로가기: {FAQ_SOURCE_URL}\n고객센터 상담: {CONSULT_URL}"
                    ),
                },
            ],
            temperature=0.2,
        )
        return (response.choices[0].message.content or fallback_answer(question, matches)).strip(), matches
    except Exception:
        return fallback_answer(question, matches), matches
