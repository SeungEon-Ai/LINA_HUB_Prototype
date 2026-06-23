from __future__ import annotations


TYPE_META = {
    "gum": {
        "title": "잇몸 경고등형",
        "copy": "양치할 때 피가 나거나 치석 관리 공백이 쌓이면 잇몸 쪽 신호가 먼저 켜질 수 있습니다.",
        "link": "스케일링, 잇몸 치료, 정기 검진",
    },
    "cavity": {
        "title": "단짠 간식 공격형",
        "copy": "단 음료와 간식 빈도가 높으면 충치 위험이 올라갈 수 있습니다. 특히 자기 전 간식은 점수에 크게 반영했습니다.",
        "link": "충전치료, 크라운, 치아우식 관리",
    },
    "sensitive": {
        "title": "시린이 예민형",
        "copy": "차갑거나 뜨거운 음식에 민감하고 씹을 때 불편하면 치아 마모, 충치, 잇몸 문제를 함께 확인해볼 필요가 있습니다.",
        "link": "치과 검진, 보존치료, 보철 가능성",
    },
    "delay": {
        "title": "치과 미루기 장인형",
        "copy": "통증이 있어도 치과 방문을 미루는 습관은 작은 치료를 큰 치료로 키울 수 있습니다.",
        "link": "정기검진, 치료비 대비, 면책기간 확인",
    },
    "steady": {
        "title": "반짝반짝 루틴형",
        "copy": "현재 답변 기준으로는 구강관리 루틴이 비교적 안정적입니다. 지금의 습관을 유지하는 것이 핵심입니다.",
        "link": "예방관리, 정기검진, 보장 점검",
    },
}


PUBLIC_SOURCES = [
    {
        "label": "국가건강정보포털 구강병 예방 및 관리방법",
        "url": "https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=6291",
        "basis": "치면세균막 제거, 당류 섭취 조절, 불소 활용 등 구강병 예방 원칙",
    },
    {
        "label": "국민건강보험공단 치석제거 급여안내",
        "url": "https://www.nhis.or.kr/static/html/wbma/c/wbmac0218.html",
        "basis": "만 19세 이상 치석제거 연 1회 급여 기준",
    },
    {
        "label": "국민건강보험 웹진 스케일링 건강보험 혜택",
        "url": "https://www.nhis.or.kr/static/alim/paper/oldpaper/202209/sub/06.html",
        "basis": "스케일링은 치태와 치석을 제거해 구강질환 예방 및 치료에 도움",
    },
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def calculate_dental_score(inputs: dict) -> dict:
    score = 100.0
    risks = {"gum": 0.0, "cavity": 0.0, "sensitive": 0.0, "delay": 0.0, "cost": 0.0}
    positives = []
    warnings = []
    factor_log = []

    age_map = {
        "10대 후반": 18,
        "20대": 27,
        "30대": 36,
        "40대": 46,
        "50대 이상": 56,
    }
    age = int(inputs.get("age") or age_map.get(inputs.get("age_group"), 29))

    def add(label: str, penalty: float = 0, bonus: float = 0, **risk_values):
        nonlocal score
        score += bonus - penalty
        if bonus:
            positives.append(label)
            factor_log.append((label, bonus, "plus"))
        if penalty:
            warnings.append(label)
            factor_log.append((label, penalty, "minus"))
        for key, value in risk_values.items():
            risks[key] += value

    brushing = inputs["brushing"]
    if brushing == "매 식후 3회 이상":
        add("양치 빈도가 안정적입니다.", bonus=4)
    elif brushing == "하루 2회":
        add("기본 양치 루틴은 유지되고 있습니다.", bonus=1)
    elif brushing == "하루 1회":
        add("양치 빈도가 낮아 치태 관리 공백이 생길 수 있습니다.", penalty=10, cavity=10, gum=7)
    elif brushing == "가끔 하루를 넘김":
        add("양치 공백이 생기는 날이 있어 충치와 잇몸 리스크가 함께 올라갑니다.", penalty=17, cavity=17, gum=11)
    else:
        add("며칠씩 양치를 놓치면 치태가 오래 남아 치료 리스크가 크게 올라갑니다.", penalty=24, cavity=23, gum=16)

    brushing_time_map = {
        "3분 이상 꼼꼼히": (-4, 0, "양치 시간이 충분해 치태 제거에 유리합니다."),
        "2분 정도": (-1, 0, "양치 시간이 기본 수준입니다."),
        "1분 안팎": (5, 0, "양치 시간이 짧아 닦이지 않는 부위가 남을 수 있습니다."),
        "대충 빠르게": (10, 0, "양치를 빠르게 끝내는 편이면 치아 사이와 잇몸선 관리가 약해질 수 있습니다."),
        "기억 안 날 정도로 짧음": (16, 0, "양치 시간이 매우 짧아 충치와 잇몸 리스크가 함께 올라갑니다."),
    }
    penalty, bonus, label = brushing_time_map[inputs["brushing_time"]]
    add(label, penalty=max(penalty, 0), bonus=max(-penalty, bonus), cavity=max(penalty, 0) * 0.7, gum=max(penalty, 0) * 0.6)

    night_map = {
        "거의 매일 지킴": (-4, "자기 전 양치를 잘 지키는 편입니다."),
        "일주일 1~2회 놓침": (4, "자기 전 양치를 가끔 놓쳐 야간 치태 관리 공백이 생길 수 있습니다."),
        "절반 정도 놓침": (9, "자기 전 양치를 절반 정도 놓치면 당류와 치태가 밤새 남을 수 있습니다."),
        "자주 놓침": (14, "자기 전 양치를 자주 놓치면 충치 리스크가 크게 올라갑니다."),
        "거의 안 함": (20, "자기 전 양치 공백이 커서 충치 리스크가 가장 크게 반영됩니다."),
    }
    value, label = night_map[inputs["night_brushing"]]
    add(label, penalty=max(value, 0), bonus=max(-value, 0), cavity=max(value, 0) * 1.15)

    if inputs["floss"] == "매일 사용":
        add("치실/치간칫솔 사용은 치아 사이 관리에 좋습니다.", bonus=5)
    elif inputs["floss"] == "주 3~4회":
        add("치실/치간칫솔을 꽤 꾸준히 사용하고 있습니다.", bonus=2)
    elif inputs["floss"] == "가끔 사용":
        add("치실/치간칫솔 사용 빈도가 낮아 치아 사이 관리가 아쉬울 수 있습니다.", penalty=3, gum=4, cavity=3)
    elif inputs["floss"] == "거의 안 씀":
        add("치아 사이는 칫솔만으로 놓치기 쉬워 치실이나 치간칫솔이 도움이 됩니다.", penalty=9, gum=12, cavity=8)
    else:
        add("치실/치간칫솔 경험이 거의 없으면 치아 사이 충치와 잇몸 리스크가 올라갑니다.", penalty=12, gum=15, cavity=10)

    snack = inputs["sweet_snack"]
    snack_map = {
        "거의 안 먹음": (-3, 0, "단 간식 빈도가 낮은 편입니다."),
        "주 1~2회": (1, 0, "단 간식 빈도는 낮은 편입니다."),
        "주 3~5회": (5, 0, "단 간식이 반복되어 충치 리스크가 조금 올라갑니다."),
        "하루 1회": (10, 0, "단 간식/음료가 매일 있으면 충치 리스크가 올라갑니다."),
        "하루 2회 이상": (17, 0, "단 간식/음료 빈도가 높아 충치 리스크가 크게 올라갑니다."),
    }
    penalty, bonus, label = snack_map[snack]
    add(label, penalty=max(penalty, 0), bonus=max(-penalty, bonus), cavity=max(penalty, 0) * 1.2)

    drink_map = {
        "거의 안 마심": (-2, "산성 음료 빈도가 낮습니다."),
        "주 1~2회": (1, "커피/탄산 빈도는 낮은 편입니다."),
        "주 3~5회": (4, "커피/탄산이 반복되면 치아 시림이나 착색 관리가 필요할 수 있습니다."),
        "하루 1회": (8, "커피/탄산을 매일 마시면 산 노출과 당류 섭취가 누적될 수 있습니다."),
        "하루 2회 이상": (13, "커피/탄산 빈도가 높아 충치와 시림 리스크가 함께 올라갑니다."),
    }
    value, label = drink_map[inputs["coffee_soda"]]
    add(label, penalty=max(value, 0), bonus=max(-value, 0), cavity=max(value, 0) * 0.75, sensitive=max(value, 0) * 0.7)

    after_drink_map = {
        "대부분 물로 헹굼": (-4, "단 음료나 커피 뒤 물로 헹구는 습관이 좋습니다."),
        "가끔 헹굼": (1, "음료 뒤 물로 헹구는 습관은 조금 더 늘리면 좋습니다."),
        "잘 안 헹굼": (6, "음료 뒤 입안을 잘 헹구지 않으면 산과 당이 오래 남을 수 있습니다."),
        "바로 양치하는 편": (3, "산성 음료 직후 바로 양치하면 치아 표면에 부담이 될 수 있어 물로 먼저 헹구는 편이 좋습니다."),
        "신경 써본 적 없음": (7, "음료 뒤 관리 습관이 없어 충치와 시림 리스크가 조금 올라갑니다."),
    }
    value, label = after_drink_map[inputs["after_drink"]]
    add(label, penalty=max(value, 0), bonus=max(-value, 0), cavity=max(value, 0) * 0.6, sensitive=max(value, 0) * 0.5)

    smoking_map = {
        "비흡연": (-3, "비흡연은 잇몸 건강 점수에 좋게 반영됩니다."),
        "과거 흡연": (5, "과거 흡연 이력이 있어 잇몸 리스크를 조금 반영했습니다."),
        "가끔 흡연": (9, "가끔 흡연도 잇몸 건강에는 불리하게 작용할 수 있습니다."),
        "현재 흡연": (15, "흡연은 잇몸 건강과 구강 회복에 불리하게 작용할 수 있습니다."),
        "전자담배 포함 자주 흡연": (18, "잦은 흡연은 잇몸 리스크를 크게 높이는 요인으로 반영했습니다."),
    }
    value, label = smoking_map[inputs["smoking"]]
    add(label, penalty=max(value, 0), bonus=max(-value, 0), gum=max(value, 0) * 1.25)

    scaling = inputs["scaling"]
    if scaling == "6개월 이내":
        add("최근 스케일링 이력이 있어 치석 관리 점수가 좋습니다.", bonus=8)
    elif scaling == "1년 이내":
        add("1년 이내 스케일링 이력이 있어 치석 관리가 비교적 안정적입니다.", bonus=5)
    elif scaling == "1~2년 전":
        add("스케일링 공백이 1년을 넘어 잇몸 관리 점검이 필요합니다.", penalty=5, gum=8)
    elif scaling == "2년 이상 안 함":
        add("스케일링 공백이 길어 잇몸/치석 관리 점검이 필요합니다.", penalty=15, gum=20, delay=5)
    else:
        add("마지막 스케일링 시점이 불명확해 치석 관리 공백을 반영했습니다.", penalty=10, gum=14, delay=4)

    checkup = inputs["checkup"]
    if checkup == "6개월 이내":
        add("최근 치과 검진 이력이 좋습니다.", bonus=7)
    elif checkup == "1년 이내":
        add("1년 이내 치과 검진 이력이 있어 기본 점검은 유지되고 있습니다.", bonus=3)
    elif checkup == "1~2년 전":
        add("치과 검진 공백이 조금 있어 정기 점검을 다시 잡아보면 좋습니다.", penalty=5, delay=7)
    elif checkup == "2년 이상 안 함":
        add("검진 공백이 길면 작은 이상을 늦게 발견할 수 있습니다.", penalty=14, delay=18, cost=7)
    else:
        add("마지막 검진 시점이 기억나지 않아 점검 공백을 반영했습니다.", penalty=9, delay=13)

    symptom_fields = {
        "bleeding": {
            "label": "양치할 때 피가 남",
            "risk": "gum",
            "scores": {"거의 없음": 0, "한 달에 가끔": 4, "주 1~2회": 9, "자주 있음": 15, "거의 매번 있음": 22},
        },
        "pain": {
            "label": "욱신거리는 통증",
            "risk": "sensitive",
            "scores": {"거의 없음": 0, "아주 가끔": 4, "월 1~2회": 9, "주 1회 이상": 16, "자주 아픔": 24},
        },
        "cold": {
            "label": "찬물/뜨거운 음식에 시림",
            "risk": "sensitive",
            "scores": {"거의 없음": 0, "아주 가끔": 3, "특정 치아만 가끔": 8, "자주 시림": 15, "일상적으로 불편함": 22},
        },
        "chewing": {
            "label": "씹을 때 불편함",
            "risk": "sensitive",
            "scores": {"거의 없음": 0, "딱딱한 음식만 가끔": 5, "특정 부위만 불편": 10, "자주 불편": 18, "씹기 힘들 정도": 26},
        },
        "bad_breath": {
            "label": "입냄새/텁텁함",
            "risk": "gum",
            "scores": {"거의 없음": 0, "아침에만 가끔": 3, "피곤할 때 가끔": 5, "자주 느낌": 10, "거의 매일 신경 쓰임": 15},
        },
        "gum_swelling": {
            "label": "잇몸 붓기/내려앉음",
            "risk": "gum",
            "scores": {"전혀 없음": 0, "가끔 붓는 느낌": 6, "특정 부위만 불편": 11, "자주 붓거나 내려앉음": 20, "치아가 흔들리는 느낌도 있음": 30},
        },
    }
    symptom_count = 0
    for field, meta in symptom_fields.items():
        value = inputs[field]
        penalty = meta["scores"][value]
        if penalty >= 15:
            symptom_count += 1
            add(f"{meta['label']} 증상이 강하게 나타나면 치과 확인이 필요합니다.", penalty=penalty, **{meta["risk"]: penalty + 4, "cost": penalty * 0.35})
        elif penalty > 0:
            symptom_count += 1
            add(f"{meta['label']} 신호가 있어 해당 부위 점검 점수를 반영했습니다.", penalty=penalty * 0.55, **{meta["risk"]: penalty * 0.75})

    visit_map = {
        "정기적으로 감": (-6, "정기적으로 치과를 방문하는 습관이 좋습니다."),
        "불편하면 바로 감": (-2, "불편하면 바로 치과에 가는 편입니다."),
        "조금 미룸": (5, "치과 방문을 조금 미루는 편이라 치료 시점이 늦어질 수 있습니다."),
        "아파도 꽤 미룸": (12, "통증이 있어도 미루면 치료 범위와 비용이 커질 수 있습니다."),
        "참을 수 있을 때까지 미룸": (18, "치과 방문을 오래 미루면 작은 치료가 큰 치료로 이어질 수 있습니다."),
    }
    value, label = visit_map[inputs["visit_delay"]]
    add(label, penalty=max(value, 0), bonus=max(-value, 0), delay=max(value, 0) * 1.4, cost=max(value, 0) * 0.8)

    treatment_map = {
        "큰 치료 없음": (-2, "큰 치과치료 경험이 적은 편입니다."),
        "충전치료 경험": (4, "충전치료 경험이 있어 충치 재발 관리 점수를 반영했습니다."),
        "크라운/신경치료 경험": (8, "크라운/신경치료 경험이 있어 큰 치료 이력을 반영했습니다."),
        "임플란트/브릿지 경험": (10, "임플란트/브릿지 경험이 있어 보철 관리와 비용 리스크를 반영했습니다."),
        "여러 치료가 반복됨": (16, "치과치료가 반복된 편이라 재치료와 비용 공백 리스크를 높게 반영했습니다."),
    }
    value, label = treatment_map[inputs["past_treatment"]]
    add(label, penalty=max(value, 0), bonus=max(-value, 0), cavity=max(value, 0) * 0.6, sensitive=max(value, 0) * 0.65, cost=max(value, 0) * 1.2)

    cost_map = {
        "거의 없음": (-3, "치과비 때문에 치료를 미룬 경험은 적습니다."),
        "한두 번 있음": (3, "치과비 부담을 느낀 경험이 조금 있습니다."),
        "가끔 망설임": (7, "치과비 부담 때문에 치료를 망설이는 편입니다."),
        "자주 미룸": (13, "치과비 때문에 치료를 자주 미루면 치료 범위가 커질 수 있습니다."),
        "비용 때문에 치료를 포기한 적 있음": (20, "치과비 때문에 치료를 포기한 경험은 보장 공백 리스크에 크게 반영됩니다."),
    }
    value, label = cost_map[inputs["cost_worry"]]
    add(label, penalty=max(value, 0), bonus=max(-value, 0), delay=max(value, 0) * 0.8, cost=max(value, 0) * 1.5)

    score = int(round(clamp(score, 20, 100)))
    dental_age = int(round(age + clamp((80 - score) / 3, -4, 14)))
    ranked_risks = sorted(risks.items(), key=lambda item: item[1], reverse=True)
    main_type = "steady" if score >= 82 and symptom_count == 0 else ranked_risks[0][0]
    if main_type == "cost":
        main_type = "delay"
    risk_percent = {
        key: int(round(clamp(value, 0, 60) / 60 * 100))
        for key, value in risks.items()
    }

    if score >= 85:
        grade = "상쾌한 미소권"
    elif score >= 70:
        grade = "관리하면 반짝권"
    elif score >= 55:
        grade = "치과 알림권"
    else:
        grade = "지금 점검권"

    if not warnings:
        warnings.append("현재 답변 기준으로 큰 경고 신호는 적지만, 정기 검진은 계속 유지하는 편이 좋습니다.")

    top_factors = [label for label, _, kind in sorted(factor_log, key=lambda item: item[1], reverse=True) if kind == "minus"][:6]
    strengths = [label for label, _, kind in sorted(factor_log, key=lambda item: item[1], reverse=True) if kind == "plus"][:4]

    return {
        "score": score,
        "grade": grade,
        "dental_age": dental_age,
        "type_key": main_type,
        "type": TYPE_META[main_type],
        "risk_percent": risk_percent,
        "ranked_risks": ranked_risks,
        "top_factors": top_factors,
        "strengths": strengths,
        "positives": positives[:4],
        "warnings": warnings[:7],
        "routine_plan": build_routine_plan(risk_percent, inputs),
        "insurance_hooks": build_insurance_hooks(main_type, risk_percent, inputs),
    }


def build_insurance_hooks(main_type: str, risk_percent: dict, inputs: dict) -> list[str]:
    hooks = []
    if main_type in {"cavity", "sensitive"} or risk_percent["cavity"] >= 45:
        hooks.append("충치나 시림 신호가 있다면 충전치료, 크라운, 신경치료처럼 치료 단계가 커질 때의 비용을 함께 점검해볼 수 있습니다.")
    if main_type == "gum" or risk_percent["gum"] >= 45:
        hooks.append("잇몸 쪽 신호가 있다면 스케일링과 치주 관리를 먼저 챙기고, 치주질환 관련 보장 조건도 확인해볼 만합니다.")
    if inputs["past_treatment"] in {"크라운/신경치료 경험", "임플란트/브릿지 경험", "여러 치료가 반복됨"}:
        hooks.append("이미 큰 치과치료 경험이 있다면 보철, 크라운, 임플란트 관련 보장 범위와 면책기간을 따로 확인하는 것이 좋습니다.")
    if inputs.get("cost_worry") in {"자주 미룸", "비용 때문에 치료를 포기한 적 있음"}:
        hooks.append("치료비 때문에 미룬 경험이 있다면 보장 여부뿐 아니라 면책기간과 감액기간처럼 실제 받을 수 있는 시점도 함께 확인해볼 필요가 있습니다.")
    if not hooks:
        hooks.append("현재는 예방 관리 중심으로 보입니다. 그래도 치아보험은 가입 직후 바로 보장되지 않는 면책기간과 감액기간이 있을 수 있어 미리 확인하는 편이 좋습니다.")
    return hooks[:3]


def build_routine_plan(risk_percent: dict, inputs: dict) -> list[str]:
    plan = []
    if risk_percent["cavity"] >= 45:
        plan.append("단 음료와 간식은 횟수를 먼저 줄이고, 마신 뒤에는 물로 입안을 헹구는 루틴을 붙여보세요.")
    if risk_percent["gum"] >= 45:
        plan.append("잇몸선과 치아 사이 관리를 위해 치실 또는 치간칫솔을 주 3회 이상으로 늘려보세요.")
    if risk_percent["sensitive"] >= 45:
        plan.append("시림이나 씹을 때 불편함이 반복되면 특정 치아 문제일 수 있어 치과 검진을 우선 잡아보세요.")
    if risk_percent["delay"] >= 45 or risk_percent.get("cost", 0) >= 45:
        plan.append("치과 방문을 미루는 이유가 비용이라면 검진과 상담을 먼저 받아 치료 범위가 커지기 전 확인해보세요.")
    if inputs.get("scaling") in {"1~2년 전", "2년 이상 안 함", "기억 안 남"}:
        plan.append("스케일링 공백이 있다면 치석 관리부터 다시 시작하는 것이 좋습니다.")
    if not plan:
        plan.append("현재 루틴은 비교적 안정적입니다. 자기 전 양치와 치실/치간칫솔만 꾸준히 유지해보세요.")
    return plan[:5]
