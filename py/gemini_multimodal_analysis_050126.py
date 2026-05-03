"""
================================================================================
 Gemini API 멀티모달 분석 실습 (AI미디어코딩 강의용)
 - 모델: Gemini 2.5 Flash-Lite (무료 쿼터)
 - 다루는 모달리티: 텍스트 → 이미지 → PDF → 오디오 → 비디오 → YouTube
================================================================================

📌 학습 목표
   1) HTTP 요청 한 번이 LLM API 호출의 본질임을 이해한다.
   2) JSON "contents" 구조 안에 어떤 modality든 part로 끼워넣을 수 있음을 익힌다.
   3) 텍스트/이미지/PDF/오디오/영상/YouTube 분석을 동일한 패턴으로 수행한다.

📌 무료 쿼터 (2026년 기준, 변동 가능)
   - Gemini 2.5 Flash-Lite: 15 RPM / 1,000 RPD / 250K TPM
   - YouTube 영상 분석: 무료 티어는 하루 총 8시간까지
   - 신용카드 불필요. https://aistudio.google.com/apikey 에서 발급
   - 주의: 무료 티어 입력 데이터는 Google 모델 학습에 사용될 수 있음

📌 설치
   pip install requests python-dotenv
   # PDF, 오디오, 비디오 모두 Gemini가 "네이티브"로 이해하므로
   # PyPDF2, pydub, opencv 같은 별도 라이브러리 필요 없음
   # (샘플 파일 생성 스크립트 _make_samples.py 에는 Pillow 추가 필요)
   #   pip install Pillow

📌 API 키 설정 (.env 파일에 한 줄 추가)
   GEMINI_API_KEY="AIza..."
   # 키 발급: https://aistudio.google.com/apikey
"""

# ════════════════════════════════════════════════════════════════════════════
# 0. 환경 설정 — 모든 코드의 출발점
# ════════════════════════════════════════════════════════════════════════════
#
# LLM API를 부른다는 것은 본질적으로 "특정 URL에 JSON을 POST하는 것"입니다.
# 여기서는 Python 표준 라이브러리 + requests 만으로 그 본질을 직접 다룹니다.
# (google-genai SDK도 있지만, SDK는 내부적으로 결국 같은 HTTP 요청을 보냅니다.)

import os                    # 환경변수에서 API 키 읽기
import json                  # 응답 JSON 보기 좋게 출력하기
import base64                # 바이너리 파일을 텍스트로 인코딩 (이미지/오디오/비디오/PDF)
import requests              # pip install requests
from pathlib import Path     # 파일 경로 다루기 (확장자 추출 등)
from dotenv import load_dotenv   # pip install python-dotenv

# ── .env 파일 로드 ──────────────────────────────────────────────────────────
# 스크립트와 같은 디렉터리(또는 상위)의 .env 파일을 자동으로 읽어
# os.environ 에 주입합니다. .env 파일 예시:
#   GEMINI_API_KEY="AIzaSy..."
load_dotenv()

# ── API 키 ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    raise RuntimeError(
        ".env 파일에 GEMINI_API_KEY=AIza... 를 추가하거나\n"
        "환경변수로 직접 설정하세요.\n"
        "키 발급: https://aistudio.google.com/apikey"
    )

# ── 모델 / 엔드포인트 ───────────────────────────────────────────────────────
# Gemini API 엔드포인트는 다음 형식입니다:
#   https://generativelanguage.googleapis.com/v1beta/models/{모델명}:{메서드}
# 우리가 부를 메서드는 텍스트를 생성하는 "generateContent" 입니다.
MODEL = "gemini-2.5-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


# ════════════════════════════════════════════════════════════════════════════
# 1. 공통 호출 함수 — 이 한 함수만 이해하면 나머지는 응용일 뿐
# ════════════════════════════════════════════════════════════════════════════

def call_gemini(parts: list, max_tokens: int = 4096, temperature: float = 0.7) -> str:
    """
    Gemini API를 호출하는 핵심 함수.

    Args:
        parts: 모델에 보낼 입력 조각들의 리스트.
               각 part는 dict이고, 다음 중 하나의 형태를 가집니다.
                 - {"text": "..."}                            텍스트
                 - {"inline_data": {"mime_type": "...", "data": "<base64>"}}  파일 임베딩
                 - {"file_data": {"file_uri": "..."}}         원격 파일/YouTube URL
        max_tokens: 모델이 생성할 최대 토큰 수.
        temperature: 0에 가까울수록 결정적, 1에 가까울수록 다양/창의적.

    Returns:
        모델이 생성한 텍스트 응답.

    Gemini가 받는 JSON의 구조는 다음과 같습니다:
        {
          "contents": [ { "parts": [ <part1>, <part2>, ... ] } ],
          "generationConfig": { ... }
        }
    여기서 contents는 대화 턴의 배열이고, parts는 한 턴 안의 입력 조각들입니다.
    멀티모달이란 결국 한 turn(=하나의 contents)에 여러 종류의 part를 함께 넣는 것!
    """
    # ── 요청 본문(payload) 구성 ──────────────────────────────────────────
    payload = {
        "contents": [
            {"parts": parts}     # 단일 턴: parts 안에 텍스트·이미지·PDF·... 자유롭게
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
            "topP": 0.9,         # nucleus sampling (다양성 조절)
            "topK": 40,          # top-k sampling (다양성 조절, 0이면 미적용)
            "presencePenalty": 0.0, # 새로운 주제 언급 유도 (음수는 기존 주제 반복 유도)
            "frequencyPenalty": 0.0, # 동일 표현 반복 억제 (음수는 반복 유도)   
            "candidateCount": 1,   # 응답 후보 수 (1이면 가장 확률 높은 답변 하나만)
         },
    }

    # ── HTTP POST 요청 ──────────────────────────────────────────────────
    # API 키는 헤더(x-goog-api-key)에 넣는 것이 최신 권장 방식입니다.
    # (URL의 ?key= 방식보다 로그·캐시에 노출될 위험이 작음)
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=180)

    # 에러 발생 시 본문도 함께 보여주면 디버깅에 도움이 됩니다.
    if not response.ok:
        raise RuntimeError(
            f"[API 오류 {response.status_code}] {response.text[:500]}"
        )
    result = response.json()

    # ── 응답 파싱 ────────────────────────────────────────────────────────
    # 정상 응답 구조:
    #   { "candidates": [ { "content": { "parts": [ {"text": "..."} ] } } ] }
    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        # 안전 필터·쿼터 초과 등으로 candidates가 비는 경우가 있습니다.
        return f"[응답 파싱 실패]\n{json.dumps(result, ensure_ascii=False, indent=2)}"


# ════════════════════════════════════════════════════════════════════════════
# 2. 작은 도우미 함수 — 파일을 base64 텍스트로 바꾸기
# ════════════════════════════════════════════════════════════════════════════
#
# Gemini API는 JSON으로 통신합니다. JSON 안에 이미지·오디오·비디오 같은
# "바이너리"를 직접 넣을 수 없기 때문에, 우리는 base64라는 텍스트 인코딩으로
# 바꿔서 넣어줍니다. base64는 0/1 비트 묶음을 64개의 ASCII 글자로 표현합니다.

def file_to_base64(filepath: str) -> str:
    """파일을 읽어 base64 문자열로 반환합니다."""
    with open(filepath, "rb") as f:        # rb: 텍스트가 아니라 바이너리로 읽기
        return base64.b64encode(f.read()).decode("ascii")


def guess_mime_type(filepath: str) -> str:
    """
    파일 확장자만 보고 MIME 타입을 추정합니다.
    MIME 타입은 "이 데이터가 어떤 종류인지"를 알려주는 표식입니다(예: image/jpeg).
    """
    ext = Path(filepath).suffix.lower().lstrip(".")
    mime_table = {
        # 이미지
        "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "webp": "image/webp", "gif": "image/gif", "heic": "image/heic",
        # 문서
        "pdf": "application/pdf",
        # 오디오 (Gemini 지원 형식)
        "mp3": "audio/mpeg", "wav": "audio/wav", "m4a": "audio/mp4",
        "aac": "audio/aac", "flac": "audio/flac", "ogg": "audio/ogg",
        # 비디오 (Gemini 지원 형식)
        "mp4": "video/mp4", "mov": "video/mov", "avi": "video/avi",
        "webm": "video/webm", "mkv": "video/x-matroska",
    }
    if ext not in mime_table:
        raise ValueError(f"지원하지 않는 확장자: .{ext}")
    return mime_table[ext]


# ════════════════════════════════════════════════════════════════════════════
# 3. 텍스트 분석 — 가장 단순한 1-modal부터
# ════════════════════════════════════════════════════════════════════════════

def analyze_text(text: str) -> str:
    """
    텍스트를 9개 차원으로 깊이 있게 분석합니다.

    프롬프트 엔지니어링 포인트:
      ① 역할 부여  - "당신은 ~ 전문가입니다"
      ② 작업 명시  - "다음 9가지 항목으로 분석"
      ③ 형식 고정  - 각 항목 번호와 제목을 명시
      ④ 언어 지정  - "한국어로 작성"
      ⑤ 입력 분리  - 분석할 본문을 \"\"\"(doc string 표시)로 감싸 모델 지시문과 분리
    """
    prompt = f"""당신은 미디어 텍스트 분석 전문가입니다.
아래 텍스트를 다음 9가지 항목으로 깊이 있게 분석해 주세요.
각 항목은 반드시 포함하고, 한국어로 작성하세요.

## 분석 항목

1. **전체 요약** (3줄 이내 핵심 요약)
2. **핵심 키워드** (5~10개, 빈도·중요도 기준)
3. **등장인물 분석**
   - 이름/호칭, 역할, 주요 발화(직·간접 인용), 핵심 주장, 주요 행위
4. **배경·장소 분석**
   - 시간적 배경, 공간적 배경, 분위기에 미치는 영향
5. **인물 간 관계 분석**
   - 협력/갈등/상하/대립 등 관계 유형과 근거
6. **분위기·감정 분석**
   - 전체 톤, 감정 변화 흐름, 긴장·이완 포인트
7. **서사 구조·플롯 전개** 
   - 발단-전개-위기-절정-결말 또는 논증 흐름
8. **수사적 전략·설득 기법** 
   - 비유, 반복, 대조, 호소(logos/pathos/ethos) 등
9. **시대적·사회적 맥락 추론**
   - 텍스트가 반영하는 사회 이슈, 가치관, 이데올로기

---
분석 대상 텍스트:
\"\"\"
{text}
\"\"\"
"""
    # 텍스트만 보낼 때는 part가 1개입니다. 가장 단순한 케이스.
    return call_gemini(parts=[{"text": prompt}])


def analyze_text_file(filepath: str) -> str:
    """
    .txt 파일을 읽어 텍스트 분석을 수행합니다.
    (PDF는 별도 함수 analyze_pdf()를 사용하세요 — 네이티브 처리가 가능합니다.)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"📄 텍스트 파일 로드: {filepath} ({len(text):,}자)")
    return analyze_text(text)


# ════════════════════════════════════════════════════════════════════════════
# 4. 이미지 분석 — 정지 화면(2D 공간 정보)
# ════════════════════════════════════════════════════════════════════════════
#
# 이미지를 모델에 보내려면, 이미지 바이트를 base64로 인코딩한 뒤
# part = {"inline_data": {"mime_type": "image/jpeg", "data": "<base64>"}}
# 형태로 prompt part와 함께 contents에 넣으면 됩니다.

# 이미지·PDF·오디오·영상 모두에 재사용할 동일한 분석 프롬프트(이미지용 9차원).
IMAGE_PROMPT = """당신은 미디어 이미지 분석 전문가입니다.
이 이미지를 다음 8가지 항목으로 깊이 있게 분석해 주세요. 한국어로 작성하세요.

## 기본 분석
1. **전체 장면 묘사** — 이미지에 무엇이 보이는지 객관적 서술
2. **등장인물 분석** — 인물 수, 외모 특징, 표정, 자세, 복장, 추정 직업/역할
3. **배경·장소 분석** — 실내/실외, 도시/자연, 시간대, 날씨, 공간 특성
4. **인물 간 관계 분석** — 거리, 시선, 신체 언어로 추론되는 관계

## 심층 분석
5. **분위기·감정 분석** — 이미지 전체 톤, 인물들의 감정 상태, 긴장감/편안함
6. **시각적 구성 분석**  — 구도(삼분법, 대칭 등), 시선 유도선, 전경/중경/후경
7. **색채·조명 분석**  — 주요 색상, 명암 대비, 조명 방향, 색온도, 컬러 심리
8. **기호학적 해석**  — 상징적 요소, 문화적 코드, 내포된 메시지, 이데올로기
"""


def analyze_image_file(filepath: str) -> str:
    """로컬 이미지 파일(.jpg, .png, .webp, .gif, .heic) 분석."""
    parts = [
        {"text": IMAGE_PROMPT},
        {
            "inline_data": {
                "mime_type": guess_mime_type(filepath),
                "data": file_to_base64(filepath),
            }
        },
    ]
    return call_gemini(parts)


def analyze_image_url(image_url: str) -> str:
    """
    이미지 URL을 다운로드해서 분석합니다.
    (Gemini의 file_data 방식은 PDF·오디오·비디오·YouTube에는 동작하지만,
     일반 이미지 URL은 우리가 직접 다운로드해 inline_data로 넣는 것이 안정적입니다.)
    """
    headers = {"User-Agent": "Mozilla/5.0"}     # 일부 서버가 봇 차단을 회피
    resp = requests.get(image_url, headers=headers, timeout=30)
    resp.raise_for_status()

    # Content-Type 헤더에서 MIME 타입을 받습니다(예: "image/jpeg").
    mime_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
    img_b64 = base64.b64encode(resp.content).decode("ascii")

    parts = [
        {"text": IMAGE_PROMPT},
        {"inline_data": {"mime_type": mime_type, "data": img_b64}},
    ]
    return call_gemini(parts)


# ════════════════════════════════════════════════════════════════════════════
# 5. PDF 분석 — Gemini는 PDF를 "네이티브"로 이해합니다!
# ════════════════════════════════════════════════════════════════════════════
#
# 핵심 포인트:
#   • PyPDF2, pdfplumber 같은 외부 패키지가 필요 없습니다.
#   • Gemini는 PDF를 페이지별 "비전(이미지)"으로 이해하면서 동시에 텍스트도 읽습니다.
#     → 표·차트·레이아웃까지 함께 인식 가능 (단순 텍스트 추출이 아님)
#   • 한 페이지 ≈ 258 토큰. 1000 페이지까지 처리 가능.
#   • 인라인 전송(=base64 본문 첨부)은 ~20 MB 권장. 더 큰 파일은 File API 필요.

PDF_PROMPT = """당신은 미디어 콘텐츠 및 디자인 분석 전문가입니다.
이 PDF 문서 전체를 다음 항목으로 종합 분석해 주세요. 한국어로 작성하세요.

## 콘텐츠 분석
1. **전체 요약** (핵심 메시지 3줄)
2. **핵심 키워드** (5~10개)
3. **등장인물/주체** — 언급된 인물·조직의 역할과 주장
4. **배경·맥락** — 시간적·공간적·사회적 맥락
5. **논증 구조** — 주장-근거-결론의 흐름

## 시각·디자인 분석 
6. **레이아웃·정보 위계** — 페이지 구성, 단 배치, 시선 흐름
7. **타이포그래피·컬러** — 폰트 스타일, 색상 활용, 시각적 일관성
8. **그래픽 요소** — 도표, 사진, 아이콘, 인포그래픽 효과
9. **전체 디자인 품질 평가** — 전문성, 가독성, 목적 적합성
"""


def analyze_pdf(filepath: str) -> str:
    """
    PDF 파일을 통째로 Gemini에 보내 텍스트+시각 요소를 한 번에 분석합니다.
    20MB 이하 권장. 그보다 큰 파일은 File API(별도 업로드)를 써야 합니다.
    """
    parts = [
        {"text": PDF_PROMPT},
        {
            "inline_data": {
                "mime_type": "application/pdf",
                "data": file_to_base64(filepath),
            }
        },
    ]
    # PDF는 페이지가 많을수록 응답 길이가 길어질 수 있으므로 토큰 한도 ↑
    return call_gemini(parts, max_tokens=8192)


# ════════════════════════════════════════════════════════════════════════════
# 6. 오디오 분석 — 시간 축이 추가된 1D 신호
# ════════════════════════════════════════════════════════════════════════════
#
# Gemini 2.5 Flash-Lite는 오디오를 네이티브로 이해합니다(Whisper 등 별도 모델 불필요).
# 음성 인식(STT)뿐 아니라 음악·잡음·화자 감정·억양까지 함께 분석할 수 있습니다.
#
# 무료 티어에서 권장하는 길이:
#   • 인라인 전송 한도(~20 MB)에 맞추려면 MP3 128 kbps 기준 ≈ 20 분 정도 가능
#   • 그러나 학습·실습 용도에서는 1~5 분짜리 오디오를 추천 (응답·토큰 효율)
#
# 지원 형식: mp3, wav, m4a, aac, flac, ogg

AUDIO_PROMPT = """당신은 미디어 오디오 분석 전문가입니다.
이 오디오를 다음 항목으로 깊이 있게 분석해 주세요. 한국어로 작성하세요.

## 기본 분석
1. **오디오 종류** — 인터뷰/뉴스/연설/팟캐스트/음악/광고 등 장르 분류
2. **전체 전사(Transcript)** — 들리는 말을 한국어로 정확히 옮기기
   (가능한 경우 [00:15] 같은 시간 표시 포함)
3. **핵심 요약** (3줄 이내)
4. **핵심 키워드** (5~10개)

## 심층 분석
5. **화자 분석**  — 화자 수, 추정 성별/연령대, 역할(진행자/패널/일반인 등)
6. **발화 톤·감정 분석**  — 어조(차분/격앙), 감정 변화, 강조점
7. **수사적 전략**  — 반복, 비유, 호소(logos/pathos/ethos), 설득 기법
8. **배경음·음향 효과**  — 배경음악, 잡음, 환경음이 메시지에 미치는 영향
9. **사회·문화적 맥락 추론**  — 어떤 청중·시대·이슈를 겨냥한 발화인가
"""


def analyze_audio_file(filepath: str) -> str:
    """로컬 오디오 파일(.mp3, .wav, .m4a 등) 분석. 20MB 이하 권장."""
    parts = [
        {"text": AUDIO_PROMPT},
        {
            "inline_data": {
                "mime_type": guess_mime_type(filepath),
                "data": file_to_base64(filepath),
            }
        },
    ]
    return call_gemini(parts, max_tokens=8192)


# ════════════════════════════════════════════════════════════════════════════
# 7. 비디오 분석(로컬 파일) — 이미지(공간) + 오디오(시간)
# ════════════════════════════════════════════════════════════════════════════
#
# Gemini는 비디오를 1초당 1프레임(1 FPS)으로 샘플링하면서 동시에 오디오 트랙도
# 분석합니다. 즉, 영상의 시각적 변화 + 음성·BGM을 종합적으로 파악합니다.
#
# 인라인 전송 제한:
#   • 파일 크기 < 20 MB
#   • 영상 길이 ≈ 1분 이내
#   → 그보다 길면 File API로 별도 업로드해야 하지만, 강의·실습 단계에서는
#     30초~1분짜리 짧은 클립으로 충분히 핵심 개념을 익힐 수 있습니다.
#   → 더 긴 영상은 8번 항목(YouTube URL)을 활용하세요.

VIDEO_PROMPT = """당신은 미디어 영상 분석 전문가입니다.
이 영상을 시각·청각·시간 전개를 모두 고려하여 다음 항목으로 분석해 주세요.
한국어로 작성하고, 가능한 곳에 [MM:SS] 형식의 타임스탬프를 표기하세요.

## 콘텐츠 분석
1. **장르 분류** — 뉴스/광고/뮤직비디오/브이로그/다큐/드라마 등
2. **전체 요약** (3줄 이내, 핵심 사건 위주)
3. **씬(scene) 분할** — 주요 장면을 [MM:SS] 단위로 나누고 각 장면 묘사
4. **핵심 발화 전사** — 중요한 대사·내레이션을 시간대와 함께 옮기기

## 시각·청각 분석
5. **등장인물·배경** — 등장 인물 수, 인상 착의, 장소·시간대
6. **시각 연출**  — 카메라 앵글, 컷 전환, 색채, 조명, 자막 활용
7. **사운드 디자인**  — 배경음악 분위기, 효과음, 음성 톤
8. **편집 리듬**  — 컷 빈도, 속도감, 긴장-이완 흐름

## 메시지 분석
9. **주제·메시지** — 영상이 전달하려는 핵심 가치/주장
10. **수사적 전략** — 시청자 설득·감정 유도 기법
11. **사회·문화적 맥락** — 어떤 청중을 겨냥했고, 어떤 가치관을 반영하는가
"""


def analyze_video_file(filepath: str) -> str:
    """
    로컬 비디오 파일 분석.
    ⚠ 인라인 전송 한도: 약 20MB / 약 1분 이내. 그 이상은 YouTube URL 또는 File API 사용.
    """
    parts = [
        {"text": VIDEO_PROMPT},
        {
            "inline_data": {
                "mime_type": guess_mime_type(filepath),
                "data": file_to_base64(filepath),
            }
        },
    ]
    return call_gemini(parts, max_tokens=8192)


# ════════════════════════════════════════════════════════════════════════════
# 8. YouTube URL 분석 — 다운로드 없이 URL 한 줄로!
# ════════════════════════════════════════════════════════════════════════════
#
# Gemini API의 매우 강력한 기능: YouTube 링크만 넘기면 모델이 알아서 가져와 분석!
#   → 비디오 파일을 다운로드하거나 base64 인코딩할 필요 자체가 없음
#   → 사용 방식: part = {"file_data": {"file_uri": "<YouTube URL>"}}
#
# 무료 티어 제한 (2026년 기준)
#   • 하루 총 8시간(YouTube 기준 누적 영상 길이) 분석 가능
#   • 공개(public) 영상만 가능. 미등록(unlisted)·비공개(private) 불가
#   • 권장 영상 길이: 강의·실습 시 5~10분 정도가 적절
#       - 5분 영상이면 하루 약 96회, 10분이면 48회 분석 가능 (8시간/길이)
#       - 너무 긴 영상은 토큰을 많이 소모해 응답 속도가 느려짐
#   • 동일 영상을 여러 번 분석할 예정이면 Context Caching 사용을 고려

def analyze_youtube(youtube_url: str, custom_prompt: str | None = None) -> str:
    """
    YouTube 영상을 URL만으로 분석합니다.

    Args:
        youtube_url: 공개된 YouTube 영상 URL (예: https://www.youtube.com/watch?v=XXX)
        custom_prompt: 분석 프롬프트를 직접 지정하고 싶을 때만 입력.
                       지정하지 않으면 위의 VIDEO_PROMPT(11개 차원)가 사용됩니다.

    Tip: 강의 실습용으로는 5~10분짜리 짧고 메시지가 분명한 영상을 추천합니다.
         예) 뉴스 클립, 광고, TED-Ed, 정치 연설 일부, 뮤직비디오 등.
    """
    prompt = custom_prompt or VIDEO_PROMPT
    parts = [
        {"text": prompt},
        # ⭐ 핵심: inline_data가 아니라 file_data + file_uri 를 사용한다는 점!
        {"file_data": {"file_uri": youtube_url}},
    ]
    return call_gemini(parts, max_tokens=8192)


# ════════════════════════════════════════════════════════════════════════════
# 9. 실행 예시 — 필요한 부분의 주석을 풀고 실행해 보세요
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("  Gemini 2.5 Flash-Lite 멀티모달 분석 실습")
    print("  텍스트 → 이미지 → PDF → 오디오 → 비디오 → YouTube")
    print("=" * 70)

    # ── 1) 텍스트 직접 입력 분석 ─────────────────────────────────────────
    sample_text = """
    서울 광화문 광장에서 수천 명의 시민들이 모여 기후 위기 대응을 촉구하는
    집회를 열었다. 참가자들은 "지구를 살려라", "탄소 중립 지금 당장"이라는
    구호를 외치며 종로 일대를 행진했다. 환경단체 대표 김모 씨는 "정부의
    탄소 감축 목표가 국제 기준에 한참 못 미친다"고 비판하면서, "2030년까지
    실질적인 감축 로드맵을 제시하라"고 요구했다. 경찰은 만일의 사태에
    대비해 1,500명의 병력을 배치했으나, 집회는 평화롭게 마무리되었다.
    집회 현장 인근 카페 주인 이모 씨는 "주말 장사에 타격이 크다"며
    불만을 토로했고, 지나가던 직장인 박모 씨는 "불편하지만 의미 있는
    목소리라고 생각한다"며 지지를 표했다.
    """

    print("\n📝 [1] 텍스트 분석")
    print(analyze_text(sample_text))

    # ── 2) 텍스트 파일(.txt) 분석 ────────────────────────────────────────
    #print("\n📄 [2] 텍스트 파일 분석")
    #print(analyze_text_file("gemini_multimodal_src/기후집회.txt"))

    # ── 3) 이미지 파일 분석 ──────────────────────────────────────────────
    #print("\n🖼️ [3] 이미지 파일 분석")
    #print(analyze_image_file("gemini_multimodal_src/기후집회.jpg"))

    # ── 4) 이미지 URL 분석 ───────────────────────────────────────────────
    #print("\n🌐 [4] 이미지 URL 분석")
    #print(analyze_image_url("https://img4.yna.co.kr/etc/inner/KR/2025/09/27/AKR20250927045100004_01_i_P4.jpg"))

    # ── 5) PDF 분석 (네이티브 — 외부 라이브러리 불필요) ─────────────────
    #print("\n📑 [5] PDF 분석")
    #print(analyze_pdf("gemini_multimodal_src/기후집회.pdf"))

    # ── 6) 오디오 파일 분석 ──────────────────────────────────────────────
    #print("\n🎧 [6] 오디오 파일 분석")
    #print(analyze_audio_file("gemini_multimodal_src/기후집회.mp3"))

    # ── 7) 로컬 비디오 파일 분석 (1분/20MB 이하 권장) ────────────────────
    # 자신의 영상을 gemini_multimodal_src/ 에 넣고 경로 수정
    # print(analyze_video_file("gemini_multimodal_src/~예제필요~.mp4"))

    # ── 8) YouTube URL 분석 (2~10분 영상 권장) ───────────────────────────
    #print("\n▶️ [8] YouTube 분석")
    #print(analyze_youtube("https://www.youtube.com/watch?v=d3WfmONUH_E"))

    print("\n✅ 분석 완료!")
    print(f"   모델 : {MODEL}")
    print(f"   무료 쿼터 : 15 RPM / 1,000 RPD / 250K TPM")
    print(f"   YouTube 무료 한도 : 하루 누적 8시간")
