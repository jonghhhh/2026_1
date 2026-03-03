# 컴퓨테이셔널연구방법론 — 강의개요

**경희대학교 미디어학과 일반대학원 | DOM701100 | 목 13:00~15:45 | 정408**

**담당교수**: 이종혁 (정경대 교수회관 620호, 02-961-2179, jonghhhh@khu.ac.kr)

> ← [주차별 수업 내용으로 돌아가기](index.md)

---

## 수업 목표

- LLM·챗봇·에이전트를 활용한 컴퓨테이셔널연구방법론의 최신 동향을 이해한다.
- LLM 기반 내용분석(텍스트·이미지·영상·음성), 챗봇 실험, 설문 시뮬레이션, 에이전트 기반 시뮬레이션 등 확장된 연구방법을 습득한다.
- BERT, Sentence-BERT 모형의 추론 활용과 LLM API를 통한 멀티모달 분석 능력을 함양한다.
- 매주 관련 선행연구 논문 발표와 비판적 토론을 통해 연구 역량을 강화한다.
- 파이썬과 VSCode + Gemini CLI 환경에서 AI 코딩 워크플로우를 습득한다.

## 수업 개요

본 수업은 LLM 시대의 컴퓨테이셔널 연구방법론을 체계적으로 학습하는 것을 목표로 한다. 전반부(1~7주)에서는 파이썬 기초, 데이터 수집, 딥러닝 이론, BERT/GPT 추론 활용을 다루고, 후반부(8~15주)에서는 LLM API 활용 내용분석, 임베딩 기반 분석, RAG 챗봇, 챗봇-인간 실험, LLM 설문 시뮬레이션(Silicon Sampling), 에이전트 워크플로우, 멀티 에이전트 토론, Generative ABM 시뮬레이션까지 확장한다. 매주 관련 논문 발표와 토론이 병행되며, 학기말에는 수강생 각자가 컴퓨테이셔널 방법론을 활용한 연구를 수행하여 분석 결과를 제출한다.

---

## 개발환경

- **코드 에디터**: VSCode + Gemini CLI
- **API**: Google AI Studio (Gemini) / OpenAI / Anthropic
- **AI 챗봇**: [chat.khu.ac.kr](https://chat.khu.ac.kr/) — 경희대 구성원 무료 제공
- **OS**: Windows → WSL(Windows Subsystem for Linux) 사용 / Mac → 그대로 사용

---

## 전체 구조

| 파트                               | 주차   | 내용                                                         |
|:-----------------------------------|:-------|:-------------------------------------------------------------|
| **Part 1: 기초 & 데이터**          | 1~5주  | 환경 설정, 파이썬, Pandas/NumPy, 텍스트 수집, 이미지·영상 수집 |
| **Part 2: 딥러닝 & 추론**          | 6~7주  | 딥러닝 이론, Transformer/BERT/GPT, 추론 활용                |
| **Part 3: LLM 내용분석**           | 8~10주 | LLM 텍스트 코딩, 멀티모달 분석, 임베딩·유사도                |
| **Part 4: 챗봇 & 실험**            | 11~13주 | RAG 챗봇, Search Grounding, 챗봇 실험, LLM 설문 시뮬레이션  |
| **Part 5: 에이전트 & 시뮬레이션**  | 14~15주 | 에이전트 워크플로우, 멀티에이전트 토론, Generative ABM       |

---

## 평가 방법

| 항목             | 비율 |
|:-----------------|:-----|
| 출석             | 10%  |
| 토론 참여        | 10%  |
| 논문 발표        | 10%  |
| 분석 능력 테스트 | 30%  |
| 연구 결과        | 40%  |

- 분석 능력 테스트: 코드리딩 + 텍스트·이미지 처리 분석 (오픈북)
- 연구 결과: 간단 이론과 분석 결과

---

## 주차별 일정 요약

| 주차 | 날짜 | 내용                              |
|:-----|:-----|:----------------------------------|
| 1    | 3/5  | 수업 소개, 환경 설정              |
| 2    | 3/12 | 파이썬 기초                       |
| 3    | 3/19 | Pandas & NumPy                    |
| 4    | 3/26 | 텍스트 수집 — 웹스크래핑          |
| 5    | 4/2  | 이미지·영상·음성 수집과 처리      |
| 6    | 4/9  | 딥러닝 이론 & PyTorch             |
| 7    | 4/16 | Transformer, BERT, GPT & 추론    |
| 8    | 4/23 | LLM 내용분석 — 텍스트             |
| 9    | 4/30 | LLM 내용분석 — 이미지, 영상, 음성 |
| 10   | 5/7  | 임베딩, 유사도, 벡터 DB           |
| 11   | 5/14 | RAG 챗봇 & Search Grounding      |
| 12   | 5/21 | 챗봇 실험 설계                    |
| 13   | 5/28 | LLM 설문 시뮬레이션               |
| 14   | 6/4  | 에이전트 & LangGraph              |
| 15   | 6/11 | 에이전트 토론 & Generative ABM    |
| 16   | 6/18 | **분석 능력 테스트**              |


## 학습할 논문 리스트

- 박대민. (2022). 미디어 인공지능: 컴퓨터 비전 관련 딥러닝 모델의 미디어 동영상 분야 적용 가능성에 관한 연구. *커뮤니케이션 이론*, 18(1), 111-154.

- 박영균, & 이종혁. (2026). 언론 시스템과 정치적 성향에 따른 김정은 보도사진의 시각적 프레이밍 연구: Multimodal LLM을 활용한 국제 언론 비교 분석. *언론정보연구*, 63(1), 157-198.

- 백강희, 이승윤, & 이종혁. (2025). 언론사와 증권사 간 인용 연결망을 통한 정보 불균형 탐구: 토픽모델링, 감성분석, 연결망분석을 통해. *언론정보연구*, 62(1), 97-144.

- 안순태, 임유진, & 이하나. (2020). 온라인 먹방(먹는 방송, Mukbang)의 댓글 연구: 식행동 관련 인식에 대한 빅데이터 분석. *한국언론학보*, 64(2), 269-310.

- 윤호영, & 오령. (2024). 사회적 재난 방송 뉴스 보도 화면 분석: 이태원 참사 보도 화면 구성으로 본 저널리즘 실천 방식. *한국방송학보*, 38(4), 155-203.

- 이문혁. (2025). K-POP 뮤직비디오의 이미지 유형화를 통한 시각적 특징 분석: 임베딩 벡터 추출(CLIP)과 유사도 검색(FAISS)을 통한 클러스터링. *언론정보연구*, 62(2), 53-115.

- 이문혁, & 이종혁. (2024). 시위 뉴스 영상에서 폭력 프레이밍의 작동 기제 분석: 비전 트랜스포머(Vision Transformer)를 활용한 폭력 이미지 분류를 통해. *한국언론학보*, 68(2), 100-139.

- 이문혁, 김시은, 신동호, & 이종혁. (2024). 재난보도 영상과 이미지 프레임에 나타난 국가 불평등 탐색: 비전 트랜스포머(Vision Transformer)를 활용한 KBS <세계는 지금> 영상 분석. *한국방송학보*, 38(2), 154-195.

- 이문혁, 이두황, 이종혁 (세미나 발표문, 별도 배포). AI 에이전트를 활용한 뉴스 윤리 심의문 자동 생성 시스템의 개발 및 적용: 네이버 '많이 본 뉴스' 분석을 중심으로

- 이승윤, 백강희, & 이종혁. (2023). 언론의 정치 성향에 따른 기업 보도 태도의 차이와 기업인 경기평가 심리에 미치는 영향 분석: BERT 기반 딥러닝 모형을 적용한 빅데이터 분석. *한국언론학보*, 67(1), 185-229.

- 이종혁. (2021). 매체 간 뉴스 동질화 현상에 대한 탐색적 연구: Doc2Vec을 통한 문서 유사도 측정의 활용. *언론정보연구*, 58(4), 5-48.

- 이종혁. (2022). 보수 언론과 진보 언론의 북한 전문가 활용 방식의 차이 탐색: 인용문에 대한 KPF-BERT 기반 딥러닝 분석을 중심으로. *한국언론학보*, 66(6), 154-194.

- 이종혁. (2024). 온라인 뉴스의 선정성이 게재 시간과 이용자 평가에 미치는 영향: Sentence-BERT와 BERT 모델을 활용한 텍스트 유사성, 비윤리성, 감정 측정. *한국언론학보*, 68(5), 75-119.

- 이종혁. (2025). 12·3 내란과 저널리즘 원칙: 오픈소스 생성형 LLM을 활용한 언론보도 분석. *한국방송학보*, 39(3), 123-166.

- 이종혁 (세미나 발표문, 별도 배포). 한국어 팩트체크 필요성 탐지 모델 및 RAG 기반 팩트체크 자동화 시스템 개발: 대선 후보자 토론회 적용

- 정재철, & 이종혁. (2022). 한미동맹 보도에 대한 의제 도출과 '동맹-자주' 관점의 비교 분석: BERT 모델 기반 딥러닝 모형의 활용. *사이버커뮤니케이션학보*, 39(4), 205-263.

- 조원정, & 이종혁. (2023). 장애인 시위 관련 뉴스 댓글의 비윤리성 측정과 정치 성향에 따른 차이 비교: BERT 기반 딥러닝 분류기 개발과 적용. *한국방송학보*, 37(2), 232-269.

- Anthis, J. R., Liu, R., Richardson, S. M., Kozlowski, A. C., Koch, B., Evans, J., ... & Bernstein, M. (2025). LLM social simulations are a promising research method. *arXiv preprint arXiv:2504.02234*.

- Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of one, many: Using language models to simulate human samples. *Political Analysis*, 31(3), 337-351.

- Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024). Synthetic replacements for human survey data? The perils of large language models. *Political Analysis*, 32(4), 401-416.

- Chuang, Y. S., Goyal, A., Harlalka, N., Suresh, S., Hawkins, R., Yang, S., ... & Rogers, T. (2024, June). Simulating opinion dynamics with networks of LLM-based agents. In *Findings of the Association for Computational Linguistics: NAACL 2024* (pp. 3326-3346).

- Costello, T. H., Pennycook, G., & Rand, D. G. (2024). Durably reducing conspiracy beliefs through dialogues with AI. *Science*, 385(6714), eadq1814.

- Freelon, D. (2018). Computational research in the post-API age. *Political Communication*, 35(4), 665-668.

- Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. *Proceedings of the National Academy of Sciences*, 120(30), e2305016120.

- Lazer, D. M., Pentland, A., Watts, D. J., Aral, S., Athey, S., Contractor, N., ... & Wagner, C. (2020). Computational social science: Obstacles and opportunities. *Science*, 369(6507), 1060-1062.

- Park, J. S., O'Brien, J., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023, October). Generative agents: Interactive simulacra of human behavior. In *Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology* (pp. 1-22).

- Park, J. S., Zou, C. Q., Shaw, A., Hill, B. M., Cai, C., Morris, M. R., ... & Bernstein, M. S. (2024). Generative agent simulations of 1,000 people. *arXiv preprint arXiv:2411.10109*.

- Salvi, F., Horta Ribeiro, M., Gallotti, R., & West, R. (2025). On the conversational persuasiveness of GPT-4. *Nature Human Behaviour*, 9(8), 1645-1653.

- Törnberg, P. (2023). How to use LLMs for text analysis. *arXiv preprint arXiv:2307.13106*.

- Törnberg, P., Valeeva, D., Uitermark, J., & Bail, C. (2023). Simulating social media using large language models to evaluate alternative news feed algorithms. *arXiv preprint arXiv:2310.05984*.

- Xi, Z., Chen, W., Guo, X., He, W., Ding, Y., Hong, B., ... & Gui, T. (2025). The rise and potential of large language model based agents: A survey. *Science China Information Sciences*, 68(2), 121101.

- Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., & Yang, D. (2024). Can large language models transform computational social science?. *Computational Linguistics*, 50(1), 237-291.

---

## 교재

### 파이썬 관련
- 박응용 (2024). 점프 투 파이썬. https://wikidocs.net/book/1
- 조대표, 유대표 (2024). 초보자를 위한 파이썬 300제. https://wikidocs.net/book/922
- 김태준 (2022). Pandas DataFrame 완전정복. https://wikidocs.net/book/7188

### 딥러닝 관련
- 윤성진 (2021). Do it! 딥러닝 교과서. 이지스퍼블리싱.
- 유원준, 안상준 (2025). 러닝 파이토치 교과서. https://wikidocs.net/book/2788
- 최성필 (2023). Transformers 강좌. https://wikidocs.net/book/8056

### LLM·에이전트 관련
- 테디노트 (2025). 랭체인LangChain 노트. https://wikidocs.net/book/14314
- 이승우 (2025). 자세히 쓰는 Gemini API. https://wikidocs.net/book/14285
- LangGraph Documentation. https://langchain-ai.github.io/langgraph/

### 참고 사이트
- Kaggle: https://www.kaggle.com/
- Hugging Face: https://huggingface.co/
- Papers With Code: https://paperswithcode.com/
- AI Hub: https://www.aihub.or.kr/
