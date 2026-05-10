# 뉴스 중심 LLM + API/MCP 가이드 (2026)

> **핵심 스택**: Gemini 2.5 Flash Lite (`GEMINI_API_KEY`) + 공공·민간 API + MCP 서버  
> **목적**: LLM이 외부 데이터로 grounding된 사실 기반 답변·분석을 산출하도록 파이프라인 구축  
> **1차 수집 출처**: [`yybmion/public-apis-4Kr`](https://github.com/yybmion/public-apis-4Kr) (한국 260+), [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers), [`wong2/awesome-mcp-servers`](https://github.com/wong2/awesome-mcp-servers), [`appcypher/awesome-mcp-servers`](https://github.com/appcypher/awesome-mcp-servers), [`tolkonepiu/best-of-mcp-servers`](https://github.com/tolkonepiu/best-of-mcp-servers), [`Koomook/data-go-mcp-servers`](https://github.com/Koomook/data-go-mcp-servers)

> **본 가이드의 URL 검증 표기 (2026-05 기준)**
> 
> -   ✅ **공식 문서·검색결과로 작동 확인** — 안정적
> -   ⚠️ **미검증** — 패턴상 작동 가능성 높음. 사용 전 직접 확인 권장
> -   ❌ **폐지·마이그레이션 확인됨** → 새 엔드포인트 제시

---

## 0\. 빠른 요약

| 레이어 | 역할 | 권장 도구 |
| --- | --- | --- |
| **LLM** | 추론·요약·구조화 | Gemini 2.5 Flash Lite (`gemini-2.5-flash-lite`), 또는 latest alias `gemini-flash-lite-latest` |
| **Grounding 1** | 단순 fact lookup | Function Calling으로 직접 REST API 호출 |
| **Grounding 2** | 도구 모음 표준화 | MCP 서버 (Python `mcp` SDK, FastMCP) |
| **데이터 소스 (한국)** | — | [data.go.kr](https://www.data.go.kr), [KOSIS](https://kosis.kr), [한국은행 ECOS](https://ecos.bok.or.kr), [BIGKINDS](https://www.bigkinds.or.kr), [Open DART](https://opendart.fss.or.kr), [국가법령정보](https://open.law.go.kr) |
| **데이터 소스 (글로벌)** | — | [World Bank](https://data.worldbank.org), [IMF](https://data.imf.org), [OECD](https://data-explorer.oecd.org), [FRED](https://fred.stlouisfed.org), [GDELT](https://www.gdeltproject.org), [Wayback Machine](https://archive.org/web/), [OpenAlex](https://openalex.org), [GNews](https://gnews.io) |
| **배포** | 웹 | FastAPI, Streamlit, Gradio |

---

## 1\. Gemini 2.5 Flash Lite 셋업 (with `.env`)

### 1-1. 모델 선택 근거

-   **속도/비용 최적**: 분류·요약·번역·구조화 추출 등 데이터저널리즘 반복 작업에 적합
-   **함수 호출(Function Calling) 지원**: 외부 API 자동 호출 가능
-   **MCP 클라이언트 내장**: Google GenAI Python SDK가 MCP `ClientSession`을 `tools` 파라미터로 직접 받음 → boilerplate 최소화
-   **대용량 컨텍스트 윈도**: 100만 토큰급 → 긴 기사/문서 일괄 분석 가능
-   모델 ID: `gemini-2.5-flash-lite` 또는 `gemini-flash-lite-latest` (별칭, 최신 버전 자동 추적)

### 1-2. 설치 및 키 발급

```bash
# Python 가상환경 (WSL/Linux 기준)
python -m venv .venv
source .venv/bin/activate

# 새 SDK (구 google-generativeai 아님 — 통합 SDK)
pip install google-genai python-dotenv requests httpx pandas

# MCP를 함께 쓸 경우
pip install "mcp[cli]" fastmcp
```

`.env` 파일 (프로젝트 루트):

```env
GEMINI_API_KEY=AIzaSy...your_key
DATA_GO_KR_KEY=...           # 공공데이터포털 일반인증키 (Decoding)
KOSIS_API_KEY=...
BOK_API_KEY=...              # 한국은행 ECOS
DART_API_KEY=...             # Open DART
BIGKINDS_API_KEY=...
NEWSAPI_KEY=...
TAVILY_API_KEY=...           # 웹검색 grounding용
OPENALEX_API_KEY=...         # ⚠️ 2025-02부터 필수 (무료 발급)
```

API 키는 [Google AI Studio](https://aistudio.google.com/apikey)에서 무료 발급(Tier에 따라 RPM/RPD 제한 있음).

### 1-3. 최소 호출 예제

```python
# basic_call.py
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

resp = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="2024년 한국 합계출산율을 한 문장으로 정리해줘."
)
print(resp.text)
```

> ⚠️ 위 예제는 LLM 내부 지식만 사용 → **할루시네이션 위험**. 데이터저널리즘에서는 반드시 다음 섹션의 grounding 패턴을 사용.

---

## 2\. Function Calling — REST API 직접 호출

### 2-1. 핵심 아이디어

1.  Python 함수를 정의 (실제 데이터 출처 호출)
2.  Gemini에게 함수 목록을 `tools=[...]`로 전달
3.  모델이 필요시 `FunctionCall` 응답 → 실행 → 결과 다시 모델에 주입
4.  Python SDK는 `automatic_function_calling`이 기본 활성화 → 위 루프를 자동 수행

### 2-2. 실전 예제: 한국은행 ECOS + 통계청 KOSIS 통합

```python
# grounded_macro.py
import os, requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
BOK_KEY = os.environ["BOK_API_KEY"]
KOSIS_KEY = os.environ["KOSIS_API_KEY"]

def get_bok_series(stat_code: str, item_code1: str, start: str, end: str, cycle: str = "M") -> str:
    """한국은행 ECOS 통계 시계열 조회.
    Args:
        stat_code: 통계표 코드 (예: '722Y001'=한국은행 기준금리)
        item_code1: 항목코드1
        start: 시작 기간 (YYYYMM 또는 YYYYQ1 등)
        end: 종료 기간
        cycle: 주기 'A'=년 'Q'=분기 'M'=월 'D'=일
    """
    url = (f"https://ecos.bok.or.kr/api/StatisticSearch/{BOK_KEY}/json/kr/1/100/"
           f"{stat_code}/{cycle}/{start}/{end}/{item_code1}")
    return requests.get(url, timeout=10).text[:4000]

def get_kosis_data(orgId: str, tblId: str, prdSe: str, startPrdDe: str, endPrdDe: str) -> str:
    """KOSIS 통계자료 조회 API.
    Args: orgId(기관코드), tblId(통계표ID), prdSe(주기), startPrdDe~endPrdDe(YYYY/YYYYMM)
    """
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    params = dict(method="getList", apiKey=KOSIS_KEY, format="json", jsonVD="Y",
                  orgId=orgId, tblId=tblId, prdSe=prdSe,
                  startPrdDe=startPrdDe, endPrdDe=endPrdDe)
    return requests.get(url, params=params, timeout=10).text[:4000]

resp = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="2023년 1월부터 2024년 12월까지 한국은행 기준금리 변화를 ECOS에서 가져와 표로 정리해줘. stat_code는 722Y001, item_code1은 0101000.",
    config=types.GenerateContentConfig(
        tools=[get_bok_series, get_kosis_data],
        temperature=0,
    ),
)
print(resp.text)
```

### 2-3. Built-in 도구

Gemini에는 자체 내장 도구도 있어 바로 grounding 가능 (무료 API 제한 가능) :

-   `google_search` — Google 검색 grounding (RPD 제한 있음)
-   `url_context` — URL 직접 fetch (URL을 contents에 포함하면 자동)
-   `code_execution` — 모델이 Python 실행 (계산·플로팅)

```python
from google.genai.types import Tool, GoogleSearch, GenerateContentConfig
resp = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="오늘 코스피 종가와 변동률을 알려줘.",
    config=GenerateContentConfig(tools=[Tool(google_search=GoogleSearch())]),
)
```

---

## 3\. 한국 API 카탈로그 (뉴스 중심 우선순위)

> 출처: [`yybmion/public-apis-4Kr`](https://github.com/yybmion/public-apis-4Kr) (2026-02 기준 260+개) + 추가 보강. 대부분 무료, `apiKey` 인증. 강의 우선순위는 ⭐로 표기 (★★★ = 거의 매주 활용 가능).

### 3-1. 정부·공공기관 (탐사보도 코어)

| 기관 | API URL / 안내 페이지 | 인증 | 우선도 |
| --- | --- | --- | --- |
| ✅ [**공공데이터포털 (data.go.kr)**](https://www.data.go.kr/) | [https://www.data.go.kr/](https://www.data.go.kr/) — 10만+ 데이터셋 통합 게이트웨이 | apiKey | ★★★ |
| ✅ [**KOSIS 통계청**](https://kosis.kr) | [https://kosis.kr/serviceInfo/openAPIGuide.do](https://kosis.kr/serviceInfo/openAPIGuide.do) — 134,586종 국가통계 / API base: `https://kosis.kr/openapi/` | apiKey | ★★★ |
| ✅ [**한국은행 ECOS**](https://ecos.bok.or.kr) | [https://ecos.bok.or.kr/api/](https://ecos.bok.or.kr/api/) — 금리·환율·물가 시계열 | apiKey | ★★★ |
| ✅ [**Open DART (금감원)**](https://opendart.fss.or.kr) | [https://opendart.fss.or.kr/](https://opendart.fss.or.kr/) — 상장사 공시·재무 / API base: `https://opendart.fss.or.kr/api/` | apiKey | ★★★ |
| ✅ [**국가법령정보 Open API**](https://open.law.go.kr) | [https://open.law.go.kr/](https://open.law.go.kr/) — 현행 법령·조문 | apiKey | ★★ |
| ✅ [**국가법령정보 판례 API**](https://open.law.go.kr) | [https://open.law.go.kr/](https://open.law.go.kr/) — 법원 판례 전문 | apiKey | ★★ |
| ✅ [**열린국회정보**](https://open.assembly.go.kr) | [https://open.assembly.go.kr/portal/openapi/main.do](https://open.assembly.go.kr/portal/openapi/main.do) — 의원 표결·발의·본회의 | apiKey | ★★★ |
| ⚠️ [**열린재정**](https://www.openfiscaldata.go.kr) | [https://www.openfiscaldata.go.kr/](https://www.openfiscaldata.go.kr/) — 국가·지방 예산·결산·보조금 | apiKey | ★★ |
| ⚠️ [**국가지표통합 지표누리**](https://www.index.go.kr) | [https://www.index.go.kr/unity/openApi/openApiIntro.do](https://www.index.go.kr/unity/openApi/openApiIntro.do) — 국가 통계지표 | apiKey | ★★ |
| ⚠️ [**국토교통부 실거래가**](https://www.molit.go.kr) | [https://www.data.go.kr/dataset/3050988/openapi.do](https://www.data.go.kr/dataset/3050988/openapi.do) — 아파트·오피스텔 실거래 | apiKey | ★★★ |
| ⚠️ [**한국환경공단 에어코리아**](https://www.airkorea.or.kr) | [https://www.data.go.kr/data/15073861/openapi.do](https://www.data.go.kr/data/15073861/openapi.do) — 실시간 미세먼지·대기질 | apiKey | ★★ |
| ⚠️ [**기상청 단기예보**](https://www.kma.go.kr) | [https://www.data.go.kr/data/15084084/openapi.do](https://www.data.go.kr/data/15084084/openapi.do) — 초단기·단기 예보 | apiKey | ★★ |
| ⚠️ [**기상청 API허브**](https://apihub.kma.go.kr) | [https://apihub.kma.go.kr/](https://apihub.kma.go.kr/) — 관측·위성·레이더 등 12종 | apiKey | ★★ |
| ⚠️ [**정부24 공공서비스 API**](https://www.gov.kr) | [https://www.gov.kr/openapi/info](https://www.gov.kr/openapi/info) — 행정정보 실시간 | apiKey | ★ |
| ⚠️ [**국가과학기술정보 NTIS**](https://www.ntis.go.kr) | [https://www.ntis.go.kr/rndopen/api/mng/apiMain.do](https://www.ntis.go.kr/rndopen/api/mng/apiMain.do) — R&D 과제·성과 | apiKey | ★★ |
| ⚠️ [**통계지리정보 SGIS**](https://sgis.kostat.go.kr) | [https://sgis.kostat.go.kr/](https://sgis.kostat.go.kr/) — 행정구역 단위 통계지도 | apiKey | ★★ |
| ⚠️ [**Localdata 인허가**](https://www.localdata.go.kr) | [https://www.localdata.go.kr/](https://www.localdata.go.kr/) — 자치단체 인허가 (`데이터포털 이관 예정`) | apiKey | ★★ |

### 3-2. 뉴스·미디어·콘텐츠

| 기관 | API URL / 안내 | 인증 | 우선도 |
| --- | --- | --- | --- |
| ✅ [**BIGKINDS** (한국언론진흥재단)](https://www.bigkinds.or.kr) | [https://www.bigkinds.or.kr/](https://www.bigkinds.or.kr/) — 뉴스 빅데이터 (54개사+) | apiKey (신청제) | ★★★ |
| ⚠️ [**딥서치 뉴스 API**](https://news.deepsearch.com) | [https://news.deepsearch.com](https://news.deepsearch.com) — 국내 150개·해외 50개 언론사 | apiKey | ★★ |
| ⚠️ [**영화진흥위원회 KOBIS**](https://www.kobis.or.kr) | [https://www.kobis.or.kr/kobisopenapi/homepg/main/main.do](https://www.kobis.or.kr/kobisopenapi/homepg/main/main.do) — 박스오피스·영화·영화인 | apiKey | ★★ |
| ⚠️ [**KOPIS 공연예술**](https://www.kopis.or.kr) | [https://www.kopis.or.kr/](https://www.kopis.or.kr/) — 공연·공연장·예매 통계 | apiKey | ★ |
| ⚠️ [**KMDb 영화상세**](https://www.kmdb.or.kr) | [https://www.kmdb.or.kr/info/api/](https://www.kmdb.or.kr/info/api/) — 한국영화 상세 메타데이터 | apiKey | ★ |
| ⚠️ [**도서관 정보나루**](https://www.data4library.kr) | [https://www.data4library.kr/](https://www.data4library.kr/) — 전국 공공도서관 회원·장서·대출 | apiKey | ★★ |
| ⚠️ [**국립중앙도서관**](https://www.nl.go.kr) | [https://www.nl.go.kr/NL/contents/N31101030700.do](https://www.nl.go.kr/NL/contents/N31101030700.do) — 소장자료·디지털컬렉션 | apiKey | ★ |

> **BIGKINDS 활용 팁**: 한국 뉴스 분석의 사실상 표준 코퍼스. 일반 공개 API는 검색·시계열 위주, 본문 전체는 신청 필요. 강의용으로는 회원가입 후 `news` 검색 → 메타+요약 활용.

### 3-3. 금융·경제

| 기관 | API URL | 인증 |
| --- | --- | --- |
| ✅ [**한국은행 ECOS**](https://ecos.bok.or.kr) | [https://ecos.bok.or.kr/api/](https://ecos.bok.or.kr/api/) — 모든 한은 통계지표 | apiKey |
| ✅ [**Open DART**](https://opendart.fss.or.kr) | [https://opendart.fss.or.kr/](https://opendart.fss.or.kr/) — 공시·재무·지분 | apiKey |
| ⚠️ [**한국투자증권 KIS**](https://www.koreainvestment.com) | [https://apiportal.koreainvestment.com/intro](https://apiportal.koreainvestment.com/intro) — 국내외 시세·주문 | OAuth |
| ⚠️ [**한국수출입은행**](https://www.koreaexim.go.kr) | [https://www.koreaexim.go.kr/ir/HPHKIR019M01](https://www.koreaexim.go.kr/ir/HPHKIR019M01) — 환율·국제금리 | apiKey |
| ⚠️ [**업비트 Open API**](https://upbit.com) | [https://docs.upbit.com/kr](https://docs.upbit.com/kr) — 암호화폐 시세·거래 | JWT |
| ⚠️ [**빗썸 프로 API**](https://www.bithumb.com) | [https://apidocs.bithumb.com/](https://apidocs.bithumb.com/) — 가상자산 거래 | apiKey |
| ⚠️ [**한국부동산원**](https://www.reb.or.kr) | [https://www.reb.or.kr/r-one/portal/openapi/openApiIntroPage.do](https://www.reb.or.kr/r-one/portal/openapi/openApiIntroPage.do) — 부동산 시장통계 | apiKey |
| ⚠️ [**금융결제원 오픈뱅킹**](https://www.kftc.or.kr) | [https://openapi.kftc.or.kr/](https://openapi.kftc.or.kr/) — 19개+ 은행 통합 | OAuth |
| ⚠️ [**CODEF API** (쿠콘)](https://www.codef.io) | [https://developer.codef.io/](https://developer.codef.io/) — 금융·보험·통신 스크래핑 통합 | OAuth |

### 3-4. 의료·보건·안전

| 기관 | API URL | 인증 |
| --- | --- | --- |
| ⚠️ [**건강보험심사평가원**](https://www.hira.or.kr) | [https://opendata.hira.or.kr/](https://opendata.hira.or.kr/) — 의료빅데이터 | apiKey |
| ⚠️ [**국민건강보험공단**](https://www.nhis.or.kr) | [https://www.nhis.or.kr/](https://www.nhis.or.kr/) — 검진·요양시설 | apiKey |
| ⚠️ [**중앙응급의료센터 (E-Gen)**](https://www.e-gen.or.kr) | [https://www.e-gen.or.kr/nemc/open\_api.do](https://www.e-gen.or.kr/nemc/open_api.do) — 병의원·약국·AED | apiKey |
| ⚠️ [**식약처 식품의약품 데이터**](https://www.mfds.go.kr) | [https://data.mfds.go.kr/OPCAA01F01](https://data.mfds.go.kr/OPCAA01F01) — 약품·식품·의료기기 | apiKey |
| ⚠️ [**재난안전데이터 공유플랫폼**](https://www.safetydata.go.kr) | [https://www.safetydata.go.kr/](https://www.safetydata.go.kr/) — 재난·피해통계 | apiKey |
| ⚠️ [**소방청**](https://www.nfa.go.kr) | [https://www.nfa.go.kr/](https://www.nfa.go.kr/) — 화재·구급·소방시설 | apiKey |
| ⚠️ [**안전드림 실종** (경찰청)](https://www.safe182.go.kr) | [https://www.safe182.go.kr/](https://www.safe182.go.kr/) — 실종자 정보 | apiKey |
| ⚠️ [**생활안전정보 SafeMap**](https://safemap.go.kr) | [https://safemap.go.kr/](https://safemap.go.kr/) — 범죄·사고·생활안전시설 | apiKey |

### 3-5. 교통·지도·위치

| 기관 | API URL | 인증 |
| --- | --- | --- |
| ✅ [**카카오맵**](https://map.kakao.com) | [https://apis.map.kakao.com/web/guide/](https://apis.map.kakao.com/web/guide/) — 지도·검색·좌표·경로 | apiKey |
| ✅ [**네이버 지도**](https://map.naver.com) | [https://www.ncloud.com/product/applicationService/maps](https://www.ncloud.com/product/applicationService/maps) — 지도·Geocoding·Direction | apiKey |
| ⚠️ [**브이월드 V-World**](https://www.vworld.kr) | [https://www.vworld.kr/](https://www.vworld.kr/) — 국토부 3D 지도·공간정보 | apiKey |
| ⚠️ [**도로명주소**](https://www.juso.go.kr) | [https://business.juso.go.kr](https://business.juso.go.kr) — 도로명주소 검색·DB | apiKey |
| ⚠️ [**T맵**](https://tmap.life) | [https://openapi.sk.com/](https://openapi.sk.com/) — 내비·경로 | apiKey |
| ⚠️ [**ODsay 대중교통**](https://www.odsay.com) | [https://lab.odsay.com/](https://lab.odsay.com/) — 전국 대중교통·고속·항공 | apiKey |
| ⚠️ [**서울시 지하철 실시간**](https://data.seoul.go.kr) | [https://data.seoul.go.kr/dataList/OA-12764/A/1/datasetView.do](https://data.seoul.go.kr/dataList/OA-12764/A/1/datasetView.do) — 2~8호선 실시간 도착 | apiKey |
| ⚠️ [**서울 버스 도착정보**](https://topis.seoul.go.kr) | [http://api.bus.go.kr/](http://api.bus.go.kr/) — 시내버스 실시간 | apiKey |
| ⚠️ [**한국도로공사**](https://www.ex.co.kr) | [https://www.data.go.kr/data/15076872/openapi.do](https://www.data.go.kr/data/15076872/openapi.do) — 고속도로 실시간 교통량 | apiKey |
| ⚠️ [**레일포털 KRIC**](https://www.kric.go.kr) | [https://data.kric.go.kr/](https://data.kric.go.kr/) — 전국 철도 정보 | apiKey |
| ⚠️ **국내항공운항정보** | [https://www.data.go.kr/data/15098526/openapi.do](https://www.data.go.kr/data/15098526/openapi.do) — 국내선 운항일정 | apiKey |
| ⚠️ [**인천공항 여객운항**](https://www.airport.kr) | [https://www.data.go.kr/data/15095074/openapi.do](https://www.data.go.kr/data/15095074/openapi.do) — 출도착 현황 | apiKey |

### 3-6. 지역별 공공데이터

[서울](https://data.seoul.go.kr) · [부산](https://data.busan.go.kr) · [대구](https://data.daegu.go.kr) · [인천](https://www.incheon.go.kr/data) · [광주](https://data.gwangju.go.kr) · [대전](https://www.daejeon.go.kr/dat) · [울산](https://data.ulsan.go.kr) · [세종](https://www.sejong.go.kr/openapi.do) · [경기](https://data.gg.go.kr) · [강원](https://data.gwd.go.kr) · 충북·충남 · 전북·전남 · 경북·경남 · [제주](https://www.jeju.go.kr/open/open/iopenapi.htm) — 모두 자체 포털 운영. 지역 르포에 필수.

### 3-7. AI·NLP (한국어 특화)

| 서비스 | URL |
| --- | --- |
| ⚠️ [**네이버 CLOVA Studio**](https://clovastudio.ncloud.com) | [https://api.ncloud-docs.com/docs/ai-naver-clovastudio-summary](https://api.ncloud-docs.com/docs/ai-naver-clovastudio-summary) — 한국어 LLM HyperCLOVA X |
| ✅ [**Upstage Solar / Document AI**](https://www.upstage.ai) | [https://developers.upstage.ai/](https://developers.upstage.ai/) — 한국어 LLM·OCR·문서파싱 |
| ✅ [**SKT A.X 4.0**](https://www.sktelecom.com) | [https://github.com/SKT-AI/A.X-4.0](https://github.com/SKT-AI/A.X-4.0) — 한국어 특화 LLM |
| ⚠️ [**ETRI AI Open API**](https://www.etri.re.kr) | [https://epretx.etri.re.kr/](https://epretx.etri.re.kr/) — 형태소·개체명·발음 등 다수 |
| ✅ [**국립국어원 우리말샘**](https://www.korean.go.kr) | [https://opendict.korean.go.kr/](https://opendict.korean.go.kr/) — 표준국어대사전 검색 |
| ✅ [**AI Hub**](https://aihub.or.kr) | [https://aihub.or.kr](https://aihub.or.kr) — AI 학습용 데이터셋 |
| ✅ [**파파고 번역**](https://papago.naver.com) | [https://developers.naver.com/docs/papago/README.md](https://developers.naver.com/docs/papago/README.md) — 신경망 기반 번역 |

### 3-8. 검색·소셜

| 서비스 | URL |
| --- | --- |
| ✅ [**네이버 검색**](https://developers.naver.com) | [https://developers.naver.com/products/service-api/search/search.md](https://developers.naver.com/products/service-api/search/search.md) — 블로그·뉴스·이미지·웹·카페 통합 검색 (★★★) |
| ✅ [**네이버 데이터랩 검색어트렌드**](https://datalab.naver.com) | [https://developers.naver.com/docs/serviceapi/datalab/search/search.md](https://developers.naver.com/docs/serviceapi/datalab/search/search.md) — 통합검색어 트렌드 (★★) |
| ✅ [**네이버 데이터랩 쇼핑인사이트**](https://datalab.naver.com) | [https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md) — 쇼핑 카테고리 트렌드 |
| ✅ [**카카오 검색**](https://developers.kakao.com) | [https://developers.kakao.com/docs/latest/ko/daum-search/common](https://developers.kakao.com/docs/latest/ko/daum-search/common) — 다음 검색 (웹·이미지·동영상·블로그) |

> **데이터저널리즘 강의 핵심 5종**:
> 
> 1.  **[공공데이터포털](https://www.data.go.kr)** — 인허가, 행정 데이터 일반 접근
> 2.  **[KOSIS](https://kosis.kr)** — 인구·고용·물가 시계열
> 3.  **[한국은행 ECOS](https://ecos.bok.or.kr)** — 거시경제
> 4.  **[Open DART](https://opendart.fss.or.kr)** — 기업
> 5.  **[BIGKINDS](https://www.bigkinds.or.kr) + [네이버 검색](https://developers.naver.com)** — 뉴스 코퍼스

---

## 4\. 글로벌 API 카탈로그

### 4-1. 거시경제·개발지표

| 기관 | API URL | 인증 |
| --- | --- | --- |
| ✅ [**World Bank Open Data**](https://data.worldbank.org) | [https://api.worldbank.org/v2/](https://api.worldbank.org/v2/) — 200개국 1,400+ 지표. 예: [`/country/KOR/indicator/NY.GDP.MKTP.CD?format=json`](https://api.worldbank.org/v2/country/KOR/indicator/NY.GDP.MKTP.CD?format=json) | 불필요 |
| ✅ [**IMF DataMapper**](https://www.imf.org/external/datamapper/) | [https://www.imf.org/external/datamapper/api/v2/](https://www.imf.org/external/datamapper/api/v2/) — **주의: v2** (사용자 자료의 v1은 구버전). 도움말: [https://www.imf.org/external/datamapper/api/help](https://www.imf.org/external/datamapper/api/help) | 불필요 |
| ✅ [**IMF Data (SDMX 3.0)**](https://data.imf.org) | [https://data.imf.org](https://data.imf.org) — **2025-11-05 기존 dataservices.imf.org 폐쇄**, 신 SDMX 3.0 API로 마이그레이션. 안내: [https://data.imf.org/en/Resource-Pages/IMF-API](https://data.imf.org/en/Resource-Pages/IMF-API) | 불필요 |
| ❌ [**OECD (OECD.Stat)**](https://www.oecd.org) | `https://stats.oecd.org/SDMX-JSON/data/` **2024-07-01 폐쇄됨** → 신 엔드포인트: [`https://sdmx.oecd.org/public/rest/data/`](https://sdmx.oecd.org/public/rest/data/) (OECD Data Explorer). 데이터 탐색: [https://data-explorer.oecd.org/](https://data-explorer.oecd.org/) | 불필요 |
| ✅ [**FRED (St. Louis Fed)**](https://fred.stlouisfed.org) | [https://api.stlouisfed.org/fred/](https://api.stlouisfed.org/fred/) — 80만+ 시계열 | apiKey 무료 |
| ✅ [**Eurostat**](https://ec.europa.eu/eurostat) | [https://ec.europa.eu/eurostat/web/main/data/web-services](https://ec.europa.eu/eurostat/web/main/data/web-services) — EU 통계 | 불필요 |
| ⚠️ [**UN Data**](https://data.un.org) / [**UN Comtrade**](https://comtradeplus.un.org) | [https://data.un.org](https://data.un.org) / [https://comtradeplus.un.org/](https://comtradeplus.un.org/) — 인구·무역 | 불필요 / apiKey |

```python
# 예: World Bank — 한국 GDP (currency current US$) (✅ 검증된 v2 엔드포인트)
import requests
url = "https://api.worldbank.org/v2/country/KOR/indicator/NY.GDP.MKTP.CD?format=json&per_page=50"
data = requests.get(url, timeout=10).json()
```

```python
# 예: OECD — 신 엔드포인트 (sdmx.oecd.org)
import requests
# 한국 실업률 (월별, 2023년 이후)
url = ("https://sdmx.oecd.org/public/rest/data/"
       "OECD.SDD.TPS,DSD_LFS@DF_IALFS_UNE_M,1.0/"
       "KOR..PT_LF_SUB._Z.Y._T.Y_GE15..M"
       "?startPeriod=2023-01&dimensionAtObservation=AllDimensions"
       "&format=csvfilewithlabels")
data = requests.get(url, timeout=15).text
```

### 4-2. 뉴스·미디어 분석

| 서비스 | URL | 비고 |
| --- | --- | --- |
| ✅ [**GDELT 2.0**](https://www.gdeltproject.org) | [https://api.gdeltproject.org/api/v2/](https://api.gdeltproject.org/api/v2/) (Doc/Event/GKG API) | 100+ 언어, 거의 실시간 글로벌 뉴스·이벤트 코딩 — 무인증 |
| ⚠️ [**Common Crawl News**](https://commoncrawl.org) | [https://commoncrawl.org/get-started](https://commoncrawl.org/get-started) — WARC 형식 월간/뉴스 크롤 | 무인증 |
| ✅ [**Wayback Machine API**](https://archive.org/web/) | [https://archive.org/help/wayback\_api.php](https://archive.org/help/wayback_api.php) — 특정 URL의 스냅샷 조회 | 무인증 |
| ✅ [**Internet Archive Search**](https://archive.org) | [https://archive.org/advancedsearch.php](https://archive.org/advancedsearch.php) — 도서·영상·웹 통합 검색 | 무인증 |
| ✅ [**GNews API**](https://gnews.io) | [https://gnews.io/](https://gnews.io/) — 60+ 언어 뉴스 검색 | 무료 100req/day |
| ⚠️ [**NewsAPI.org**](https://newsapi.org) | [https://newsapi.org](https://newsapi.org) — 영어 위주, 무료 dev tier | apiKey |
| ⚠️ [**Mediastack**](https://mediastack.com) / [**NewsData.io**](https://newsdata.io) / [**Currents**](https://currentsapi.services) | 무료 tier 있는 뉴스 집계 | apiKey |
| ✅ [**NYT Developer**](https://developer.nytimes.com) | [https://developer.nytimes.com/](https://developer.nytimes.com/) — 기사 검색·아카이브·서평 | apiKey |
| ✅ [**Guardian Open Platform**](https://open-platform.theguardian.com) | [https://open-platform.theguardian.com/](https://open-platform.theguardian.com/) — 1999~ 가디언 전체 본문 | apiKey 무료 |

> [GDELT](https://www.gdeltproject.org)는 데이터저널리즘에서 **무인증 + 100언어 + 30분 단위 갱신**으로 가장 강력. 본문은 주지 않지만 URL·테마·톤·지명·인물·이벤트 코드 제공. 검증된 base: [`api.gdeltproject.org/api/v2/doc/doc`](https://api.gdeltproject.org/api/v2/doc/doc).

### 4-3. 학술·과학·연구

| 서비스 | URL | 비고 |
| --- | --- | --- |
| ✅ [**OpenAlex**](https://openalex.org) | [https://api.openalex.org/](https://api.openalex.org/) — 2.5억+ 논문 / docs: [https://docs.openalex.org/](https://docs.openalex.org/) | **2025-02-13부터 API 키 필수** (무료, [발급](https://openalex.org/settings/api)). 무료 100k credits/day |
| ✅ [**Crossref**](https://www.crossref.org) | [https://api.crossref.org/](https://api.crossref.org/) — DOI 메타데이터 | 무인증 (polite pool 권장: `mailto=` 파라미터) |
| ⚠️ [**Semantic Scholar**](https://www.semanticscholar.org) | [https://api.semanticscholar.org/](https://api.semanticscholar.org/) — 인용·임베딩 | apiKey 무료 |
| ✅ [**arXiv API**](https://arxiv.org) | [http://export.arxiv.org/api/query](http://export.arxiv.org/api/query) — 프리프린트 | 무인증 |
| ✅ [**PubMed E-utilities** (NCBI)](https://www.ncbi.nlm.nih.gov) | [https://www.ncbi.nlm.nih.gov/books/NBK25501/](https://www.ncbi.nlm.nih.gov/books/NBK25501/) — 의학 | 무인증 (3 req/sec, key 시 10) |
| ✅ [**NASA APIs**](https://www.nasa.gov) | [https://api.nasa.gov/](https://api.nasa.gov/) — APOD·EPIC·EONET (재난) 등 | apiKey 무료 |

### 4-4. 정치·정부·법률

| 서비스 | URL |
| --- | --- |
| ⚠️ [**OpenCorporates**](https://opencorporates.com) | [https://opencorporates.com](https://opencorporates.com) — 1.8억+ 기업 (rate-limited 무료) |
| ✅ [**OpenSanctions**](https://www.opensanctions.org) | [https://www.opensanctions.org/](https://www.opensanctions.org/) — 제재·PEP·범죄 인물 DB |
| ⚠️ [**ProPublica Congress**](https://projects.propublica.org/api-docs/congress-api/) / [**Nonprofit Explorer**](https://projects.propublica.org/nonprofits/api) | 미국 의회·비영리 |
| ✅ [**GovInfo**](https://www.govinfo.gov) / [**data.gov**](https://www.data.gov) | [https://api.govinfo.gov/](https://api.govinfo.gov/) / [https://www.data.gov/](https://www.data.gov/) — 미 연방 정부 데이터 |
| ✅ [**EU Open Data Portal**](https://data.europa.eu) | [https://data.europa.eu/en](https://data.europa.eu/en) — EU 데이터 |

### 4-5. 지리·날씨·환경

| 서비스 | URL |
| --- | --- |
| ⚠️ [**OpenWeatherMap**](https://openweathermap.org) | [https://openweathermap.org/api](https://openweathermap.org/api) — 무료 tier, 전세계 날씨 |
| ✅ [**Open-Meteo**](https://open-meteo.com) | [https://open-meteo.com/](https://open-meteo.com/) — 무인증·무료 기상 (★ 권장) |
| ⚠️ [**NOAA**](https://www.noaa.gov) / [**NASA POWER**](https://power.larc.nasa.gov) | 기후 재분석 |
| ✅ [**OpenStreetMap Nominatim**](https://nominatim.openstreetmap.org) / [**Overpass**](https://overpass-api.de) | [https://nominatim.openstreetmap.org/](https://nominatim.openstreetmap.org/) / [https://overpass-api.de/](https://overpass-api.de/) — Geocoding·POI |
| ⚠️ [**Mapbox**](https://www.mapbox.com) / [**HERE**](https://www.here.com) | 지도·내비 (무료 tier) |
| ⚠️ [**Google Earth Engine**](https://earthengine.google.com) | [https://earthengine.google.com/](https://earthengine.google.com/) — 위성 영상 (학술 무료) |
| ⚠️ [**Sentinel Hub**](https://www.sentinel-hub.com) / [**Copernicus**](https://www.copernicus.eu) | EU 위성 |
| ⚠️ [**NASA FIRMS**](https://firms.modaps.eosdis.nasa.gov) | 산불 위치 |
| ⚠️ [**EONET**](https://eonet.gsfc.nasa.gov) | 자연재해 |

### 4-6. 소셜·플랫폼·검색

| 서비스 | URL |
| --- | --- |
| ✅ [**YouTube Data API v3**](https://developers.google.com/youtube/v3) | [https://developers.google.com/youtube/v3](https://developers.google.com/youtube/v3) — 검색·댓글·통계 (무료 quota) |
| ⚠️ [**Reddit API**](https://www.reddit.com/dev/api) | [https://www.reddit.com/dev/api](https://www.reddit.com/dev/api) — OAuth 무료 |
| ✅ [**Mastodon API**](https://docs.joinmastodon.org/api/) | [https://docs.joinmastodon.org/api/](https://docs.joinmastodon.org/api/) — OAuth 무료, 전역 |
| ✅ [**Bluesky AT Protocol**](https://atproto.com) | [https://atproto.com/](https://atproto.com/) — 무료 |
| ✅ [**Tavily Search**](https://tavily.com) | [https://tavily.com/](https://tavily.com/) — LLM-friendly 웹검색 (1k/월 무료) |
| ✅ [**Brave Search API**](https://brave.com/search/api/) | [https://brave.com/search/api/](https://brave.com/search/api/) — 2k/월 무료 |
| ⚠️ [**SerpAPI**](https://serpapi.com) / [**SearchAPI**](https://www.searchapi.io) / [**Serper.dev**](https://serper.dev) | Google SERP |
| ✅ [**Wikipedia**](https://en.wikipedia.org/api/rest_v1/) / [**Wikidata SPARQL**](https://query.wikidata.org) | [https://en.wikipedia.org/api/rest\_v1/](https://en.wikipedia.org/api/rest_v1/) / [https://query.wikidata.org/](https://query.wikidata.org/) — 무인증 |

### 4-7. 금융·시장

| 서비스 | URL |
| --- | --- |
| ⚠️ [**Alpha Vantage**](https://www.alphavantage.co) | [https://www.alphavantage.co/](https://www.alphavantage.co/) — 무료 시세·환율 |
| ✅ [**Yahoo Finance** (yfinance)](https://github.com/ranaroussi/yfinance) | [https://github.com/ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) — 비공식 wrapper |
| ✅ [**CoinGecko**](https://www.coingecko.com) / [**CoinCap**](https://coincap.io) | [https://www.coingecko.com/en/api](https://www.coingecko.com/en/api) / [https://coincap.io/](https://coincap.io/) — 암호화폐 무료 |
| ✅ [**SEC EDGAR**](https://www.sec.gov/edgar) | [https://www.sec.gov/edgar/sec-api-documentation](https://www.sec.gov/edgar/sec-api-documentation) — 미국 공시 |

---

## 5\. MCP 서버 카탈로그 (Python · 웹 배포)

### 5-1. MCP란?

**Model Context Protocol** — [Anthropic](https://www.anthropic.com)이 2024-11 발표한 JSON-RPC 2.0 기반 개방 표준. LLM↔도구 연결의 USB-C. Claude/Gemini/GPT 모두 지원. 2026 Q1 공식 [레지스트리](https://github.com/mcp)에 2,000+ 서버.

세 가지 primitive:

-   **Tools** (model-controlled): 모델이 호출하는 함수
-   **Resources** (app-controlled): 모델이 읽는 데이터
-   **Prompts** (user-controlled): 재사용 프롬프트 템플릿

전송 방식: `stdio` (로컬 자식 프로세스) 또는 `Streamable HTTP/SSE` (원격, OAuth 가능).

### 5-2. Gemini에서 MCP 직접 사용 (2026 SDK)

```python
# gemini_mcp.py
import asyncio, os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 예: 공식 fetch 서버를 stdio로 띄움
server_params = StdioServerParameters(
    command="uvx",
    args=["mcp-server-fetch"],
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            resp = await client.aio.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents="https://www.bok.or.kr/portal/main/main.do 페이지의 헤드라인 5개를 요약해.",
                config=genai.types.GenerateContentConfig(
                    tools=[session],   # ★ ClientSession을 그대로 전달 — 자동 함수 변환
                    temperature=0,
                ),
            )
            print(resp.text)

asyncio.run(main())
```

> Python SDK는 `tools=[session]`만으로 MCP 서버의 모든 tool을 자동 노출. 비활성화하려면 `automatic_function_calling=ToolConfig(disabled=True)`.

### 5-3. 공식 reference 서버 ([modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers))

| 서버 | 설명 | 설치 |
| --- | --- | --- |
| **fetch** | URL → 마크다운 변환 (LLM 친화) | `uvx mcp-server-fetch` |
| **filesystem** | 안전한 파일 R/W | `npx @modelcontextprotocol/server-filesystem` |
| **git** | Git repo 읽기·검색 | `uvx mcp-server-git` |
| **memory** | Knowledge graph 메모리 | `npx ...server-memory` |
| **sequential-thinking** | 다단계 사고 도우미 | `npx ...server-sequential-thinking` |
| **time** | 타임존·시간 변환 | `uvx mcp-server-time` |
| **everything** | 테스트용 reference | — |

### 5-4. 데이터저널리즘 추천 서드파티 MCP

#### 검색·웹크롤

-   [**Brave Search MCP**](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search) — [Brave Search API](https://brave.com/search/api/) (2k/월 무료) 래핑
-   [**Tavily MCP**](https://github.com/tavily-ai/tavily-mcp) — LLM-친화 웹검색 grounding
-   [**Exa MCP**](https://github.com/exa-labs/exa-mcp-server) — semantic search 특화
-   [**Perplexity MCP**](https://github.com/ppl-ai/modelcontextprotocol) — 검색+요약
-   [**Firecrawl MCP**](https://github.com/mendableai/firecrawl-mcp-server) — 페이지 크롤·구조화 추출
-   [**Apify Actors MCP**](https://apify.com/apify/actors-mcp-server) — 3,000+ 스크레이퍼 actor
-   [**Playwright MCP**](https://github.com/microsoft/playwright-mcp) / [**Puppeteer MCP**](https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer) — 브라우저 자동화
-   [**`@pskill9/web-search`**](https://github.com/pskill9/web-search) — Google 결과 (무 API키)

#### 한국 공공데이터

-   [**`Koomook/data-go-mcp-servers`**](https://github.com/Koomook/data-go-mcp-servers) — `data.go.kr` 통합 — NPS·NTS 사업자, PPS 나라장터, FSC, 대통령기록 등 PyPI: `data-go-mcp.*`
-   [**`hjsh200219/korea-public-data-mcp`**](https://github.com/hjsh200219/korea-public-data-mcp) — 법제처 + DART + data.go.kr 통합. [`https://public-data.up.railway.app/`](https://public-data.up.railway.app/) 원격 호스팅 버전 제공
-   [**`pinnaclesoft-ko/be-node-seoul-data-mcp`**](https://github.com/pinnaclesoft-ko/be-node-seoul-data-mcp) — [서울 열린데이터광장](https://data.seoul.go.kr) (지하철·문화행사)

#### 지식·학술·문서

-   **OpenAlex MCP** / **Crossref MCP** / **arXiv MCP** / **PubMed MCP** — 학술 grounding
-   [**Wikipedia MCP**](https://github.com/Rudra-ravi/wikipedia-mcp) — 무인증
-   **NotebookLM MCP** — 자체 노트북 기반 무할루시 답변

#### 데이터베이스·지식

-   **PostgreSQL** / **SQLite** / **MySQL MCP** — `mcp-server-postgres` 등
-   [**Neo4j MCP**](https://github.com/neo4j-contrib/mcp-neo4j) — 그래프 DB
-   [**DuckDB MCP**](https://github.com/motherduckdb/mcp-server-motherduck) — 분석용 in-process DB
-   **MongoDB MCP**
-   [**Chroma**](https://github.com/chroma-core/chroma-mcp) / **Qdrant** / **Pinecone MCP** — 벡터 DB (RAG)
-   [**MindsDB MCP**](https://github.com/mindsdb/mindsdb_mcp_server) — 통합 데이터 게이트웨이 (200+ 소스)
-   [**`julien040/anyquery`**](https://github.com/julien040/anyquery) — 40+ 앱을 SQL로 쿼리

#### 시각화·분석

-   [**`isaacwasserman/mcp-vegalite-server`**](https://github.com/isaacwasserman/mcp-vegalite-server) — Vega-Lite 차트 생성
-   [**AntV Chart MCP**](https://github.com/antvis/mcp-server-chart) — 차트 자동 생성
-   [**`mcp-server-pandoc`**](https://github.com/vivekVells/mcp-pandoc) — 문서 포맷 변환

#### 미디어·소셜

-   [**`@kimtaeyoon83/mcp-server-youtube-transcript`**](https://github.com/kimtaeyoon83/mcp-server-youtube-transcript) — 자막·트랜스크립트 추출
-   **YouTube Data MCP**
-   **Slack MCP** / **Discord MCP** / **Telegram MCP**
-   [**Twitter (twikit) MCP**](https://github.com/adhikasp/mcp-twikit) — `adhikasp/mcp-twikit`

#### 클라우드·인프라

-   **AWS** · **GCP** · **Azure MCP** — 공식 서버 다수
-   [**Cloudflare MCP**](https://github.com/cloudflare/mcp-server-cloudflare) — Workers·KV·R2·D1
-   **DigitalOcean** — 서버 환경에 맞춤 (커뮤니티)

### 5-5. MCP 서버 직접 만들기 (FastMCP)

가장 일반적 형태: **공공데이터 API → MCP wrapper**.

```python
# my_kosis_mcp.py
import os, requests
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()
mcp = FastMCP("KOSIS-Korean-Stats")
KOSIS_KEY = os.environ["KOSIS_API_KEY"]

@mcp.tool()
def kosis_search(searchNm: str, page: int = 1, num: int = 10) -> dict:
    """KOSIS 통계표 검색.
    Args:
        searchNm: 검색어 (예: '합계출산율')
        page: 페이지
        num: 페이지당 결과 수
    """
    url = "https://kosis.kr/openapi/statisticsList.do"
    params = dict(method="getList", apiKey=KOSIS_KEY, format="json", jsonVD="Y",
                  vwCd="MT_ZTITLE", searchNm=searchNm, parentListId="", pageNo=page, numOfRows=num)
    return requests.get(url, params=params, timeout=15).json()

@mcp.tool()
def kosis_data(orgId: str, tblId: str, prdSe: str, startPrdDe: str, endPrdDe: str) -> dict:
    """KOSIS 통계표의 실제 데이터 조회."""
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    params = dict(method="getList", apiKey=KOSIS_KEY, format="json", jsonVD="Y",
                  orgId=orgId, tblId=tblId, prdSe=prdSe,
                  startPrdDe=startPrdDe, endPrdDe=endPrdDe)
    return requests.get(url, params=params, timeout=15).json()

if __name__ == "__main__":
    mcp.run()  # 기본 stdio
    # HTTP로 띄우려면: mcp.run(transport="http", port=8000)
```

설치/실행:

```bash
pip install fastmcp python-dotenv requests
python my_kosis_mcp.py
```

Claude Desktop / Cursor 연결 (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "kosis": {
      "command": "python",
      "args": ["/abs/path/my_kosis_mcp.py"],
      "env": { "KOSIS_API_KEY": "..." }
    }
  }
}
```

### 5-6. MCP 서버 웹 배포 (FastAPI)

```python
# kosis_mcp_http.py — Streamable HTTP transport
from fastmcp import FastMCP
mcp = FastMCP("kosis")
# ... @mcp.tool() 함수 정의 ...
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")
```

[`fastapi_mcp`](https://github.com/tadata-org/fastapi_mcp) (zero-config wrapper):

```bash
pip install fastapi-mcp uvicorn
```

```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
app = FastAPI()
@app.get("/kosis/{tbl}")
def kosis(tbl: str, start: str, end: str): ...

mcp = FastApiMCP(app)
mcp.mount()
# uvicorn kosis_mcp_http:app --host 0.0.0.0 --port 8000
```

→ `https://yourserver/mcp` 엔드포인트가 MCP-호환. Claude/Gemini/Cursor 모두 원격 등록 가능.

서버에 배포:

1.  systemd service로 등록 (`/etc/systemd/system/mcp-kosis.service`)
2.  nginx reverse proxy + SSL (Let's Encrypt)
3.  OAuth가 필요하면 `mcp.server.auth` 모듈 또는 [Auth0](https://auth0.com) SaaS 연동
4.  학생들에게 endpoint URL만 공유 → 각자 클라이언트 등록

### 5-7. MCP 디렉터리

| 디렉터리 | URL |
| --- | --- |
| **공식 MCP Registry** | [https://github.com/mcp](https://github.com/mcp) — 검증된 서버 카탈로그 |
| **mcpservers.org** | [https://mcpservers.org](https://mcpservers.org) — UI 기반 탐색 |
| [**`punkpeye/awesome-mcp-servers`**](https://github.com/punkpeye/awesome-mcp-servers) | 가장 인기 큐레이션 |
| [**`appcypher/awesome-mcp-servers`**](https://github.com/appcypher/awesome-mcp-servers) | 카테고리별 정리 |
| [**`wong2/awesome-mcp-servers`**](https://github.com/wong2/awesome-mcp-servers) | 알파벳순 |
| [**`tolkonepiu/best-of-mcp-servers`**](https://github.com/tolkonepiu/best-of-mcp-servers) | 주간 랭킹 |
| [**`MobinX/awesome-mcp-list`**](https://github.com/MobinX/awesome-mcp-list) | 콤팩트 |
| [**`TensorBlock/awesome-mcp-servers`**](https://github.com/TensorBlock/awesome-mcp-servers) | 자동 큐레이션 (7,000+ 추적) |
| [**Klavis AI**](https://www.klavis.ai) | 호스팅 MCP infra |
| [**Pipedream**](https://pipedream.com/mcp) | 2,500 API · 8,000 도구 통합 MCP |

---

## 6\. 사용 패턴

### 패턴 A — 단일 API + Function Calling

**용도**: 단일 통계표 기반 사실 확인 기사

-   예: "지난 5년 합계출산율 추이"
-   구현: [KOSIS API](https://kosis.kr) 함수 1개 + Gemini → 표·요약 자동 생성

### 패턴 B — 다중 API 병렬 grounding

**용도**: 복합 컨텍스트 기사 (뉴스 + 통계 + 지도)

-   예: "전국 미세먼지 수치 + 관련 보도 추이"
-   구현: [에어코리아](https://www.airkorea.or.kr) + [BIGKINDS](https://www.bigkinds.or.kr) + 행정동 코드 함수 3개 → Gemini orchestration

### 패턴 C — RAG (벡터 DB) + LLM

**용도**: 장문 기사 코퍼스 분석

-   임베딩: `gemini-embedding-001` 또는 multilingual-e5-large
-   벡터 DB: [ChromaDB](https://www.trychroma.com) / [Qdrant](https://qdrant.tech)
-   검색 → Gemini 2.5 Flash Lite로 합성

### 패턴 D — MCP 서버 통합 워크플로

**용도**: 반복 가능 분석 파이프라인 (수업 과제 표준)

-   KOSIS MCP + DART MCP + GDELT MCP + Vega-Lite MCP
-   Claude Desktop / Gemini CLI에서 자연어로 호출
-   결과 자동 시각화

### 패턴 E — Agent + 검증 체인

**용도**: 팩트체킹 자동화 (LangGraph 시스템과 호환)

-   주장 추출 → 키워드화 → 다중 소스 grounding → 일치/불일치 판정 → 인용
-   LLM coordinator: Gemini 2.5 Flash Lite (비용·속도 우위)
-   Verifier: 별도 LLM(예: Gemini 2.5 Pro 또는 GPT-4 mini) 교차검증

---

## 7\. 강의용 실습 프로젝트 (단계별)

### Lab 1. Hello Gemini + KOSIS (1주차)

-   `.env` 셋업, `client.models.generate_content()` 호출
-   단일 함수 KOSIS `getList` 호출 → 출생아수 시계열 표

### Lab 2. 부동산 실거래 + 지도 시각화 (2~3주차)

-   [국토교통부 실거래가](https://www.molit.go.kr) API
-   [Folium](https://python-visualization.github.io/folium/) / [kepler.gl](https://kepler.gl) / [Plotly](https://plotly.com/python/)로 시각화
-   Gemini가 핫스팟 자동 해설

### Lab 3. BIGKINDS + 정치 발화 분석 (4~5주차)

-   [빅카인즈](https://www.bigkinds.or.kr) 검색 → 정당별/시기별 빈도
-   Gemini로 프레임 분석·요약
-   WordCloud + 토픽 모델링

### Lab 4. DART 공시 자동 모니터링 (6주차)

-   특정 키워드 공시 발생 시 [Slack](https://api.slack.com)/[Telegram](https://core.telegram.org/bots/api) 알림
-   Gemini가 공시 요약 + 영향도 평가

### Lab 5. GDELT 글로벌 이벤트 추적 (7주차)

-   [GDELT 2.0 Doc API](https://api.gdeltproject.org/api/v2/doc/doc)로 한국 관련 외신 수집
-   톤(tone) 시계열 + 지명 빈도
-   Gemini로 주요 이슈 클러스터링

### Lab 6. Open DART + ECOS + 거시-기업 연결 분석 (8~9주차)

-   환율·금리 + 수출기업 영업이익 상관
-   Gemini가 인과 가설 후보 생성 → 학생이 검증

### Lab 7. 자기만의 MCP 서버 (10~12주차) ⭐

-   학생이 관심 분야 공공API를 골라 [FastMCP](https://github.com/jlowin/fastmcp)로 래핑
-   DigitalOcean에 배포
-   Claude Desktop / Gemini에서 호출 시연
-   동료 검토 발표

### Lab 8. 종합 — Agentic 팩트체크 시스템 (13~15주차)

-   정치인 발언 입력 → 다중 API/MCP grounding → 검증 결과 + 인용
-   LangGraph + Gemini 2.5 Flash Lite + 학생 자작 MCP 결합
-   최종 평가: 라이브 데모 + 보고서

---

## 8\. 보안·윤리 체크리스트

### 보안

-    `.env`는 절대 git push 금지 (`.gitignore`에 추가)
-    API 키는 서버 측에서만 사용 (프론트 노출 금지)
-    공공데이터 키도 부정사용 시 정지 가능 — rate limit 준수
-    HTTPS + SSH 키 인증 (DigitalOcean 운영 패턴 유지)
-    MCP 원격 서버는 OAuth/Bearer 인증 필수

### 저작권·이용약관

-    [BIGKINDS](https://www.bigkinds.or.kr), [네이버 검색](https://developers.naver.com) 등 일부는 **언론보도/연구 목적** 한정
-    뉴스 본문 재배포 금지 — **요약·인용만 허용**
-    공공데이터도 데이터셋별 라이선스 확인 (대부분 [CC-BY](https://creativecommons.org/licenses/by/4.0/) 또는 [KOGL](https://www.kogl.or.kr))
-    LLM 출력 인용 시 원 출처 표기 (저널리즘 윤리)

### 개인정보

-    실거래가, 사업자번호, 의료데이터 등 결합 시 식별 위험
-    익명화·집계화 전제, IRB 검토 필요한 경우 사전 신청

### 할루시네이션 방지

-    **항상 grounding** — 순수 LLM 답변 금지
-    출력에 출처 URL 포함 의무화
-    `temperature=0` 또는 낮게 설정
-    Pro 모델로 재검증 (Critical claim의 경우)

### URL 운영 체크

-    **본 가이드 ❌ 마크 API는 즉시 신 엔드포인트로 교체**: OECD `stats.oecd.org` → [`sdmx.oecd.org`](https://sdmx.oecd.org/public/rest/), IMF DataMapper `v1` → [`v2`](https://www.imf.org/external/datamapper/api/v2/)
-    **OpenAlex는 2025-02부터 API 키 필수** — `OPENALEX_API_KEY` `.env`에 추가
-    ⚠️ 마크 API는 fetch 후 응답 코드 체크하여 자동 fallback (예: 작동 안 하면 RSSHub 또는 Google News 검색 RSS)

---

## 9\. 참고 자료

### 공식 문서

### 카탈로그

-   한국 API: [https://github.com/yybmion/public-apis-4Kr](https://github.com/yybmion/public-apis-4Kr) (260+, 2026-02 업데이트)
-   글로벌 API: [https://github.com/public-apis/public-apis](https://github.com/public-apis/public-apis)
-   글로벌 API (대안): [https://github.com/public-api-lists/public-api-lists](https://github.com/public-api-lists/public-api-lists) (730+)
-   MCP: [https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
-   MCP curated: [https://github.com/punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
-   MCP Korean: [https://github.com/Koomook/data-go-mcp-servers](https://github.com/Koomook/data-go-mcp-servers)
-   저널리즘 도구: [https://github.com/peterdalle/mediacommtools](https://github.com/peterdalle/mediacommtools)

### 데이터저널리즘 학습

-   [DataJournalism.com (EJC)](https://datajournalism.com)
-   [GIJN Data Journalism Resources](https://gijn.org/stories/?gijn_topic=data-journalism)
-   [Sigma Awards](https://sigmaawards.org) (연도별 best practice 사례 — 2026 31 finalists)
-   [Knight Center](https://journalismcourses.org) 무료 강좌 (climate journalism 등)

---

## 10\. 빠른 시작 템플릿 (한 파일)

```python
# starter.py — 강의용 미니 템플릿 (2026-05 검증 URL)
import os, requests, json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def worldbank_indicator(country_iso3: str, indicator: str,
                        start_year: int, end_year: int) -> str:
    """World Bank 단일 지표 시계열. (✅ 검증 v2 엔드포인트)
    예) country_iso3='KOR', indicator='NY.GDP.MKTP.CD' (GDP, current US$)
    """
    url = (f"https://api.worldbank.org/v2/country/{country_iso3}/indicator/"
           f"{indicator}?date={start_year}:{end_year}&format=json&per_page=200")
    r = requests.get(url, timeout=15)
    return json.dumps(r.json(), ensure_ascii=False)[:6000]

def gdelt_doc(query: str, timespan: str = "1d", maxrec: int = 10) -> str:
    """GDELT 2.0 Doc API — 글로벌 뉴스 검색. (✅ 검증)
    timespan 예: '1d', '7d'  /  query 예: 'Korea AND inflation'
    """
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = dict(query=query, mode="ArtList", maxrecords=maxrec,
                  timespan=timespan, format="json", sort="HybridRel")
    return requests.get(url, params=params, timeout=15).text[:6000]

def naver_news(query: str, display: int = 10) -> str:
    """네이버 뉴스 검색 (한국어). (✅ 검증)"""
    headers = {
        "X-Naver-Client-Id": os.environ.get("NAVER_CLIENT_ID", ""),
        "X-Naver-Client-Secret": os.environ.get("NAVER_CLIENT_SECRET", ""),
    }
    r = requests.get("https://openapi.naver.com/v1/search/news.json",
                     params={"query": query, "display": display, "sort": "date"},
                     headers=headers, timeout=15)
    return r.text[:6000]

def oecd_data(dataflow: str, query_filter: str, start_period: str = "2020-01") -> str:
    """OECD Data Explorer (신 엔드포인트, ✅ 2024-07 마이그레이션 후).
    Args:
        dataflow: 예) 'OECD.SDD.TPS,DSD_LFS@DF_IALFS_UNE_M,1.0'
        query_filter: 예) 'KOR..PT_LF_SUB._Z.Y._T.Y_GE15..M'
        start_period: 예) '2023-01'
    """
    url = (f"https://sdmx.oecd.org/public/rest/data/{dataflow}/{query_filter}"
           f"?startPeriod={start_period}&dimensionAtObservation=AllDimensions"
           f"&format=csvfilewithlabels")
    return requests.get(url, timeout=20).text[:6000]

def main(question: str):
    resp = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=question,
        config=types.GenerateContentConfig(
            tools=[worldbank_indicator, gdelt_doc, naver_news, oecd_data],
            temperature=0,
            system_instruction=(
                "당신은 데이터저널리즘 어시스턴트다. "
                "정량 주장은 반드시 도구를 호출해 확인하고, "
                "인용한 모든 출처 URL을 답변 끝에 나열한다."
            ),
        ),
    )
    print(resp.text)

if __name__ == "__main__":
    main("최근 한국 GDP 성장률을 World Bank 데이터로 확인하고, "
         "관련 외신 보도 톤을 GDELT로 살펴봐줘.")
```

실행:

```bash
python starter.py
```

이 한 파일로 **글로벌 거시지표 + 글로벌 뉴스 + 한국 뉴스 + OECD**를 동시에 grounding하는 데이터저널리즘 어시스턴트가 동작.

---

## 11\. 트러블슈팅 (FAQ)

| 증상 | 원인·해결 |
| --- | --- |
| `API key not valid` | `.env` 로딩 안 됨 → `load_dotenv()` 호출 위치 확인, 환경변수명 대소문자 일치 |
| `429 Too Many Requests` | 무료 tier 분당 제한 초과 → exponential backoff, 또는 `gemini-2.5-flash` (상위) 일시 사용 |
| `400 Schema validation` | Function 인자 타입 어노테이션 누락/복잡 → `int \&#124; str` 같은 union은 피하고 단순 타입 사용 |
| KOSIS 빈 결과 | `prdSe`, `orgId`, `tblId` 일치 필수 — 통계지표 조회 API로 먼저 메타 확보 |
| BIGKINDS 401 | 비공개 API 키, [한국언론진흥재단](https://www.kpf.or.kr) 직접 신청 필요 |
| MCP 서버 미연결 | `uvx`/`npx` PATH 확인, Windows에서는 절대경로 권장 |
| 한국어 함수 docstring 무시 | docstring을 영문으로 작성하거나 영문+한글 병기 — 모델 파싱 안정성 ↑ |
| **OECD `stats.oecd.org` 503/timeout** | **2024-07 폐쇄됨**. 즉시 [`sdmx.oecd.org/public/rest/`](https://sdmx.oecd.org/public/rest/)로 변경 |
| **IMF DataMapper 404** | `/api/v1/`은 일부 엔드포인트 정상이나 `/api/v2/`가 현재 권장 버전 |
| **OpenAlex 401 (2025-02 이후)** | API 키 필수 — [https://openalex.org/settings/api](https://openalex.org/settings/api)에서 무료 발급 후 `?api_key=...` 또는 `mailto=` 파라미터 추가 |
| **`feeds.reuters.com` 404** | Reuters 자체 RSS 2020년 폐지 → RSSHub `/reuters/...` 사용 |

---

## 부록 A. URL 검증 요약 (Quick Reference)

### ✅ 검증된 안정 API (직접 사용 권장)

| 카테고리 | API (homepage) | 엔드포인트 |
| --- | --- | --- |
| 한국 거시 | [공공데이터포털](https://www.data.go.kr) | `data.go.kr` |
| 한국 통계 | [KOSIS](https://kosis.kr) | [`kosis.kr/openapi/`](https://kosis.kr/openapi/) |
| 한국 금융 | [한국은행 ECOS](https://ecos.bok.or.kr) | [`ecos.bok.or.kr/api/`](https://ecos.bok.or.kr/api/) |
| 한국 기업 | [Open DART](https://opendart.fss.or.kr) | [`opendart.fss.or.kr/api/`](https://opendart.fss.or.kr/api/) |
| 한국 법령 | [국가법령정보](https://open.law.go.kr) | [`open.law.go.kr`](https://open.law.go.kr) |
| 한국 국회 | [열린국회정보](https://open.assembly.go.kr) | [`open.assembly.go.kr/portal/openapi/`](https://open.assembly.go.kr/portal/openapi/main.do) |
| 한국 뉴스 | [BIGKINDS](https://www.bigkinds.or.kr) | (신청제) |
| 한국 검색 | [네이버 검색](https://developers.naver.com) | [`openapi.naver.com/v1/search/`](https://developers.naver.com/products/service-api/search/search.md) |
| 한국 지도 | [카카오맵](https://apis.map.kakao.com), [네이버 지도](https://www.ncloud.com/product/applicationService/maps) | — |
| 글로벌 거시 | [World Bank](https://data.worldbank.org) | [`api.worldbank.org/v2/`](https://api.worldbank.org/v2/) |
| 글로벌 거시 | [IMF DataMapper](https://www.imf.org/external/datamapper/) | [`imf.org/external/datamapper/api/v2/`](https://www.imf.org/external/datamapper/api/v2/) |
| 글로벌 거시 | [FRED](https://fred.stlouisfed.org) | [`api.stlouisfed.org/fred/`](https://api.stlouisfed.org/fred/) |
| 글로벌 뉴스 | [GDELT 2.0](https://www.gdeltproject.org) | [`api.gdeltproject.org/api/v2/`](https://api.gdeltproject.org/api/v2/) |
| 학술 | [arXiv](https://arxiv.org), [Crossref](https://www.crossref.org), [PubMed](https://www.ncbi.nlm.nih.gov), [NASA](https://api.nasa.gov) | 각 base |

### ❌ 변경·폐지된 API (즉시 교체 필요)

| API | 옛 엔드포인트 (작동 안 함) | 새 엔드포인트 |
| --- | --- | --- |
| **OECD** | `https://stats.oecd.org/SDMX-JSON/data/` (2024-07 폐쇄) | [`https://sdmx.oecd.org/public/rest/data/`](https://sdmx.oecd.org/public/rest/) |
| **IMF (legacy)** | `https://dataservices.imf.org` (2025-11 폐쇄) | [`https://data.imf.org`](https://data.imf.org) (SDMX 3.0) |
| **IMF DataMapper** | `https://www.imf.org/external/datamapper/api/v1/` | [`https://www.imf.org/external/datamapper/api/v2/`](https://www.imf.org/external/datamapper/api/v2/) |
| **Reuters RSS** | `feeds.reuters.com/Reuters/worldNews` (2020 폐지) | RSSHub `/reuters/:category` (자매 RSS 가이드 §6 참조) |
| **OpenAlex (인증)** | (이전 무인증) | [`api.openalex.org`](https://api.openalex.org/) — **API 키 필수** (2025-02 이후) |

### ⚠️ 미검증 항목 운영 패턴

```python
# 자동 fallback 패턴
import requests, time

def safe_call(url, params=None, timeout=15, retries=2):
    """API 호출 with 자동 재시도 + fallback URL 알림."""
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                return r.json() if 'json' in r.headers.get('Content-Type', '') else r.text
            elif r.status_code in (404, 410):
                print(f"⚠️ {url} 폐기 가능성 — 본 가이드 ❌ 마크 확인")
                break
        except Exception as e:
            print(f"[err] {url}: {e}")
            time.sleep(2 ** i)
    return None
```

이 패턴으로 ⚠️ 마크 API의 갑작스런 폐지에도 대응 가능. ❌ 마크 API는 본 가이드의 새 엔드포인트로 즉시 교체.

---