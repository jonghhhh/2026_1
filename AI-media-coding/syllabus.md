# 인공지능미디어코딩 — 강의개요

**경희대학교 미디어학과 | JCOMM307600 | 월수 15:00~16:15 | 정408**

**담당교수**: 이종혁 (정경대 교수회관 620호, 02-961-2179, jonghhhh@khu.ac.kr)

> ← [주차별 수업 내용으로 돌아가기](index.md)

---

## 수업 목표

- 미디어 유형(텍스트, 음성, 이미지, 영상)별 인공지능 활용에 대한 이해를 넓힌다.
- 딥러닝, BERT, GPT, LLM 에이전트에 대한 개념, 구조, 기능을 파악한다.
- VSCode + Gemini CLI 환경에서 AI 코딩 워크플로우를 습득한다.
- LLM API를 활용한 멀티모달 내용분석, 임베딩 기반 문장 분석, RAG 챗봇, 에이전트 워크플로우를 구현한다.
- 파이썬을 중심으로 프로그래밍 기초 지식을 습득한다.

## 수업 개요

이 수업은 다양한 미디어 데이터를 AI로 분석하고, LLM 기반 챗봇과 에이전트를 개발하는 것을 목표로 한다. 전반에는 파이썬 기초, 데이터 수집, 딥러닝 이론을 다루고, 후반에는 LLM API 활용 내용분석, RAG 챗봇 구축, 챗봇 실험 설계, LangGraph를 활용한 에이전트 워크플로우 구축까지 본격적으로 다룬다. 전 과정에서 VSCode + Gemini CLI를 활용한 AI 코딩 환경을 기본으로 사용한다. 학기말에는 특수 목적 Vertical AI 프로젝트(공모전용) 기획안을 제출한다.

---

## 개발환경

- **코드 에디터**: VSCode + Gemini CLI
- **API**: Google AI Studio (Gemini) / OpenAI / Anthropic
- **AI 챗봇**: [chat.khu.ac.kr](https://chat.khu.ac.kr/) — 경희대 구성원 무료 제공
- **OS**: Windows → WSL(Windows Subsystem for Linux) 사용 / Mac → 그대로 사용

---

## 평가 방법

| 항목                       | 비율 |
|:---------------------------|:-----|
| 출석                       | 10%  |
| 참여                       | 10%  |
| 코딩분석능력 테스트 (중간) | 30%  |
| 코딩분석능력 테스트 (기말) | 30%  |
| AI 프로젝트 기획안 | 20%  |

- 코딩분석능력 테스트: 코드리딩 + 텍스트·이미지 처리 분석

---

## 주차별 일정 요약

| 주차 | 날짜       | 비고                | 내용                                     |
|:-----|:-----------|:--------------------|:-----------------------------------------|
| 1    | 3/4(수)    | ⚠️ 3/2 대체공휴일  | 수업 소개, VSCode+Gemini CLI 설정        |
| 2    | 3/9, 3/11  |                     | 파이썬 기초                              |
| 3    | 3/16, 3/18 |                     | Pandas & NumPy                           |
| 4    | 3/23, 3/25 |                     | 텍스트 수집 — 웹스크래핑                 |
| 5    | 3/30, 4/1  |                     | 이미지·영상 수집 — 구글, 네이버, 유튜브  |
| 6    | 4/6, 4/8   |                     | 이미지·영상 수집과 처리                  |
| 7    | 4/13, 4/15 |                     | 딥러닝 이론                              |
| 8    | 4/20, 4/22 | **중간고사**        | 리뷰 + 시험                              |
| 9    | 4/27, 4/29 |                     | Transformer, BERT, GPT & 추론            |
| 10   | 5/4, 5/6   |                     | LLM 내용분석 (텍스트·이미지·영상·음성)   |
| 11   | 5/11, 5/13 |                     | 임베딩 & RAG 챗봇                        |
| 12   | 5/18, 5/20 |                     | Search Grounding & 챗봇 실험             |
| 13   | 5/27(수)   | ⚠️ 5/25 대체공휴일 | LLM 에이전트 & LangGraph                 |
| 14   | 6/1(월)    | ⚠️ 6/3 지방선거    | AI 프로젝트                     |
| 15   | 6/8, 6/10  |                     | AI 실전 구현 & 배포             |
| 16   | 6/15, 6/17 | **기말고사**        | 시험 + 기획안 제출(6/22)                 |

---

## 교재

### 파이썬 관련
- 박응용 (2024). 점프 투 파이썬. https://wikidocs.net/book/1  
- 조대표, 유대표 (2024). 초보자를 위한 파이썬 300제. https://wikidocs.net/book/922  
- 김태준 (2022). Pandas DataFrame 완전정복. https://wikidocs.net/book/7188  
- 김왼손의 왼손코딩:Hello Coding 한입에 쏙 파이썬. https://www.youtube.com/channel/UC0h8NzL2vllvp3PjdoYSK4g                                                                             
- 나도코딩. (2020). 파이썬 코딩 무료 강의 (기본편) ? 6시간 뒤면 나도 개발자.  https://www.youtube.com/watch?v=kWiCuklohdY                                            -                    
- 조코딩 JoCoding. (2024). 2024 점프 투 파이썬 통합본 ? 파이썬 기초부터 실습까지 https://www.youtube.com/@jocoding                                                                 
- 생활코딩. (2023). Python ? 입문자를 위한 프로그래밍 기초. https://www.youtube.com/watch?v=qYOk-d9bIBs  
- 이종혁 교수 파이썬 기초 강의편집본(지루할 수 있음): https://sites.google.com/khu.ac.kr/pythoncodingvideo/%ED%99%88  

### 딥러닝 관련
- 박해선 (2019). Do it! 정직하게 코딩하며 배우는 딥러닝 입문. 이지스퍼블리싱.
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
