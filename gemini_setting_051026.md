# Gemini API 호출 + 설정 가이드 (2026)

> **목표**: AI Studio의 모든 설정 항목 → Python SDK 코드 일대일 매핑 **핵심**: **검색·URL 읽기·코드 실행은 외부 API 불필요**. Gemini가 직접 처리 **SDK**: `google-genai` (구 `google-generativeai`는 deprecated)

---

## 0\. 한눈에 보는 매핑

AI Studio의 우측 패널 설정은 모두 Python SDK의 `types.GenerateContentConfig`로 1:1 매핑.

```python
from google import genai
from google.genai import types

client = genai.Client()  # GEMINI_API_KEY 환경변수 자동 인식

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",                     # 모델 선택
    contents="질문",                                   # 사용자 입력
    config=types.GenerateContentConfig(
        system_instruction="페르소나 정의",            # System instructions
        temperature=0.7,                               # Temperature
        top_p=0.95,                                    # Top P
        top_k=40,                                      # Top K
        max_output_tokens=8192,                        # Output length
        thinking_config=types.ThinkingConfig(          # Thinking level
            thinking_budget=1024),
        safety_settings=[...],                         # Safety settings
        response_mime_type="application/json",         # Structured output
        response_schema=MyPydanticModel,
        tools=[                                        # Tools
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(url_context=types.UrlContext()),
            types.Tool(code_execution=types.ToolCodeExecution()),
            my_python_function,
        ],
        media_resolution=types.MediaResolution.MEDIA_RESOLUTION_HIGH,
        stop_sequences=["END"],
        candidate_count=1,
    ),
)
print(response.text)
```

이 한 블록이 본 문서의 전부. 이하는 각 옵션의 의미·사용법·실전 코드.

> **중요한 SDK 변경 사항**: 사용자 예시 코드의 `import google.generativeai as genai`는 deprecated. 통합 SDK인 `google-genai`만 사용한다. 두 라이브러리는 import 경로·메서드 시그니처가 모두 다르므로 혼용 불가.
> 
> 설치: `pip install google-genai`

---

## 1\. 환경 준비

### 1-1. 설치

```bash
pip install google-genai pydantic python-dotenv
# 비동기 성능 향상 (선택):
pip install "google-genai[aiohttp]"
```

### 1-2. API 키

1.  [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) 에서 "Get API key" → 키 복사
2.  프로젝트 루트에 `.env` 생성: `GEMINI_API_KEY=AIza...`
3.  코드:

```python
from dotenv import load_dotenv; load_dotenv()
from google import genai
client = genai.Client()  # 환경변수 자동 인식
```

### 1-3. 첫 호출 (smoke test)

```python
r = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="한 문장으로: AI는 어떻게 작동하나요?")
print(r.text)
```

한국어로 한 문장이 출력되면 성공.

---

## 2\. 모델 선택 — 어떤 모델을 언제 쓸까

| 모델 | 입력/출력 단가 (per 1M tokens) | 강점 | 데이터저널리즘 권장 용도 |
| --- | --- | --- | --- |
| **gemini-2.5-flash-lite** | $0.10 / $0.40 | 최저가, 393 tok/s, 1M 컨텍스트 | RSS 분류·요약·추출·번역 |
| **gemini-2.5-flash** | $0.30 / $2.50 | 추론·코딩·다단계 | 본문 분석, 프레임 비교 |
| **gemini-2.5-pro** | $1.25 / $10 | 최고 추론 | 학술 논문 검토, 법률 분석 |

> **실전 패턴**: 75% Flash-Lite + 20% Flash + 5% Pro 라우팅 → all-Pro 대비 ~85% 비용 절감.

```python
def llm(prompt, complexity="low"):
    model = {
        "low":    "gemini-2.5-flash-lite",
        "medium": "gemini-2.5-flash",
        "high":   "gemini-2.5-pro",
    }[complexity]
    return client.models.generate_content(model=model, contents=prompt).text

quick_summary = llm("이 헤드라인 분류: ...", "low")
deep_analysis  = llm("이 5개 보도의 프레임 차이를 비교: ...", "medium")
```

---

## 3\. 기본 생성 파라미터 (Temperature / Top P / Top K / Output Length)

이 네 가지는 모델의 응답 분포를 조절. 모두 `GenerateContentConfig`에 입력.

### 3-1. Temperature (무작위성)

-   **0.0**: 결정적. 같은 입력에 거의 같은 출력. 분류·추출·번역에 권장
-   **0.5**: 약간의 다양성. 일반 답변
-   **1.0**: 균형. 대화·설명에 적합
-   **1.5~2.0**: 매우 창의적. 브레인스토밍·아이디에이션

### 3-2. Top P (Nucleus Sampling)

누적 확률 P 이내 토큰만 샘플링 후보로. 0.95이 사실상 표준. 낮추면 보수적, 1에 가까우면 모든 토큰 허용.

### 3-3. Top K

상위 K개 토큰만 후보로. Gemini 2.5+에서는 기본값(40~64) 그대로 둬도 무방.

### 3-4. Max Output Tokens

응답 길이 상한. 비용 통제·잘림 방지용. Flash 계열은 65,536까지 가능하나 보통 2,048~8,192면 충분.

### 3-5. 실전 코드 — 용도별 프리셋

```python
from google import genai
from google.genai import types
client = genai.Client()

# 결정적 (분류·추출·정형화)
DETERMINISTIC = types.GenerateContentConfig(
    temperature=0, top_p=0.95, max_output_tokens=2048)

# 균형 (요약·일반 응답)
BALANCED = types.GenerateContentConfig(
    temperature=0.7, top_p=0.95, max_output_tokens=4096)

# 창의 (헤드라인 후보·브레인스토밍)
CREATIVE = types.GenerateContentConfig(
    temperature=1.3, top_p=0.98, max_output_tokens=4096)

r = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="다음 기사를 3줄로 요약: [본문]",
    config=BALANCED)
print(r.text)
```

> **팁**: `temperature=0`을 써도 완벽히 결정적이지 않다. 재현성이 중요하면 `seed`도 고려.

---

## 4\. System Instructions — 페르소나·역할·제약

대화 전반에 적용되는 메타 지시. 사용자 입력은 매번 바뀌어도 시스템 지시는 고정. 응답의 톤·형식·금지 사항을 일관되게 통제.

### 4-1. 기본

```python
r = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="합계출산율이란?",
    config=types.GenerateContentConfig(
        system_instruction=(
            "당신은 한국 인구통계 전문 데이터 저널리스트다. "
            "통계청 공식 정의를 우선 인용하고, "
            "최근 5년 추이가 있으면 함께 제시한다. "
            "응답은 한국어 존댓말로 한다."
        ),
        temperature=0.3,
    ),
)
print(r.text)
```

### 4-2. 좋은 system instruction의 5요소

1.  **역할** — "당신은 X 전문가다"
2.  **대상 독자** — "초등학생도 이해할 수 있게" / "동료 연구자에게 설명하듯"
3.  **출력 형식** — "마크다운 헤더 사용" / "3줄 요약 후 상세"
4.  **금지 사항** — "추측하지 말고 자료에 없으면 모른다고 답하라"
5.  **인용 규칙** — "각 주장 뒤 \[번호\] 인용 표기"

### 4-3. 실전 — 데이터저널리즘 페르소나

```python
DJ_REPORTER = """
당신은 데이터 저널리즘 전문 기자다.
응답 원칙:

1. 자료에 명시된 사실만 인용한다. 없으면 "확인 불가"라고 한다
2. 모든 수치 옆에 출처와 시점 병기 (예: "5.7명 (KOSIS, 2024Q3)")
3. 인과 추론이 아닌 상관·기술 통계 수준에 머무른다
4. 한국 사회 맥락 — OECD 비교, 지역격차, 시계열 추이 — 를 의식한다
5. 응답은 4섹션: ① 핵심 사실 ② 데이터 근거 ③ 한계·주의 ④ 추가 취재 가설
"""

r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="청년 고용률과 출산율 관계를 어떻게 분석할 수 있나요?",
    config=types.GenerateContentConfig(
        system_instruction=DJ_REPORTER, temperature=0.3))
print(r.text)
```

> **비용 팁**: 큰 배경 자료(코퍼스)는 **Context Caching API**로 분리 저장 → 90% 비용 절감.

---

## 5\. Thinking — 모델의 추론 깊이 조절

Gemini 2.5/3 시리즈는 답변 전 내부 "추론 과정"을 거친다. 추론 토큰도 과금되지만 복잡한 문제 정확도가 크게 향상.

### 5-1. 두 가지 API 패턴

-   **Gemini 2.5 시리즈**: `thinking_budget` (정수, 토큰 수)
-   **Gemini 3 시리즈**: `thinking_level` (enum: minimal / low / medium / high)

### 5-2. Gemini 2.5 — `thinking_budget`

```python
from google.genai import types

# 추론 비활성화 (속도·비용 우선)
r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="수도가 서울인 나라는?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0)))

# 적당한 추론 (기본값에 가까움)
r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="주사위 두 개를 굴려 합이 7이 될 확률은?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=1024)))

# 깊은 추론 (복잡 문제)
r = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="이 1973년 중앙정보부 검열 기록을 분석해 패턴을 찾아라: ...",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=8192,
            include_thoughts=True)))  # 추론 과정 노출
```

### 5-3. Gemini 3 — `thinking_level`

```python
r = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="복잡한 멀티홉 추론 질문",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="low")))   # minimal / low / medium / high
```

### 5-4. 모델별 thinking 정책

| 모델 | 기본 | 비활성화 가능 | 권장 |
| --- | --- | --- | --- |
| gemini-2.5-flash-lite | OFF | ✅ | 단순 작업은 OFF, 복잡 추론에만 ON |
| gemini-2.5-flash | ON (auto) | ✅ (`thinking_budget=0`) | auto 그대로 |
| gemini-2.5-pro | ON | ❌ | 그대로 |
| gemini-3-flash-preview | dynamic high | ✅ (`level="minimal"`) | auto 그대로 |
| gemini-3.x-pro | dynamic high | ❌ | 그대로 |

### 5-5. 추론 토큰 확인

```python
r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="...",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=1024)))

print(r.usage_metadata.prompt_token_count)      # 입력
print(r.usage_metadata.candidates_token_count)  # 출력 (보이는 답변)
print(r.usage_metadata.thoughts_token_count)    # 추론 (보이지 않지만 과금)
print(r.usage_metadata.total_token_count)
```

### 5-6. 알려진 함정 (2026-05 기준)

-   `gemini-2.5-flash-preview-09-2025` + `response_mime_type="application/json"` 조합 시 `thinking_budget=0`이 무시되는 버그 보고됨. JSON 출력 + thinking 끄기 필요하면 stable `gemini-2.5-flash` 사용 권장.
-   추론은 보이지 않지만 출력 단가로 과금된다. 일일 만 건 처리 시 무시 못할 비용.

---

## 6\. Safety Settings — 콘텐츠 안전 필터

Gemini는 5개 카테고리에서 위험도(NEGLIGIBLE/LOW/MEDIUM/HIGH)를 평가하고, 임계값 이상이면 응답을 차단.

### 6-1. 5개 카테고리

| 카테고리 | enum |
| --- | --- |
| 괴롭힘 | `HARM_CATEGORY_HARASSMENT` |
| 증오 표현 | `HARM_CATEGORY_HATE_SPEECH` |
| 성적 노출 | `HARM_CATEGORY_SEXUALLY_EXPLICIT` |
| 위험 콘텐츠 | `HARM_CATEGORY_DANGEROUS_CONTENT` |
| 시민 무결성 (선거 등) | `HARM_CATEGORY_CIVIC_INTEGRITY` |

### 6-2. 5개 차단 임계값

| 임계값 | 효과 |
| --- | --- |
| `BLOCK_LOW_AND_ABOVE` | 가장 엄격 (LOW 이상 모두 차단) |
| `BLOCK_MEDIUM_AND_ABOVE` | 중간 (MEDIUM 이상 차단) |
| `BLOCK_ONLY_HIGH` | 관대 (HIGH만 차단) |
| `BLOCK_NONE` | 차단 없음 (모니터링만) |
| `OFF` | 평가 자체를 안 함 |

### 6-3. 기본값 (Gemini 2.5+ 매우 중요)

**Gemini 2.5 이상에서는 모든 카테고리 기본값이 `OFF`** — 차단되지 않는다. 차단을 원하면 명시적으로 `safety_settings`를 지정.

### 6-4. 코드 — 데이터저널리즘 표준 설정

```python
from google.genai import types

# 데이터저널리즘에서는 학생용 강의 환경에서 보수적으로 운영
SAFETY_STRICT = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
]

r = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="...",
    config=types.GenerateContentConfig(safety_settings=SAFETY_STRICT))
```

### 6-5. 차단 처리

```python
# 차단됐을 때 r.text는 None이 된다
if r.candidates[0].finish_reason == "SAFETY":
    print("응답이 안전 필터로 차단됨")
    for rating in r.candidates[0].safety_ratings:
        print(f"  {rating.category}: {rating.probability}")

# 입력 자체가 차단됐을 때
if r.prompt_feedback and r.prompt_feedback.block_reason:
    print(f"입력 차단: {r.prompt_feedback.block_reason}")
```

### 6-6. 주의점

-   **언론 보도 분석 시**: 혐오 발언·극단주의 자료를 분석하려면 차단으로 막힐 수 있다. 이 경우 임계값을 `BLOCK_ONLY_HIGH` 또는 `BLOCK_NONE`으로 완화하되, 별도 윤리 가이드라인 필수.
-   **차단됐다고 모델이 거짓말하지는 않는다** — 응답이 비어 있을 뿐. 이를 명확히 처리하지 않으면 빈 문자열로 진행해 후속 코드가 오작동.
-   **시민 무결성 카테고리**는 선거 보도와 직결되므로 임계값 결정에 신중.

---

## 7\. Structured Output — 정해진 JSON 스키마로 응답 받기

자유 텍스트 응답을 파싱하는 대신, **모델에게 JSON 스키마를 강제**해 안정적으로 구조화된 데이터를 받는다. 데이터저널리즘에서 분류·추출·정형화 작업의 핵심.

### 7-1. 두 가지 방법

1.  **Pydantic 모델** (가장 깔끔)
2.  **JSON Schema dict** (수동)

Gemini 2.5+는 두 방법 모두 완전 지원. JSON Schema의 `anyOf`, `$ref` 등도 처리 가능. 키 순서도 보장.

### 7-2. Pydantic 방식 (권장)

```python
from pydantic import BaseModel, Field
from typing import List, Literal
from google import genai
from google.genai import types

client = genai.Client()

class Article(BaseModel):
    title: str = Field(description="기사 제목")
    summary: str = Field(description="3줄 요약")
    topic: Literal["정치", "경제", "사회", "문화", "국제", "기타"]
    sentiment: Literal["positive", "neutral", "negative"]
    key_entities: List[str] = Field(description="등장 인물·기관·지역")

# 단일 객체
r = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="다음 기사를 분석: [본문 ...]",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Article,
    ),
)
# r.parsed가 자동으로 Pydantic 인스턴스로 변환
article: Article = r.parsed
print(article.topic, article.sentiment, article.key_entities)
```

### 7-3. 리스트 출력

```python
# 여러 기사를 동시에 분류
r = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="""다음 헤드라인 10개를 각각 분류:

1. 합계출산율 0.7명대 진입 ...
2. 코스피 2,800선 회복 ...
...
""",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[Article]),  # ← list 타입
)
articles: list[Article] = r.parsed
for a in articles:
    print(a.title, "→", a.topic)
```

### 7-4. 중첩 구조

```python
class GroundingHit(BaseModel):
    source: str
    url: str
    excerpt: str

class FactCheck(BaseModel):
    claim: str
    verdict: Literal["TRUE", "MOSTLY_TRUE", "MIXED", "MOSTLY_FALSE", "FALSE", "UNVERIFIABLE"]
    confidence: float = Field(ge=0, le=1, description="0~1 신뢰도")
    reasoning: str
    evidence: List[GroundingHit]

r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="다음 주장을 검증: [주장]",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=FactCheck,
        temperature=0))
fc: FactCheck = r.parsed
```

### 7-5. JSON Schema 직접 사용

```python
# Pydantic을 쓸 수 없는 환경
schema = {
    "type": "object",
    "properties": {
        "topic": {"type": "string", "enum": ["정치","경제","사회","문화"]},
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["topic", "score"],
    "propertyOrdering": ["topic", "score", "tags"],  # 순서 보장
}

r = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="...",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema))
import json
data = json.loads(r.text)
```

### 7-6. 저널리즘 실전 — RSS 헤드라인 일괄 분류

```python
class HeadlineClassification(BaseModel):
    idx: int
    relevance_score: float = Field(ge=0, le=1)
    main_topic: str
    actors: List[str]
    is_breaking: bool
    requires_factcheck: bool
    reason: str

headlines = [
    "1. 합계출산율 0.7명대 진입, 정책 한계 노출",
    "2. 코스피 2,800선 회복",
    "3. K-콘텐츠 수출 사상 최대",
    # ... 100개
]

r = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=(
        "관심 주제: '한국 인구·노동·복지 정책'\n"
        "각 헤드라인을 분류하라:\n" + "\n".join(headlines)),
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=list[HeadlineClassification],
        temperature=0))

results: list[HeadlineClassification] = r.parsed
relevant = [h for h in results if h.relevance_score >= 0.7]
```

### 7-7. Tools와 결합 (Gemini 2.5+ 가능, Gemini 3에서 더 안정)

```python
class Match(BaseModel):
    winner: str
    score: str
    scorers: List[str]

# 검색 + 구조화 결과 동시
r = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="2024 UEFA Euro 결과를 검색해서 정리",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(url_context=types.UrlContext()),
        ],
        response_mime_type="application/json",
        response_json_schema=Match.model_json_schema()))
match = Match.model_validate_json(r.text)
```

> **함정**:
> 
> -   일부 모델은 tools + structured output 조합이 제한된다. Gemini 3 시리즈가 가장 안정.
> -   너무 깊은 중첩 스키마는 토큰 소모가 크다. 가능하면 평면화.
> -   `Optional[X]`나 `Union[X, Y]`는 `anyOf`로 변환되며 일부 모델에서는 정확도 저하.

---

## 8\. 내장 도구 (Built-in Tools) — 외부 API 없이 검색·URL·코드 실행

**Gemini의 가장 강력한 기능.** 이 세 가지는 Google 서버에서 실행되며 **외부 API 키·구현 불필요**. `tools=[...]` 한 줄로 활성화.

| 도구 | 효과 | 외부 API 필요? |
| --- | --- | --- |
| `google_search` | 실시간 구글 검색·인용 | ❌ |
| `url_context` | 임의 URL 본문 fetch·읽기 | ❌ |
| `code_execution` | 파이썬 샌드박스 실행 | ❌ |
| (참고) `google_maps` | 지리 정보 | ❌ (일부 모델만) |
| (참고) `file_search` | 업로드 파일 검색 | ❌ (Files API 연계) |

### 8-1. Google Search Grounding — 실시간 검색

#### 기본

```python
from google.genai import types

r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="2026년 한국 합계출산율 가장 최근 발표값은?",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=1.0,  # 검색 결과 종합 시 1.0 권장
    ),
)
print(r.text)
```

모델이 자동으로:

1.  검색 필요 여부 판단
2.  검색 쿼리 생성·실행
3.  결과 종합·인용
4.  그라운딩 메타데이터 반환

#### 그라운딩 메타데이터 추출

```python
gm = r.candidates[0].grounding_metadata

# 모델이 사용한 검색 쿼리
print("검색 쿼리:", gm.web_search_queries)
# 예: ['2026년 한국 합계출산율 통계청', 'Korea TFR 2026']

# 출처 청크 (URL + 제목)
for chunk in gm.grounding_chunks:
    print(chunk.web.title, "→", chunk.web.uri)

# 본문 ↔ 출처 매핑 (인라인 인용용)
for sup in gm.grounding_supports:
    print(f"문장 [{sup.segment.start_index}:{sup.segment.end_index}]")
    print(f"  → 청크 인덱스: {sup.grounding_chunk_indices}")
```

#### 검색 추천 위젯 (서비스 약관)

검색 그라운딩 응답을 사용자에게 노출할 때는 `searchEntryPoint.rendered_content` HTML을 함께 표시해야 한다 (Google 약관).

```python
from IPython.display import HTML, display
display(HTML(gm.search_entry_point.rendered_content))
```

#### 한도

일 1,000,000 쿼리. 상업 서비스라면 충분, 데이터저널리즘 강의·연구에도 풍족.

### 8-2. URL Context — 임의 URL 본문 자동 읽기

웹스크래핑 코드 작성 없이 URL 그대로 넘기면 모델이 fetch.

```python
r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
        "다음 두 기사의 프레임 차이를 비교: "
        "https://www.hani.co.kr/arti/society/society_general/1000000.html, "
        "https://www.chosun.com/national/national_general/2026/05/01/.html"),
    config=types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext())],
    ),
)
print(r.text)

# 어떤 URL을 실제로 읽었는지 확인
for ucm in r.candidates[0].url_context_metadata.url_metadata:
    print(ucm.retrieved_url, ucm.url_retrieval_status)
```

**용도**:

-   여러 기사 비교·통합
-   PDF·논문 URL 직접 분석 (PDF 본문도 추출)
-   GitHub README·문서 분석
-   정부 보도자료 직접 분석

**제약**: 로그인 필요 사이트, JS 렌더링만 되는 사이트, 매우 큰 PDF 등은 실패할 수 있음. `url_retrieval_status`로 확인.

### 8-3. Code Execution — 모델이 파이썬을 직접 실행

수치 계산·통계·간단한 시각화·데이터 검증 등을 모델이 코드로 푼다. 결과는 응답에 통합.

```python
r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
        "한국 합계출산율 시계열 (2010=1.23, 2015=1.24, 2020=0.84, "
        "2023=0.72, 2024=0.75)을 받아 연평균 변화율과 추세를 계산하라."),
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())]),
)

# 응답에는 코드와 실행 결과가 모두 포함
for part in r.candidates[0].content.parts:
    if part.text:
        print("[텍스트]", part.text)
    if part.executable_code:
        print("[실행 코드]\n", part.executable_code.code)
    if part.code_execution_result:
        print("[결과]", part.code_execution_result.output)
```

샌드박스에는 numpy, pandas, matplotlib, scipy, sympy 등 표준 데이터과학 스택이 사전 설치돼 있다. 외부 인터넷 접속은 불가 (그래서 `google_search`와 결합하면 강력).

### 8-4. 도구 결합 — Gemini의 진짜 강점

**검색 + URL 읽기 + 코드 실행 + Function Calling을 동시에 활성화 가능** (특히 Gemini 3 시리즈).

```python
# 한국 출산율 자료를 검색해서 PDF 다운받고 통계까지 계산
r = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=(
        "통계청의 가장 최근 인구동향조사 보도자료를 찾아 PDF 본문을 분석하고, "
        "합계출산율의 5년 변화율을 계산해 시각화 코드까지 제시하라."),
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(url_context=types.UrlContext()),
            types.Tool(code_execution=types.ToolCodeExecution()),
        ],
        temperature=1.0))
print(r.text)
```

이 한 호출이 자동으로:

1.  통계청 보도자료를 검색
2.  PDF URL을 fetch해서 본문 추출
3.  수치 데이터를 파이썬 코드로 계산
4.  결과를 종합한 답변 생성

기존이라면 (1) 검색 API + (2) 웹 크롤러 + (3) PDF 파서 + (4) 데이터 분석 파이프라인을 직접 구성해야 함.

---

## 9\. Custom Function Calling — 외부 API 연결

내장 도구 외에 본인이 정의한 함수를 모델이 호출하게 한다. KOSIS / DART / RSS / 사내 DB 등.

### 9-1. SDK가 자동으로 처리하는 것

-   docstring과 타입 어노테이션 → JSON 스키마 자동 생성
-   모델이 `FunctionCall` 응답하면 → 함수 자동 실행 → 결과 다시 모델에 전달
-   멀티-턴 자동 루프

### 9-2. 기본

```python
import requests, os, feedparser
from google import genai
from google.genai import types

client = genai.Client()

def kosis_data(orgId: str, tblId: str, prdSe: str,
               startPrdDe: str, endPrdDe: str) -> dict:
    """KOSIS 통계자료 조회.

    Args:
        orgId: 기관코드 (예: '101' = 통계청)
        tblId: 통계표 ID
        prdSe: 주기 ('Y'/'Q'/'M')
        startPrdDe, endPrdDe: 시작·종료 시점 (YYYY 또는 YYYYMM)
    """
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    return requests.get(url, params=dict(
        method="getList", apiKey=os.environ["KOSIS_API_KEY"],
        format="json", jsonVD="Y",
        orgId=orgId, tblId=tblId, prdSe=prdSe,
        startPrdDe=startPrdDe, endPrdDe=endPrdDe), timeout=15).json()

def fetch_rss(url: str, limit: int = 20) -> list:
    """RSS 피드의 최신 기사 limit개를 반환."""
    d = feedparser.parse(url)
    return [{"title": e.title, "link": e.link,
             "published": e.get("published", "")}
            for e in d.entries[:limit]]

r = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=("한겨레(https://www.hani.co.kr/rss/) 헤드라인 10개를 가져와 "
              "출산율 관련 기사가 있으면 KOSIS에서 최근 합계출산율도 조회하라."),
    config=types.GenerateContentConfig(
        tools=[kosis_data, fetch_rss],   # ← 함수 객체 그대로
        temperature=0))
print(r.text)
```

### 9-3. 자동 호출 비활성화 (수동 제어 원할 때)

```python
config = types.GenerateContentConfig(
    tools=[kosis_data, fetch_rss],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True)  # 모델이 functionCall만 반환, 실행은 사용자가
)
```

### 9-4. 강제 호출 모드

```python
config = types.GenerateContentConfig(
    tools=[kosis_data],
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode="ANY",  # AUTO/ANY/NONE
            allowed_function_names=["kosis_data"]))
)
```

-   `AUTO`: 모델이 알아서 (기본)
-   `ANY`: 반드시 도구 호출
-   `NONE`: 도구 사용 금지 (텍스트만)

### 9-5. 내장 도구 + Custom Function 결합

```python
r = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=(
        "오늘 한겨레 RSS에서 출산율 관련 기사를 찾고, "
        "기사가 인용한 통계 수치를 KOSIS에서 검증한 뒤, "
        "추가로 OECD 평균과 비교한 시각화 코드까지 작성하라."),
    config=types.GenerateContentConfig(
        tools=[
            fetch_rss, kosis_data,                              # custom
            types.Tool(google_search=types.GoogleSearch()),     # built-in
            types.Tool(code_execution=types.ToolCodeExecution()),
        ]))
```

> Gemini 3 시리즈는 built-in tools와 custom function의 자유 결합을 정식 지원. 2.5 시리즈도 가능하나 일부 조합에서 제약.

---

## 10\. Media Resolution — 이미지·비디오 처리 해상도

이미지/비디오 입력 시 토큰 사용량과 정확도의 트레이드오프 조절.

### 10-1. 옵션

| 값 | 효과 | 토큰 비용 |
| --- | --- | --- |
| `MEDIA_RESOLUTION_LOW` | 64 토큰/이미지 | 최저 |
| `MEDIA_RESOLUTION_MEDIUM` | 256 토큰/이미지 | 보통 |
| `MEDIA_RESOLUTION_HIGH` | 모델별 최대 (예: 1290 for 1024×1024) | 최고 |

### 10-2. 코드

```python
import PIL.Image
img = PIL.Image.open("chart.png")

r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=["이 차트의 데이터를 모두 추출해 표로 정리하라.", img],
    config=types.GenerateContentConfig(
        media_resolution=types.MediaResolution.MEDIA_RESOLUTION_HIGH))
```

### 10-3. 데이터저널리즘 권장

-   **차트·표·인포그래픽 OCR**: HIGH (작은 텍스트가 핵심)
-   **사진 분류·태깅**: MEDIUM (충분)
-   **대량 자동 태깅**: LOW (비용 우선)
-   **비디오 프레임 분석**: 주로 LOW~MEDIUM (여러 프레임 누적)

---

## 11\. 도구 조합 매트릭스 (어떤 조합이 가능한가)

Gemini 모델·버전별로 도구 조합 가능 여부가 다름. 2026-05 기준:

| 조합 | Gemini 2.5 Flash-Lite | Gemini 2.5 Flash/Pro | Gemini 3+ |
| --- | --- | --- | --- |
| google\_search 단독 | ✅ | ✅ | ✅ |
| url\_context 단독 | ✅ | ✅ | ✅ |
| code\_execution 단독 | ✅ | ✅ | ✅ |
| function\_calling 단독 | ✅ | ✅ | ✅ |
| **search + url\_context** | ✅ | ✅ | ✅ |
| **search + code\_execution** | 일부 | ✅ | ✅ |
| **search + function\_calling** | ❌ (구버전) | ❌ (구버전) | ✅ (Gemini 3) |
| **structured output + tools** | 제한 | 제한 | ✅ |
| **여러 사용자 함수 + 내장 도구** | 제한 | 부분 | ✅ |

### 11-1. 권장 패턴 — Gemini 2.5 Flash-Lite

```python
# 패턴 A: 검색 grounding + structured 출력 (별도 호출)
# 1) 검색·요약
search_resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="...",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
    ),
)
# 2) 그 결과를 구조화
struct_resp = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=f"다음 내용을 JSON으로 정리:\n{search_resp.text}",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=MyModel,
    ),
)
```

### 11-2. 권장 패턴 — Gemini 3+

```python
# 한 호출로 모두
resp = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="2024년 한국 합계출산율 변화와 정책 함의를 JSON으로",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(url_context=types.UrlContext()),
            types.Tool(code_execution=types.ToolCodeExecution()),
        ],
        response_json_schema=PolicyAnalysis.model_json_schema(),
        response_mime_type="application/json",
    ),
)
result = PolicyAnalysis.model_validate_json(resp.text)
```

---

## 12\. 추가 옵션 — 자주 쓰지만 누락하기 쉬운 것들

### 12-1. Stop Sequences

지정 문자열이 나타나면 생성 중단.

```python
config=types.GenerateContentConfig(
    stop_sequences=["END", "\n\n---"])
```

### 12-2. Candidate Count

한 호출로 여러 응답 후보를 받는다 (브레인스토밍·다양성 비교용).

```python
config=types.GenerateContentConfig(
    candidate_count=3, temperature=1.5)

for i, c in enumerate(r.candidates):
    print(f"=== 후보 {i+1} ===")
    print(c.content.parts[0].text)
```

### 12-3. Response Modalities

응답 형식 지정 (텍스트·이미지·오디오).

```python
# 이미지 생성 (gemini-2.5-flash-image)
r = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A minimalist infographic of Korea's TFR decline 2010-2025",
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="9:16")))
```

### 12-4. Logprobs

토큰별 확률 노출 (분석·디버깅).

```python
config=types.GenerateContentConfig(
    response_logprobs=True, logprobs=5)
```

### 12-5. Streaming

응답을 토큰 단위로 받는다.

```python
for chunk in client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="긴 응답이 필요한 질문 ..."):
    print(chunk.text, end="", flush=True)
```

### 12-6. Async (asyncio)

```python
import asyncio
from google import genai

async def main():
    client = genai.Client()
    r = await client.aio.models.generate_content(
        model="gemini-2.5-flash-lite", contents="...")
    print(r.text)

asyncio.run(main())
```

### 12-7. Context Caching (대규모 코퍼스 반복 사용 시 90% 비용 절감)

```python
cache = client.caches.create(
    model="gemini-2.5-flash",
    config=types.CreateCachedContentConfig(
        system_instruction="당신은 한국 인구통계 전문가다.",
        contents=[long_research_corpus],   # 수십만 토큰
        ttl="3600s"))

r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="합계출산율과 청년 고용률 상관관계는?",
    config=types.GenerateContentConfig(cached_content=cache.name))
```

### 12-8. Batch Mode (50% 할인, 24시간 내 처리)

```python
# 야간 대량 분류 등 비실시간 작업에 권장
batch_job = client.batches.create(
    model="gemini-2.5-flash-lite",
    src=[
        {"contents": [{"parts":[{"text": p}]}]}
        for p in many_prompts
    ])
# 완료 후 결과 폴링
```

---

## 13\. 실전 레시피

지금까지의 내장 기능들을 조합한 실전 패턴.

### 13-1. 검색 그라운딩 팩트체크

```python
from pydantic import BaseModel
from typing import Literal, List
from google import genai
from google.genai import types

client = genai.Client()

class Source(BaseModel):
    title: str
    url: str
    quote: str

class FactCheck(BaseModel):
    claim: str
    verdict: Literal["사실", "대체로 사실", "혼합", "대체로 거짓", "거짓", "검증불가"]
    confidence: float
    explanation: str
    sources: List[Source]

def factcheck(claim: str) -> FactCheck:
    r = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"다음 주장을 검색을 통해 검증하고 한국어로 답하라:\n{claim}",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=1.0,
            system_instruction=(
                "당신은 신중한 팩트체커다. "
                "검색 결과만을 근거로 판단하고, 출처를 반드시 명시한다.")))
    # 검색 그라운딩과 structured output을 동시에 쓰려면 별도 요약 단계 필요
    summary = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"다음 검증 결과를 구조화된 JSON으로 정리:\n{r.text}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FactCheck))
    return summary.parsed

result = factcheck("2024년 한국 합계출산율이 0.7 미만으로 떨어졌다")
print(result.verdict, result.confidence)
for s in result.sources:
    print(f"  - {s.title}: {s.url}")
```

### 13-2. 다중 매체 프레임 비교 (URL Context 활용)

```python
class FrameAnalysis(BaseModel):
    media: str
    headline: str
    framing: str
    key_phrases: List[str]
    emphasized_actors: List[str]
    sentiment: Literal["비판적", "중립적", "옹호적"]

class FrameComparison(BaseModel):
    topic: str
    analyses: List[FrameAnalysis]
    overall_difference: str

urls = [
    "https://www.hani.co.kr/arti/.../1234567.html",
    "https://www.chosun.com/national/.../2026/05/01/AB.html",
    "https://www.khan.co.kr/national/.../202605012100001.html",
]

r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
        f"다음 3개 매체의 동일 사건 보도 프레임을 비교 분석하라:\n"
        + "\n".join(urls)),
    config=types.GenerateContentConfig(
        tools=[types.Tool(url_context=types.UrlContext())],
        response_mime_type="application/json",
        response_schema=FrameComparison,
        temperature=0.3))
comparison = r.parsed
```

### 13-3. RSS + 검색 + 코드 실행 — 자동 일일 브리핑

```python
def daily_briefing(topic: str) -> str:
    """관심 주제에 대해 RSS·검색·통계 분석을 종합한 일일 브리핑 생성."""
    return client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"""오늘({date.today()}) 한국 언론에서 '{topic}' 관련 보도를
종합하여 데이터저널리즘 관점의 일일 브리핑을 작성하라.

요구사항:

1. 한국 주요 매체 RSS 또는 구글 검색으로 최신 보도 5건 이상 수집
2. 발표된 통계가 있으면 코드 실행으로 추세 계산
3. 매체 간 프레임 차이 비교
4. 추가 취재 가능한 데이터 가설 2개 제시""",
        config=types.GenerateContentConfig(
            system_instruction="당신은 한국 데이터저널리즘 전문 기자다.",
            tools=[
                types.Tool(google_search=types.GoogleSearch()),
                types.Tool(url_context=types.UrlContext()),
                types.Tool(code_execution=types.ToolCodeExecution()),
            ],
            temperature=0.7,
            max_output_tokens=8192)).text

print(daily_briefing("청년 노동시장과 출산율"))
```

### 13-4. PDF 보고서 일괄 분석 (Files API + Structured Output)

```python
class ReportSummary(BaseModel):
    title: str
    publisher: str
    publish_date: str
    key_findings: List[str]
    data_sources: List[str]
    methodology_notes: str
    recommendations: List[str]

# 정부 보고서 PDF 10개 일괄 처리
import glob
results = []
for pdf_path in glob.glob("./reports/*.pdf"):
    pdf = client.files.upload(file=pdf_path)
    r = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=["이 보고서를 구조화된 JSON으로 요약:", pdf],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ReportSummary,
            temperature=0))
    results.append(r.parsed)

# DataFrame으로 변환
import pandas as pd
df = pd.DataFrame([r.model_dump() for r in results])
df.to_csv("report_summary.csv", index=False)
```

### 13-5. 한국 정부 보도자료 모니터링 (URL Context + Function Calling)

```python
def list_recent_briefings(category: str = "보건복지부") -> list:
    """policybriefing.korea.kr에서 최근 보도자료 URL 목록 반환."""
    # 실제로는 RSS 또는 정책브리핑 API 사용
    return [...]

class BriefingAnalysis(BaseModel):
    department: str
    title: str
    url: str
    key_policies: List[str]
    affected_groups: List[str]
    data_cited: List[str]
    journalistic_value: Literal["high", "medium", "low"]
    suggested_angle: str

r = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="오늘 보건복지부 보도자료를 모두 분석해 취재 가치 순으로 정리하라.",
    config=types.GenerateContentConfig(
        tools=[
            list_recent_briefings,
            types.Tool(url_context=types.UrlContext()),
        ],
        response_mime_type="application/json",
        response_schema=list[BriefingAnalysis],
        temperature=0.3))
analyses = r.parsed
```

---

## 14\. 모든 설정을 합친 완전체 예제 (사용자 제공 코드의 신 SDK 버전)

사용자 제공 deprecated 코드를 **완전한 실용 코드**로 재작성:

```python
# full_example.py
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()   # GEMINI_API_KEY 자동 로드

# ── 1. System instructions (페르소나) ──
SYSTEM = """당신은 친절하고 유머러스한 AI 비서입니다.
필요하면 코드를 실행해 정확한 답을 제시합니다.
한국어로 답하되 코드와 결과는 그대로 보여줍니다.
"""

# ── 2~4. 모든 설정을 GenerateContentConfig 한 곳에 ──
config = types.GenerateContentConfig(
    # 페르소나
    system_instruction=SYSTEM,

    # 생성 파라미터
    temperature=0.7,
    top_p=0.95,
    max_output_tokens=4096,
    stop_sequences=["END_OF_RESPONSE"],

    # 추론 깊이 (Flash-Lite는 기본 OFF, 가볍게만 켜기)
    thinking_config=types.ThinkingConfig(thinking_budget=512),

    # 안전 설정 (보수적)
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
    ],

    # 내장 도구 (외부 API 키 불필요!)
    tools=[
        types.Tool(google_search=types.GoogleSearch()),     # 실시간 검색
        types.Tool(code_execution=types.ToolCodeExecution()), # 코드 실행
    ],
    # ※ Gemini 2.5 Flash에서는 search+code 동시 지원
    # ※ Gemini 3에서는 + structured output까지 결합 가능
)

# ── 5. 호출 ──
resp = client.models.generate_content(
    model="gemini-2.5-flash",   # Flash-Lite로 바꾸면 더 저렴
    contents="안녕! 서울의 오늘 날씨와 어울리는 노래 추천하고, "
             "1부터 100까지 짝수 합을 코드로 계산해줘.",
    config=config,
)

# ── 6. 응답 처리 ──
print("=" * 60)
print("최종 답변:")
print(resp.text)
print()

# 추론 토큰
if resp.usage_metadata.thoughts_token_count:
    print(f"추론에 사용된 토큰: {resp.usage_metadata.thoughts_token_count}")

# 코드 실행 흔적
for part in resp.candidates[0].content.parts:
    if part.executable_code:
        print(f"\n[실행한 코드]\n{part.executable_code.code}")
    if part.code_execution_result:
        print(f"\n[코드 출력]\n{part.code_execution_result.output}")

# 검색 grounding 정보
gm = resp.candidates[0].grounding_metadata
if gm and gm.grounding_chunks:
    print("\n[검색 출처]")
    for c in gm.grounding_chunks:
        print(f"  - {c.web.title}: {c.web.uri}")
    if gm.web_search_queries:
        print(f"\n[검색어]: {gm.web_search_queries}")

# 종료 사유
print(f"\n종료 사유: {resp.candidates[0].finish_reason}")
print(f"총 토큰: {resp.usage_metadata.total_token_count}")
```

---

## 15\. 강의용 실습 커리큘럼 (5주 미니 모듈)

자매 가이드의 RSS·MCP 커리큘럼과 결합 가능.

### 1주차 — 기본 파라미터 마스터

-   Temperature 0/0.5/1.5 비교 실험
-   `max_output_tokens` 설정에 따른 잘림 관찰
-   System instruction 역할 다르게 두고 동일 질문에 응답 비교
-   **과제**: 같은 헤드라인에 대해 5가지 페르소나(보수 / 진보 / 중립 / 학자 / 시민)로 분석 → 차이 정리

### 2주차 — Structured Output

-   Pydantic 모델 정의 → 헤드라인 100개 일괄 분류
-   중첩 스키마로 인용·수치까지 추출
-   **과제**: 본인 관심 분야 RSS 100건 → JSON 추출 → DataFrame → CSV → Excel

### 3주차 — 내장 도구 (검색·URL·코드 실행) ⭐

-   `google_search` 그라운딩으로 팩트체크
-   `url_context`로 동일 사건 5개 매체 비교
-   `code_execution`으로 통계 계산
-   **과제**: "오늘 화제가 된 한국 사회 이슈"에 대해 검색·URL·코드 통합 브리핑 작성

### 4주차 — Function Calling + MCP

-   KOSIS·DART 함수 작성 → SDK에 전달
-   자작 RSS-MCP 서버 연결 (자매 가이드 §11)
-   내장 도구와 custom 도구 결합
-   **과제**: 자기만의 "데이터저널리즘 어시스턴트" 구축

### 5주차 — 멀티모달 + 종합

-   이미지(차트·인포그래픽) 분석 + Files API
-   인터뷰 음성 → 전사 → 발언 추출
-   모든 도구를 결합한 종합 보도 시나리오
-   **과제**: 지정된 주제에 대해 텍스트·이미지·음성·통계를 모두 활용한 자동 기사 시안 작성

---

## 16\. 비용·속도 가이드 (의사결정 치트시트)

| 작업 | 권장 모델 | 권장 옵션 |
| --- | --- | --- |
| 헤드라인 분류 (~100건) | flash-lite | temp=0, structured output |
| RSS 의미 필터 | flash-lite | temp=0, JSON 출력, batch (50% 할인) |
| 본문 요약 (~500자) | flash-lite | temp=0.3, max=512 |
| 5개 매체 프레임 비교 | flash | temp=0.3, url\_context |
| 팩트체크 (단순 사실) | flash-lite | google\_search, temp=1.0 |
| 팩트체크 (복잡 주장) | flash | search + url\_context + thinking |
| 통계 계산·시각화 | flash | code\_execution |
| 학술 논문 검토 | pro | thinking\_budget=4096 |
| 인터뷰 음성 전사 | flash | Files API + media\_resolution |
| 차트 OCR | flash | media\_resolution=HIGH |
| 야간 대량 처리 | flash-lite | Batch mode (50% 할인) |
| 큰 코퍼스 반복 질의 | flash | Context Caching (90% 할인) |

---

## 17\. 트러블슈팅

| 증상 | 원인·해결 |
| --- | --- |
| `r.text`가 None | 안전 필터 차단 → `r.candidates[0].finish_reason`, `safety_ratings` 확인 |
| `r.parsed`가 None | JSON 파싱 실패 → `r.text` 직접 보고 스키마 점검. 너무 깊은 중첩 회피 |
| `quota exceeded` | 무료 tier 한도 초과 → 1분 대기 + exponential backoff |
| `404 model not found` | 모델 ID 오타 또는 신규 모델 권한 미부여 |
| 추론 토큰 0인데 답이 길다 | 정상. thinking 안 한 모델일 수 있음 |
| `thinking_budget=0`이 무시됨 | preview 모델 + JSON 출력 조합 버그 → stable 모델 사용 |
| URL context 빈 응답 | `url_retrieval_status` 확인. JS·로그인 사이트는 실패 가능 |
| 검색 결과 없음 | `web_search_queries` 확인. 쿼리 한국어 추가 또는 `temperature=1.0` |
| Function이 호출 안 됨 | docstring·타입 어노테이션 보강. `tool_config.mode="ANY"` 강제 |
| 응답이 잘림 | `max_output_tokens` 증가 또는 streaming 사용 |
| Structured + Tools 충돌 | 일부 모델은 동시 사용 제한. Gemini 3 시리즈로 |
| 응답 한국어가 어색 | system\_instruction에 "한국어 존댓말" 명시 + temp 낮춤 |

---

## 18\. 빠른 참조 — 옵션 한눈에

```python
types.GenerateContentConfig(
    # 페르소나
    system_instruction: str,

    # 분포 제어
    temperature: float = 1.0,           # 0.0 ~ 2.0
    top_p: float = 0.95,                # 0.0 ~ 1.0
    top_k: int = 40,                    # 1 이상
    max_output_tokens: int = 8192,
    stop_sequences: list[str],
    candidate_count: int = 1,
    seed: int,                          # 일부 모델

    # 추론
    thinking_config: types.ThinkingConfig(
        thinking_budget: int,           # 2.5 시리즈
        thinking_level: str,            # 3 시리즈: minimal/low/medium/high
        include_thoughts: bool,
    ),

    # 안전
    safety_settings: list[types.SafetySetting],

    # 구조화 출력
    response_mime_type: "application/json",
    response_schema: PydanticModel | dict | list[Model],
    response_json_schema: dict,         # alt
    response_modalities: list[str],     # ["TEXT"], ["IMAGE"]

    # 도구
    tools: list[                        # 자유 조합
        types.Tool(google_search=types.GoogleSearch()),
        types.Tool(url_context=types.UrlContext()),
        types.Tool(code_execution=types.ToolCodeExecution()),
        my_python_function,             # custom
    ],
    tool_config: types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode: "AUTO" | "ANY" | "NONE",
            allowed_function_names: list[str])),
    automatic_function_calling: types.AutomaticFunctionCallingConfig(
        disable: bool),

    # 미디어
    media_resolution: types.MediaResolution.MEDIA_RESOLUTION_HIGH,
    image_config: types.ImageConfig(aspect_ratio="9:16"),

    # 캐시
    cached_content: str,                # cache.name

    # 디버깅
    response_logprobs: bool,
    logprobs: int,
)
```

---

## 19\. 참고 자료

### 공식 문서

### Cookbook (실전 예제)

-   Gemini Cookbook: [https://github.com/google-gemini/cookbook](https://github.com/google-gemini/cookbook)
-   Gemini by Example: [https://geminibyexample.com](https://geminibyexample.com)
-   philschmid/gemini-samples: [https://github.com/philschmid/gemini-samples](https://github.com/philschmid/gemini-samples)

### 비교·벤치마크

-   Artificial Analysis: [https://artificialanalysis.ai](https://artificialanalysis.ai)
-   OpenRouter (다양한 모델): [https://openrouter.ai](https://openrouter.ai)

---

## 20\. 핵심 요약 (1쪽)

1.  **`google-genai` 사용**. `google-generativeai`는 deprecated.
    
2.  **호출 패턴은 항상 동일**: `client.models.generate_content(model, contents, config)`
    
3.  **모든 설정은 `types.GenerateContentConfig(...)`** 한 곳에 들어감.
    
4.  **모델 선택**:
    
    -   일반 작업·대량 → `gemini-2.5-flash-lite` ($0.10/$0.40)
    -   복잡한 추론·창작 → `gemini-2.5-flash` ($0.30/$2.50)
5.  **Temperature**: 분류·추출은 0, 창작은 1.0.
    
6.  **Thinking**:
    
    -   Flash-Lite는 OFF → 켜고 싶으면 `thinking_budget=512+`
    -   Flash는 ON → 끄려면 `thinking_budget=0` (단, JSON 모드와 일부 충돌)
7.  **Safety**: 2.5+ 기본 OFF. 필요시 5개 카테고리 임계값 설정.
    
8.  **Structured Output**: Pydantic + `response_mime_type="application/json"` + `response_schema=Model`. `resp.parsed`로 받음.
    
9.  **내장 도구는 외부 API 키 불필요**:
    
    -   `google_search` — 검색 (일 100만 쿼리 무료)
    -   `url_context` — URL 자동 fetch
    -   `code_execution` — Python 자동 실행
10.  **Function Calling**: 사용자 함수를 그대로 `tools=[fn]`에 — SDK가 docstring·타입 자동 변환.
     
11.  **Search/Code는 Gemini 서버에서 실행 → 한 번의 API 호출**로 끝.
     
12.  **Tool 조합 제한**: 2.5는 부분 지원, 3+에서 자유로운 조합.
     
13.  **비용 절감 3대 무기**:
     
     -   모델 라우팅 (Lite vs Flash vs Pro)
     -   Context Caching (반복 자료)
     -   Batch mode (50% 할인, 야간 작업)
14.  **응답 검증 필수**: `finish_reason`, `prompt_feedback.block_reason`, `usage_metadata`.
     
15.  **데이터저널리즘 표준 스택**:
     

`Flash-Lite + Pydantic structured output + google_search/url_context (필요시) + RSS·API 사용자 함수 (자매 가이드) → SQLite/Chroma 적재 → Telegram/Notion 알림`