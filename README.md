# LINA HUB

라이나생명 프로젝트용 프로토타입입니다.

Streamlit으로 만든 라이나 HUB 데모 앱입니다. 보험 약관, 보험용어, 고객센터 FAQ, 보험뉴스, 생활형 테스트 기능을 한 화면에서 탐색할 수 있도록 구성했습니다. 최종 발표나 내부 공유에서 바로 실행해볼 수 있도록 홈 화면, 좌측 관심사 메뉴, 우측 이벤트/상담 카드, 기능별 배너와 설명 영역을 맞춰두었습니다.

## 주요 기능

- 홈 화면: 추천 기능, 많이 찾는 보험 정보, 공지사항, 고객센터 바로가기
- AI보험용어사전: 보험용어 검색과 쉬운 설명
- 라이나 약관 AI: 상품약관 PDF 원본 DB와 검색용 인덱스를 기반으로 보장 조건, 면책기간, 감액기간, 제외사항 안내. 근거 카드에서 원문 PDF를 새 탭으로 열 수 있습니다.
- 라이나 궁금톡: 라이나생명 FAQ 기반 상담형 질의응답
- 보험뉴스 한입 AI: 네이버/구글 보험뉴스 수집 및 AI 요약
- 오늘의 직관! 미세먼지는?: 지역별 대기질 조회와 보험 관점 안내
- 라이프타임 계산기, 미래 걱정 유형 테스트, 오늘 한 끼 판정단, 치아 건강점수
- 이벤트 관리 화면: 홈에 보여줄 이벤트 카드 작성 및 이미지 등록

## 폴더 구조

```text
.
├─ app.py                      # Streamlit 진입점
├─ features/                   # 기능별 화면과 로직
├─ assets/                     # 배너, 아이콘, 홈 이미지
├─ data/                       # 앱에서 쓰는 기본 데이터`r`n├─ features/policy_graph_rag/data/policy_pdfs/  # 상품약관 PDF 원본 DB 1407개
├─ .streamlit/
│  ├─ config.toml              # Streamlit 실행 설정
│  └─ secrets.example.toml     # 배포용 secrets 예시
├─ requirements.txt            # Python 패키지 목록
├─ runtime.txt                 # 배포용 Python 버전
└─ README.md
```

`work/`, `outputs/`, 로그 파일, 로컬 secrets 파일은 배포에 필요하지 않아 `.gitignore`에서 제외했습니다.

## 로컬 실행

Python 3.11 기준으로 확인했습니다.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:8501/?feature=home
```

Windows에서 기존 배치 파일을 쓰는 경우에는 프로젝트 폴더에서 `start_streamlit.bat`을 실행해도 됩니다.

## Secrets 설정

AI 기능을 쓰려면 OpenAI API 키가 필요합니다. 키는 GitHub에 올리지 말고 Streamlit Cloud의 **Secrets** 메뉴나 로컬 `.streamlit/local_secrets.toml`에 넣습니다.

```toml
OPENAI_API_KEY = "sk-your-openai-api-key"
```

미세먼지 기능에서 실시간 공공데이터를 쓰려면 공공데이터포털 대기오염정보 조회 서비스 키를 아래 이름 중 하나로 등록합니다.

```toml
AIRKOREA_SERVICE_KEY = "your-data-go-kr-service-key"
```

대체 이름도 지원합니다.

```toml
DATA_GO_KR_SERVICE_KEY = "your-data-go-kr-service-key"
PUBLIC_DATA_SERVICE_KEY = "your-data-go-kr-service-key"
```


## 약관 PDF DB

라이나 약관 AI에는 상품약관 PDF 원본 DB를 함께 포함했습니다.

```text
features/policy_graph_rag/data/policy_pdfs/
features/policy_graph_rag/data/policy_pdf_manifest.csv
features/policy_graph_rag/data/core_policy_graph.json.gz
```

`policy_pdfs/`에는 현재 판매상품 기준 상품약관 PDF 1407개가 들어 있습니다. `core_policy_graph.json.gz`는 앱에서 빠르게 검색하기 위한 인덱스 파일입니다. 발표와 배포에서는 PDF 원본을 함께 보관하되, 화면 응답 속도를 위해 인덱스를 같이 사용합니다. 답변 근거 카드에는 `원문 PDF 열기` 링크가 표시되며, 라이나 원문 PDF를 새 탭에서 확인할 수 있습니다.
## Streamlit Cloud 배포

1. GitHub에 새 repository를 만듭니다.
2. 이 폴더의 파일을 repository에 올립니다.
3. Streamlit Cloud에서 **New app**을 선택합니다.
4. Repository와 branch를 고르고, Main file path는 `app.py`로 지정합니다.
5. Advanced settings 또는 App settings의 Secrets에 필요한 키를 입력합니다.
6. Deploy를 누릅니다.

배포 후 첫 로딩은 패키지 설치와 이미지 로딩 때문에 시간이 조금 걸릴 수 있습니다.

## 배포 전에 확인할 것

- `.streamlit/local_secrets.toml` 또는 `.streamlit/secrets.toml`이 GitHub에 올라가지 않았는지 확인
- `work/`, `outputs/`, `__pycache__/`, 로그 파일이 제외됐는지 확인
- `requirements.txt`가 repository 루트에 있는지 확인`r`n- `features/policy_graph_rag/data/policy_pdfs/`에 상품약관 PDF가 포함됐는지 확인
- Streamlit Cloud Secrets에 `OPENAI_API_KEY`가 들어갔는지 확인
- 보험뉴스와 미세먼지 기능은 외부 네트워크/API 상태에 따라 응답 시간이 달라질 수 있음

## 기능별 URL

```text
/?feature=home
/?feature=dictionary
/?feature=policy_graph_rag
/?feature=lina_faq_ai
/?feature=insurance_news_summary
/?feature=dust_health_check
/?feature=life_expectancy
/?feature=future_worry_test
/?feature=meal_judgement
/?feature=dental_score
/?feature=event
```

## 메모

이 앱은 운영 서비스가 아니라 시연과 검토를 위한 프로토타입입니다. 실제 서비스로 전환할 경우에는 개인정보 처리, 외부 API 장애 대응, 로그 관리, 관리자 권한 분리, 사용량 제한을 별도로 점검해야 합니다.
