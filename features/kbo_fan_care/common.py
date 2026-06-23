import hashlib

import streamlit as st


TEAMS = [
    "KIA 타이거즈",
    "LG 트윈스",
    "삼성 라이온즈",
    "두산 베어스",
    "롯데 자이언츠",
    "SSG 랜더스",
    "한화 이글스",
    "NC 다이노스",
    "KT 위즈",
    "키움 히어로즈",
]

BALLPARK_FOODS = [
    "치킨",
    "떡볶이",
    "핫도그",
    "라면",
    "김밥",
    "오징어",
    "탄산음료",
    "맥주",
    "아이스크림",
    "나초",
]


def stable_index(value, size):
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % size


def render_kbo_css():
    st.markdown(
        """
        <style>
        .kbo-intro-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem 1.1rem;
            color: #334155;
            line-height: 1.65;
            margin: .6rem 0 1rem;
            background: #fff;
            word-break: keep-all;
        }
        .kbo-section-title {
            color: #111827;
            font-size: 1.04rem;
            font-weight: 900;
            margin: 1.15rem 0 .55rem;
        }
        .kbo-card-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .7rem;
            margin: .7rem 0;
        }
        .kbo-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: .9rem 1rem;
            background: #fff;
            color: #334155;
            line-height: 1.62;
            word-break: keep-all;
        }
        .kbo-card.gold {
            border-color: #f2b71b;
            background: #fff9e8;
        }
        .kbo-card-title {
            color: #111827;
            font-size: .96rem;
            font-weight: 900;
            margin-bottom: .32rem;
        }
        .kbo-card-body {
            color: #475569;
            font-size: .83rem;
            line-height: 1.62;
        }
        .kbo-score-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .65rem;
            margin: .65rem 0;
        }
        .kbo-score-pill {
            border: 1px solid #e2e8f0;
            border-radius: 999px;
            padding: .75rem .8rem;
            text-align: center;
            background: #f8fafc;
            color: #64748b;
            font-size: .8rem;
            font-weight: 700;
        }
        .kbo-score-pill strong {
            display: block;
            color: #111827;
            font-size: 1.18rem;
            line-height: 1.2;
            margin-top: .14rem;
        }
        .kbo-tag-row {
            display: flex;
            flex-wrap: wrap;
            gap: .42rem;
            margin: .65rem 0;
        }
        .kbo-tag {
            display: inline-flex;
            align-items: center;
            border: 1px solid #dbe3ef;
            border-radius: 999px;
            padding: .26rem .58rem;
            color: #475569;
            background: #fff;
            font-size: .76rem;
            font-weight: 700;
            white-space: nowrap;
        }
        .kbo-tag.warn {
            border-color: #f2b71b;
            background: #fff8e6;
            color: #111827;
        }
        .kbo-report {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem 1.1rem;
            background: #f8fafc;
            color: #334155;
            line-height: 1.65;
            word-break: keep-all;
        }
        @media (max-width: 760px) {
            .kbo-card-grid,
            .kbo-score-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def card(title, body, gold=False):
    class_name = "kbo-card gold" if gold else "kbo-card"
    return f"""
    <div class="{class_name}">
        <div class="kbo-card-title">{title}</div>
        <div class="kbo-card-body">{body}</div>
    </div>
    """


def score_pill(label, value, suffix="점"):
    return f"""
    <div class="kbo-score-pill">
        {label}
        <strong>{value}{suffix}</strong>
    </div>
    """


def tags(items):
    html = "".join(
        f'<span class="kbo-tag{" warn" if warn else ""}">{label}</span>'
        for label, warn in items
    )
    st.markdown(f'<div class="kbo-tag-row">{html}</div>', unsafe_allow_html=True)


def level_label(score):
    if score >= 75:
        return "높음"
    if score >= 48:
        return "주의"
    return "낮음"
