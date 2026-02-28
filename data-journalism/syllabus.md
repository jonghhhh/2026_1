# 데이터저널리즘 — 강의개요

**경희대학교 미디어학과 | JCOMM305900 | 월수 10:30~11:45 | 정408**

**담당교수**: 이종혁 (정경대 교수회관 620호, 02-961-2179, jonghhhh@khu.ac.kr)

> ← [주차별 수업 내용으로 돌아가기](index.md)

---

## 수업 목표

- 데이터저널리즘의 개념·역할·전망을 이해하고, 실제 취재·보도 방법론을 익힌다.
- 파이썬 기초와 Pandas를 활용한 데이터 분석 역량을 갖춘다.
- VSCode + Gemini CLI **프롬프트코딩**으로 파이썬·JavaScript 시각화·챗봇까지 구현한다.
- PDF OCR, 정보공개청구, 공공데이터 API, 웹 스크래핑 등 실제 언론사 데이터 수집 스킬을 습득한다.
- LLM API를 활용한 대량 텍스트·이미지 자동 분석 기법을 익힌다.
- Chart.js, D3.js, Leaflet, vis.js, Scrollama 등 JavaScript 인터랙티브 시각화를 구현한다.
- **Streamlit**을 통합 플랫폼으로 활용하여 시각화+검색+챗봇이 결합된 데이터저널리즘 웹앱을 배포한다.

## 수업 개요

본 수업은 **기초 → 수집 → 분석 → 시각화 → 웹앱** 5단계로 구성된다. 전 과정에서 VSCode + Gemini CLI를 활용한 프롬프트코딩 환경을 기본으로 사용한다. 전반부(1~4주)에서 파이썬 기초와 Pandas를 학습하고, 데이터 수집(5~6주)에서 크롤링·API·PDF OCR 등 실제 언론사 취재팀의 수집 방법을 다루며, LLM 대량 분석(7주)을 거쳐 JavaScript 인터랙티브 시각화(8~10주)에서 그래프·네트워크·지도·Scrollytelling을 구현한다. 후반부(11~13주)에서는 **Streamlit**을 통합 플랫폼으로 사용하여 JS 시각화를 임베드하고, 맞춤형 검색·필터링 인터페이스를 구축하며, Gemini File Search 기반 RAG 챗봇을 간단히 구현하여 하나의 데이터저널리즘 웹앱으로 통합 배포한다.

---

## 수업 데이터: 전국교통사고다발지역 표준데이터 (2025)

- **출처**: 한국도로교통공단 (공공데이터포털 data.go.kr, TAAS taas.koroad.or.kr)
- **규모**: 12,780건 (2012~2024년)
- **사고유형**: 보행어린이(1,212건), 보행노인(5,991건), 스쿨존어린이(531건), 자전거(5,046건)
- **주요 컬럼 (18개)**: 사고지역관리번호, 사고연도, 사고유형구분, 위치코드, 사고다발지역시도시군구, 사고지역위치명, 사고건수, 사상자수, 사망자수, 중상자수, 경상자수, 부상신고자수, 위도, 경도, 사고다발지역폴리곤정보, 데이터기준일자, 제공기관코드, 제공기관명
- **특징**: 위도·경도 좌표 + 폴리곤 정보 포함 → 지도 시각화에 최적

---

## 개발환경

- **코드 에디터**: VSCode + Gemini CLI
- **API**: Google AI Studio (Gemini 2.5 Flash-Lite)
- **통합 플랫폼**: Streamlit + `components.html()` JS 임베드
- **AI 챗봇**: [chat.khu.ac.kr](https://chat.khu.ac.kr/) — 경희대 구성원 무료 제공
- **OS**: Windows → WSL(Windows Subsystem for Linux) 사용 / Mac → 그대로 사용

---

## 기술 아키텍처

```
┌─────────────────────────────────────────────────┐
│                  Streamlit 웹앱                    │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 네이티브  │  │ JS 시각화 │  │  챗봇    │       │
│  │  위젯    │  │ (임베드)  │  │ (RAG)   │       │
│  │          │  │          │  │          │       │
│  │ selectbox│  │ Chart.js │  │ File     │       │
│  │ slider   │→│ Leaflet  │  │ Search   │       │
│  │ text_in  │  │ vis.js   │  │ +chat_in │       │
│  │ columns  │  │ Scrollama│  │          │       │
│  └──────────┘  └──────────┘  └──────────┘       │
│        ↕              ↑              ↑           │
│     Pandas         JSON 주입    Gemini API       │
│    필터·집계      components     File Search      │
│                   .html()                        │
└─────────────────────────────────────────────────┘
        ↓ 배포
   Hugging Face Spaces / Streamlit Cloud
```

---

## 핵심 AI 모델 & 도구

| 도구                         | 용도                                               | 비용            |
|:-----------------------------|:---------------------------------------------------|:----------------|
| **Gemini CLI** (VSCode)      | 프롬프트코딩 — Python/JS/HTML 코드 생성·수정·디버깅 | 무료            |
| **Gemini 2.5 Flash-Lite API** | 텍스트·이미지 대량 분석, 분류, 요약 (1,000건/일)    | 무료            |
| **Gemini File Search**       | 관리형 RAG — CSV·PDF 업로드 → 의미 검색 Q&A 챗봇   | 인덱싱만 유료   |
| **Streamlit**                | 통합 웹앱 플랫폼 — UI + 검색 + 시각화 임베드 + 챗봇 | 무료            |
| **구글 시트 =AI() 함수**    | 스프레드시트에서 대량 텍스트 분류·요약 자동화       | Workspace 플랜  |
| **NotebookLM**               | 문서 요약, FAQ, 타임라인, 오디오 브리핑 생성        | 무료            |

---

## 평가 방법

| 항목                          | 비율 | 세부                                              |
|:------------------------------|:-----|:--------------------------------------------------|
| 출석                          | 10%  |                                                   |
| 참여                          | 10%  | 수업 내 실습 참여, 질문·토론                      |
| AI 활용 데이터분석 능력 테스트 | 30%  | 코드리딩 + AI 프롬프트 작성 + 프롬프트코딩 실기   |
| 조별 프로젝트 기획안          | 10%  | 중간고사 대체 (8주차 제출)                        |
| 조별 최종 프로젝트            | 40%  | Streamlit 웹앱 + 취재노트 + 발표 + 조원평가      |

---

## 주차별 일정 요약

| 주차 | 날짜       | 비고                 | 단계   | 내용                                        |
|:-----|:-----------|:---------------------|:-------|:--------------------------------------------|
| 1    | 3/4(수)    | ⚠️ 3/2 대체공휴일   | 기초   | 데이터저널리즘 소개, VSCode+Gemini CLI 설정 |
| 2    | 3/9, 3/11  |                      | 기초   | 파이썬 기초 (1)                             |
| 3    | 3/16, 3/18 |                      | 기초   | 파이썬 기초 (2)                             |
| 4    | 3/23, 3/25 |                      | 기초   | Pandas 데이터 분석                          |
| 5    | 3/30, 4/1  |                      | 수집   | 웹 기초 + 프롬프트코딩 + 웹스크래핑        |
| 6    | 4/6, 4/8   |                      | 수집   | API · PDF OCR · 정보공개청구               |
| 7    | 4/13, 4/15 |                      | 분석   | 데이터 정제 + LLM API 대량 분석            |
| 8    | 4/20, 4/22 | ★ 기획안 제출        | 시각화 | JS 입문 + Chart.js 인터랙티브 그래프       |
| 9    | 4/27, 4/29 |                      | 시각화 | 네트워크(vis.js) + 지도(Leaflet)           |
| 10   | 5/4, 5/6   |                      | 시각화 | Scrollytelling + 시각화 종합               |
| 11   | 5/11, 5/13 |                      | 웹앱   | Streamlit 입문 & JS 시각화 임베드          |
| 12   | 5/18, 5/20 |                      | 웹앱   | 맞춤형 데이터 검색 & 통합 대시보드         |
| 13   | 5/27(수)   | ⚠️ 5/25 대체공휴일  | 웹앱   | RAG 챗봇 (간단) & 최종 통합                |
| 14   | 6/1(월)    | ⚠️ 6/3 지방선거     | 웹앱   | 취재 방법론 + 배포 + 최종 점검             |
| 15   | 6/8, 6/10  |                      | 발표   | 조별 발표                                   |
| 16   | 6/15, 6/17 | **시험**             | 평가   | 데이터처리능력 테스트                       |

---

## 주요 데이터 취재처

### 국내

| 취재처 | URL | 활용 |
|:---|:---|:---|
| 공공데이터포털 | data.go.kr | 10만+ 데이터셋, Open API |
| KOSIS | kosis.kr | 400+ 기관 통계 |
| DART | dart.fss.or.kr | 기업 공시, 재무제표 |
| 국회 의안정보 | likms.assembly.go.kr/bill | 발의법안, 표결 |
| 빅카인즈 | bigkinds.or.kr | 뉴스 아카이브 (54매체) |
| 정보공개포털 | open.go.kr | 정보공개청구 |
| 뉴스타파 DATA | data.newstapa.org | 탐사보도 원본 데이터 |

### 국제

| 취재처 | URL | 활용 |
|:---|:---|:---|
| ICIJ Offshore Leaks | offshoreleaks.icij.org | 역외법인 DB |
| OCCRP Aleph | aleph.occrp.org | 글로벌 문서·기업 DB |
| SEC EDGAR | sec.gov/edgar | 미국 기업 공시 |
| Bellingcat Toolkit | bellingcat.gitbook.io/toolkit | OSINT 도구 |
| GIJN 리소스 | gijn.org/resource | 탐사보도 가이드 |

---

## 교재

### 데이터저널리즘
- 최윤원 외 (2022). 세상을 바꾸는 데이터저널리즘 with 뉴스타파
- 안혜민 (2023). 설명하기 지친 사람을 위한 데이터. 스리체어스
- GIJN Data Journalism: gijn.org/resource

### 파이썬
- 박응용 (2024). 점프 투 파이썬. https://wikidocs.net/book/1
- 조대표, 유대표 (2024). 초보자를 위한 파이썬 300제. https://wikidocs.net/book/922
- 김태준 (2022). Pandas DataFrame 완전정복. https://wikidocs.net/book/7188

### AI·LLM
- Google AI Studio: aistudio.google.com
- Gemini CLI: github.com/google-gemini/gemini-cli
- Gemini File Search: ai.google.dev/gemini-api/docs/file-search

### JavaScript · 시각화
- Chart.js: chartjs.org
- D3.js: d3js.org
- Leaflet.js: leafletjs.com
- vis.js Network: visjs.github.io/vis-network
- Scrollama.js: github.com/russellsamora/scrollama

### Streamlit
- Streamlit Docs: docs.streamlit.io
- Streamlit Components: docs.streamlit.io/develop/api-reference/custom-components
- Streamlit Cloud: streamlit.io/cloud

### 참고 사이트
- Kaggle: https://www.kaggle.com/
- Hugging Face: https://huggingface.co/
- Papers With Code: https://paperswithcode.com/
