# Gemini 멀티모달 분석 실습

> \*\*AI미디어코딩 강의용\*\* · 모델: `gemini-2.5-flash-lite` (무료)
> 텍스트 → 이미지 → PDF → 오디오 → 비디오 → YouTube 까지 한 번에

\---

## 목차

1. [학습 목표와 핵심 아이디어](#1-학습-목표와-핵심-아이디어)
2. [API 키 발급과 환경 설정](#2-api-키-발급과-환경-설정)
3. [Gemini API의 작동 원리](#3-gemini-api의-작동-원리-한-눈에-보는-요청-구조)
4. [모달리티별 사용법](#4-모달리티별-사용법)
5. [무료 쿼터와 모범 사례](#5-무료-쿼터와-모범-사례)
6. [자주 만나는 오류와 해결법](#6-자주-만나는-오류와-해결법)
7. [학생 실습 과제](#7-학생-실습-과제)

\---

## 1\. 학습 목표와 핵심 아이디어

### 핵심 목표

LLM API 호출은 **"특정 URL에 JSON을 POST하는 일"** 그 이상도 이하도 아닙니다. 화려한 SDK가 있긴 하지만, 내부적으로는 똑같은 HTTP 요청을 보낼 뿐입니다. 여기에서는 SDK를 거치지 않고 `requests` 라이브러리만으로 직접 요청을 만들어, **"무엇이 어디로 어떻게 보내지는가"** 를 눈으로 확인합니다.

### 멀티모달의 본질

복잡해 보이지만 패턴은 단 하나입니다.

```
contents = \[ { "parts": \[ <part1>, <part2>, ... ] } ]
```

`parts` 배열 안에 텍스트·이미지·PDF·오디오·비디오·YouTube URL을 자유롭게 섞어 넣을 수 있습니다. 모달리티가 무엇이든 **part 한 조각의 형식만 다를 뿐, 구조는 동일**합니다. 이것이 이 코드를 관통하는 핵심 통찰입니다.

|Part 종류|형식|사용 예|
|-|-|-|
|텍스트|`{"text": "..."}`|프롬프트, 본문|
|인라인 파일|`{"inline\_data": {"mime\_type": "...", "data": "<base64>"}}`|이미지·PDF·오디오·짧은 영상|
|원격 파일|`{"file\_data": {"file\_uri": "..."}}`|YouTube URL, File API 업로드|

\---

## 2\. API 키 발급과 환경 설정

### 2.1 API 키 발급 (3분 소요)

1. [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) 접속
2. Google 계정으로 로그인
3. **Create API key** 클릭 → 새 프로젝트 생성 또는 기존 프로젝트 선택
4. 발급된 키(예: `AIzaSy...`)를 안전한 곳에 복사
5. 신용카드 등록 **불필요**

### 2.2 환경변수에 키 저장

코드에 키를 직접 적으면 GitHub 등에 실수로 노출될 위험이 있습니다. **환경변수**로 관리하세요.

```bash
# Windows PowerShell (현재 세션만)
$env:GEMINI\_API\_KEY = "AIzaSy..."

# Windows PowerShell (영구 저장)
\[Environment]::SetEnvironmentVariable("GEMINI\_API\_KEY", "AIzaSy...", "User")

# macOS / Linux Bash
export GEMINI\_API\_KEY="AIzaSy..."
# 영구 저장은 \~/.bashrc 또는 \~/.zshrc 끝에 위 줄 추가
```

### 2.3 패키지 설치

```bash
pip install requests
```

끝입니다. **`PyPDF2`, `pydub`, `opencv`, `Pillow` 같은 멀티미디어 라이브러리는 일절 필요 없습니다.** Gemini가 PDF·오디오·영상을 모두 네이티브로 이해하기 때문입니다.

\---

## 3\. Gemini API의 작동 원리

### 3.1 우리가 보내는 것 (Request)

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent
Headers:
    Content-Type: application/json
    x-goog-api-key: <YOUR\_KEY>
Body (JSON):
{
  "contents": \[
    {
      "parts": \[
        { "text": "이 이미지를 분석해 주세요." },
        { "inline\_data": { "mime\_type": "image/jpeg", "data": "<base64...>" } }
      ]
    }
  ],
  "generationConfig": {
    "maxOutputTokens": 4096,
    "temperature": 0.7,

&#x20;     "candidateCount": 1,  
  }
}
```

### 3.2 받는 것 (Response)

```json
{
  "candidates": \[
    {
      "content": {
        "parts": \[ { "text": "이 이미지는 ..." } ]
      },
      "finishReason": "STOP"
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 1023,
    "candidatesTokenCount": 412,
    "totalTokenCount": 1435
  }
}
```

### 3.3 핵심 함수 `call\_gemini()` 한 줄씩 읽기

```python
def call\_gemini(parts, max\_tokens=4096, temperature=0.7):
    payload = {
        "contents": \[{"parts": parts}],          # ① 입력 조각들을 turn에 담음
        "generationConfig": {                     # ② 생성 옵션
            "maxOutputTokens": max\_tokens,
            "temperature": temperature,
        },
    }
    headers = {                                   # ③ API 키는 헤더로
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI\_API\_KEY,
    }
    response = requests.post(API\_URL, headers=headers, json=payload, timeout=180)
    response.raise\_for\_status()                   # ④ 에러면 즉시 예외
    result = response.json()
    return result\["candidates"]\[0]\["content"]\["parts"]\[0]\["text"]   # ⑤ 응답 텍스트만 추출
```

이 함수만 이해하면 나머지 분석 함수들은 **"parts 리스트를 어떻게 만드는가"** 의 차이일 뿐입니다.

\---

## 4\. 모달리티별 사용법

### 4.1 텍스트 분석 — `analyze\_text()`

가장 단순한 케이스. parts에 텍스트 하나만 들어갑니다.

```python
result = analyze\_text("분석할 본문...")
print(result)
```

**프롬프트 설계 5원칙** (코드의 분석 프롬프트가 따르는 패턴)

1. **역할 부여** — "당신은 \~ 전문가입니다"
2. **작업 명시** — "다음 9가지 항목으로 분석"
3. **형식 고정** — 항목마다 번호와 제목을 명시
4. **언어 지정** — "한국어로 작성하세요"
5. **입력 분리** — 분석 대상은 `"""..."""` 로 감싸 지시문과 구분

### 4.2 이미지 분석 — `analyze\_image\_file()`, `analyze\_image\_url()`

```python
# 로컬 파일
analyze\_image\_file("photo.jpg")

# 인터넷 이미지 URL
analyze\_image\_url("https://...jpg")
```

**왜 URL 분석 함수도 다운로드를 직접 할까?**
Gemini의 `file\_data` 방식은 PDF·YouTube에는 잘 동작하지만, 일반 이미지 URL은 서버 권한·핫링크 차단 등으로 실패가 잦습니다. 우리가 `requests.get()`으로 받아 base64로 인코딩해 `inline\_data`로 넣는 편이 안정적입니다.

**지원 형식**: `.png`, `.jpg/.jpeg`, `.webp`, `.gif`, `.heic`

### 4.3 PDF 분석 — `analyze\_pdf()` 

```python
analyze\_pdf("report.pdf")    # 텍스트 추출 라이브러리 없이 그대로!
```

**왜 PyPDF2가 필요 없는가?**

* Gemini는 PDF를 받으면 페이지마다 **이미지(비전) + 임베디드 텍스트** 둘 다를 봅니다.
* 즉 PyPDF2가 못 잡는 표·차트·도표·레이아웃까지 그대로 이해합니다.
* 한 페이지 ≈ 258 토큰. 최대 1,000 페이지까지 처리 가능.

**한도**:

* 인라인(base64 본문 첨부) 권장: **20 MB 이하**
* 그보다 큰 PDF는 별도 File API 업로드가 필요 (이번 강의 범위 밖)

### 4.4 오디오 분석 — `analyze\_audio\_file()`

```python
analyze\_audio\_file("interview.mp3")
```

**Gemini가 오디오에서 뽑아내는 것**:

* 음성 → 텍스트 전사 (Whisper 같은 별도 STT 모델 불필요)
* 화자 수, 추정 성별/연령, 톤·감정
* 배경음·BGM·효과음의 의미
* 발화의 수사적 전략

**지원 형식**: `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`

**권장 길이**: 1\~5분 (인라인 20 MB 한도 안에서 충분)

### 4.5 로컬 비디오 분석 — `analyze\_video\_file()`

```python
analyze\_video\_file("clip.mp4")
```

**Gemini가 비디오를 보는 방식**:

* 1초당 1프레임을 샘플링하면서 **동시에** 오디오 트랙도 분석
* 시각 변화 + 음성·BGM을 종합적으로 이해
* 타임스탬프(`\[MM:SS]`)로 특정 시점을 지목 가능

**⚠️ 인라인 한도**:

* **20 MB 이하 + 약 1분 이내**
* 더 긴 영상은 다음 항목(YouTube)을 사용하세요.

**지원 형식**: `.mp4`, `.mov`, `.avi`, `.webm`, `.mkv`

### 4.6 YouTube URL 분석 — `analyze\_youtube()` 

```python
analyze\_youtube("https://www.youtube.com/watch?v=XXXXXXXX")
```

**한 줄로 끝!** 다운로드도, 인코딩도 필요 없습니다.

**이 기능이 다른 모달리티와 다른 점**:

```python
# 다른 모달리티: inline\_data 사용
{"inline\_data": {"mime\_type": "...", "data": "<base64>"}}

# YouTube: file\_data 사용 (mime\_type도 불필요!)
{"file\_data": {"file\_uri": "https://www.youtube.com/watch?v=..."}}
```

**제약사항**:

* 공개(public) 영상만 가능. **비공개·미등록 영상 안됨**
* 무료 티어: **하루 총 8시간** (영상 누적 길이 기준)
* 한 요청에 한 영상 권장 (Gemini 2.5부터 최대 10개까지 가능하지만 품질 저하)

**강의·실습용 권장 길이: 5\~10분**

|영상 길이|하루 가능 횟수|추천 용도|
|-|-|-|
|3분|\~160회|광고, 짧은 뉴스, TikTok 형식|
|5분|\~96회|뉴스 클립, 토픽 영상|
|10분|\~48회|TED 강연 일부, 다큐 발췌|
|30분|\~16회|풀 인터뷰, 연설 (개인 연구용)|

> \*\*권장\*\*: 학생 실습은 \*\*5분 영상\*\*으로 시작하세요. 응답이 빠르고 토큰 소모가 적어 시행착오를 많이 거칠 수 있습니다.

\---

## 5\. 무료 쿼터와 모범 사례

### 5.1 Gemini 2.5 Flash-Lite 무료 한도 (2026년 기준)

|항목|한도|
|-|-|
|RPM (분당 요청 수)|15|
|RPD (일일 요청 수)|1,000|
|TPM (분당 토큰 수)|250,000|
|YouTube 영상 누적 길이|8 시간/일|
|Context window|1,000,000 토큰|

> 무료 티어 입력 데이터는 \*\*Google 모델 학습에 사용될 수 있습니다.\*\* 민감 정보·연구 윤리상 보호되어야 할 데이터는 절대 무료 티어로 보내지 마세요. 유료 티어로 전환하면 학습 사용을 거부할 수 있습니다.

### 5.2 토큰 절약 팁

* **PDF**: 한 페이지 ≈ 258 토큰. 100 페이지면 약 25,800 토큰. 필요한 페이지만 추리면 비용이 1/10로.
* **오디오**: 초당 약 32 토큰. 5분이면 9,600 토큰.
* **비디오**: 초당 약 300 토큰(영상 258 + 오디오 32 + 메타데이터). 5분이면 90,000 토큰. **가장 비싼 모달리티!**
* **이미지**: 장당 약 258 토큰. 매우 저렴.

### 5.3 빠른 실험을 위한 팁

1. **`temperature=0.0`** 으로 시작 → 같은 입력에 같은 출력이 나와 디버깅 쉬움
2. **`max\_tokens=1024`** 로 짧게 응답받아 빠른 반복 후, 만족스러우면 늘리기
3. 같은 PDF·영상을 여러 번 분석할 거면 **Context Caching** 사용 (이번 강의 범위 밖)

\---

## 6\. 자주 만나는 오류와 해결법

### `\[API 오류 400]` — Bad Request

요청 JSON 형식이 잘못된 경우. 흔한 원인:

* `inline\_data`의 `data` 값이 base64가 아니거나 `b''` 같은 Python 바이트 표기 그대로
* `mime\_type` 누락
* YouTube 분석에서 `inline\_data`를 사용 (`file\_data` 가 맞음)

### `\[API 오류 401 / 403]` — 인증 실패

* API 키 오타 / 환경변수 미설정
* 키가 비활성화됨 → AI Studio에서 새로 발급
* `x-goog-api-key` 헤더 이름 오타

### `\[API 오류 429]` — Rate Limit 초과

* 분당 15회 / 일일 1,000회 초과
* 해결: 1\~2분 기다렸다가 재시도. 배치 처리 시 `time.sleep(5)` 권장

### `\[API 오류 413]` — Payload Too Large

* 인라인 데이터가 20 MB 초과
* 해결: 파일 압축, 더 짧은 클립 사용, 또는 File API 업로드

### `\[응답 파싱 실패]` (candidates가 빔)

* 안전 필터에 걸린 경우(폭력·성·증오 등)
* 응답 본문에 `promptFeedback.blockReason`이 표시됨
* 해결: 다른 콘텐츠로 시도, 프롬프트 표현 완화

### YouTube 영상 분석이 안 됨

* 비공개·미등록 영상은 불가
* 일부 지역 차단된 영상 불가
* 8시간 일일 한도 초과 시 다음 날 자정(태평양 시간) 리셋

\---

## 7\. 학생 실습 과제

### 단계 1: 기본 동작 확인

1. 환경변수에 API 키 등록
2. `if \_\_name\_\_ == "\_\_main\_\_":` 블록의 텍스트 분석 예시 주석 해제 → 실행
3. 출력에서 9개 항목이 모두 나오는지 확인

### 단계 2: 모달리티 한 바퀴 돌기 (각자)

|과제|입력 예시|
|-|-|
|이미지 분석|본인이 찍은 사진 1장|
|PDF 분석|정부 보도자료 PDF (10페이지 내외)|
|오디오 분석|라디오 뉴스 1\~2분 클립 (mp3)|
|비디오 분석|30초\~1분 짜리 광고 영상 (mp4)|
|YouTube 분석|2분짜리 뉴스 클립 URL|

### 단계 3: 비교 분석 응용

같은 사건을 다룬 **두 개의 다른 매체**를 각각 분석한 뒤, 어떤 차이가 있었는지 직접 글로 정리해 보기.

### 단계 4: 프롬프트 커스터마이징

`VIDEO\_PROMPT` 등의 분석 프롬프트를 자기 연구 주제에 맞게 수정해 보기. 예:

* 광고 분석 전공: "광고가 사용한 설득 기법 분류" 항목 추가
* 정치 보도 분석: "프레이밍 유형(전략 프레임 vs 이슈 프레임)" 항목 추가
* 영화 분석: "감독의 화면 구성 스타일" 항목 추가

### 단계 5: 자동화 파이프라인 구축

* 폴더에 들어 있는 모든 영상을 차례로 분석해 결과를 CSV/JSON으로 저장
* 같은 YouTube 영상을 5번 분석해 응답 안정성(consistency) 측정
* 무료 쿼터 안에서 안전하게 동작하도록 `time.sleep(5)` 와 재시도 로직 추가

\---

## 부록: 모달리티별 part 형식 한눈에 보기

```python
# 텍스트
{"text": "분석해 주세요"}

# 이미지/PDF/오디오/짧은 영상 (인라인)
{
    "inline\_data": {
        "mime\_type": "image/jpeg",          # 모달리티에 맞춰 변경
        "data": "<base64 인코딩된 바이트>"
    }
}

# YouTube URL (또는 File API URI)
{
    "file\_data": {
        "file\_uri": "https://www.youtube.com/watch?v=..."
        # YouTube는 mime\_type 불필요
    }
}
```

**한 turn에 여러 part를 함께 넣어 멀티모달 분석**도 가능합니다:

```python
parts = \[
    {"text": "이 텍스트와 이미지를 비교 분석하세요."},
    {"inline\_data": {"mime\_type": "text/plain", "data": text\_b64}},
    {"inline\_data": {"mime\_type": "image/jpeg", "data": image\_b64}},
]
```

이 패턴이 바로 멀티모달 LLM의 본질입니다.

\---

*작성일: 2026* · *모델 정보는 시간이 지나면서 변할 수 있습니다. 최신 정보는* [*Google AI 공식 문서*](https://ai.google.dev/gemini-api/docs)*를 확인하세요.*

