from __future__ import annotations

import json

from openai import OpenAI


SYSTEM_PROMPT = """
당신은 사용자의 구강관리 답변을 바탕으로 치아 건강 셀프체크 결과를 쉽게 설명하는 AI입니다.
모든 문장은 존댓말로 작성합니다.

중요한 원칙:
1. 의학적 진단처럼 단정하지 않습니다.
2. 사용자가 치과에 가야 할 수 있는 경고 신호는 분명히 말합니다.
3. 너무 겁주거나 보험 가입을 노골적으로 권유하지 않습니다.
4. 치아보험 연결은 자연스럽게, 치료비 공백이나 면책기간/감액기간 확인 정도로만 말합니다.
5. Markdown 굵게 표시용 별표(**)를 쓰지 않습니다.
6. "위험합니다"만 말하지 말고 왜 그런지, 어떤 습관과 연결되는지 설명합니다.
7. 번호만 단독 줄에 두지 않습니다. 예: "2." 다음 줄에 설명을 쓰지 말고, "2. 왜 이런 점수가 나왔는지: ..."처럼 같은 줄에 이어서 씁니다.
""".strip()


def generate_dental_commentary(api_key: str, inputs: dict, result: dict) -> str | None:
    if not api_key:
        return None

    payload = {
        "inputs": inputs,
        "result": result,
    }
    user_prompt = f"""
아래는 사용자의 치아 건강 셀프체크 입력값과 룰 기반 계산 결과입니다.

{json.dumps(payload, ensure_ascii=False, indent=2)}

아래 형식으로 답변해 주세요. 번호와 제목, 설명은 같은 줄에서 시작해 주세요.

1. 한 줄 총평:
점수와 유형을 자연스럽게 언급합니다.

2. 왜 이런 점수가 나왔는지:
양치, 치실/치간칫솔, 단 음료/간식, 스케일링, 증상, 치과 방문 공백을 구체적으로 연결해 설명합니다.

3. 지금 바로 바꾸면 좋은 것:
실천 가능한 행동 3가지를 짧게 제안합니다.

4. 치아보장 관점에서 확인할 점:
충전치료, 크라운, 임플란트, 스케일링, 면책기간, 감액기간 중 사용자 결과와 연결되는 항목만 자연스럽게 언급합니다.

답변은 너무 길지 않게 5~8문장 정도로 작성하세요.
""".strip()

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.35,
        max_tokens=900,
    )
    return response.choices[0].message.content.strip().replace("**", "")
