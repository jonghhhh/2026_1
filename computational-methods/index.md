# 컴퓨테이셔널연구방법론 (2026)

## **경희대학교 미디어학과 일반대학원 | 목 13:00~15:45 | 정408**

## 📋 [강의개요 · 평가방법 · 교재 · 논문목록](syllabus.md)

---

> 💻 **개발환경**: VSCode + Gemini CLI  
> 🔑 **API**: Google AI Studio (Gemini) / OpenAI / Anthropic  
> 🤖 **AI 챗봇**: [chat.khu.ac.kr](https://chat.khu.ac.kr/) — 경희대 구성원 무료 제공  
> 🖥️ **OS**: Windows → WSL 사용 / Mac → 그대로 사용

---
> **[출석체크](https://jonghhhh.github.io/test/attendance_compmethod.html)**
> 
## Part 1: 기초 & 데이터 (1~5주)

---

### 1주차 (3/5): 컴퓨테이셔널연구방법론 소개 & 환경 설정

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [2026년 컴퓨테이셔널연구방법론 소개](https://jonghhhh.github.io/2026_1/computational-methods/컴퓨테이셔널연구방법론_2026.pdf)  
- (실습) WSL, VSCode, Gemini CLI 사용법  
-- [윈도우](https://jonghhhh.github.io/2026_1/WSL_VSCode_GeminiCLI_가이드)  
-- [Mac](https://jonghhhh.github.io/2026_1/Mac_VSCode_GeminiCLI_가이드)   
- (실습) Gemini CLI로 첫 번째 파이썬 코드 생성 체험  

</details>

---

### 2주차 (3/12): 파이썬 기초

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) [파이썬 기초 실습](https://jonghhhh.github.io/2026_1/ipynb/python_basic_vscode.ipynb): 변수, 자료형, 리스트, 조건문, 반복문, 함수, 클래스 등
- (자료) [cheat sheet: python](https://jonghhhh.github.io/2026_1/cheatsheets/python_basics.html)

**📄 논문 발표**
- Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., & Yang, D. (2024). Can large language models transform computational social science?. Computational Linguistics, 50(1), 237-291.  
- Lazer, D. M., Pentland, A., Watts, D. J., Aral, S., Athey, S., Contractor, N., ... & Wagner, C. (2020). Computational social science: Obstacles and opportunities. Science, 369(6507), 1060-1062.  

</details>

---

### 3주차 (3/19): 데이터 관리 — Pandas & NumPy

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (실습) [pandas 실습](https://jonghhhh.github.io/2026_1/ipynb/pandas_vscode.ipynb): 표 형태의 데이터(DataFrame)를 다루고 분석  
- (자료) [cheat sheet: pandas ](https://jonghhhh.github.io/2026_1/cheatsheets/pandas.html)  
- (실습) [numpy 실습](https://jonghhhh.github.io/2026_1/ipynb/numpy_vscode.ipynb): 수치 계산과 배열 연산  
- (자료) [cheat sheet: numpy](https://jonghhhh.github.io/2026_1/cheatsheets/numpy.html)
- (데이터) [교통사고다발지역](https://jonghhhh.github.io/2026_1/전국교통사고다발지역표준데이터-20260301.xls)  

**📄 논문 발표**
- 안순태, 임유진, & 이하나. (2020). 온라인 먹방 (먹는 방송, Mukbang) 의 댓글 연구: 식행동 관련 인식에 대한 빅데이터 분석. 한국언론학보, 64(2), 269-310.  
- 백강희, 이승윤, & 이종혁. (2025). 언론사와 증권사 간 인용 연결망을 통한 정보 불균형 탐구: 토픽모델링, 감성분석, 연결망분석을 통해. 언론정보연구, 62(1), 97-144.  

</details>

---

### 4주차 (3/26): 텍스트 수집 — 웹스크래핑

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

- (강의) [웹크롤링](https://jonghhhh.github.io/2026_1/ipynb/web_crawling_vscode.ipynb): HTML 구조, BeautifulSoup, Network 활용, playwright 등
- (자료) [HTML](https://jonghhhh.github.io/2026_1/ipynb/html_basic_vscode.ipynb): HTML 코드 원리 기초
- (실습) [네이버뉴스 수집](https://jonghhhh.github.io/2026_1/py/navernews_crawl.py): 네이버 뉴스 검색 수집  

**📄 논문 발표**
- 이종혁. (2021). 매체 간 뉴스 동질화 현상에 대한 탐색적 연구: Doc2Vec 을 통한 문서 유사도 측정의 활용. 언론정보연구, 58(4), 5-48.   
- Freelon, D. (2018). Computational research in the post-API age. Political Communication, 35(4), 665-668.  

</details>

---

### 5주차 (4/2): 이미지·영상 수집과 분석  

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- (강의) [youtube 분석](https://jonghhhh.github.io/2026_1/ipynb/youtube_vscode.ipynb)  
- (강의) [키프레임 추출](https://jonghhhh.github.io/2026_1/ipynb/keyframe_extract_vscode.ipynb)  
- (자료) [open_cv](https://jonghhhh.github.io/2026_1/ipynb/opencv_vscode.ipynb)  

**📄 논문 발표**
- 박대민. (2022). 미디어 인공지능: 컴퓨터 비전 관련 딥러닝 모델의 미디어 동영상 분야 적용 가능성에 관한 연구. 커뮤니케이션 이론, 18(1), 111-154.   
- 이문혁. (2025). K-POP 뮤직비디오의 이미지 유형화를 통한 시각적 특징 분석: 임베딩 벡터 추출 (CLIP) 과 유사도 검색 (FAISS) 을 통한 클러스터링. 언론정보연구, 62(2), 53-115.  

</details>

---

## Part 2: 딥러닝 & 추론 (6~7주)

---

### 6주차 (4/9): 딥러닝 이론 & PyTorch

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**  
- (강의) [딥러닝: 개념과 작동 원리](https://jonghhhh.github.io/2026_1/딥러닝_개념과작동원리_040226.pdf)    
- (자료) [PyTorch 실습](https://jonghhhh.github.io/2026_1/ipynb/pytorch_vscode.ipynb)   

**📄 논문 발표**
- 이문혁, 김시은, 신동호, & 이종혁. (2024). 재난보도 영상과 이미지 프레임에 나타난 국가 불평등 탐색: 비전 트랜스포머 (Vision Transformer) 를 활용한 KBS< 세계는 지금> 영상 분석. 한국방송학보, 38(2), 154-195.  
- 이종혁. (2022). 보수 언론과 진보 언론의 북한 전문가 활용 방식의 차이 탐색: 인용문에 대한 KPF-BERT 기반 딥러닝 분석을 중심으로. 한국언론학보, 66(6), 154-194.  
- 이문혁, & 이종혁. (2024). 시위 뉴스 영상에서 폭력 프레이밍의 작동 기제 분석: 비전 트랜스포머 (Vision Transformer) 를 활용한 폭력 이미지 분류를 통해. 한국언론학보, 68(2), 100-139.  

</details>

---

### 7주차 (4/16): Transformer, BERT, GPT & 추론 활용

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- Transformer: Self-Attention, Multi-Head Attention
- BERT: 양방향 인코더 / Sentence-BERT: 문장 임베딩
- GPT: 자기회귀 디코더, Instruction Tuning, RLHF
- Hugging Face Transformers Pipeline 추론

**실습**
- KcBERT / KcELECTRA 한국어 감성분석 추론
- Sentence-BERT로 문장 유사도 측정

**📄 논문 발표**
- 조원정, & 이종혁. (2023). 장애인 시위 관련 뉴스 댓글의 비윤리성 측정과 정치 성향에 따른 차이 비교: BERT 기반 딥러닝 분류기 개발과 적용. 한국방송학보, 37(2), 232-269.  
- 이승윤, 백강희, & 이종혁. (2023). 언론의 정치 성향에 따른 기업 보도 태도의 차이와 기업인 경기평가 심리에 미치는 영향 분석: BERT 기반 딥러닝 모형을 적용한 빅데이터 분석. 한국언론학보, 67(1), 185-229.  
- 정재철, & 이종혁. (2022). 한미동맹 보도에 대한 의제 도출과 ‘동맹-자주’관점의 비교 분석: BERT 모델 기반 딥러닝 모형의 활용. 사이버커뮤니케이션학보, 39(4), 205-263.  

</details>

---

## Part 3: LLM 내용분석 (8~10주)

---

### 8주차 (4/23): LLM API 활용 내용분석 — 텍스트

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- LLM API 구조: 시스템 프롬프트, Few-shot, JSON mode, 배치 처리
- 뉴스 텍스트 자동 코딩: 프레임, 감성, 논조, 인용 패턴
- LLM 코딩의 신뢰도 평가: 인간 코더 vs LLM 일치도

**실습**
- Gemini API로 뉴스 기사 100건 자동 코딩 (프레임, 감성, 논조)
- 코딩 결과의 일관성 검증

**📄 논문 발표**
- 이종혁. (2025). 12· 3 내란과 저널리즘 원칙: 오픈소스 생성형 LLM 을 활용한 언론보도 분석. 한국방송학보, 39(3), 123-166.   
- Törnberg, P. (2023). How to use LLMs for text analysis. arXiv preprint arXiv:2307.13106.  
- Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120.  

</details>

---

### 9주차 (4/30): LLM API 활용 내용분석 — 이미지, 영상, 음성

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- 멀티모달 LLM: 이미지 분석 (인물 표현, 감정, 구도, 맥락 해석)
- 영상 분석: 키프레임 → 멀티모달 LLM 분석 → 시계열 요약
- 음성 분석: Whisper STT → LLM 텍스트 분석 파이프라인
- 멀티모달 내용분석의 코딩 스키마 설계

**실습**
- 멀티모달 LLM으로 정치인 뉴스 사진 분석 (표정, 제스처, 앵글)
- 유튜브 뉴스 영상 → 키프레임 + 자막 → 통합 분석

**📄 논문 발표**
- 박영균, & 이종혁. (2026). 언론 시스템과 정치적 성향에 따른 김정은 보도사진의 시각적 프레이밍 연구: Multimodal LLM 을 활용한 국제 언론 비교 분석. 언론정보연구, 63(1), 157-198.  
- 윤호영, & 오령. (2024). 사회적 재난 방송 뉴스 보도 화면 분석: 이태원 참사 보도 화면 구성으로 본 저널리즘 실천 방식. 한국방송학보, 38(4), 155-203.  

</details>

---

### 10주차 (5/7): 임베딩, 유사도, 벡터 DB

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- 문장 임베딩: Sentence-BERT, 코사인 유사도
- K-Means 클러스터링, 차원 축소 시각화 (t-SNE, UMAP)
- 벡터 데이터베이스: ChromaDB
- 의미적 검색(Semantic Search)

**실습**
- 한국어 뉴스 임베딩 생성 → 유사도 매트릭스, K-Means 클러스터링
- ChromaDB에 뉴스 기사 임베딩 저장 및 유사 기사 검색

**📄 논문 발표**
- 이종혁. (2024). 온라인 뉴스의 선정성이 게재 시간과 이용자 평가에 미치는 영향: Sentence-BERT 와 BERT 모델을 활용한 텍스트 유사성, 비윤리성, 감정 측정. 한국언론학보, 68(5), 75-119.  

</details>

---

## Part 4: 챗봇 & 실험 (11~13주)

---

### 11주차 (5/14): RAG 챗봇 & Search Grounding

> 📌 **연구 아이디어 제출 (5/15, ecampus > 과제및평가)**

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- RAG(Retrieval-Augmented Generation) 원리: 문서 청킹 → 임베딩 → 벡터 검색 → LLM 생성
- LangChain을 활용한 RAG 파이프라인 구축
- Search Grounding: 실시간 웹 검색 기반 응답 생성
- 챗봇 인터페이스: Gradio, Streamlit, Hugging Face Spaces 배포

**실습**
- 특정 이슈 관련 뉴스 문서 기반 RAG 챗봇 구축
- Search Grounding 기능 추가 챗봇 구현

**📄 논문 발표**
- 이종혁 (세미나 발표문, 별도 배포). 한국어 팩트체크 필요성 탐지 모델 및 RAG 기반 팩트체크 자동화 시스템 개발: 대선 후보자 토론회 적용  

</details>

---

### 12주차 (5/21): 챗봇 실험 설계 — 인간 피험자 연구

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- 챗봇 기반 커뮤니케이션 실험의 이론적 배경: 설득, 프레이밍, 태도 변화
- 실험 설계: 시스템 프롬프트로 실험 조건 조작 (보수 vs 진보, 공감형 vs 정보형)
- 대화 로그 수집 및 분석 방법, 사전-사후 태도 측정
- IRB(연구윤리) 고려사항

**실습**
- 실험용 챗봇 프로토타입 개발 (조건별 시스템 프롬프트, 대화 로그 자동 저장)

**📄 논문 발표**
- Costello, T. H., Pennycook, G., & Rand, D. G. (2024). Durably reducing conspiracy beliefs through dialogues with AI. Science, 385(6714), eadq1814.   
- Salvi, F., Horta Ribeiro, M., Gallotti, R., & West, R. (2025). On the conversational persuasiveness of GPT-4. Nature Human Behaviour, 9(8), 1645-1653.  


</details>

---

### 13주차 (5/28): LLM 설문 시뮬레이션 (Silicon Sampling)

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- Silicon Sampling: LLM을 활용한 설문 응답 시뮬레이션
  - 인구통계 페르소나 부여 → LLM 응답 생성 → 실제 설문 결과와 비교
- Algorithmic Fidelity: LLM 시뮬레이션의 정확성 평가
- Homo Silicus: LLM을 경제·사회적 행위자로 활용
- 한계: 스테레오타이핑, 사회적 바람직성 편향, WEIRD 편향

**실습**
- 한국 사회 이슈에 대한 Silicon Sampling 실험
  - 인구통계(연령, 성별, 지역, 정치 성향) 페르소나 → LLM 응답 → 실제 여론조사 비교

**📄 논문 발표**
- Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024). Synthetic replacements for human survey data? The perils of large language models. Political Analysis, 32(4), 401-416.  
- Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of one, many: Using language models to simulate human samples. Political Analysis, 31(3), 337-351.  


</details>

---

## Part 5: 에이전트 & 시뮬레이션 (14~15주)

---

### 14주차 (6/4): LLM 에이전트 & LangGraph 워크플로우

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- 에이전트란 무엇인가: Tool Use, Planning, Memory
- 에이전트 아키텍처: ReAct, Function Calling
- LangGraph를 활용한 에이전트 워크플로우 설계: 상태 관리, 노드/엣지, 조건부 분기
- 에이전트 프레임워크: LangChain Agents, Google ADK, CrewAI

**실습**
- LangGraph로 팩트체크 에이전트 구현
- 뉴스 분석 에이전트: 기사 수집 → 프레임 분석 → 요약 → 보고서

**📄 논문 발표**
- 이문혁, 이두황, 이종혁 (세미나 발표문, 별도 배포). AI 에이전트를 활용한 뉴스 윤리 심의문 자동 생성 시스템의 개발 및 적용: 네이버 '많이 본 뉴스' 분석을 중심으로
- Xi, Z., Chen, W., Guo, X., He, W., Ding, Y., Hong, B., ... & Gui, T. (2025). The rise and potential of large language model based agents: A survey. Science China Information Sciences, 68(2), 121101.  

</details>

---

### 15주차 (6/11): 에이전트 간 토론 & Generative ABM

<details markdown="1">
<summary>📖 강의 내용 보기</summary>

**강의**
- 에이전트 간 토론 시스템
  - 숙의 민주주의 이론 기반 멀티 에이전트 토론
  - 에이전트에 페르소나 부여 (인구통계, 정치 성향, 미디어 이용 패턴)
  - 토론 프로토콜 설계 (라운드제, 자유토론, 모더레이터)
- Generative Agent-Based Modeling (ABM)
  - 생성적 에이전트: 기억, 반성, 계획
  - 태도 극화(polarization) 시뮬레이션
  - 미디어 노출 → 에이전트 간 상호작용 → 의견 변화 추적
  - 에코 챔버, 필터 버블 시뮬레이션

**실습**
- 멀티 에이전트 토론 시스템 구현: 3~5개 에이전트가 특정 이슈에 대해 토론
- 소규모 Generative ABM: 10~20개 에이전트, 5라운드 상호작용, 태도 변화 시각화

**📄 논문 발표**
- Park, J. S., Zou, C. Q., Shaw, A., Hill, B. M., Cai, C., Morris, M. R., ... & Bernstein, M. S. (2024). Generative agent simulations of 1,000 people. arXiv preprint arXiv:2411.10109.
- Park, J. S., O'Brien, J., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023, October). Generative agents: Interactive simulacra of human behavior. In Proceedings of the 36th annual acm symposium on user interface software and technology (pp. 1-22).
- - Anthis, J. R., Liu, R., Richardson, S. M., Kozlowski, A. C., Koch, B., Evans, J., ... & Bernstein, M. (2025). LLM social simulations are a promising research method. arXiv preprint arXiv:2504.02234.   
- Chuang, Y. S., Goyal, A., Harlalka, N., Suresh, S., Hawkins, R., Yang, S., ... & Rogers, T. (2024, June). Simulating opinion dynamics with networks of llm-based agents. In Findings of the association for computational linguistics: NAACL 2024 (pp. 3326-3346).  
- Törnberg, P., Valeeva, D., Uitermark, J., & Bail, C. (2023). Simulating social media using large language models to evaluate alternative news feed algorithms. arXiv preprint arXiv:2310.05984.  

</details>

---

### 16주차 (6/18): 분석 능력 테스트 (오픈북)

- **분석 능력 테스트 (6/18)**: 코드해석 + 오픈북 분석 테스트
- **연구 분석 결과 제출 (6/25, ecampus > 과제및평가에 제출)**
