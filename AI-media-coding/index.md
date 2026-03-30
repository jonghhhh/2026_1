# 인공지능미디어코딩 (2026)

## **경희대학교 미디어학과 | 월수 15:00~16:15 | 정408**

## 📋 [강의개요 · 평가방법 · 교재](syllabus.md)

---

> 💻 **개발환경**: VSCode + Gemini CLI  
> 🔑 **API**: Google AI Studio (Gemini) / OpenAI / Anthropic  
> 🤖 **AI 챗봇**: [chat.khu.ac.kr](https://chat.khu.ac.kr/) — 경희대 구성원 무료 제공  
> 🖥️ **OS**: Windows → WSL 사용 / Mac → 그대로 사용

---
> **[출석체크](https://jonghhhh.github.io/test/attendance_aicoding.html)**

### 1주차 (3/4, 3/9) 

**수업 소개 & 개발환경 설정**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [인공지능과 미디어](https://jonghhhh.github.io/2026_1/AI-media-coding/인공지능과미디어_2026.pdf) 
- (실습) WSL, VSCode, Gemini CLI 사용법  
-- [윈도우](https://jonghhhh.github.io/2026_1/WSL_VSCode_GeminiCLI_가이드)  
-- [Mac](https://jonghhhh.github.io/2026_1/Mac_VSCode_GeminiCLI_가이드)  
- (실습) Gemini CLI로 첫 번째 파이썬 코드 생성 체험

</details>

---

### 2주차 (3/11, 3/16): 파이썬 기초

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) [파이썬 기초 실습](https://jonghhhh.github.io/2026_1/ipynb/python_basic_vscode.ipynb): 변수, 자료형, 리스트, 조건문, 반복문, 함수, 클래스 등
- (자료) [cheat sheet: python](https://jonghhhh.github.io/2026_1/cheatsheets/python_basics.html)

</details>

---

### 3주차 (3/18, 3/23): 데이터 관리 — Pandas & NumPy

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) [pandas 실습](https://jonghhhh.github.io/2026_1/ipynb/pandas_vscode.ipynb): 표 형태의 데이터(DataFrame)를 다루고 분석  
- (자료) [cheat sheet: pandas ](https://jonghhhh.github.io/2026_1/cheatsheets/pandas.html)  
- (실습) [numpy 실습](https://jonghhhh.github.io/2026_1/ipynb/numpy_vscode.ipynb): 수치 계산과 배열 연산  
- (자료) [cheat sheet: numpy](https://jonghhhh.github.io/2026_1/cheatsheets/numpy.html)
- (데이터) [교통사고다발지역](https://jonghhhh.github.io/2026_1/전국교통사고다발지역표준데이터-20260301.xls)  

</details>

---

### 4주차 (3/25, 3/30): 임베딩 ① — 벡터와 유사도

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [임베딩_벡터와유사도](https://jonghhhh.github.io/2026_1/임베딩_벡터와유사도.pdf): One-hot → TF-IDF → 밀집 벡터, 텍스트·이미지의 벡터 표현과 코사인 유사도


</details>

---

### 5주차 (4/1, 4/6): 임베딩 ② — 클러스터링

<details markdown="1">
<summary>📖 강의 내용 보기</summary>  
- (강의) [임베딩_토크나이징과클러스터링](https://jonghhhh.github.io/2026_1/임베딩_토크나이징과클러스터링.pdf): 토크나이징, 클러스터링(k-means)    

</details>

---

### 6주차 (4/8, 4/13): 딥러닝 기초 — 학습 원리 & PyTorch

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) 딥러닝
- (실습) [PyTorch 실습](https://jonghhhh.github.io/2026_1/ipynb/pytorch_vscode.ipynb)

</details>

---

### 7주차 (4/15, 4/20): CNN & RNN — 이미지와 텍스트의 딥러닝

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) CNN: 합성곱, 풀링, 특징 추출 — 이미지 인식의 핵심
- (강의) RNN / LSTM: 순차 데이터 처리 — 텍스트·시계열의 핵심
- (강의) CNN → ViT, RNN → Transformer로의 발전 흐름
- (실습) PyTorch CNN으로 간단한 이미지 분류 (MNIST 또는 뉴스 이미지)
- (실습) PyTorch RNN/LSTM으로 간단한 텍스트 감성 분류

</details>

---

### 8주차 (4/22, 4/27): 중간고사

- 보강 수업 (4/22)
- **중간고사 (4/27)**: 코드해석 시험 + 오픈북 분석 테스트

---

### 9주차 (4/29, 5/4): Transformer & BERT — 이론과 감성분석 실습

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) Transformer: Self-Attention, Multi-Head Attention, 위치 인코딩
- (강의) BERT: 양방향 인코더, MLM, NSP — 사전학습과 파인튜닝
- (강의) Sentence-BERT: 문장 수준 임베딩과 유사도
- (실습) Hugging Face Transformers 기초: Pipeline API 사용법
- (실습) KcBERT / KcELECTRA로 한국어 뉴스 감성분석
- (실습) Hugging Face Hub 탐색: 모델·데이터셋 검색, 불러오기, 추론
  - 감성분석, NER, 문장 유사도, 이미지 분류, 요약 등

</details>

---

### 10주차 (5/6, 5/11): GPT & LLM API — 텍스트·멀티모달 내용분석

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) GPT: 자기회귀 디코더, Instruction Tuning, RLHF
- (강의) LLM API 구조: 시스템 프롬프트, Few-shot, JSON mode
- (강의) 텍스트 자동 코딩: 프레임, 감성, 논조, 인용 패턴
- (강의) 멀티모달 LLM: 뉴스 사진 분석 (인물 표현, 감정, 구도)
- (강의) 영상 분석: 키프레임 → 멀티모달 LLM / 음성: Whisper STT → LLM
- (실습) Gemini API로 뉴스 기사 100건 자동 코딩 (배치 처리)
- (실습) 멀티모달 LLM으로 뉴스 사진 분석
- (실습) LLM 코딩 신뢰도 평가: 인간 코더 vs LLM 일치도

</details>

---

### 11주차 (5/13, ~~5/18~~): 데이터 수집 & LLM 분석 파이프라인

> ※ 5/18(월) 휴일 — 1회 수업

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) API 기반 데이터 수집: 뉴스 API, 공공데이터 API, YouTube Data API
- (강의) 수집 → 정제 → LLM 분석 파이프라인 설계
- (실습) 뉴스 API(예: NewsAPI, 네이버 검색 API)로 기사 수집
- (실습) 수집한 기사에 LLM API 적용: 자동 분류·요약·감성 분석
- (실습) 결과를 DataFrame으로 정리 → CSV 저장 → 시각화

</details>

---

### 12주차 (5/20, ~~5/25~~): 챗봇 만들기 — RAG & Search Grounding

> ※ 5/25(일) 휴일 — 1회 수업

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) RAG(Retrieval-Augmented Generation) 원리
  - 문서 청킹 → 임베딩 → 벡터 검색 → LLM 생성
- (강의) LangChain을 활용한 RAG 파이프라인
- (강의) Search Grounding: 실시간 웹 검색 기반 응답 생성
- (강의) 챗봇 기반 커뮤니케이션 실험 설계
  - 시스템 프롬프트로 실험 조건 조작, 대화 로그 수집
- (실습) 뉴스 문서 기반 RAG 챗봇 구축 (ChromaDB + LangChain + Gemini)
- (실습) Search Grounding 기능 추가
- (실습) Gradio / Streamlit 챗봇 인터페이스 구현

</details>

---

### 13주차 (5/27, 6/1)

**LLM 에이전트 & LangGraph 워크플로우**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) 에이전트란 무엇인가: Tool Use, Planning, Memory
- (강의) 에이전트 아키텍처: ReAct, Function Calling
- (강의) LangGraph를 활용한 에이전트 워크플로우 설계
  - 상태(State) 관리, 노드와 엣지, 조건부 분기
- (실습) LangGraph로 팩트체크 에이전트 구현
  - 웹 검색 → 정보 수집 → 검증 → 보고서 생성

</details>

---

### 14주차 (~~6/3~~, 6/8)

> ※ 6/3(수) 휴일 — 1회 수업

**LangGraph 멀티에이전트 시스템**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) 멀티에이전트 시스템: 역할 분담, 협업 워크플로우
- (강의) 특수 목적 AI 서비스 기획
  - 예시: 뉴스 윤리 검증 AI, 선거 공약 비교 AI, 미디어 리터러시 교육 AI, 콘텐츠 기획 AI
- (강의) 공모전 프로젝트 전략: 문제 정의 → 아키텍처 → 프로토타입 → 발표
- (실습) LangGraph 멀티에이전트 실습
  - 기획자-조사자-작성자-검수자 역할 분담 에이전트
- (토론) 프로젝트 아이디어 피칭 및 피드백

</details>

---

### 15주차 (6/10, 6/15): 멀티에이전트 시스템 구현 & 배포

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) 멀티에이전트 서비스 아키텍처: 프론트엔드(Gradio/Streamlit) + 백엔드(LangGraph) + DB(ChromaDB)
- (강의) 배포 파이프라인: Hugging Face Spaces, Firebase, Cloud Run
- (강의) 프로젝트 완성도 높이기: UX 설계, 에러 핸들링, 프롬프트 최적화
- (강의) 공모전 포트폴리오 전략: 문제 정의 → 데모 영상 → 기술 문서 → 발표 자료
- (실습) 팀별 멀티에이전트 프로토타입 통합 구현 및 배포
  - RAG + Search Grounding + 에이전트 기능 결합
- (실습) 배포된 서비스 테스트 및 피드백

</details>

---

### 16주차 (6/17, 6/22): 기말고사 & 기획안 제출

- 보강 수업 (6/17)
- **기말고사 (6/22)**: 코드해석 + 오픈북 분석 테스트
- **멀티에이전트 프로젝트 기획안 제출 (6/22, ecampus > 과제및평가에 제출)**
