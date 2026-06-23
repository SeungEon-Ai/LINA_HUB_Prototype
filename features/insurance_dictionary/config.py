from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FEATURE_NAME = "AI 보험용어 설명 챗봇"
MODEL_NAME = "gpt-4o-mini"
DATA_PATH = ROOT / "outputs" / "combined_insurance_terms_seed_with_life.csv"
LOGO_MARK = ROOT / "assets" / "lina_mark_color_sharp.png"
