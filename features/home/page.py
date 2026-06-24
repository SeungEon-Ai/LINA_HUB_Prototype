import base64
import html as html_module
from datetime import date
from pathlib import Path

import streamlit as st


def _html(markup):
    st.markdown(markup, unsafe_allow_html=True)




def _feature_icon_img(icon_uri, alt):
    if not icon_uri:
        return '<div class="home-icon home-icon-slate">AI</div>'
    return f'<div class="home-feature-img"><img src="{icon_uri}" alt="{alt}"></div>'


def _daily_recommendations(items, count=5):
    if not items:
        return []
    offset = date.today().toordinal() % len(items)
    rotated = items[offset:] + items[:offset]
    return rotated[:count]

def _asset_data_uri(path):
    asset_path = Path(path)
    if not asset_path.exists():
        return ""
    encoded = base64.b64encode(asset_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def render():
    root = Path(__file__).resolve().parents[2]
    hero_illustration_uri = _asset_data_uri(root / "assets" / "home" / "hero-illustration.png")
    dictionary_card_bg_uri = _asset_data_uri(root / "assets" / "home" / "dictionary-card-bg.png")
    chat_orb_uri = _asset_data_uri(root / "assets" / "home" / "chat-gunggeum-orb.png")
    bottom_icon_uris = {
        "chatbot": _asset_data_uri(root / "assets" / "home" / "bottom" / "chatbot.png"),
        "one_to_one": _asset_data_uri(root / "assets" / "home" / "bottom" / "one_to_one.png"),
        "branch": _asset_data_uri(root / "assets" / "home" / "bottom" / "branch.png"),
    }
    homepage_banner_uris = [
        _asset_data_uri(root / "assets" / "home" / "banners" / "life_cropped.png"),
        _asset_data_uri(root / "assets" / "home" / "banners" / "direct_cropped.png"),
        _asset_data_uri(root / "assets" / "home" / "banners" / "damage_cropped.png"),
    ]
    homepage_banner_srcdoc = html_module.escape(f"""
<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;background:transparent;overflow:hidden;font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif}}
.carousel{{position:relative;width:100%;height:188px;border:1px solid #e5edf7;border-radius:16px;overflow:hidden;background:#fff;box-shadow:0 10px 24px rgba(15,23,42,.04)}}
.track{{display:flex;width:300%;height:100%;transition:transform .42s ease}}
.slide{{width:33.3333%;height:100%;display:block;background:#fff}}
.slide img{{width:100%;height:100%;display:block;object-fit:cover;object-position:center center;background:#fff}}
.nav{{position:absolute;top:50%;transform:translateY(-50%);z-index:5;border:0;background:transparent;color:#0f172a;font-size:1.35rem;line-height:1;font-weight:950;padding:.2rem .35rem;cursor:pointer;text-shadow:0 1px 5px rgba(255,255,255,.9)}}
.prev{{left:.45rem}} .next{{right:.45rem}}
.dots{{position:absolute;left:50%;bottom:.35rem;transform:translateX(-50%);display:flex;gap:.28rem;z-index:4}}
.dot{{width:5px;height:5px;border-radius:999px;background:rgba(37,18,160,.22);transition:all .2s ease}}
.dot.active{{width:14px;background:#2512a0}}
</style></head><body>
<div class="carousel">
  <div class="track" id="track">
    <a class="slide" href="https://www.lina.co.kr" target="_blank" rel="noopener noreferrer"><img src="{homepage_banner_uris[0]}" alt="라이나생명 홈페이지"></a>
    <a class="slide" href="https://direct.lina.co.kr" target="_blank" rel="noopener noreferrer"><img src="{homepage_banner_uris[1]}" alt="라이나생명 다이렉트"></a>
    <a class="slide" href="https://www.chubb.com/kr-kr/" target="_blank" rel="noopener noreferrer"><img src="{homepage_banner_uris[2]}" alt="라이나손해보험 홈페이지"></a>
  </div>
  <button class="nav prev" type="button" aria-label="이전 배너">&lt;</button>
  <button class="nav next" type="button" aria-label="다음 배너">&gt;</button>
  <div class="dots"><span class="dot active"></span><span class="dot"></span><span class="dot"></span></div>
</div>
<script>
const track=document.getElementById('track');
const dots=[...document.querySelectorAll('.dot')];
let index=0;
function show(i){{index=(i+3)%3;track.style.transform=`translateX(${{-index*33.3333}}%)`;dots.forEach((d,n)=>d.classList.toggle('active',n===index));}}
document.querySelector('.prev').addEventListener('click',(e)=>{{e.preventDefault();e.stopPropagation();show(index-1);}});
document.querySelector('.next').addEventListener('click',(e)=>{{e.preventDefault();e.stopPropagation();show(index+1);}});
setInterval(()=>show(index+1),5000);
</script></body></html>
""", quote=True)
    feature_icon_uris = {
        "dictionary": _asset_data_uri(root / "assets" / "home" / "features" / "dictionary.png"),
        "policy_graph_rag": _asset_data_uri(root / "assets" / "home" / "features" / "policy_graph_rag.png"),
        "life_expectancy": _asset_data_uri(root / "assets" / "home" / "features" / "life_expectancy.png"),
        "future_worry_test": _asset_data_uri(root / "assets" / "home" / "features" / "future_worry_test.png"),
        "meal_judgement": _asset_data_uri(root / "assets" / "home" / "features" / "meal_judgement.png"),
        "dental_score": _asset_data_uri(root / "assets" / "home" / "features" / "dental_score.png"),
        "dust_health_check": _asset_data_uri(root / "assets" / "home" / "features" / "dust_health_check.png"),
        "insurance_news_summary": _asset_data_uri(root / "assets" / "home" / "features" / "insurance_news_summary.png"),
        "lina_faq_ai": _asset_data_uri(root / "assets" / "home" / "chat-gunggeum-orb.png"),
    }
    recommendation_items = [
        {"key": "lina_faq_ai", "label": "라이나 궁금톡", "desc": "보험 상담 전 궁금한 점을 먼저 물어보세요"},
        {"key": "policy_graph_rag", "label": "라이나 약관 AI", "desc": "약관 궁금증을 해결해드려요"},
        {"key": "dictionary", "label": "AI보험용어사전", "desc": "보험용어를 쉽게 풀어드려요"},
        {"key": "life_expectancy", "label": "라이프타임 계산기", "desc": "내 생애 비용을 계산해보세요"},
        {"key": "future_worry_test", "label": "미래 걱정 유형 테스트", "desc": "나의 걱정 유형을 알아봐요"},
        {"key": "meal_judgement", "label": "오늘 한 끼 판정단", "desc": "오늘의 한 끼를 점검해요"},
        {"key": "dental_score", "label": "치아 건강점수", "desc": "치아 상태를 체크해요"},
        {"key": "dust_health_check", "label": "오늘의 직관! 미세먼지는?", "desc": "오늘 공기 상태를 확인해요"},
        {"key": "insurance_news_summary", "label": "보험뉴스 한입 AI", "desc": "보험 관련 뉴스를 짧고 쉽게 살펴보세요"},
    ]
    recommendation_cards = "\n".join(
        f'<a class="home-feature" href="?feature={item["key"]}" target="_self">'
        f'{_feature_icon_img(feature_icon_uris.get(item["key"], ""), item["label"])}'
        f'<div><strong>{item["label"]}</strong><span>{item["desc"]}</span></div></a>'
        for item in _daily_recommendations(recommendation_items, 5)
    )
    _html(
        """
<style>
.lina-footer {
    margin-top: 1.4rem !important;
    border-top: 0 !important;
    position: relative !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}
.lina-footer:before {
    content: "";
    position: absolute;
    top: 0;
    left: clamp(20.5rem, calc((100vw - 1040px) / 4 + 107px), 23rem);
    right: clamp(4.5rem, calc((100vw - 1840px) / 2 + 4.5rem), 7rem);
    border-top: 1px solid #e5e7eb;
}
.lina-footer .lina-footer-main,
.lina-footer .lina-footer-bottom {
    max-width: none !important;
    width: auto !important;
    margin-left: clamp(20.5rem, calc((100vw - 1040px) / 4 + 107px), 23rem) !important;
    margin-right: clamp(4.5rem, calc((100vw - 1840px) / 2 + 4.5rem), 7rem) !important;
}
.home-shell {
    width: 100vw;
    margin-left: calc(50% - 50vw);
    padding: 0 clamp(84px, 5.4vw, 124px) 0 var(--lina-left-reserved, clamp(360px, 22vw, 460px));
    font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
    color: #111827;
}
.home-shell a { color: inherit !important; text-decoration: none !important; }
.home-grid {
    display: grid;
    grid-template-columns: minmax(0, 2.35fr) minmax(280px, .85fr);
    gap: 1rem;
}
.home-hero {
    --home-hero-action-width: min(720px, 64%);
    min-height: 316px;
    border: 1px solid #e5edf7;
    border-radius: 18px;
    background: #eaf0fd;
    box-shadow: 0 14px 34px rgba(15, 23, 42, .06);
    padding: 1.5rem 1.9rem;
    position: relative;
    overflow: hidden;
}
.home-hero h1,
.home-hero-sub,
.home-search,
.home-tags {
    position: relative;
    z-index: 3;
}
.home-hero-art {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    background-repeat: no-repeat;
    background-size: 100% 100%;
    background-position: center center;
    z-index: 1;
    pointer-events: none;
}
.home-hero-art:after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(234,240,253,.96) 0%, rgba(234,240,253,.78) 25%, rgba(234,240,253,.18) 52%, rgba(234,240,253,0) 72%);
    pointer-events: none;
}
.home-hero h1 {
    margin: 0;
    font-size: 2.08rem;
    line-height: 1.18;
    font-weight: 950;
    letter-spacing: 0;
}
.home-hero h1 strong { color: #2817a3; font-weight: 950; }
.home-hero-sub {
    margin-top: .55rem;
    color: #334155;
    font-size: .93rem;
    font-weight: 850;
}
.home-search {
    position: absolute;
    left: 1.9rem;
    bottom: 5.78rem;
    margin-top: 0;
    width: var(--home-hero-action-width);
    min-height: 50px;
    border: 1.5px solid #f2b72d;
    border-radius: 999px;
    background: rgba(255,255,255,.96);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: .6rem;
    padding: 0 .45rem 0 1.45rem;
    color: #334155 !important;
    font-size: .9rem;
    font-weight: 850;
    box-shadow: 0 12px 26px rgba(245, 181, 27, .12);
}
.home-search > span:first-child {
    flex: 1 1 auto;
    text-align: center;
    padding-left: 36px;
}
.home-search-go {
    width: 36px;
    height: 36px;
    flex: 0 0 36px;
    border-radius: 999px;
    background: #ffb71b;
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.16rem;
    font-weight: 950;
}
.home-tags {
    position: absolute;
    left: 1.9rem;
    bottom: 1.85rem;
    width: var(--home-hero-action-width);
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: .5rem;
    margin-top: 0;
}
.home-tags span {
    min-height: 28px;
    padding: 0 .82rem;
    border: 1px solid #dbe5f0;
    border-radius: 999px;
    background: #fff;
    display: inline-flex;
    align-items: center;
    color: #334155;
    font-size: .76rem;
    font-weight: 850;
}
.home-phone {
    position: absolute;
    right: 95px;
    top: 14px;
    width: 116px;
    height: 178px;
    border-radius: 28px;
    background:
        linear-gradient(#fff, #fff) padding-box,
        linear-gradient(135deg, #1f2b57, #273568) border-box;
    border: 7px solid transparent;
    transform: rotate(9deg);
    box-shadow: 0 24px 46px rgba(37, 18, 160, .16);
    z-index: 1;
}
.home-phone span {
    position: absolute;
    top: 24px;
    left: 16px;
    color: #f5b51b;
    font-size: .7rem;
    font-weight: 950;
}
.home-phone:before {
    content: "";
    position: absolute;
    top: 52px;
    left: 19px;
    width: 70px;
    height: 32px;
    border-radius: 14px;
    background: linear-gradient(145deg, #f4f7ff, #e8efff);
    box-shadow: 0 12px 22px rgba(37, 18, 160, .08);
}
.home-phone:after {
    content: "";
    position: absolute;
    top: 64px;
    left: 34px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #b8c7ff;
    box-shadow: 20px 0 0 #cfd9ff, 40px 0 0 #b8c7ff;
}
.home-phone-notch {
    position: absolute;
    right: 132px;
    top: 17px;
    width: 46px;
    height: 11px;
    border-radius: 0 0 999px 999px;
    background: #1f2b57;
    transform: rotate(9deg);
    z-index: 3;
}
.home-phone-search {
    position: absolute;
    right: 108px;
    top: 49px;
    width: 15px;
    height: 15px;
    border: 3px solid #1f2b57;
    border-radius: 50%;
    transform: rotate(9deg);
    z-index: 3;
}
.home-phone-search:after {
    content: "";
    position: absolute;
    right: -6px;
    bottom: -4px;
    width: 7px;
    height: 3px;
    border-radius: 999px;
    background: #1f2b57;
    transform: rotate(45deg);
}
.home-bubble {
    position: absolute;
    right: 166px;
    top: 92px;
    width: 126px;
    height: 60px;
    border-radius: 22px;
    background: rgba(255,255,255,.78);
    box-shadow: 0 18px 34px rgba(37, 18, 160, .12);
    z-index: 4;
}
.home-bubble:before {
    content: "";
    position: absolute;
    left: 24px;
    top: 24px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #c1ccff;
    box-shadow: 30px 0 0 #d8e0ff, 60px 0 0 #c1ccff;
}
.home-cloud {
    position: absolute;
    right: 68px;
    bottom: 45px;
    width: 225px;
    height: 74px;
    border-radius: 999px;
    background: rgba(255,255,255,.92);
    box-shadow: 0 22px 40px rgba(37, 18, 160, .09);
    z-index: 1;
}
.home-cloud:before {
    content: "";
    position: absolute;
    left: 34px;
    top: -30px;
    width: 86px;
    height: 86px;
    border-radius: 50%;
    background: rgba(255,255,255,.95);
}
.home-cloud:after {
    content: "";
    position: absolute;
    right: 26px;
    top: -22px;
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: rgba(255,255,255,.95);
}
.home-mascot {
    position: absolute;
    right: 40px;
    bottom: 72px;
    width: 114px;
    height: 104px;
    border-radius: 49% 49% 52% 52%;
    background:
        radial-gradient(circle at 35% 62%, #ffcf3d 0 7px, transparent 8px),
        radial-gradient(circle at 67% 62%, #ffcf3d 0 7px, transparent 8px),
        linear-gradient(145deg, #ffd238 0%, #ffc21c 58%, #f8ad13 100%);
    box-shadow: 0 30px 50px rgba(251, 185, 28, .28);
    z-index: 5;
}
.home-mascot:before {
    content: "";
    position: absolute;
    left: 38px;
    top: 38px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #111827;
    box-shadow: 39px 0 0 #111827;
}
.home-mascot:after {
    content: "";
    position: absolute;
    left: 50px;
    top: 55px;
    width: 24px;
    height: 15px;
    border-bottom: 3px solid #111827;
    border-radius: 0 0 999px 999px;
}
.home-mascot-face {
    position: absolute;
    right: 77px;
    bottom: 114px;
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #fff3d5;
    z-index: 6;
    box-shadow: 46px 18px 0 #f79d13;
}
.home-mascot-eye {
    position: absolute;
    right: 94px;
    bottom: 129px;
    width: 14px;
    height: 8px;
    border-bottom: 3px solid #111827;
    border-radius: 0 0 999px 999px;
    transform: rotate(32deg);
    z-index: 6;
}
.home-mascot-leg {
    position: absolute;
    right: 71px;
    bottom: 53px;
    width: 22px;
    height: 34px;
    border-radius: 999px;
    background: #f5aa13;
    transform: rotate(20deg);
    z-index: 3;
    box-shadow: 37px 0 0 #f5aa13;
}
.home-mascot-arm {
    position: absolute;
    right: 42px;
    bottom: 111px;
    width: 18px;
    height: 45px;
    border-radius: 999px;
    background: #ffc21c;
    transform: rotate(-35deg);
    transform-origin: bottom center;
    z-index: 4;
    box-shadow: 0 10px 18px rgba(251, 185, 28, .18);
}
.home-mascot-arm:after {
    content: "";
    position: absolute;
    top: -9px;
    left: 5px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #ffb71b;
}
.home-mascot-antenna {
    position: absolute;
    right: 71px;
    bottom: 174px;
    width: 36px;
    height: 30px;
    border-top: 4px solid #ffc21c;
    border-right: 4px solid #ffc21c;
    border-radius: 0 999px 0 0;
    transform: rotate(-8deg);
    z-index: 4;
}
.home-mascot-antenna:after {
    content: "";
    position: absolute;
    right: -9px;
    top: -9px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #ffb71b;
    box-shadow: 0 6px 14px rgba(245, 181, 27, .3);
}
.home-spark {
    position: absolute;
    width: 36px;
    height: 36px;
    border-radius: 14px;
    background: linear-gradient(145deg, #dbe5ff, #f6f8ff);
    box-shadow: 0 16px 28px rgba(37, 18, 160, .08);
    transform: rotate(-18deg);
    z-index: 0;
}
.home-spark:after {
    content: "✓";
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-weight: 950;
    font-size: 1.15rem;
    text-shadow: 0 1px 0 rgba(37, 18, 160, .12);
}
.home-spark.one { right: 255px; top: 34px; }
.home-spark.two {
    right: 22px;
    top: 55px;
    width: 32px;
    height: 32px;
    border-radius: 10px;
    transform: rotate(16deg);
}
.home-spark.two:after { content: "□"; font-size: .9rem; color: #c7d2fe; }
.home-phone,
.home-phone-notch,
.home-phone-search,
.home-bubble,
.home-cloud,
.home-mascot,
.home-mascot-arm,
.home-mascot-leg,
.home-mascot-antenna,
.home-mascot-face,
.home-mascot-eye,
.home-spark {
    display: none;
}
.home-side { display: grid; gap: 1rem; }
.home-event {
    min-height: 224px;
    border-radius: 18px;
    background: radial-gradient(circle at 88% 82%, rgba(255, 183, 27, .32), transparent 22%), #24138d;
    color: #fff !important;
    padding: 1.18rem 1.3rem;
    box-shadow: 0 14px 30px rgba(36, 19, 141, .18);
}
.home-event-pill {
    min-height: 28px;
    padding: 0 .72rem;
    border-radius: 999px;
    background: #fff;
    color: #24138d;
    display: inline-flex;
    align-items: center;
    font-size: .62rem;
    font-weight: 950;
}
.home-event h3 {
    margin: .82rem 0 .36rem;
    color: #fff;
    font-size: 1.34rem;
    line-height: 1.26;
    font-weight: 950;
}
.home-event p {
    margin: 0;
    color: rgba(255,255,255,.82);
    font-size: .72rem;
    font-weight: 750;
}
.home-event-button {
    margin-top: .9rem;
    min-height: 32px;
    padding: 0 .9rem;
    border-radius: 999px;
    background: #fff;
    color: #24138d;
    display: inline-flex;
    align-items: center;
    font-size: .72rem;
    font-weight: 950;
}
.home-find {
    min-height: 134px;
    border: 1px solid #e5edf7;
    border-radius: 16px;
    background-color: #f8fbff;
    background-repeat: no-repeat;
    background-size: 100% 100%;
    background-position: center center;
    padding: .58rem .86rem .6rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: .48rem;
    box-shadow: 0 10px 24px rgba(15, 23, 42, .04);
    overflow: hidden;
    position: relative;
}
.home-find:before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(255,255,255,.96) 0%, rgba(255,255,255,.88) 43%, rgba(255,255,255,.36) 67%, rgba(255,255,255,.05) 100%);
    pointer-events: none;
}
.home-find-copy,
.home-find-chat { position: relative; z-index: 1; }
.home-find-copy { width: 62%; min-width: 0; }
.home-find strong { display: block; font-size: .9rem; font-weight: 950; }
.home-find span { display: block; margin-top: .18rem; color: #64748b; font-size: .62rem; font-weight: 800; }
.home-find-chat {
    width: min(84%, 470px);
    max-width: calc(100% - 88px);
}
.home-find-input {
    width: 100%;
    height: 34px;
    border: 1px solid #dbe5f0;
    border-radius: 999px;
    background: #fff;
    color: #111827;
    font: 800 .62rem/1.2 "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
    padding: 0 2.7rem 0 .82rem;
    outline: none;
    box-sizing: border-box;
    box-shadow: inset 0 1px 0 rgba(15, 23, 42, .03);
}
.home-find-input::placeholder { color: #94a3b8; }
.home-find-input:focus {
    border-color: #f5b51b;
    box-shadow: 0 0 0 3px rgba(245, 181, 27, .14);
}
.home-find-icon {
    position: absolute;
    right: 4px;
    top: 50%;
    transform: translateY(-50%);
    width: 28px;
    height: 28px;
    border: 0;
    border-radius: 999px;
    background: #ffb71b;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 1rem;
    font-weight: 950;
    cursor: pointer;
    box-shadow: 0 6px 14px rgba(245, 181, 27, .24);
}
.home-find-icon:hover { background: #2512a0; color: #fff; }
.home-section {
    margin-top: 1rem;
    border: 1px solid #e5edf7;
    border-radius: 18px;
    background: rgba(255,255,255,.96);
    box-shadow: 0 10px 24px rgba(15, 23, 42, .04);
    padding: 1.05rem 1.2rem;
}
.home-section-head {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: .48rem;
    margin-bottom: .78rem;
}
.home-section-title { font-size: .98rem; font-weight: 950; }
.home-more { color: #64748b !important; font-size: .68rem; font-weight: 900; }
.home-feature-row { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: .72rem; }
.home-feature, .home-info {
    border: 1px solid #e7edf5;
    border-radius: 14px;
    background: #fff;
    display: flex;
    align-items: center;
    gap: .72rem;
    padding: .82rem .9rem;
    min-width: 0;
}
.home-feature { min-height: 74px; }
.home-feature-img {
    width: 42px;
    height: 42px;
    border-radius: 13px;
    flex: 0 0 42px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #f3f7ff;
    overflow: hidden;
    box-shadow: inset 0 0 0 1px rgba(219, 229, 240, .7);
}
.home-feature-img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scale(1.45);
}
.home-info {
    gap: .26rem;
    padding: .5rem .42rem;
}
.home-icon {
    width: 40px;
    height: 40px;
    border-radius: 14px;
    background: linear-gradient(145deg, #ffffff, #eef4ff);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.55rem;
    flex: 0 0 40px;
    font-weight: 950;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.92), 0 9px 18px rgba(15, 23, 42, .08);
}
.home-info .home-icon {
    width: 28px;
    height: 28px;
    flex-basis: 28px;
    border-radius: 9px;
    font-size: 1rem;
}
.home-info .home-icon svg {
    width: 21px;
    height: 21px;
}
.home-icon svg {
    width: 23px;
    height: 23px;
    stroke: currentColor;
    stroke-width: 2.2;
    fill: none;
}
.home-icon .filled {
    fill: currentColor;
    stroke: none;
}
.home-icon-blue { background: linear-gradient(145deg, #f8fbff, #dbeafe); color: #2563eb; }
.home-icon-ai { background: linear-gradient(145deg, #eef6ff, #dbeafe 48%, #e0e7ff); color: #2563eb; }
.home-icon-indigo { background: linear-gradient(145deg, #fafaff, #e0e7ff); color: #4338ca; }
.home-icon-violet { background: linear-gradient(145deg, #fdf7ff, #f3e8ff); color: #7c3aed; }
.home-icon-green { background: linear-gradient(145deg, #f7fffb, #d1fae5); color: #059669; }
.home-icon-rose { background: linear-gradient(145deg, #fffafa, #ffe4e6); color: #e11d48; }
.home-icon-amber { background: linear-gradient(145deg, #fffdf5, #fef3c7); color: #d97706; }
.home-icon-cyan { background: linear-gradient(145deg, #f7fdff, #cffafe); color: #0891b2; }
.home-icon-slate { background: linear-gradient(145deg, #ffffff, #f1f5f9); color: #475569; }
.home-feature > div:last-child,
.home-info > div:last-child {
    min-width: 0;
}
.home-feature strong,
.home-info strong {
    display: block;
    font-size: .9rem;
    font-weight: 950;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.home-info strong {
    font-size: .5rem;
}
.home-feature span,
.home-info span {
    display: block;
    margin-top: .24rem;
    color: #64748b;
    font-size: .72rem;
    font-weight: 800;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.home-info span {
    font-size: .4rem;
}
.home-content-grid { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(320px, .95fr); gap: 1rem; margin-top: 1rem; }
.home-info-tabs { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: .55rem; padding-bottom: 1.05rem; border-bottom: 1px solid #edf2f7; }
.home-info-tab {
    min-height: 86px;
    border: 1px solid #e5edf7;
    border-radius: 14px;
    background: #fff;
    display: flex;
    align-items: center;
    gap: .5rem;
    padding: .86rem .62rem;
    text-decoration: none !important;
    color: #0f172a !important;
    box-shadow: 0 8px 18px rgba(15, 23, 42, .035);
}
.home-info-tab:hover { border-color: #f4b21b; background: #fffaf0; }
.home-info-tab-icon {
    width: 30px;
    height: 30px;
    flex: 0 0 30px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    background: #eef4ff;
}
.home-info-tab strong { display:block; font-size:.82rem; font-weight:950; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.home-info-tab span { display:block; margin-top:.16rem; color:#64748b; font-size:.64rem; font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.home-rank-list { display: grid; grid-template-columns: 1fr 1fr; gap: .88rem .7rem; margin-top: 1.05rem; }
.home-rank-card {
    display: grid;
    grid-template-columns: 26px minmax(0, 1fr) auto;
    align-items: center;
    gap: .45rem;
    min-height: 72px;
    border-bottom: 1px solid #f1f5f9;
    color: #1e293b !important;
    text-decoration: none !important;
}
.home-rank-no {
    width: 22px;
    height: 22px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #eef4ff;
    color: #2512a0;
    font-size: .6rem;
    font-weight: 950;
}
.home-rank-card strong { display:block; font-size:.84rem; font-weight:900; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.home-rank-card span { color:#64748b; font-size:.64rem; font-weight:850; white-space:nowrap; }
.home-rank-ask {
    border: 1px solid #dbe6f3;
    background: #f8fafc;
    color: #0f172a !important;
    border-radius: 999px;
    padding: .22rem .45rem;
    font-size: .62rem;
    font-weight: 950;
    white-space: nowrap;
}
.home-notice-list { display: grid; gap: .86rem; }
.home-notice {
    display: grid;
    grid-template-columns: 62px minmax(0, 1fr) 74px;
    align-items: center;
    gap: .7rem;
    font-size: .9rem;
    font-weight: 850;
    min-height: 40px;
}
.home-badge {
    min-height: 24px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #eef4ff;
    color: #2512a0;
    font-size: .7rem;
    font-weight: 950;
}
.home-date { color: #94a3b8; font-size: .8rem; text-align: right; }
.home-banner-carousel {
    position: relative;
    margin-top: .85rem;
    width: 100%;
    height: 188px;
    border: 1px solid #e5edf7;
    border-radius: 16px;
    overflow: hidden;
    background: #fff;
    box-shadow: 0 10px 24px rgba(15, 23, 42, .04);
}
.home-banner-carousel input { display: none; }
.home-banner-track {
    display: flex;
    width: 300%;
    height: 100%;
    transition: transform .42s ease;
    animation: homeBannerAuto 12s infinite;
}
.home-banner-slide {
    width: 33.3333%;
    height: 100%;
    overflow: hidden;
}
.home-banner-slide img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: contain;
    background: #fff;
}
.home-banner-arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 5;
    border: 0;
    background: transparent;
    color: #0f172a;
    font-size: 1.35rem;
    line-height: 1;
    font-weight: 950;
    padding: .2rem .35rem;
    cursor: pointer;
    text-decoration: none !important;
    text-shadow: 0 1px 5px rgba(255,255,255,.85);
}
.home-banner-prev { left: .4rem; }
.home-banner-next { right: .4rem; }
.home-banner-dotbar {
    position: absolute;
    left: 50%;
    bottom: .35rem;
    transform: translateX(-50%);
    display: flex;
    gap: .28rem;
    z-index: 4;
}
.home-banner-dotbar span {
    width: 5px;
    height: 5px;
    border-radius: 999px;
    background: rgba(37,18,160,.22);
}
.home-banner-dotbar span:nth-child(1) { background: #2512a0; width: 14px; }
#home-banner-1:checked ~ .home-banner-track { transform: translateX(0); animation: none; }
#home-banner-2:checked ~ .home-banner-track { transform: translateX(-33.3333%); animation: none; }
#home-banner-3:checked ~ .home-banner-track { transform: translateX(-66.6667%); animation: none; }
#home-banner-1:checked ~ .home-banner-dotbar span:nth-child(1),
#home-banner-2:checked ~ .home-banner-dotbar span:nth-child(2),
#home-banner-3:checked ~ .home-banner-dotbar span:nth-child(3) { background: #2512a0; width: 14px; }
#home-banner-2:checked ~ .home-banner-dotbar span:nth-child(1),
#home-banner-3:checked ~ .home-banner-dotbar span:nth-child(1) { background: rgba(37,18,160,.22); width: 5px; }
.home-banner-carousel label { display: none; }
#home-banner-1:checked ~ .home-banner-prev-1,
#home-banner-1:checked ~ .home-banner-next-1,
#home-banner-2:checked ~ .home-banner-prev-2,
#home-banner-2:checked ~ .home-banner-next-2,
#home-banner-3:checked ~ .home-banner-prev-3,
#home-banner-3:checked ~ .home-banner-next-3 { display: block; }
@keyframes homeBannerAuto {
    0%, 28% { transform: translateX(0); }
    33%, 61% { transform: translateX(-33.3333%); }
    66%, 94% { transform: translateX(-66.6667%); }
    100% { transform: translateX(0); }
}
.home-banner-frame {
    margin-top: .85rem;
    width: 100%;
    height: 188px;
    border: 0;
    display: block;
    border-radius: 16px;
    background: transparent;
}
.home-bottom {
    margin-top: 1rem;
    border: 1px solid #e5edf7;
    border-radius: 16px;
    background: #fff;
    min-height: 64px;
    display: grid;
    grid-template-columns: 1.2fr repeat(3, 1fr) 1.25fr;
    align-items: center;
    overflow: hidden;
    box-shadow: 0 10px 24px rgba(15, 23, 42, .04);
}
.home-bottom-thumb {
    width: 34px;
    height: 34px;
    flex: 0 0 34px;
    border-radius: 11px;
    background: #f4f8ff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
.home-bottom-thumb img {
    width: 29px;
    height: 29px;
    object-fit: contain;
    display: block;
}
.home-bottom-item {
    height: 100%;
    padding: .68rem .85rem;
    display: flex;
    align-items: center;
    gap: .55rem;
    border-right: 1px solid #edf2f7;
    font-size: .72rem;
    font-weight: 900;
}
.home-bottom-item span { display: block; color: #64748b; font-size: .6rem; margin-top: .16rem; }
.home-socials { justify-content: space-between; }
.home-social-icons { display: flex; gap: .45rem; }
.home-social-icons a {
    width: 24px;
    height: 24px;
    border-radius: 7px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: .62rem;
    font-weight: 950;
    text-decoration: none !important;
}
.home-social-icons svg {
    width: 15px;
    height: 15px;
    fill: currentColor;
}

.home-chat-orb {
    position: fixed;
    right: clamp(0px, 1.2vw, 22px);
    bottom: 96px;
    z-index: 10010;
    width: 78px;
    height: 78px;
    display: block;
    border-radius: 999px;
    background: transparent center / cover no-repeat;
    color: transparent !important;
    text-decoration: none !important;
    box-shadow: none;
    background-color: transparent !important;
    border: 0;
    overflow: hidden;
    transition: transform .2s ease, filter .2s ease;
}
.home-chat-orb::before,
.home-chat-orb::after { display: none !important; content: none !important; }
.home-chat-orb span,
.home-chat-orb small { display: none !important; }
.home-chat-orb:hover { transform: translateY(-2px) scale(1.03); filter: drop-shadow(0 16px 26px rgba(37,18,160,.18)); }
.home-mini-chat-panel {
    position: fixed;
    right: clamp(24px, 4vw, 72px);
    bottom: 42px;
    z-index: 10030;
    width: min(420px, calc(100vw - 34px));
    height: min(500px, calc(100vh - 86px));
    border: 1px solid #dfe7f1;
    border-radius: 22px;
    overflow: hidden;
    background: #fff;
    box-shadow: 0 18px 50px rgba(15,23,42,.20);
    display: none;
}
#lina-home-mini-chat:target {
    display: block;
}
.home-mini-chat-head {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 1rem;
    background: #24138d;
    color: #fff;
    font-weight: 950;
}
.home-mini-chat-head button,
.home-mini-chat-close {
    width: 2rem;
    height: 2rem;
    border: 1px solid rgba(255,255,255,.28);
    border-radius: 999px;
    background: rgba(255,255,255,.16);
    color: #fff;
    font-size: 1.2rem;
    font-weight: 950;
    cursor: pointer;
    display:flex;
    align-items:center;
    justify-content:center;
    text-decoration:none !important;
}
.home-mini-chat-frame {
    display: block;
    width: 100%;
    height: calc(100% - 64px);
    border: 0;
    background: #fff;
    overflow: auto;
}
@media (max-width: 1380px) {
    .home-shell {
        padding-left: clamp(40px, 6vw, 84px);
        padding-right: clamp(40px, 6vw, 84px);
    }
}
@media (max-width: 980px) {
    .home-shell {
        width: 100%;
        margin-left: 0;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .home-grid,
    .home-content-grid,
    .home-feature-row,
    .home-info-row,
    .home-bottom {
        grid-template-columns: 1fr;
    }
    .home-grid {
        gap: .9rem;
    }
    .home-hero {
        --home-hero-action-width: 100%;
        min-height: auto;
        padding: 1.45rem 1rem 1.15rem;
        border-radius: 18px;
        display: flex;
        flex-direction: column;
        gap: .78rem;
    }
    .home-hero-art {
        background-size: cover;
        background-position: 58% center;
        opacity: .88;
    }
    .home-hero-art:after {
        background: linear-gradient(90deg, rgba(234,240,253,.96) 0%, rgba(234,240,253,.86) 52%, rgba(234,240,253,.34) 100%);
    }
    .home-hero h1 {
        font-size: clamp(1.72rem, 10.5vw, 2.25rem);
        line-height: 1.13;
        max-width: 92%;
    }
    .home-hero-sub {
        margin-top: 0;
        font-size: clamp(.82rem, 4vw, .98rem);
        max-width: 90%;
    }
    .home-search {
        position: static !important;
        left: auto !important;
        bottom: auto !important;
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
        min-height: 48px;
        order: 3;
        padding: .42rem .38rem .42rem .95rem;
        font-size: clamp(.82rem, 3.8vw, .92rem);
        line-height: 1.35;
    }
    .home-search > span:first-child {
        padding-left: 0;
        text-align: center;
    }
    .home-search-go {
        width: 34px;
        height: 34px;
        flex-basis: 34px;
    }
    .home-tags {
        position: static !important;
        left: auto !important;
        bottom: auto !important;
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
        justify-content: flex-start;
        order: 4;
        gap: .44rem;
    }
    .home-tags span {
        min-height: 30px;
        padding: 0 .7rem;
        font-size: .76rem;
    }
    .home-phone,
    .home-mascot {
        opacity: .18;
    }
    .home-side-card,
    .home-ai-card,
    .home-section {
        border-radius: 16px;
    }
    .home-feature-row {
        gap: .6rem;
    }
}
@media (max-width: 430px) {
    .home-shell {
        padding-left: .8rem;
        padding-right: .8rem;
    }
    .home-hero {
        padding-left: .86rem;
        padding-right: .86rem;
    }
    .home-tags span {
        width: 100%;
        justify-content: center;
    }
}
</style>
        """
    )
    _html(
        f"""
<style>
.home-hero-art {{
    background-image: url("{hero_illustration_uri}");
}}
.home-find {{
    background-image: url("{dictionary_card_bg_uri}");
}}
.home-chat-orb {{
    background-image: url("{chat_orb_uri}");
}}
</style>
        """
    )

    _html(
        """
<a class="home-chat-orb" href="?feature=home&mini_chat=1" target="_self" aria-label="라이나 궁금톡 열기"><span>궁금톡</span></a>
<div id="lina-home-mini-chat" class="home-mini-chat-panel">
    <div class="home-mini-chat-head">
        <strong>라이나 궁금톡</strong>
        <a class="home-mini-chat-close" href="#" aria-label="상담창 닫기">×</a>
    </div>
    <iframe class="home-mini-chat-frame" src="?feature=lina_faq_ai&amp;mini_embed=1&amp;chat=1" scrolling="yes" title="라이나 궁금톡"></iframe>
</div>
<div class="home-shell">
    <div class="home-grid">
        <div class="home-hero">
            <div class="home-hero-art"></div>
            <h1>어떨 때 받을 수 있지?<br>어떨 때 <strong>못</strong> 받지?</h1>
            <div class="home-hero-sub">보험, 약관까지 쉽게 이해하는 라이나 약관 AI</div>
            <a class="home-search" href="?feature=policy_graph_rag" target="_self">
                <span>약관이나 보장 조건에 대해 궁금한 점을 물어보세요.</span>
                <span class="home-search-go">&gt;</span>
            </a>
            <div class="home-tags">
                <span>암보험 면책기간 &gt;</span>
                <span>치아보험 임플란트 보장 &gt;</span>
                <span>감액기간 &gt;</span>
                <span>보험금 청구 서류 &gt;</span>
            </div>
            <div class="home-spark one"></div>
            <div class="home-spark two"></div>
            <div class="home-cloud"></div>
            <div class="home-bubble"></div>
            <div class="home-phone"><span>LINA HUB</span></div>
            <div class="home-phone-notch"></div>
            <div class="home-phone-search"></div>
            <div class="home-mascot-antenna"></div>
            <div class="home-mascot-arm"></div>
            <div class="home-mascot-leg"></div>
            <div class="home-mascot"></div>
            <div class="home-mascot-face"></div>
            <div class="home-mascot-eye"></div>
        </div>
        <div class="home-side">
            <a class="home-event" href="https://direct.lina.co.kr/event" target="_blank" rel="noopener noreferrer">
                <span class="home-event-pill">EVENT</span>
                <h3>다이렉트 보험<br>신규 가입 혜택!</h3>
                <p>다양한 이벤트와 혜택을 확인하세요</p>
                <span class="home-event-button">자세히 보기</span>
            </a>
            <form class="home-find" action="" method="get">
                <input type="hidden" name="feature" value="dictionary">
                <div class="home-find-copy">
                    <strong>AI보험용어사전</strong>
                    <span>궁금한 보험용어를 바로 물어보세요</span>
                </div>
                <div class="home-find-chat">
                    <input class="home-find-input" type="text" name="dictionary_q" placeholder="예: 보험금과 보험료 차이가 뭐야?" autocomplete="off" required>
                    <button class="home-find-icon" type="submit" aria-label="AI보험용어사전에서 검색">↑</button>
                </div>
            </form>
        </div>
    </div>
</div>
        """
    )

    _html(
        f"""
<div class="home-shell">
    <div class="home-section">
        <div class="home-section-head"><div class="home-section-title">오늘의 추천 기능</div></div>
        <div class="home-feature-row">
            {recommendation_cards}
        </div>
    </div>
</div>
        """
    )

    _html(
        f"""
<div class="home-shell">
    <div class="home-content-grid">
        <div class="home-section" style="margin-top:0;">
            <div class="home-section-head">
                <div class="home-section-title">많이 찾는 보험 정보</div>
                <a class="home-more" href="?feature=policy_graph_rag" target="_self">더보기 &gt;</a>
            </div>
            <div class="home-info-tabs">
                <a class="home-info-tab" href="?feature=policy_graph_rag" target="_self"><div class="home-info-tab-icon" style="background:#eef4ff;">💰</div><div><strong>받을 수 있나요?</strong><span>보장·보험금</span></div></a>
                <a class="home-info-tab" href="?feature=policy_graph_rag" target="_self"><div class="home-info-tab-icon" style="background:#fff7ed;">🚫</div><div><strong>못 받는 경우</strong><span>면책·제외사항</span></div></a>
                <a class="home-info-tab" href="?feature=dictionary" target="_self"><div class="home-info-tab-icon" style="background:#ecfdf5;">🔁</div><div><strong>납입·해지</strong><span>보험료·환급</span></div></a>
                <a class="home-info-tab" href="?feature=policy_graph_rag" target="_self"><div class="home-info-tab-icon" style="background:#f5f3ff;">📄</div><div><strong>청구 서류</strong><span>준비·절차</span></div></a>
                <a class="home-info-tab" href="?feature=policy_graph_rag" target="_self"><div class="home-info-tab-icon" style="background:#ecfeff;">🦷</div><div><strong>치아·건강</strong><span>특약·조건</span></div></a>
            </div>
            <div class="home-section-head" style="margin-top:.9rem;">
                <div class="home-section-title">자주 묻는 질문 TOP 6</div>
                <a class="home-more" href="?feature=lina_faq_ai" target="_self">더보기 &gt;</a>
            </div>
            <div class="home-rank-list">
                <a class="home-rank-card" href="?feature=lina_faq_ai&faq_q=%ED%95%B4%EC%95%BD%ED%99%98%EA%B8%89%EA%B8%88%EC%9D%80%20%EC%96%B4%EB%94%94%EC%84%9C%20%EC%A1%B0%ED%9A%8C%ED%95%98%EB%82%98%EC%9A%94%3F" target="_self"><span class="home-rank-no">1</span><div><strong>해약환급금은 어디서 조회하나요?</strong><span>해지·환급 조회</span></div><span class="home-rank-ask">질문</span></a>
                <a class="home-rank-card" href="?feature=lina_faq_ai&faq_q=%EC%B9%98%EC%95%84%EB%B3%B4%ED%97%98%EA%B8%88%20%EC%B2%AD%EA%B5%AC%EC%8B%9C%20%ED%95%84%EC%9A%94%ED%95%9C%20%EC%84%9C%EB%A5%98%EB%8A%94%20%EB%AC%B4%EC%97%87%EC%9D%B4%20%EC%9E%88%EB%82%98%EC%9A%94%3F" target="_self"><span class="home-rank-no">2</span><div><strong>치아보험금 청구시 필요한 서류는 무엇이 있나요?</strong><span>청구 서류 확인</span></div><span class="home-rank-ask">질문</span></a>
                <a class="home-rank-card" href="?feature=lina_faq_ai&faq_q=%EC%98%A8%EB%9D%BC%EC%9D%B8%EC%9C%BC%EB%A1%9C%20%EB%B3%B4%ED%97%98%EA%B8%88%20%EC%B2%AD%EA%B5%AC%ED%95%98%EB%8A%94%20%EB%B0%A9%EB%B2%95%EC%9D%80%3F" target="_self"><span class="home-rank-no">3</span><div><strong>온라인으로 보험금 청구하는 방법은?</strong><span>온라인 청구 절차</span></div><span class="home-rank-ask">질문</span></a>
                <a class="home-rank-card" href="?feature=lina_faq_ai&faq_q=%EB%B3%B4%ED%97%98%EB%A3%8C%EB%A5%BC%20%EC%96%BC%EB%A7%88%EB%82%98%20%EB%AF%B8%EB%82%A9%ED%95%98%EB%A9%B4%20%EC%8B%A4%ED%9A%A8%28%ED%95%B4%EC%A7%80%29%EA%B0%80%20%EB%90%98%EB%82%98%EC%9A%94%3F" target="_self"><span class="home-rank-no">4</span><div><strong>보험료를 얼마나 미납하면 실효(해지)가 되나요?</strong><span>납입·실효 안내</span></div><span class="home-rank-ask">질문</span></a>
                <a class="home-rank-card" href="?feature=lina_faq_ai&faq_q=%EB%B3%B4%ED%97%98%EB%A3%8C%20%EB%82%A9%EC%9E%85%20%EC%B9%B4%EB%93%9C%EB%A5%BC%20%EB%B3%80%EA%B2%BD%ED%95%98%EA%B3%A0%20%EC%8B%B6%EC%96%B4%EC%9A%94" target="_self"><span class="home-rank-no">5</span><div><strong>보험료 납입 카드를 변경하고 싶어요</strong><span>납입 카드 변경</span></div><span class="home-rank-ask">질문</span></a>
                <a class="home-rank-card" href="?feature=lina_faq_ai&faq_q=%EB%B3%B8%EC%9D%B8%20%EC%9D%B8%EC%A6%9D%EC%9D%B4%20%EB%84%88%EB%AC%B4%20%EB%A7%8E%EC%95%84%EC%9A%94" target="_self"><span class="home-rank-no">6</span><div><strong>본인 인증이 너무 많아요</strong><span>인증 문의</span></div><span class="home-rank-ask">질문</span></a>
            </div>
        </div>
        <div>
            <div class="home-section" style="margin-top:0;">
                <div class="home-section-head">
                    <div class="home-section-title">공지사항</div>
                    <a class="home-more" href="https://www.lina.co.kr/customer/notice" target="_blank" rel="noopener noreferrer">더보기 &gt;</a>
                </div>
                <div class="home-notice-list">
                    <div class="home-notice"><span class="home-badge">EVENT</span><span>다이렉트 보험 신규 가입 이벤트</span><span class="home-date">2026-06-01</span></div>
                    <div class="home-notice"><span class="home-badge" style="background:#f1f5f9;color:#64748b;">안내</span><span>26년 6월 24일 - 시스템 점검 일정 안내</span><span class="home-date">2026-06-16</span></div>
                    <div class="home-notice"><span class="home-badge" style="background:#f1f5f9;color:#64748b;">안내</span><span>안정적 서비스 제공을 위한 시스템 점검 일정 안내</span><span class="home-date">2026-05-06</span></div>
                    <div class="home-notice"><span class="home-badge" style="background:#f1f5f9;color:#64748b;">안내</span><span>[라이나생명] 휴면보험금 출연예정 안내</span><span class="home-date">2026-05-06</span></div>
                </div>
            </div>
            <iframe class="home-banner-frame" title="라이나 홈페이지 배너" srcdoc="{homepage_banner_srcdoc}"></iframe>
        </div>
    </div>
</div>
        """
    )

    _html(
        f"""
<div class="home-shell">
    <div class="home-bottom">
        <div class="home-bottom-item"><strong>고객센터&nbsp;&nbsp;1588-0058</strong><span>평일 09:00 ~ 18:00</span></div>
        <a class="home-bottom-item" href="https://www.lina.co.kr/customer/consult" target="_blank"><div class="home-bottom-thumb"><img src="{bottom_icon_uris['chatbot']}" alt="챗봇 상담"></div><div><strong>챗봇 상담</strong><span>24시간 운영</span></div></a>
        <a class="home-bottom-item" href="https://www.lina.co.kr/customer/consult" target="_blank"><div class="home-bottom-thumb"><img src="{bottom_icon_uris['one_to_one']}" alt="1:1 문의"></div><div><strong>1:1 문의</strong><span>빠른 상담 접수</span></div></a>
        <a class="home-bottom-item" href="https://www.lina.co.kr" target="_blank"><div class="home-bottom-thumb"><img src="{bottom_icon_uris['branch']}" alt="지점/서비스 찾기"></div><div><strong>지점/서비스 찾기</strong><span>가까운 지점 안내</span></div></a>
        <div class="home-bottom-item home-socials">
            <strong>라이나생명 공식 채널</strong>
            <div class="home-social-icons"><a style="background:#ef4444;" aria-label="라이나생명 공식 유튜브" href="https://www.youtube.com/channel/UCIkZUiFqcEO07SUmdN61w9w" target="_blank" rel="noopener noreferrer"><svg viewBox="0 0 24 24"><path d="M22 12s0-3.4-.44-5.04c-.25-.9-.95-1.6-1.84-1.84C18.08 4.68 12 4.68 12 4.68s-6.08 0-7.72.44c-.89.24-1.59.94-1.84 1.84C2 8.6 2 12 2 12s0 3.4.44 5.04c.25.9.95 1.6 1.84 1.84 1.64.44 7.72.44 7.72.44s6.08 0 7.72-.44c.89-.24 1.59-.94 1.84-1.84C22 15.4 22 12 22 12zM10 15.2V8.8l5.4 3.2z"/></svg></a><a style="background:#03c75a;" aria-label="라이나생명 네이버 블로그" href="https://blog.naver.com/lina_insurance" target="_blank" rel="noopener noreferrer"><svg viewBox="0 0 24 24"><path d="M5 5h4.1l5.8 8.3V5H19v14h-4.1L9.1 10.7V19H5z"/></svg></a><a style="background:linear-gradient(135deg,#f9ce34,#ee2a7b,#6228d7);" aria-label="라이나생명 공식 인스타그램" href="https://www.instagram.com/linalife_official/" target="_blank" rel="noopener noreferrer"><svg viewBox="0 0 24 24"><path d="M7.5 2h9A5.5 5.5 0 0 1 22 7.5v9a5.5 5.5 0 0 1-5.5 5.5h-9A5.5 5.5 0 0 1 2 16.5v-9A5.5 5.5 0 0 1 7.5 2zm0 2A3.5 3.5 0 0 0 4 7.5v9A3.5 3.5 0 0 0 7.5 20h9a3.5 3.5 0 0 0 3.5-3.5v-9A3.5 3.5 0 0 0 16.5 4zM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6zm5.25-2.2a1.2 1.2 0 1 1 0 2.4 1.2 1.2 0 0 1 0-2.4z"/></svg></a></div>
        </div>
    </div>
</div>
        """
    )






