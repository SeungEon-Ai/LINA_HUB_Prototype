import base64
import html
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
LOGO_MARK = ROOT / "assets" / "lina_mark_color_sharp.png"


def _image_data_uri(path):
    if not path.exists():
        return ""
    suffix = path.suffix.lower()
    mime_type = "image/jpeg" if suffix in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def render_feature_header(title, subtitle=None, logo_path=None, logo_alt="LINA", logo_size=30):
    logo_file = Path(logo_path) if logo_path else LOGO_MARK
    logo_uri = _image_data_uri(logo_file)
    title_html = "".join(f"<span>{part}</span>" for part in title.split(" "))
    logo_html = f'<img class="feature-header-logo" src="{logo_uri}" alt="{logo_alt}">' if logo_uri else ""
    subtitle_html = f'<div class="feature-header-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <style>
        .feature-header-wrap {{
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            min-height: {max(34, int(logo_size) + 2)}px !important;
            margin: 0 0 8px 0 !important;
            padding: 0 !important;
        }}
        .feature-header-logo {{
            width: {int(logo_size)}px !important;
            height: {int(logo_size)}px !important;
            min-width: {int(logo_size)}px !important;
            max-width: {int(logo_size)}px !important;
            object-fit: contain !important;
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .feature-header-title {{
            display: inline-flex !important;
            align-items: center !important;
            gap: 5px !important;
            color: #15202b !important;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif !important;
            font-size: 26px !important;
            font-weight: 900 !important;
            line-height: 34px !important;
            margin: 0 !important;
            padding: 0 !important;
            letter-spacing: 0 !important;
            word-spacing: 0 !important;
            white-space: nowrap !important;
        }}
        .feature-header-title span {{
            display: inline-block !important;
            color: inherit !important;
            font: inherit !important;
            line-height: inherit !important;
            letter-spacing: 0 !important;
            word-spacing: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .feature-header-subtitle {{
            color: #64748b !important;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif !important;
            font-size: 11px !important;
            font-weight: 400 !important;
            line-height: 20px !important;
            margin: 0 0 16px 0 !important;
            padding: 0 !important;
            letter-spacing: 0 !important;
            word-spacing: 0 !important;
        }}
        </style>
        <div class="feature-header-wrap">
            {logo_html}
            <div class="feature-header-title">{title_html}</div>
        </div>
        {subtitle_html}
        """,
        unsafe_allow_html=True,
    )


def render_feature_banner(banner_path, alt="", compact=False):
    banner_file = Path(banner_path)
    if not banner_file.is_absolute():
        banner_file = ROOT / banner_file
    banner_uri = _image_data_uri(banner_file)
    if not banner_uri:
        return
    alt_html = html.escape(str(alt or "feature banner"), quote=True)
    max_width = "1080px" if compact else "1160px"
    margin_bottom = "8px" if compact else "8px"
    st.markdown(
        f"""
        <style>
        .feature-visual-banner {{
            width: 100% !important;
            max-width: {max_width} !important;
            margin: 0 auto {margin_bottom} auto !important;
            border: 1px solid #dfe7f2 !important;
            border-radius: 24px !important;
            overflow: hidden !important;
            background: #ffffff !important;
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06) !important;
            box-sizing: border-box !important;
        }}
        .feature-visual-banner img {{
            display: block !important;
            width: 100% !important;
            height: auto !important;
            object-fit: contain !important;
        }}
        @media (max-width: 760px) {{
            .feature-visual-banner {{
                border-radius: 16px !important;
                margin-bottom: 8px !important;
            }}
        }}
        </style>
        <div class="feature-visual-banner">
            <img src="{banner_uri}" alt="{alt_html}">
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_intro_card(text):
    text_html = html.escape(" ".join(str(text or "").splitlines()))
    st.markdown(
        f"""
        <style>
        .feature-intro-card {{
            border: 1px solid #dfe7f1 !important;
            border-radius: 18px !important;
            background: #ffffff !important;
            color: #334155 !important;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif !important;
            font-size: 14px !important;
            font-weight: 400 !important;
            line-height: 1.45 !important;
            letter-spacing: 0 !important;
            word-break: keep-all !important;
            overflow-wrap: normal !important;
            padding: 9px 12px !important;
            margin: 0 0 14px 0 !important;
            box-sizing: border-box !important;
        }}
        @media (max-width: 640px) {{
            .feature-intro-card {{
                font-size: 10.5px !important;
                line-height: 1.45 !important;
                padding: 8px 10px !important;
                margin: 0 0 12px 0 !important;
            }}
        }}
        </style>
        <div class="feature-intro-card">{text_html}</div>
        """,
        unsafe_allow_html=True,
    )
