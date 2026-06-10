# 데이터저널리즘 (2026)

## **경희대학교 미디어학과 | 월수 10:30~11:45 | 정408**

## 📋 [강의개요 · 평가방법 · 교재](syllabus.md)

---

> 💻 **개발환경**: VSCode + Gemini CLI  
> 🔑 **API**: Google AI Studio (Gemini 2.5 Flash-Lite)  
> 🌐 **통합 플랫폼**: Streamlit + `components.html()` JS 임베드  
> 🤖 **AI 챗봇**: [chat.khu.ac.kr](https://chat.khu.ac.kr/) — 경희대 구성원 무료 제공  
> 🖥️ **OS**: Windows → WSL 사용 / Mac → 그대로 사용

> **[조 구성 및 출석체크](https://jonghhhh.github.io/test/attendance_datajour.html)**  
> **[취재보도용 AI도구 모음](https://jonghhhh.github.io/2026_1/datajour_ai.html)**    
> **[데이터 수집용 사이트 모음](https://jonghhhh.github.io/2026_1/datajour_source.html)**    
> **[한국 Public API 모음](https://github.com/yybmion/public-apis-4Kr)**      
---

## Part 1. 기초 — 파이썬 & Pandas (1~4주)

---

### 1주차 (3/4, 3/9)

**데이터저널리즘 소개 & 환경 설정**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [데이터저널리즘: 이론과 실무](https://jonghhhh.github.io/2026_1/data-journalism/데이터저널리즘_이론과실무_022826.pdf)
- (실습) WSL, VSCode, Gemini CLI 사용법     
-- [윈도우](https://jonghhhh.github.io/2026_1/WSL_VSCode_GeminiCLI_완전초보_가이드)    
-- [Mac](https://jonghhhh.github.io/2026_1/Mac_VSCode_GeminiCLI_완전초보_가이드)     
- AI 도구 체험: NotebookLM, Perplexity, Google AI Studio
- (데이터) 공공데이터포털 [교통사고다발지역](https://www.data.go.kr/data/15029185/standard.do)
</details>

---

### 2주차 (3/11, 3/16): 파이썬 기초 (1)

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) [파이썬 기초 실습](https://jonghhhh.github.io/2026_1/ipynb/python_basic_vscode.ipynb): 변수, 자료형, 리스트, 조건문, 반복문, 함수, 클래스 등  
- (자료) [cheat sheet](https://jonghhhh.github.io/2026_1/cheatsheets/python_basics.html)  
</details>

---

### 3주차 (3/18, 3/23): 파이썬 기초 (2)

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) [pandas 실습](https://jonghhhh.github.io/2026_1/ipynb/pandas_vscode.ipynb): 표 형태의 데이터(DataFrame)를 다루고 분석  
- (자료) [cheat sheet: pandas ](https://jonghhhh.github.io/2026_1/cheatsheets/pandas.html)  
- (실습) [numpy 실습](https://jonghhhh.github.io/2026_1/ipynb/numpy_vscode.ipynb): 수치 계산과 배열 연산  
- (자료) [cheat sheet: numpy](https://jonghhhh.github.io/2026_1/cheatsheets/numpy.html)
- (데이터) [교통사고다발지역](https://jonghhhh.github.io/2026_1/전국교통사고다발지역표준데이터-20260301.xls)    
 
</details>

---

### 4주차 (3/25, 3/30): 데이터 분석 — Pandas

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- 위 내용 계속   
</details>

---

## Part 2. 수집 — 크롤링 · API (5~6주)

---

### 5주차 (4/1, 4/6): 웹 기초 + 웹스크래핑

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [웹크롤링](https://jonghhhh.github.io/2026_1/ipynb/web_crawling_vscode.ipynb): HTML 구조, BeautifulSoup, Network 활용, playwright 등
- (자료) [HTML](https://jonghhhh.github.io/2026_1/ipynb/html_basic_vscode.ipynb): HTML 코드 원리 기초
- (실습) [네이버뉴스 수집](https://jonghhhh.github.io/2026_1/py/navernews_crawl.py): 네이버 뉴스 검색 수집
</details>

---

### 6주차 (4/8, 4/13): 데이터 수집 심화 — API 활용

<details markdown="1">
<summary>📖 강의 내용 보기</summary>  
  
- (강의) [API: 이론과 실습](https://jonghhhh.github.io/2026_1/API활용_데이터수집_040226.pdf)
- (실습) [네이버 API 수집](https://jonghhhh.github.io/2026_1/py/naver_search_api.py): 네이버 API 검색 수집(엔드포인트 7종)    

</details>

---

## Part 3. 분석 — AI 대량 분석 자동화 (7주)

---

### 7주차 (4/15, 4/20): LLM 활용 데이터 분석: 텍스트 + 이미지

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [LLM 활용 데이터 분석](https://jonghhhh.github.io/2026_1/ipynb/llm_content_analysis.ipynb): API, 텍스트, 이미지, json, pandas  
- (실습) 구글 시트 =AI()로 대량 텍스트 분류  
- (실습) NotebookLM 심층 활용  

</details>

---

## Part 4. 시각화 — JavaScript 인터랙티브 시각화 (8~10주)

---

### 8주차 (4/22, 4/27): JS 시각화 입문 — JavaScript 기초

> ★ **조별 프로젝트 기획안 제출 (4/27, 중간고사 대체)**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [JavaScript 기초](https://jonghhhh.github.io/2026_1/js/js_basics.html): javaScript 기초 - 변수(let/const), 함수, 조건문, 반복문, DOM 조작   

</details>

---

### 9주차 (4/29, 5/4): 인터랙티브 그래프(Chart.js) +  

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [charts](https://jonghhhh.github.io/2026_1/js/js_charts.html): Bar, Line, Pie, Doughnut, Radar, Scatter, Bubble, Mixed, Treemap, 인터랙티브 필터   
- (강의) [more charts](https://jonghhhh.github.io/2026_1/js/js_more_charts.html): 워드클라우드, Sankey, Calendar Heatmap, Sunburst, Boxplot, Gauge, Funnel 등 시각화 추가

</details>

---

### 10주차 (5/6, 5/11): 네트워크 시각화(vis.js), 지도 시각화(Leaflet), Scrollytelling

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

-(강의) [network](https://jonghhhh.github.io/2026_1/js/js_network.html): vis-network, D3, Cytoscape 기반 Force Network, Tree, 양분망, 의미연결망  
-(강의) [maps](https://jonghhhh.github.io/2026_1/js/js_maps.html): Leaflet 지도, 마커, 클러스터링, 히트맵, 코로플레스, 폴리라인·폴리곤, 베이스맵 전환  
-(강의) [scrollytelling](https://jonghhhh.github.io/2026_1/js/js_scrollytelling.html): DataTables, Scrollama, 스크롤리텔링, 스티키 차트, 인터랙티브 기사 제작  
-(강의) [js 시각화를 위한 프롬프트 사용법: 교통사고 데이터 사례](https://jonghhhh.github.io/2026_1/js/js_프롬프트5_교통사고.html): 위 시각화에 대한 사례 실습. 프롬프트 중심 바이브 코딩


</details>

---

## Part 5. 웹앱 — 통합 · 배포 (11~14주)

---

### 11주차 (5/13, ~~5/18~~): 웹 개발, 빌드, 배포 + 챗봇

> ※ 5/18(월) 휴일 — 1회 수업

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

-(강의) [웹 개발 빌드 배포](https://jonghhhh.github.io/2026_1/웹_개발_빌드_배포.html)  
-(강의) [github 사용법: 배포를 위해](https://jonghhhh.github.io/2026_1/github_사용법.html)  
-(실습 예제) [챗봇 만들기 프롬프트](https://jonghhhh.github.io/2026_1/프롬프트_GoogleAIStudio_Build_JS_챗봇.html)     

</details>

---

### 12주차 (5/20, ~~5/25~~): 내용 통합 웹 배포

> ※ 5/25(일) 휴일 — 1회 수업

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) [프로젝트 웹페이지 구성_프롬프트](https://jonghhhh.github.io/2026_1/웹구성_프롬프트.md)
- (실습 자료) [프로젝트 웹페이지 구성_가상자료](https://jonghhhh.github.io/2026_1/웹구성자료.zip)

</details>

---

### 13주차 (5/27, 6/1): 전통적 취재보도 방법론 

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [취재방법론](https://jonghhhh.github.io/2026_1/data-journalism/취재_현장_사람_자료.html): 현장 취재, 인터뷰, 자료 취재
- (강의) [보도_기사작성](https://jonghhhh.github.io/2026_1/data-journalism/보도_기사작성_유형원칙.html): 스트레이트, 해설, 피처, 기획기사 사례
- (강의) [보도사진_촬영편집_원칙](https://jonghhhh.github.io/2026_1/data-journalism/보도사진_촬영편집_원칙.html): 보도사진의 특성, 촬영과 편집, 윤리       

</details>

---

### 14주차 (~~6/3~~, 6/8): 데이터 수집-분석-시각화-배포 통합 실습

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- 자유 주제 강의 및 실습 복습 상담

</details>

---

## Part 6. 발표 & 평가 (15~16주)

---

### 15주차 (6/10, 6/15): 최종과제 제출(6/14 오후 3시, 이캠퍼스), 조별 발표(6/15, 6/17)

- (6/15) 1~3조 발표
- (6/17) 4~6조 발표
   
---

### 16주차 (6/17, 6/22): 데이터처리능력 테스트

 
- **시험 (6/22)**: 코드리딩 + AI 프롬프트 작성 + JS 시각화 코드 이해 + Streamlit 코드 이해


---

## 참고자료(프로젝트는 접속 안되는 경우 있음)

- [2025년 데이터저널리즘 프로젝트](https://sites.google.com/khu.ac.kr/2025datajour-projects/%ED%99%88)

- [2024년 데이터저널리즘 프로젝트](https://sites.google.com/khu.ac.kr/datajour2024/%ED%99%88)

- [조별 데이터저널리즘 프로젝트 제출과  평가 가이드라인](https://docs.google.com/document/d/1f1FttS7dG9aAQ9kd4menLzrDeBFY9-HD/edit#heading=h.gjdgxs)
