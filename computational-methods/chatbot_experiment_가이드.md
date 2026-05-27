# 챗봇 실험 플랫폼 만들기

> Streamlit + \*\*Hugging Face Dataset\*\* + Hugging Face Spaces + \*\*Gemini 2.5 Flash-Lite\*\*로 만드는 LLM 실험 환경
> 디폴트 사례: \*\*"AI 시대 진로상담 챗봇의 페르소나가 대학생의 정보 수용에 미치는 영향"\*\*

\---

## 0\. 이 강의에서 무엇을 배우는가

이 강의가 끝나면 다음 세 가지를 할 수 있습니다.

1. **챗봇 실험의 원리**를 이해하고 자기 연구 질문을 실험설계로 옮길 수 있다.
2. **Streamlit + Gemini API**로 동작하는 챗봇 실험 플랫폼을 직접 만들 수 있다.
3. **Hugging Face Spaces**에 무료로 배포하고, **데이터를 잃지 않게** 운영할 수 있다.

Python만 알면 됩니다. HTML/JS 지식은 필요 없습니다.

\---

## 1\. 챗봇 실험이란 무엇인가 — 개념과 원리

### 1.1 정의

**챗봇 실험**은 LLM 기반 챗봇을 자극(stimulus)으로 사용하여, 사람이 챗봇과 대화한 전후에 어떤 변화가 일어나는지를 측정하는 실험입니다. 전통적 실험의 "동영상을 보여준다", "글을 읽힌다" 자리에 "챗봇과 대화하게 한다"가 들어간 것입니다.

```
\[사전조사] → \[챗봇과 대화 (조건별로 다름)] → \[사후조사]
                      ↑
              이것이 독립변수
```

### 1.2 왜 챗봇 실험이 중요해졌는가

**첫째, 자극의 표준화와 다양성을 동시에 얻습니다.** 챗봇은 참여자 발언에 반응하면서도 시스템 프롬프트로 핵심 성격을 유지합니다. "통제되면서도 자연스러운" 자극입니다.

**둘째, LLM이 사회적 영향력을 가지는 시대가 왔습니다.** Salvi 등(2025)은 *Nature Human Behaviour*에서 GPT-4가 인간보다 설득력이 높음을, Costello 등(2024)은 *Science*에서 LLM이 음모론 신념을 지속적으로 약화시킬 수 있음을 보였습니다. LLM은 이제 연구 도구이자 **연구 대상**입니다.

**셋째, 빠르고 싸게 할 수 있습니다.** 과거 인간 공모자(confederate)를 쓰던 대화 실험을, 학부생 한 명이 한 학기에 할 수 있습니다.

### 1.3 챗봇 실험의 5요소

|요소|의미|본 강의 디폴트|
|-|-|-|
|**참여자**|누구를 모집하는가|대학생|
|**조건(독립변수)**|무엇을 다르게 하는가|챗봇 페르소나(분석가형 vs 멘토형)|
|**무작위 배정**|어떻게 조건을 나누는가|입장 순서로 번갈아 배정|
|**대화 과제**|무엇에 대해 대화하는가|졸업 후 진로 고민|
|**측정(종속변수)**|무엇을 잴 것인가|정보 유용성, 신뢰, 진로 자기효능감 변화|

이 5요소만 자기 주제에 맞게 채우면 실험이 됩니다.

\---

## 2\. 유용성 — 어디에 쓰는가

* **커뮤니케이션**: "뉴스 챗봇의 톤(객관 vs 해설)이 정보 신뢰에 주는 영향"
* **교육공학**: "AI 튜터가 정답을 직접 줄 때 vs 소크라테스식으로 물을 때 학습성과 차이" (Kestin \& Miller 2024)
* **정치·사회심리**: "음모론 신봉자가 LLM과 대화하면 신념이 약화되는가" (Costello et al. 2024)
* **진로·상담**: "AI 진로상담 챗봇 페르소나가 진로 자기효능감에 주는 영향" (← 본 강의 디폴트)
* **소비자행동**: "쇼핑 챗봇의 전문가형 vs 친구형 페르소나가 구매의도에 주는 영향"
* **저널리즘**: "팩트체크 챗봇이 미디어 리터러시를 향상시키는가"

디폴트 사례 하나만 만들 수 있으면, 같은 인프라로 위 모든 질문에 답할 수 있습니다.

\---

## 3\. 선행 연구 — 반드시 읽어야 할 3편

### 3.1 Salvi et al. (2025) — *On the Conversational Persuasiveness of GPT-4*

*Nature Human Behaviour*. GPT-4가 인구통계 정보를 받으면 인간 토론자보다 81.2% 더 높은 확률로 상대 의견을 바꿨습니다. 2×2×3 요인설계(N=900), 코드는 [debategpt 저장소](https://github.com/epfl-dlab/debategpt) 공개.

**시사점**: 챗봇 실험에서 **조건(condition)을 어떻게 정의하는지**의 모범.

### 3.2 Costello et al. (2024) — *Durably reducing conspiracy beliefs through dialogues with AI*

*Science*, 2024 AAAS Newcomb Cleveland Prize 수상. 음모론 신봉자 2,000여 명이 GPT-4 Turbo와 평균 8분 대화 후 신념이 약 20% 감소, 효과가 2개월 후에도 유지.

**시사점**: **사후조사를 시간차로 두 번** 하는 설계의 힘. 참여자 자유응답을 챗봇이 받아 맞춤 반박하는 패턴.

### 3.3 Kestin \& Miller (2024) — *AI Tutoring Outperforms Active Learning*

Harvard 물리학 수업 194명 무작위 배정 실험. 맞춤형 GPT 튜터로 학습한 학생이 전통적 능동학습 학생보다 학습량이 약 2배.

**시사점**: **within-subjects 설계**(같은 학생이 두 조건 경험, 순서만 무작위). 표본이 작아도 검정력이 높아 학부 프로젝트에 적합.

### 3.4 도구 측면의 선행 연구

* **Bermudez Schettino et al. (2025)** — *Simple Chat* ([GitHub](https://github.com/center-for-humans-and-machines/simple-chat)). Max Planck 오픈소스 챗봇 실험 인터페이스. 세 원칙: ① 임베드 가능한 채팅 UI, ② 조건 간 통일된 인터페이스, ③ 이탈을 줄이는 스트리밍. **본 강의 코드도 이 세 원칙을 따릅니다.**
* **McKenna (2023)** — [oTree GPT](https://github.com/clintmckenna/oTree_gpt). 조건 무작위 배정 + long-form CSV 내보내기.
* **Lamprou et al. (2025)** — *Customizable LLM-Powered Chatbot (CLPC)*. https://arxiv.org/abs/2501.05541

### 3.5 진로상담 이론 배경

* **Fiske, Cuddy, \& Glick (2007)** — Stereotype Content Model(SCM). 사회적 지각의 두 차원: \*\*따뜻함(warmth)\*\*과 **유능함(competence)**.
* **Betz et al. (1996)** — *Career Decision Self-Efficacy Scale(CDSE)*. 한국어판 존재.
* **Gati et al. (1996)** — *Career Decision-Making Difficulties Questionnaire(CDDQ)*.

보고서에서 "페르소나 → 지각된 따뜻함·유능함 → 정보 신뢰 → 진로 자기효능감 변화" 매개 모형을 그리면 깔끔합니다.

\---

## 4\. 본 강의 디폴트 사례: 진로상담 챗봇의 페르소나 효과

### 4.1 왜 이 주제인가

대학생 모두가 당사자라 모집·몰입도가 높고, 페르소나 조작이 실제 진로상담의 두 학파(객관적 정보 vs 정서적 지지)와 자연스럽게 대응됩니다. 정치·종교·정신건강 같은 민감 영역을 피하면서 학술적 깊이를 확보합니다.

### 4.2 연구 질문

> \*\*진로상담 챗봇의 페르소나(분석가형 vs 멘토형)가 대학생의 정보 유용성 지각, 챗봇 신뢰, 진로 자기효능감 변화, 추천 의향에 어떤 영향을 주는가?\*\*

### 4.3 설계 한눈에

* **설계**: 2조건 between-subjects (참여자당 한 조건만)
* **독립변수**: 페르소나 (A: 분석가형 / B: 멘토형)
* **무작위 배정**: 입장 순서 기반 교대 (짝수 → A, 홀수 → B)
* **과제**: "졸업 후 진로 고민을 챗봇과 5턴 이상 정리"
* **사전조사**: 학년, 전공계열, 진로 결정 단계, 진로 불안, AI 사용 빈도 (5문항)
* **사후조사**: 정보 유용성, 따뜻함·유능함, 신뢰, 정리도, 추천 의향, 자유응답 (7문항)

### 4.4 이론적 근거

> 본 연구는 Salvi 등(2025)이 챗봇 조건 조작만으로 인간 의견에 영향을 줄 수 있음을 보인 점, Fiske 등(2007)의 SCM에서 따뜻함과 유능함이 정보 수용을 매개한다는 선행연구에 근거한다. 진로상담 챗봇 페르소나의 두 양식(분석가형/멘토형)이 대학생의 정보 수용과 진로 자기효능감 변화에 미치는 효과를 검증한다.

\---

## 5\. 시스템 아키텍처

### 5.1 전체 그림

```
참여자 브라우저
      │
      ▼
┌─────────────────────────────────────────────┐
│  Streamlit 앱 (streamlit\_app.py)             │
│  ┌────────┐  ┌────────┐  ┌────────┐         │
│  │ 사전조사│→ │ 대화창 │→ │ 사후조사│         │
│  └────────┘  └───┬────┘  └────────┘         │
│                  ▼                           │
│         ┌──────────────────┐                 │
│         │  storage.py      │  ← 이중 안전망   │
│         │  ① HF Dataset 업로드│               │
│         │  ② 메모리 누적    │                 │
│         └──────────────────┘                 │
│  사이드바: (위) 연구 안내 / (아래) CSV 다운로드 │
└──────┬────────────────────────┬──────────────┘
       │                        │
       ▼                        ▼
Gemini 2.5 Flash-Lite      HF Dataset
   API                     (participants/messages/surveys CSV)
```

### 5.2 왜 이 스택인가

**Streamlit** — Python만으로 웹앱. `st.chat\_input()`, `st.chat\_message()` 채팅 UI 내장. HF Spaces에 한 번에 배포.

> 학부생 실험(N=40\~200, 동시접속 ≤ 10명)이면 Streamlit으로 충분합니다. 단, 무료 등급은 비활성 시 슬립하므로 첫 접속자는 잠깐 기다립니다. 참여자 안내에 적어두세요.

**Gemini 2.5 Flash-Lite** — 무료 등급 제공, 빠른 응답, 안정적 한국어, 스트리밍 지원. 모델 교체는 `llm.py`에서 한 줄.

**HF Dataset (SQLite 대체)** — 무료, Space 바깥의 git 저장소라 재시작과 무관하게 **영구 보존**, 여러 참여자 데이터 **자동 통합**. 이미 HF Spaces를 쓰므로 **토큰 1개만** 추가하면 되어 설정이 간단합니다.

### 5.3 데이터 구조 — long format

데이터 모양은 **long format**(한 행 = 한 기록)으로 HF Dataset에 3개 CSV로 쌓입니다. 새 설문 문항을 추가해도 구조를 바꿀 필요가 없습니다.

|워크시트|한 행의 의미|주요 컬럼|
|-|-|-|
|`participants`|한 사람|participant\_id, condition, assigned\_at, completed|
|`messages`|대화 한 턴|participant\_id, condition, turn, role, content, latency\_ms, created\_at|
|`surveys`|설문 한 문항|participant\_id, condition, phase, question\_id, answer, created\_at|

### 5.4 무작위 배정

```python
# 입장 순서로 교대 배정 (A, B, A, B, ...). 작은 N에서 쏠림 방지.
n = len(st.session\_state\["rows\_participants"])
cond = "A" if n % 2 == 0 else "B"
```

진짜 무작위(`random.choice`)보다 교대 배정을 권합니다. N=40이면 random은 17:23 같은 불균형이 흔합니다.

### 5.5 API 키 / 시크릿 관리

|환경|위치|
|-|-|
|로컬|프로젝트 폴더의 `.env` (반드시 `.gitignore`에)|
|HF Spaces|Settings → Repository secrets|

```bash
# .env (절대 git에 올리지 말 것)
GEMINI\_API\_KEY=AIzaSy...
# HF Dataset을 쓸 때만:
HF\_TOKEN=hf\_...write권한토큰
```

```
# .gitignore
.env
\_\_pycache\_\_/
\*.csv
```

\---

## 6\. 코드 — 6개 파일로 끝나는 실전

### 6.1 파일 구조 (v4)

```
project/
├── streamlit\_app.py  # 메인 앱 (사이드바 안내 + 다운로드 포함)
├── prompts.py        # 조건별 시스템 프롬프트
├── llm.py            # Gemini 호출 래퍼
├── storage.py        # 이중 안전망 (HF Dataset + 메모리)  ← SQLite 대체
├── analyze.py        # 분석 스크립트
├── requirements.txt
├── .env              # 키 (git 제외)
└── .gitignore
```

### 6.2 `requirements.txt`

```
streamlit>=1.30
google-genai>=0.3
python-dotenv>=1.0
pandas>=2.0
# --- HF Dataset 저장용 ---
huggingface\_hub>=0.20
```

### 6.3 `prompts.py`

```python
# prompts.py
# ───────────────────────────────────────────────────────────────────────────
# 실험 조건별 시스템 프롬프트와 과제 안내문.
# 학생이 자기 주제로 바꿀 때 "거의 이 파일만" 수정하면 되도록 분리해 두었다.
# 핵심 규칙: 두 프롬프트는 '사실 내용은 동일하게, 조작점(스타일)만 다르게'.
# ───────────────────────────────────────────────────────────────────────────

SYSTEM\_PROMPTS = {
    # 조건 A — 분석가형 (객관적 정보 중심)
    "A": """당신은 노동시장 데이터와 직업 트렌드에 정통한 진로 분석가입니다.

답변 원칙:
- 통계, 산업 동향, 직무 요구역량 등 객관적 정보를 중심으로 설명한다.
- 감정 위로보다는 사실 정보와 구체적 옵션을 제시한다.
- 친근한 호칭이나 이모지를 사용하지 않는다.
- 한국어로, 한 답변당 4\~6문장.
- 사용자가 결정을 강요받는다고 느끼지 않도록, 정보 제공에 머문다.
- 의학·법률·금융의 전문 자문이 필요한 경우 해당 전문가 상담을 권한다.""",

    # 조건 B — 멘토형 (정서적 지지 중심)
    "B": """당신은 진로 고민을 함께 나누는 따뜻한 멘토입니다.

답변 원칙:
- 사용자의 불안과 고민을 먼저 인정하고 공감을 표현한다.
- "충분히 그런 고민 할 수 있어요", "\~하시는군요" 같은 공감 표현을 자연스럽게 사용한다.
- 사용자 스스로 답을 찾아가도록 열린 질문을 적절히 활용한다.
- 한국어로, 한 답변당 4\~6문장.
- 사용자를 평가하거나 판단하지 않는다.
- 의학·법률·금융의 전문 자문이 필요한 경우 해당 전문가 상담을 권한다.""",
}

# 참여자에게 보여줄 대화 과제 안내문
TASK\_INSTRUCTION = (
    "당신은 졸업 후 진로에 대해 고민이 있습니다. "
    "챗봇과 최소 5턴 이상 대화하며 자신의 진로 고민을 정리해보세요. "
    "무엇이든 솔직하게 이야기해도 좋습니다."
)
```

### 6.4 `llm.py` — Gemini 래퍼

```python
# llm.py
# ───────────────────────────────────────────────────────────────────────────
# Gemini 2.5 Flash-Lite 호출 래퍼. 모델명만 한 줄 바꾸면 다른 모델로 교체 가능.
# 스트리밍(generate\_content\_stream)을 쓰는 이유: 응답이 한 글자씩 흘러나와
# 참여자 이탈을 줄인다(Simple Chat 논문이 강조한 원칙).
# ───────────────────────────────────────────────────────────────────────────
import os
from dotenv import load\_dotenv
from google import genai
from google.genai import types

load\_dotenv()  # 로컬: .env 읽음 / HF Spaces: 무시되고 환경변수에서 직접 읽음

API\_KEY = os.getenv("GEMINI\_API\_KEY")
if not API\_KEY:
    raise RuntimeError(
        "GEMINI\_API\_KEY가 설정되지 않았습니다. "
        "로컬은 .env, Spaces는 Settings → Repository secrets에 등록하세요."
    )

MODEL\_NAME = "gemini-2.5-flash-lite"  # ← 모델 교체 지점 (한 줄)
client = genai.Client(api\_key=API\_KEY)


def \_to\_gemini(messages):
    """Streamlit 내부 메시지 → Gemini 포맷 변환.
    Gemini는 role이 'user'와 'model'만 허용한다('assistant' 아님)."""
    return \[
        {"role": "model" if m\["role"] == "assistant" else "user",
         "parts": \[{"text": m\["content"]}]}
        for m in messages
    ]


def stream\_response(system\_prompt, messages, temperature=0.7):
    """응답을 청크 단위로 yield하는 제너레이터."""
    config = types.GenerateContentConfig(
        system\_instruction=system\_prompt,  # 시스템 프롬프트는 매 호출마다 주입
        temperature=temperature,
    )
    stream = client.models.generate\_content\_stream(
        model=MODEL\_NAME,
        contents=\_to\_gemini(messages),
        config=config,
    )
    for chunk in stream:
        if chunk.text:
            yield chunk.text
```

### 6.5 `storage.py` — 이중 안전망 (이 강의의 핵심)

```python
# storage.py  (Hugging Face Dataset 버전)
# ───────────────────────────────────────────────────────────────────────────
# 데이터 저장 — SQLite도 구글시트도 쓰지 않고 '이중 안전망'으로 저장한다.
#
#   안전망 1) HF Dataset 업로드 : 영구 저장 + 여러 참여자 통합 (구글시트 대체)
#   안전망 2) 메모리(session\_state): 사이드바에서 즉시 CSV 다운로드 (백업)
#
# 왜 HF Dataset인가:
#   - 구글 방식(서비스계정·JSON 키·시트 공유)이 초보자에게 너무 복잡하다.
#   - 이미 HF Spaces에 배포하므로, 같은 HF 안에서 '토큰 1개'만 더 만들면 끝.
#   - Dataset 저장소는 Space와 달리 재시작에 영향받지 않는 git 저장소라
#     데이터가 영구 보존된다(Space가 슬립/재빌드돼도 안전).
#
# 작동 방식:
#   - 모든 기록은 일단 메모리 리스트(rows\_\*)에 쌓인다(안전망 2).
#   - '참여자 완료' 시점에만, 그때까지 모인 전체 CSV를 Dataset에 덮어쓴다(안전망 1).
#     → 매 메시지마다 올리면 너무 잦으므로, 완료 시 한 번만 통째로 올린다.
#   - 단, 메모리는 '현재 브라우저 세션'만 담는다. 여러 참여자를 한 파일로
#     합치기 위해, 업로드 전에 Dataset의 기존 CSV를 내려받아 '머지(merge)'한다.
#
# 설정(1회): README/강의 7장 참조.
#   1) HF에서 빈 Dataset 생성 (예: yourname/career-chatbot-data, Private 권장)
#   2) write 권한 토큰 발급 → Space secret에 HF\_TOKEN으로 등록
#   3) 아래 DATASET\_REPO를 본인 것으로 교체
# HF\_TOKEN이 없으면 업로드는 조용히 건너뛰고 사이드바 다운로드만 동작한다
# (로컬 개발 시 편리).
# ───────────────────────────────────────────────────────────────────────────
import os
import io
from datetime import datetime, timezone

import pandas as pd

# huggingface\_hub은 Dataset 업로드를 쓸 때만 필요. 없으면 메모리 모드로만 동작.
try:
    from huggingface\_hub import HfApi, hf\_hub\_download
    \_HAS\_HF = True
except ImportError:
    \_HAS\_HF = False

# ▼▼▼ 본인이 만든 Dataset 저장소 이름으로 교체 ▼▼▼
DATASET\_REPO = "yourname/career-chatbot-data"
# ▲▲▲ (HF에서 New Dataset으로 만든 'yourname/저장소이름') ▲▲▲

HF\_TOKEN = os.getenv("HF\_TOKEN")  # Space secret 또는 .env에 넣은 write 토큰

# Dataset 안에 저장될 3개 CSV 파일 이름
FILES = {
    "participants": "participants.csv",
    "messages": "messages.csv",
    "surveys": "surveys.csv",
}


def now\_iso():
    """UTC ISO 8601 타임스탬프 (예: 2026-05-27T12:34:56+00:00)."""
    return datetime.now(timezone.utc).isoformat()


# ── 메모리(안전망 2): 모든 기록을 세션 리스트에 누적 ─────────────────────────
def init\_state(state):
    """세션 시작 시 누적 리스트 3개를 준비(이미 있으면 그대로)."""
    state.setdefault("rows\_participants", \[])
    state.setdefault("rows\_messages", \[])
    state.setdefault("rows\_surveys", \[])


def add\_participant(state, pid, condition):
    """참여자 배정 기록(메모리에만 추가. 업로드는 완료 시 일괄)."""
    state\["rows\_participants"].append(
        {"participant\_id": pid, "condition": condition,
         "assigned\_at": now\_iso(), "completed": 0})


def add\_message(state, pid, condition, turn, role, content, latency\_ms=""):
    """대화 한 턴 기록(메모리)."""
    state\["rows\_messages"].append(
        {"participant\_id": pid, "condition": condition, "turn": turn,
         "role": role, "content": content, "latency\_ms": latency\_ms,
         "created\_at": now\_iso()})


def add\_survey(state, pid, condition, phase, question\_id, answer):
    """설문 한 문항 기록(메모리)."""
    state\["rows\_surveys"].append(
        {"participant\_id": pid, "condition": condition, "phase": phase,
         "question\_id": question\_id, "answer": str(answer),
         "created\_at": now\_iso()})


# ── HF Dataset(안전망 1): 기존 데이터와 머지 후 업로드 ───────────────────────
def \_download\_existing(api, filename):
    """Dataset에 이미 있는 CSV를 DataFrame으로 읽어온다. 없으면 빈 DF."""
    try:
        path = hf\_hub\_download(
            repo\_id=DATASET\_REPO, filename=filename,
            repo\_type="dataset", token=HF\_TOKEN,
        )
        return pd.read\_csv(path)
    except Exception:
        # 파일이 아직 없거나(첫 업로드) 네트워크 문제 → 빈 DF로 시작
        return pd.DataFrame()


def \_upload\_csv(api, df, filename):
    """DataFrame을 CSV 바이트로 만들어 Dataset에 덮어쓰기 업로드."""
    buf = io.BytesIO(df.to\_csv(index=False).encode("utf-8-sig"))
    api.upload\_file(
        path\_or\_fileobj=buf,          # 파일 경로 대신 메모리 버퍼를 직접 올림
        path\_in\_repo=filename,
        repo\_id=DATASET\_REPO,
        repo\_type="dataset",
        token=HF\_TOKEN,
        commit\_message=f"update {filename} @ {now\_iso()}",
    )


def push\_to\_dataset(state):
    """현재 세션의 누적분을 Dataset의 기존 데이터와 합쳐 업로드.
    실패해도 참여자 흐름을 막지 않도록 조용히 통과(메모리 백업이 남아 있음).
    반환: (성공여부, 메시지)."""
    if not \_HAS\_HF or not HF\_TOKEN:
        return False, "HF\_TOKEN 없음 → 업로드 건너뜀(다운로드 백업만 사용)"
    try:
        api = HfApi()
        # 세 종류(participants/messages/surveys) 각각: 기존 + 이번 세션 → 합쳐서 업로드
        for key, fname in FILES.items():
            new\_df = pd.DataFrame(state\[f"rows\_{key}"])
            if new\_df.empty:
                continue
            old\_df = \_download\_existing(api, fname)
            merged = pd.concat(\[old\_df, new\_df], ignore\_index=True)
            # 혹시 같은 세션을 두 번 올려 생기는 완전 중복 행 제거
            merged = merged.drop\_duplicates()
            \_upload\_csv(api, merged, fname)
        return True, "Dataset 업로드 완료"
    except Exception as e:
        return False, f"업로드 실패(무시하고 진행): {e}"


# ── 사이드바 다운로드용: 누적분 → CSV 바이트 ────────────────────────────────
def to\_csv\_bytes(rows):
    """누적 리스트 → UTF-8-SIG CSV(엑셀에서 한글 안 깨짐). 비면 빈 bytes."""
    if not rows:
        return b""
    return pd.DataFrame(rows).to\_csv(index=False).encode("utf-8-sig")
```

### 6.6 `streamlit\_app.py` — 메인 앱 (사이드바 안내 + 다운로드)

```python
# streamlit\_app.py
# ───────────────────────────────────────────────────────────────────────────
# 챗봇 실험 메인 앱 (SQLite 제거 버전).
# 흐름: intro → pre(사전설문) → chat(대화) → post(사후설문) → done
# 저장: storage.py의 이중 안전망(구글시트 + 메모리). DB 파일이 없다.
# 사이드바: (위) 연구 안내 설명  /  (아래) 데이터 CSV 다운로드 백업
# ───────────────────────────────────────────────────────────────────────────
import uuid
import time
import streamlit as st

import storage
from prompts import SYSTEM\_PROMPTS, TASK\_INSTRUCTION
from llm import stream\_response

st.set\_page\_config(page\_title="진로 챗봇 대화 연구", page\_icon="💬")

# ===== 세션 상태 초기화 =====
# Streamlit은 매 상호작용마다 스크립트를 위→아래로 다시 실행한다.
# 따라서 '지금 어느 단계인가'를 session\_state에 저장해 둬야 한다.
if "stage" not in st.session\_state:
    st.session\_state.stage = "intro"          # 현재 단계
    st.session\_state.participant\_id = str(uuid.uuid4())  # 익명 식별자(이름·이메일 안 받음)
    st.session\_state.condition = None         # 'A' 또는 'B'
    st.session\_state.messages = \[]            # 화면 표시용 대화 기록
    st.session\_state.turn = 0                 # 대화 턴 수

storage.init\_state(st.session\_state)  # 누적 리스트 3개 준비


# ===== 사이드바: 위쪽 안내 + 아래쪽 다운로드 =====
def render\_sidebar():
    with st.sidebar:
        # ── (위) 연구 안내 설명 ──
        st.header("📋 연구 안내")
        st.markdown(
            "- \*\*소요시간\*\*: 약 10\~15분\\n"
            "- \*\*절차\*\*: 사전 설문 → 챗봇 대화(5턴+) → 사후 설문\\n"
            "- \*\*익명성\*\*: 이름·이메일을 수집하지 않습니다.\\n"
            "- \*\*유의\*\*: 챗봇은 AI이며, 전문 자문이 필요하면 전문가에게 별도 문의하세요."
        )
        st.divider()

        # ── (아래) 데이터 다운로드 백업 ──
        # 안전망 2: HF Dataset 업로드가 실패해도 이 메모리 누적분으로 회수 가능.
        # 주의: session\_state는 '현재 브라우저 세션'의 데이터만 담는다.
        #       전체 참여자 통합본은 HF Dataset에서 받는다(안전망 1).
        st.header("⬇️ 데이터 다운로드")
        st.caption("이 세션에 쌓인 기록(백업용). 전체 통합본은 HF Dataset 참조.")
        n\_p = len(st.session\_state\["rows\_participants"])
        n\_m = len(st.session\_state\["rows\_messages"])
        n\_s = len(st.session\_state\["rows\_surveys"])
        st.download\_button("참여자 CSV", storage.to\_csv\_bytes(st.session\_state\["rows\_participants"]),
                           "participants.csv", "text/csv", disabled=(n\_p == 0))
        st.download\_button("대화 CSV", storage.to\_csv\_bytes(st.session\_state\["rows\_messages"]),
                           "messages.csv", "text/csv", disabled=(n\_m == 0))
        st.download\_button("설문 CSV", storage.to\_csv\_bytes(st.session\_state\["rows\_surveys"]),
                           "surveys.csv", "text/csv", disabled=(n\_s == 0))
        st.caption(f"참여자 {n\_p} · 대화 {n\_m}줄 · 설문 {n\_s}줄")


render\_sidebar()


# ===== Stage 1: 인트로 + 동의 =====
if st.session\_state.stage == "intro":
    st.title("AI 진로상담 챗봇 대화 연구")
    st.markdown(
        "졸업 후 진로에 대해 챗봇과 대화하는 연구입니다. "
        "사전 설문 → 대화 → 사후 설문 순으로 진행됩니다."
    )
    if st.button("동의하고 시작하기", type="primary"):
        # 입장 순서로 교대 배정(A,B,A,B...). 작은 N에서 쏠림을 막는다.
        n = len(st.session\_state\["rows\_participants"])
        cond = "A" if n % 2 == 0 else "B"
        st.session\_state.condition = cond
        storage.add\_participant(st.session\_state, st.session\_state.participant\_id, cond)
        st.session\_state.stage = "pre"
        st.rerun()

# ===== Stage 2: 사전조사 =====
elif st.session\_state.stage == "pre":
    st.title("사전 설문")
    with st.form("pre\_survey"):
        year = st.selectbox("학년", \["1학년", "2학년", "3학년", "4학년", "졸업유예/휴학", "대학원생"])
        major = st.selectbox("전공 계열", \["인문", "사회", "상경", "공학", "자연", "의약", "예체능", "기타"])
        d\_stage = st.selectbox("현재 진로 결정 단계",
                               \["아직 탐색 중", "방향이 어느 정도 잡힘", "구체적 계획 수립 중", "거의 확정"])
        anxiety = st.slider("최근 진로 불안 정도 (1: 전혀 없음 \~ 7: 매우 큼)", 1, 7, 4)
        ai\_freq = st.selectbox("AI 챗봇 사용 빈도", \["거의 안 씀", "월 1\~2회", "주 1\~2회", "거의 매일"])
        if st.form\_submit\_button("다음"):
            pid, cond = st.session\_state.participant\_id, st.session\_state.condition
            for qid, val in \[("year", year), ("major", major), ("decision\_stage", d\_stage),
                             ("career\_anxiety", anxiety), ("ai\_usage", ai\_freq)]:
                storage.add\_survey(st.session\_state, pid, cond, "pre", qid, val)
            st.session\_state.stage = "chat"
            st.rerun()

# ===== Stage 3: 대화 =====
elif st.session\_state.stage == "chat":
    st.title("진로 챗봇과 대화하기")
    st.info(TASK\_INSTRUCTION)
    st.caption(f"최소 5턴 이상 대화 후 아래 버튼을 누르세요. (현재 {st.session\_state.turn}턴)")

    # 이전 메시지 다시 그리기(매 실행마다 화면을 새로 그리므로 필요)
    for m in st.session\_state.messages:
        with st.chat\_message(m\["role"]):
            st.markdown(m\["content"])

    if prompt := st.chat\_input("메시지를 입력하세요"):
        pid, cond = st.session\_state.participant\_id, st.session\_state.condition
        st.session\_state.turn += 1

        # 1) 사용자 메시지: 화면 표시 + 저장
        st.session\_state.messages.append({"role": "user", "content": prompt})
        storage.add\_message(st.session\_state, pid, cond, st.session\_state.turn, "user", prompt)
        with st.chat\_message("user"):
            st.markdown(prompt)

        # 2) 챗봇 응답: 스트리밍으로 한 청크씩 표시
        with st.chat\_message("assistant"):
            placeholder = st.empty()
            full, t0 = "", time.time()
            try:
                for delta in stream\_response(SYSTEM\_PROMPTS\[cond], st.session\_state.messages):
                    full += delta
                    placeholder.markdown(full + "▌")  # 커서 효과
                placeholder.markdown(full)
            except Exception as e:
                full = f"\[오류가 발생했습니다: {e}]"
                placeholder.markdown(full)
            latency = int((time.time() - t0) \* 1000)
            st.session\_state.messages.append({"role": "assistant", "content": full})
            storage.add\_message(st.session\_state, pid, cond, st.session\_state.turn,
                                "assistant", full, latency)

    # 5턴 이상이면 사후설문으로 넘어가는 버튼 노출
    if st.session\_state.turn >= 5:
        if st.button("대화 종료하고 사후 설문으로", type="primary"):
            st.session\_state.stage = "post"
            st.rerun()

# ===== Stage 4: 사후조사 =====
elif st.session\_state.stage == "post":
    st.title("사후 설문")
    with st.form("post\_survey"):
        usefulness = st.slider("받은 정보가 유용했다 (1\~7)", 1, 7, 4)
        warmth = st.slider("챗봇이 따뜻했다 (1\~7)", 1, 7, 4)
        competence = st.slider("챗봇이 유능했다 (1\~7)", 1, 7, 4)
        trust = st.slider("챗봇을 신뢰한다 (1\~7)", 1, 7, 4)
        clarity = st.slider("대화 후 진로 고민이 더 정리되었다 (1\~7)", 1, 7, 4)
        recommend = st.slider("친구에게 추천할 의향 (1\~7)", 1, 7, 4)
        free\_text = st.text\_area("자유 의견: 가장 도움이 된 점, 아쉬웠던 점 (선택)")
        if st.form\_submit\_button("제출"):
            pid, cond = st.session\_state.participant\_id, st.session\_state.condition
            for qid, val in \[("usefulness", usefulness), ("warmth", warmth),
                             ("competence", competence), ("trust", trust),
                             ("clarity", clarity), ("recommend", recommend),
                             ("free\_text", free\_text)]:
                storage.add\_survey(st.session\_state, pid, cond, "post", qid, val)
            # 완료 표시(메모리): 해당 참여자 행의 completed를 1로
            for r in st.session\_state\["rows\_participants"]:
                if r\["participant\_id"] == pid:
                    r\["completed"] = 1
            # 안전망 1: 이번 세션 누적분을 HF Dataset에 일괄 업로드
            # (완료 시점에 한 번만. 실패해도 메모리 백업이 남으므로 흐름은 계속)
            storage.push\_to\_dataset(st.session\_state)
            st.session\_state.stage = "done"
            st.rerun()

# ===== Stage 5: 완료 =====
elif st.session\_state.stage == "done":
    st.title("참여해주셔서 감사합니다 🙏")
    st.markdown(f"참여자 ID: `{st.session\_state.participant\_id}`")
    st.caption("응답이 안전하게 기록되었습니다.")
```

### 6.7 핵심 설계 결정 — 이해해야 할 7가지

1. **`st.session\_state.stage`로 단계 관리**: Streamlit은 매번 코드를 위→아래로 다시 실행하므로 "어느 페이지인가"를 변수로 저장해야 한다.
2. **UUID로 익명 식별**: 이메일·이름을 안 받아 IRB에 유리.
3. **조건은 첫 진입 시 한 번만 배정**: `session\_state`에 저장해 새로고침해도 안 바뀐다.
4. **시스템 프롬프트는 매 호출마다 주입**: Gemini의 `config.system\_instruction`으로 전달.
5. **Gemini 역할 변환**: `"assistant"` → `"model"` (`\_to\_gemini`에서 처리).
6. **스트리밍 응답**: 참여자 이탈을 줄이는 핵심.
7. **메모리 누적 + 완료 시 업로드**: 대화 중에는 메모리에 쌓이고(안전망 2), 참여자 완료 시 그 세션 누적분을 HF Dataset에 일괄 업로드한다(안전망 1). 업로드는 기존 데이터와 합쳐(merge) 올리므로 여러 참여자가 한 파일에 통합된다.

### 6.8 로컬 실행

```bash
python -m venv venv
source venv/bin/activate     
pip install -r requirements.txt
echo "GEMINI\_API\_KEY=your\_key\_here" > .env
streamlit run streamlit\_app.py
```

로컬에서는 `HF\_TOKEN`이 없어도 됩니다. Dataset 업로드는 자동으로 건너뛰고 **사이드바 다운로드만** 동작합니다.

\---

## 7\. HF Dataset 설정 + Spaces 배포

> 큰 그림: 데이터는 \*\*Hugging Face Dataset\*\*(데이터 전용 저장소)에 CSV로 영구 저장합니다. 이미 Spaces를 쓰므로 같은 HF 안에서 \*\*토큰 1개만\*\* 더 만들면 끝입니다. 구글 클라우드·서비스계정·JSON 키 같은 복잡한 과정이 없습니다. Gemini 키는 \[aistudio.google.com/apikey](https://aistudio.google.com/apikey)에서 무료로 발급받아 둡니다.

### 7.1 HF Dataset 만들기 (1회, 무료)

데이터를 영구 보존하는 **안전망 1**입니다. 세 단계면 됩니다.

1. **빈 Dataset 생성**: [huggingface.co](https://huggingface.co) 로그인 → 오른쪽 위 프로필 → **New Dataset** → 이름 입력(예: `career-chatbot-data`) → **Private** 권장 → **Create dataset**. 만들어진 저장소 주소는 `본인아이디/career-chatbot-data` 형태입니다.
2. **write 토큰 발급**: 오른쪽 위 프로필 → **Settings** → 왼쪽 **Access Tokens** → **New token** → 이름 아무거나, 권한은 **Write** 선택 → 만들기 → 생성된 토큰(`hf\_...`)을 **복사해 둡니다.** (이 토큰은 비밀번호와 같으니 외부에 노출 금지)
3. **코드에 저장소 이름 적기**: `storage.py` 맨 위의 `DATASET\_REPO`를 1번에서 만든 본인 저장소로 교체합니다.

```python
DATASET\_REPO = "본인아이디/career-chatbot-data"   # ← 본인 것으로 교체
```

> 저장될 CSV 3개(participants/messages/surveys)는 앱이 자동으로 만들어 올립니다. 미리 만들 필요 없습니다.

### 7.2 Hugging Face Spaces 배포

1. **Space 생성**: [huggingface.co](https://huggingface.co) → New Space → SDK는 Docker를 클릭 → 펼쳐지는 템플릿 목록에서 **Streamlit** 선택, Hardware **CPU basic(무료)**, Public.
2. **파일 올리기**: 이 템플릿은 코드가 **`src/` 폴더** 안에서 실행되고, Dockerfile이 `src/streamlit\_app.py`를 메인으로 지정합니다. 따라서 파일 이름과 위치를 아래처럼 맞춰 올립니다. (Files 탭 → Add file → Upload files)

   * `streamlit\_app.py`(메인 앱)를 **`src/` 폴더 안**에 올립니다. Dockerfile이 이 이름을 메인으로 실행합니다.
   * `prompts.py`, `llm.py`, `storage.py`, `analyze.py` 도 **모두 `src/` 폴더 안**에 올립니다(서로 import하므로 같은 폴더에 있어야 함).
   * `requirements.txt` 는 **맨 바깥(루트)** 의 기존 것을 내 것으로 덮어씁니다.
   * `Dockerfile`, `README.md`, `.gitattributes` 는 **그대로 둡니다.**
   * `.env` 는 **절대 올리지 말 것**(키 노출).

```
   career-chatbot-exp/
   ├── Dockerfile          ← 그대로
   ├── README.md           ← 그대로
   ├── requirements.txt    ← 내 것으로 덮어쓰기
   └── src/
       ├── streamlit\_app.py  ← 메인 앱
       ├── prompts.py
       ├── llm.py
       ├── storage.py
       └── analyze.py
   ```

> 업로드 창에서 파일 이름 앞에 `src/`를 붙이면(예: `src/prompts.py`) 자동으로 그 폴더에 들어갑니다. 올린 뒤 아래 \*\*Commit changes to main\*\*을 누르면 다시 빌드됩니다.

3. **비밀 키 등록**: Settings → Variables and secrets → **New secret** 으로 두 개 등록.

   * `GEMINI\_API\_KEY` = Gemini 키
   * `HF\_TOKEN` = 7.1-2에서 만든 write 토큰(`hf\_...`)
   * (이름은 철자·대소문자까지 정확히)
4. **확인**: 자동 빌드 후 App 탭이 "Running"이 되면 완료. 그 URL을 참여자에게 배포하고, 직접 한 번 끝까지 진행해 Dataset에 CSV가 쌓이는지 점검.

### 7.3 데이터는 어디서 받나

* **전체 통합본(안전망 1)**: 본인 Dataset 저장소(`huggingface.co/datasets/본인아이디/career-chatbot-data`)의 **Files** 탭에서 `participants.csv`, `messages.csv`, `surveys.csv`를 내려받습니다. 모든 참여자가 합쳐져 있습니다.
* **즉시 백업(안전망 2)**: 앱 사이드바 아래쪽 다운로드 버튼. 단, 이건 **현재 세션** 데이터만입니다.

### 7.4 이중 안전망이 작동하는 방식

|상황|안전망 1 (HF Dataset)|안전망 2 (사이드바 다운로드)|
|-|-|-|
|평상시|참여자 완료마다 자동 누적(머지 업로드)|현재 세션 기록을 즉시 CSV로|
|Space 슬립/재시작|✅ 영향 없음(별도 저장소)|세션 끊기면 사라짐|
|여러 참여자 통합|✅ 자동 통합|세션별 분리|
|Dataset 업로드 실패|—|✅ 메모리 백업으로 회수|

> \*\*운영 원칙\*\*: 평소 데이터는 \*\*Dataset에서\*\* 받습니다(전체 통합본). 사이드바 다운로드는 업로드가 막혔을 때를 위한 \*\*즉시 백업\*\*입니다. 파일럿에서 두 경로 모두 실제로 쌓이는지 확인하세요.

### 7.5 안 될 때 — 증상별 해결

|증상|해결|
|-|-|
|`GEMINI\_API\_KEY가 설정되지 않았습니다`|secret 이름이 정확히 `GEMINI\_API\_KEY`인지 확인|
|앱은 되는데 Dataset에 안 쌓임|① `HF\_TOKEN` secret을 등록했는지 ② 토큰 권한이 **Write**인지 ③ `DATASET\_REPO`가 본인 저장소와 정확히 일치하는지|
|`401`/`403` 권한 에러|토큰이 Write가 아니거나 만료됨 → 새 write 토큰 발급 후 secret 교체|
|Space 빌드 안 끝남|Logs 탭에서 빨간 에러 줄 확인|
|첫 접속이 느림|무료 등급 슬립(정상). "처음 1분 대기" 안내|

> 토큰을 잃어버리면 재발급만 가능합니다(원본은 다시 못 봄). 7.1-2를 다시 해서 새 write 토큰을 만들고 secret을 교체하세요.



## 8\. 분석 — `analyze.py`

DB가 없으므로 HF Dataset(또는 사이드바에서 내려받은) CSV 3개를 직접 읽습니다. long format이라 pivot 한 번이면 끝납니다.

```python
# analyze.py
# ───────────────────────────────────────────────────────────────────────────
# 구글시트(또는 다운로드한 CSV) → 조건별 비교 분석.
# DB가 없으므로 CSV 3개를 직접 읽는다. long-format이라 pivot 한 번이면 끝.
# ───────────────────────────────────────────────────────────────────────────
import pandas as pd
from scipy import stats

# 구글시트에서 받은(혹은 사이드바에서 내려받은) CSV 3개
participants = pd.read\_csv("participants.csv")
messages = pd.read\_csv("messages.csv")
surveys = pd.read\_csv("surveys.csv")

# 1) 완료자만
done = participants\[participants\["completed"] == 1]
print(f"완료자: {len(done)}명")
print(done\["condition"].value\_counts())

# 2) 사후 설문을 wide format으로 (한 문항=한 열)
post = surveys\[surveys\["phase"] == "post"]
post\_wide = post.pivot\_table(index="participant\_id", columns="question\_id",
                             values="answer", aggfunc="first")

# 3) 조건과 합치기
df = done\[\["participant\_id", "condition"]].merge(post\_wide, on="participant\_id")
numeric = \["usefulness", "warmth", "competence", "trust", "clarity", "recommend"]
for c in numeric:
    df\[c] = pd.to\_numeric(df\[c], errors="coerce")

# 4) 조건별 t-test
print("\\n=== 조건별 비교 (A: 분석가형, B: 멘토형) ===")
for var in numeric:
    a = df\[df\["condition"] == "A"]\[var].dropna()
    b = df\[df\["condition"] == "B"]\[var].dropna()
    if len(a) > 1 and len(b) > 1:
        t, p = stats.ttest\_ind(a, b)
        print(f"{var:12s}: A={a.mean():.2f}, B={b.mean():.2f}, t={t:+.2f}, p={p:.3f}")
```

\---

## 9\. 학생 변형 가이드 — 자기 주제로 바꾸는 5단계

1. **연구 질문 다듬기**: "챗봇의 \[X]가 사용자의 \[Y]에 미치는 영향" 한 문장으로. (X=조작할 것, Y=측정할 것)
2. **조건 프롬프트 두 개 작성**: `prompts.py`의 `SYSTEM\_PROMPTS\["A"]`, `\["B"]`만 수정. 핵심은 **내용 동일, 조작점만 다르게**.
3. **과제 메시지 수정**: `TASK\_INSTRUCTION` 교체.
4. **설문 문항 수정**: `streamlit\_app.py`의 사전·사후 슬라이더만 교체. **저장 구조는 안 바꿔도 됨**(long format이라).
5. **시범 운영**: 본인이 두 조건을 모두 체험하고 "내용은 같고 스타일만 다른지" 확인.

### 변형 예시 7선

|분야|조건 A|조건 B|종속변수|
|-|-|-|-|
|뉴스리터러시|객관·중립 톤|해설·맥락 톤|뉴스 신뢰, 이해도|
|헬스|의사형|동료환자형|자가관리 의도|
|학습|정답 직접 제공형|소크라테스식 질문형|학습 성과|
|인간관계|분석·조언형|공감·경청형|정서 안정, 통찰|
|MBTI|학술·비판형|재미·해석형|자기이해, 만족도|
|정치(주의)|개인화 정보 사용|개인화 정보 미사용|의견 변화|
|소비자|전문가형|친구형|구매의도|

> 정치·종교·정신건강 등 민감 주제는 IRB 사전 검토가 추가로 필요할 수 있습니다.

### 강의용 Space를 복제해 내 실험 만들기 (학생용)

강의용 Space를 그대로 **복제(Duplicate)** 해서 내 실험으로 쓸 수 있습니다. 코드는 복사되지만 **키(secret)와 데이터 저장소는 복사되지 않으므로**, 복제 후 내 것으로 다시 연결해야 합니다.

**준비물 (복제 전에 미리 만들어 두기)**

1. **내 Gemini 키**: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)에서 발급 (`AIzaSy...`)
2. **내 HF Dataset**: [huggingface.co](https://huggingface.co) → New Dataset → 이름 입력(예: `내아이디/career-chatbot-data`) → Private 권장
3. **내 HF write 토큰**: Settings → Access Tokens → New token → 권한 **Write** (`hf\_...`)

**복제 단계**

1. 강의용 Space 화면 우상단 **⋮ → Duplicate this Space** 클릭
2. 복제 창에서 채우기:

   * **Owner**: 내 계정(자동으로 내 아이디가 뜸)
   * **Space name**: 원하는 이름
   * **Visibility**: **Public** (참여자가 링크로 접속해야 하므로)
   * **Space hardware**: **CPU Basic (Free)**
   * **Space secrets**: 빈 칸 두 개에 **내 키**를 채웁니다.

     * `HUGGINGFACE\_TOKEN\_WRITE` → 내 write 토큰(`hf\_...`)
     * `GEMINI\_API\_KEY` → 내 Gemini 키(`AIzaSy...`)
3. **Duplicate Space** 클릭

**복제 후 반드시 할 일 (이걸 안 하면 내 데이터가 강의용 저장소로 가려다 실패함)**

복제된 내 Space에서 `src/storage.py`를 열어, 저장소 이름을 **내 Dataset으로** 바꿉니다.

```python
DATASET\_REPO = "내아이디/career-chatbot-data"   # ← 반드시 내 것으로 변경
```

**점검**

내 Space가 "Running"이 되면 직접 한 번 끝까지(사전→5턴 대화→사후 제출) 해보고, 내 Dataset의 Files 탭에 `participants.csv` 등이 쌓이는지 확인합니다. 안 쌓이면 7.5절(증상별 해결)을 참고하세요.

> 복제해도 강의용 키·토큰은 넘어오지 않으니 안전합니다. 다만 `DATASET\_REPO`만은 코드에 직접 적혀 있으므로 꼭 내 것으로 바꿔야 합니다.

\---

## 10\. 향후 발전 방향

* **사후 추적조사**: Costello et al.(2024)처럼 1주·1개월 후 follow-up(IRB 동의 시).
* **사전등록(preregistration)**: OSF에 가설·설계·분석계획 등록. 학부생도 가능.
* **공개 데이터 공유**: 익명화 대화 로그를 OSF/GitHub에 공개.
* **모델 비교 조건**: `MODEL\_NAME`을 조건별로 다르게 두면 Gemini vs GPT vs Claude 비교 실험도 같은 코드로.
* **N이 커지면**: HF Dataset은 수천\~수만 행도 무리 없음. 본격 대규모면 그때 전용 DB로.

\---

## 11\. 체크리스트 — 시작 전 점검

* \[ ] 연구 질문이 한 문장으로 정리됐다
* \[ ] 조건 A, B 프롬프트가 "내용 동일, 스타일만 차이"를 통과한다
* \[ ] 사전·사후 설문이 5분 이내에 끝난다
* \[ ] 본인이 두 조건을 직접 체험하고 수정했다
* \[ ] IRB 신청서를 제출했다
* \[ ] `.env`가 `.gitignore`에 들어 있다
* \[ ] **HF Dataset을 만들었고, `DATASET\_REPO`가 일치하며, write 토큰을 secret으로 등록했다**
* \[ ] **파일럿에서 HF Dataset에 CSV가 실제로 쌓이는지 + 사이드바 다운로드가 되는지 확인했다**
* \[ ] Gemini API 키 사용량 한도를 설정했다
* \[ ] 참여자 3명(파일럿)에게 먼저 돌려보고 버그를 수정했다

\---

## 12\. 참고문헌

학생 보고서 작성 시 적어도 ★ 표시한 3편은 인용하시기 바랍니다.

★ Bermudez Schettino, R., Dasmeh, A., \& Brinkmann, L. (2025). *Facilitating the Integration of LLMs Into Online Experiments With Simple Chat*. arXiv:2511.19123.

★ Costello, T. H., Pennycook, G., \& Rand, D. G. (2024). Durably reducing conspiracy beliefs through dialogues with AI. *Science*, *385*(6714), eadq1814.

★ Salvi, F., Horta Ribeiro, M., Gallotti, R., \& West, R. (2025). On the conversational persuasiveness of GPT-4. *Nature Human Behaviour*, *9*(8), 1645–1653.

Betz, N. E., Klein, K. L., \& Taylor, K. M. (1996). Evaluation of a short form of the Career Decision-Making Self-Efficacy Scale. *Journal of Career Assessment*, *4*(1), 47–57.

Fiske, S. T., Cuddy, A. J., \& Glick, P. (2007). Universal dimensions of social cognition: Warmth and competence. *Trends in Cognitive Sciences*, *11*(2), 77–83.

Gati, I., Krausz, M., \& Osipow, S. H. (1996). A taxonomy of difficulties in career decision making. *Journal of Counseling Psychology*, *43*(4), 510–526.

Kestin, G., Miller, K., Klales, A., Milbourne, T., \& Ponti, G. (2024). AI tutoring outperforms active learning. *Research Square* (preprint).

Lamprou, Z. et al. (2025). *Customizable LLM-Powered Chatbot for Behavioral Science Research*. arXiv:2501.05541.

McKenna, C. (2023). *oTree GPT*. GitHub: https://github.com/clintmckenna/oTree\_gpt

