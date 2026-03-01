# 데이터저널리즘 (2026년 1학기)

## **경희대학교 미디어학과 | 월수 10:30~11:45 | 정408**

> 📋 [강의개요 · 평가방법 · 교재](syllabus.md)

---

> 💻 **개발환경**: VSCode + Gemini CLI  
> 🔑 **API**: Google AI Studio (Gemini 2.5 Flash-Lite)  
> 🌐 **통합 플랫폼**: Streamlit + `components.html()` JS 임베드  
> 🤖 **AI 챗봇**: [chat.khu.ac.kr](https://chat.khu.ac.kr/) — 경희대 구성원 무료 제공  
> 🖥️ **OS**: Windows → WSL 사용 / Mac → 그대로 사용

> **취재보도용 AI도구 모음**: https://jonghhhh.github.io/2026_1/datajour_ai.html  
> **데이터 수집용 사이트 모음**: https://jonghhhh.github.io/2026_1/datajour_source.html
---

## Part 1. 기초 — 파이썬 & Pandas (1~4주)

---

### 1주차 (3/4)

**데이터저널리즘 소개 & 환경 설정**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [데이터저널리즘: 이론과 실무](https://jonghhhh.github.io/2026_1/데이터저널리즘_이론과실무_022826.pdf)
- (실습) WSL, VSCode, Gemini CLI 사용법  
-- 윈도우: https://jonghhhh.github.io/2026_1/WSL_VSCode_GeminiCLI_완전초보_가이드
-- Mac: https://jonghhhh.github.io/2026_1/Mac_VSCode_GeminiCLI_완전초보_가이드  
- AI 도구 체험: NotebookLM, Perplexity, Google AI Studio
- (데이터) 공공데이터포털 [교통사고다발지역](https://www.data.go.kr/data/15029185/standard.do)
</details>

---

### 2주차 (3/9, 3/11): 파이썬 기초 (1)

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) 파이썬 기초
</details>

---

### 3주차 (3/16, 3/18): 파이썬 기초 (2)

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) 파이썬 기초
</details>

---

### 4주차 (3/23, 3/25): 데이터 분석 — Pandas

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) 파이썬 pandas
</details>

---

## Part 2. 수집 — 크롤링 · API · PDF OCR (5~6주)

---

### 5주차 (3/30, 4/1): 웹 기초 + 프롬프트코딩 + 웹스크래핑

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) HTML 구조와 CSS 선택자 읽기 (크롤링·시각화에 필수)
- (강의) 프롬프트코딩 5원칙: 구체성, 단계별 요청, 컨텍스트, 출력 형식, 반복 수정
- (강의) 웹 크롤링: requests + BeautifulSoup, Playwright
- (강의) 윤리적 크롤링: robots.txt, 요청 간격, 개인정보보호법
- (실습) 브라우저 개발자 도구(F12) → CSS 선택자 추출
- (실습) Gemini CLI로 네이버 뉴스 '교통사고' 기사 크롤링
- (실습) 프롬프트 비교 실험: 모호한 vs. 구체적 프롬프트

</details>

---

### 6주차 (4/6, 4/8): 데이터 수집 심화 — API · PDF OCR · 정보공개청구

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) API 이론: REST API, HTTP 메서드, JSON 응답, API 키 인증
- (강의) PDF OCR: Google AI Studio + PaddleOCR + pdfplumber
- (강의) 정보공개청구(FOI): 정보공개포털, 청구 전략, 뉴스타파 사례
- (실습) KOROAD Open API로 교통사고 통계 수집
- (실습) DART Open API로 기업 재무 데이터 수집
- (실습) Gemini API로 교통사고 PDF 보고서 표 추출 → DataFrame
- (과제) 조별 프로젝트 데이터를 2개+ 소스에서 수집

</details>

---

## Part 3. 분석 — AI 대량 분석 자동화 (7주)

---

### 7주차 (4/13, 4/15): 데이터 정제 + LLM API 대량 분석

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) Pandas 전처리: 결측치, 중복, 타입 변환, 텍스트 정제
- (강의) LLM API 대량 분석 패턴: DataFrame 순회 → API 호출 → 분류/요약 → 새 열 저장
- (강의) 모델 라우팅: Flash-Lite(대량 단순) → Flash(중간) → Pro(소량 고복잡도)
- (강의) 실제 언론사 사례: NYT, ProPublica, IStories
- (강의) 구글 시트 =AI() 함수, Gemini Vision 이미지 분석
- (실습) Flash-Lite API로 교통사고 위치명 667건 장소유형 분류
- (실습) 구글 시트 =AI()로 대량 텍스트 분류
- (실습) NotebookLM 심층 활용: 뉴스 기사 + PDF → 요약·FAQ
- (과제) 조별 데이터 전처리 + LLM 분석 결과 1건+

</details>

---

## Part 4. 시각화 — JavaScript 인터랙티브 시각화 (8~10주)

---

### 8주차 (4/20, 4/22): JS 시각화 입문 — 인터랙티브 그래프 (Chart.js)

> ★ **조별 프로젝트 기획안 제출 (중간고사 대체)**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) JavaScript 기초: 변수(let/const), 함수, DOM, 이벤트, 배열 메서드(.map/.filter/.reduce)
- (강의) **비동기 데이터 로딩**: `fetch()` + `async/await` — JSON 파일 로드 핵심 패턴
- (강의) Chart.js: CDN, 차트 유형(bar/line/pie/doughnut/radar/bubble), 데이터 업데이트
- (실습) 교통사고 연도별 추이 선·막대 그래프 (JSON fetch)
- (실습) 사고유형 드롭다운 필터 → 그래프 애니메이션 업데이트
- (실습) 도넛·레이더·버블 차트 탭 전환

</details>

---

### 9주차 (4/27, 4/29): 네트워크 시각화 (vis.js) + 지도 시각화 (Leaflet)

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) 네트워크 시각화: 그래프 기초, 노드·엣지, ICIJ 사례
- (강의) vis.js Network: 물리 시뮬레이션, 인터랙티브 (클릭, 호버, 줌)
- (강의) Leaflet.js: 마커, 코로플레스, 히트맵, 마커 클러스터, 레이어 전환
- (강의) 좌표계, 타일 맵, GeoJSON 형식
- (실습) vis.js: 시도-사고유형 네트워크 (노드 크기=건수, 클릭 시 상세)
- (실습) Leaflet: 교통사고 12,780건 마커 클러스터 (유형별 색상, 체크박스 토글)
- (실습) 시도별 코로플레스 + 히트맵

</details>

---

### 10주차 (5/4, 5/6): Scrollytelling + 시각화 종합

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) Scrollytelling: Intersection Observer, Scrollama.js, sticky 레이아웃
- (강의) 멀티미디어 요소: Napkin AI 인포그래픽, AI 삽화, Gamma 발표자료
- (강의) 데이터 검증 & 팩트체크: Bulletproofing, TAAS 교차 검증, OSINT 기초
- (실습) 교통사고 Scrollytelling 기사 (5섹션: 히트맵→도넛→확대지도→선그래프→하이라이트)
- (실습) 지금까지 만든 시각화(그래프+지도+네트워크) 통합 HTML 구성
- (과제) 조별 JS 시각화 3종+ 완성 (HTML 파일)

</details>

---

## Part 5. 웹앱 — Streamlit 통합 · 검색 · 챗봇 · 배포 (11~14주)

---

### 11주차 (5/11, 5/13): Streamlit 입문 & JS 시각화 임베드

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) **Streamlit 기초**: 설치, 실행(`streamlit run app.py`), 핫 리로드
- (강의) 레이아웃: `st.columns`, `st.tabs`, `st.sidebar`, `st.expander`
- (강의) 데이터 표시: `st.dataframe`, `st.metric`, `st.json`
- (강의) **`st.components.v1.html()` 패턴**: JS 시각화를 Streamlit에 임베드
  - Pandas → JSON 문자열 → f-string으로 JS에 주입 → `components.html(html, height=500)`
  - Chart.js, Leaflet, vis.js 모두 이 패턴으로 임베드
- (강의) 멀티페이지 앱: `pages/` 디렉토리 구조
- (실습) Streamlit "Hello World" + 교통사고 데이터 표시
- (실습) Chart.js 그래프를 `components.html()`로 임베드
- (실습) Leaflet 지도를 `components.html()`로 임베드
- (실습) 멀티페이지 구성: 메인 / 시각화 / 검색 / 챗봇

</details>

---

### 12주차 (5/18, 5/20): 맞춤형 데이터 검색 & 통합 대시보드

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) **Streamlit 네이티브 위젯으로 맞춤형 검색**
  - `st.selectbox`: 시도·사고유형 선택
  - `st.slider`: 연도 범위 선택
  - `st.multiselect`: 복수 조건 조합
  - `st.text_input`: 위치명 키워드 검색
  - `st.radio`, `st.checkbox`: 표시 옵션 토글
- (강의) **위젯-시각화 연동 패턴**
- (강의) **대시보드 설계**: 정보 계층(핵심 수치→트렌드→상세), 필터 연동
- (강의) `st.session_state`로 필터 상태 유지
- (실습) 교통사고 통합 대시보드 구축
- (실습) 키워드 검색: `st.text_input` → Pandas 텍스트 필터 → 결과 테이블 + 지도
- (과제) 조별 프로젝트 Streamlit 대시보드 프로토타입

</details>

---

### 13주차 (5/27) 

**RAG 챗봇 (간단) & 최종 웹앱 통합**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) RAG 개념: 외부 문서 기반 LLM 응답으로 환각 방지
- (강의) **Gemini File Search**: Store 생성 → CSV·PDF 업로드 → 질문 — 끝!
  - 자동: 청킹 → 임베딩 → 벡터 저장 → 의미 검색 → 인용(citation) 표시
- (강의) **Streamlit 챗봇 UI**: `st.chat_input` + `st.chat_message` + `st.session_state`
- (강의) 디지털 보안: Signal, SecureDrop, 취재원 보호
- (실습) File Search Store 생성 + 교통사고 CSV·PDF 업로드
- (실습) Streamlit 챗봇 페이지 구현
- (실습) 추천 질문 버튼 3개 + 대화 히스토리 유지
- (실습) **최종 통합**: 메인(Scrollytelling) + 대시보드(검색+시각화) + 챗봇 → 멀티페이지 앱

</details>

---

### 14주차 (6/1) 

**취재 방법론 + 배포 + 프로젝트 최종 점검**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) 취재 방법론: 현장 취재, 인터뷰, 자료 취재
- (강의) 기사 작성: 스트레이트, 해설, 피처, 기획기사 사례
- (강의) 데이터저널리즘 윤리: 정확성, AI 투명성, 개인정보·취재원 보호
- (강의) **배포**: Hugging Face Spaces / Streamlit Cloud
- (실습) 조별 Streamlit 웹앱 배포 및 최종 통합
- (실습) 크로스 리뷰: 다른 조 웹앱 사용 → 피드백
- (실습) 배포 URL 최종 확인

</details>

---

## Part 6. 발표 & 평가 (15~16주)

---

### 15주차 (6/8, 6/10): 조별 발표

- (첫 수업) 1~4조 발표: 각 15분 발표 + 10분 질의응답
- (두 번째) 5~8조 발표 + 전체 피드백 + 우수 프로젝트 선정
- 발표 내용: 기획 의도, 데이터 수집·분석, 시각화 전략, Streamlit 웹앱 시연
- 기획기사 공모전 출품 안내

---

### 16주차 (6/15, 6/17): 데이터처리능력 테스트

- 보강 수업 (6/15)
- **시험 (6/17)**: 코드리딩 + AI 프롬프트 작성 + JS 시각화 코드 이해 + Streamlit 코드 이해


---

## 참고자료(프로젝트는 접속 안되는 경우 있음)

- [2025년 데이터저널리즘 프로젝트](https://sites.google.com/khu.ac.kr/2025datajour-projects/%ED%99%88)

- [2024년 데이터저널리즘 프로젝트](https://sites.google.com/khu.ac.kr/datajour2024/%ED%99%88)

- [조별 데이터저널리즘 프로젝트 제출과  평가 가이드라인](https://docs.google.com/document/d/1f1FttS7dG9aAQ9kd4menLzrDeBFY9-HD/edit#heading=h.gjdgxs)
