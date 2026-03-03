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

| 주차 | 날짜 | 내용                              | 논문 발표                                                         |
|:-----|:-----|:----------------------------------|:------------------------------------------------------------------|
| 1    | 3/5  | 수업 소개, 환경 설정              | —                                                                 |
| 2    | 3/12 | 파이썬 기초                       | Ziems et al. (2024); Lazer et al. (2020)                          |
| 3    | 3/19 | Pandas & NumPy                    | 이종혁 (2021); 백강희 외 (2025)                                   |
| 4    | 3/26 | 텍스트 수집 — 웹스크래핑          | 조원정·이종혁 (2023); Freelon (2018)                              |
| 5    | 4/2  | 이미지·영상·음성 수집과 처리      | 이문혁 (2025); 이문혁 외 (2024)                                   |
| 6    | 4/9  | 딥러닝 이론 & PyTorch             | 이종혁 (2022); 이문혁·이종혁 (2024)                               |
| 7    | 4/16 | Transformer, BERT, GPT & 추론    | 이승윤 외 (2023); 정재철·이종혁 (2022)                            |
| 8    | 4/23 | LLM 내용분석 — 텍스트             | Gilardi et al. (2023); Törnberg (2024); 이종혁 (2025)             |
| 9    | 4/30 | LLM 내용분석 — 이미지, 영상, 음성 | 박영균·이종혁 (2026); Peng et al. (2024)                          |
| 10   | 5/7  | 임베딩, 유사도, 벡터 DB           | 이종혁 (2024); Ornstein et al. (2024)                             |
| 11   | 5/14 | RAG 챗봇 & Search Grounding      | Lewis et al. (2020); Costello et al. (2024)                       |
| 12   | 5/21 | 챗봇 실험 설계                    | Pennycook et al. (2025); Salvi et al. (2025); Bai et al. (2025)  |
| 13   | 5/28 | LLM 설문 시뮬레이션               | Argyle et al. (2023); Park et al. (2024); Bail (2024)             |
| 14   | 6/4  | 에이전트 & LangGraph              | Anthis et al. (2025); Matz et al. (2024)                          |
| 15   | 6/11 | 에이전트 토론 & Generative ABM    | Park et al. (2023); Chuang et al. (2024); Törnberg et al. (2023)  |
| 16   | 6/18 | **분석 능력 테스트**              | —                                                                 |

---

## 전체 논문 목록

### 국내 논문 (11편)
1. 이종혁 (2021). 매체 간 뉴스 동질화 현상에 대한 탐색적 연구: Doc2Vec을 통한 문서 유사도 측정의 활용. *언론정보연구*, 58(4), 5–48. (3주)
2. 이종혁 (2022). 보수 언론과 진보 언론의 북한 전문가 활용 방식의 차이 탐색. *한국언론학보*, 66(6), 154–194. (6주)
3. 이종혁 (2024). 온라인 뉴스의 선정성이 게재 시간과 이용자 평가에 미치는 영향. *한국언론학보*, 68(5), 75–119. (10주)
4. 이종혁 (2025). 12·3 내란과 저널리즘 원칙. *한국방송학보*, 39(3), 123–166. (8주)
5. 박영균, 이종혁 (2026). 김정은 보도사진의 시각적 프레이밍 연구. *언론정보연구*, 63(1), 157–198. (9주)
6. 이승윤, 백강희, 이종혁 (2023). 언론의 정치 성향에 따른 기업 보도 태도의 차이. *한국언론학보*, 67(1), 185–229. (7주)
7. 백강희, 이승윤, 이종혁 (2025). 언론사와 증권사 간 인용 연결망. *언론정보연구*, 62(1), 97–144. (3주)
8. 조원정, 이종혁 (2023). 장애인 시위 관련 뉴스 댓글의 비윤리성 측정. *한국방송학보*, 37(2), 232–269. (4주)
9. 정재철, 이종혁 (2022). 한미동맹 보도에 대한 의제 도출과 비교 분석. *사이버커뮤니케이션학보*, 39(4), 205–263. (7주)
10. 이문혁, 이종혁 (2024). 시위 뉴스 영상에서 폭력 프레이밍의 작동 기제 분석. *한국언론학보*, 68(2), 100–139. (6주)
11. 이문혁, 김시은, 신동호, 이종혁 (2024). 재난보도 영상과 이미지 프레임. *한국방송학보*, 38(2), 154–195. (5주)

### 국제 논문 (16편)
1. Ziems et al. (2024). Can Large Language Models Transform Computational Social Science? *Computational Linguistics*. (2주)
2. Lazer et al. (2020). Computational Social Science: Obstacles and Opportunities. *Science*. (2주)
3. Freelon (2018). Computational Research in the Post-API Age. *Political Communication*. (4주)
4. 이문혁 (2025). K-POP 뮤직비디오의 이미지 유형화. *언론정보연구*. (5주)
5. Gilardi et al. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. *PNAS*. (8주)
6. Törnberg (2024). How to Use LLMs for Text Analysis. *PNAS*. (8주)
7. Peng et al. (2024). What You See Is What You Get. *arXiv*. (9주)
8. Ornstein et al. (2024). How to Train Your Stochastic Parrot. *Political Analysis*. (10주)
9. Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS*. (11주)
10. Costello et al. (2024). Durably Reducing Conspiracy Beliefs Through Dialogues with AI. *Science*. (11주)
11. Pennycook et al. (2025). Persuading Voters Using Human–AI Dialogues. *Nature*. (12주)
12. Salvi et al. (2025). On the Conversational Persuasiveness of GPT-4. *Nature Human Behaviour*. (12주)
13. Bai et al. (2025). LLM-generated Messages Can Persuade Humans on Policy Issues. *Nature Communications*. (12주)
14. Argyle et al. (2023). Out of One, Many. *Political Analysis*. (13주)
15. Park et al. (2024). Generative Agent Simulations of 1,000 People. *arXiv*. (13주)
16. Bail (2024). Can Generative AI Improve Social Science? *PNAS*. (13주)
17. Anthis et al. (2025). LLM Social Simulations Are a Promising Research Method. *ICML*. (14주)
18. Matz et al. (2024). The Potential of Generative AI for Personalized Persuasion at Scale. *Scientific Reports*. (14주)
19. Park et al. (2023). Generative Agents: Interactive Simulacra of Human Behavior. *UIST*. (15주)
20. Chuang et al. (2024). Simulating Opinion Dynamics with Networks of LLM-based Agents. *NAACL Findings*. (15주)
21. Törnberg et al. (2023). Simulating Social Media Using LLMs to Examine Polarization. *arXiv*. (15주)

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
