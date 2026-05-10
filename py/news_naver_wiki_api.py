"""
═══════════════════════════════════════════════════════════════════
뉴스-정보 분석: Gemini + API Function Calling(네이버 검색 + Wikipedia)
                                              
═══════════════════════════════════════════════════════════════════

이 파일은 한국어 정보·뉴스 검색에 유요한 두 API를 사용:

  1) Wikipedia (한국어판)  — 주제의 "정의·배경·역사" 같은 정적 지식
  2) 네이버 검색          — "지금 한국에서 뭐라고 하나" (뉴스·블로그)

[원리 — Function Calling]
  도구 함수만 정의하고 Gemini에게 tools=[...]로 넘기면, 모델이 질문을 보고 
  어느 함수를 어떤 인자로 호출할지 자동으로 결정하고, 질문도 검색어로 자동 변환.

[준비]
  pip install google-genai python-dotenv requests

  .env 파일:
    GEMINI_API_KEY=AIza...           # https://aistudio.google.com/apikey
    NAVER_CLIENT_ID=...              # 아래 절차로 발급
    NAVER_CLIENT_SECRET=...

[네이버 API 키 발급 — 5분]
  1. https://developers.naver.com 접속 → 로그인
  2. 상단 [Application] → [애플리케이션 등록]
  3. 애플리케이션 이름: 아무거나 (예: "수업용")
  4. 사용 API: "검색" 체크 (뉴스/블로그/웹문서/지식iN 모두 자동 포함)
  5. 환경: "WEB 설정" → URL은 "http://localhost" 입력
  6. 등록 후 [Client ID]와 [Client Secret] 복사 → .env에 저장
  → 무료, 일 25,000회 호출 가능 (학생 수업에 충분)

[Wikipedia는?]
  완전 무인증·무료. .env에 따로 설정 필요 없음.
"""

import os
import re
from urllib.parse import quote
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

# True로 바꾸면, Gemini가 어떤 함수를 어떤 검색어로 호출했는지 콘솔에 표시.
# (질문 → 키워드 변환은 Gemini 내부에서 일어나 평소엔 안 보임)
DEBUG = False


# ═══════════════════════════════════════════════════════════════════
# 1. 도구 함수
# ═══════════════════════════════════════════════════════════════════
# Gemini는 함수의 docstring과 타입 힌트를 보고 사용법을 이해한다.
# → docstring은 "언제 / 어떻게" 쓸지 풍부하게 적을 것.
# ───────────────────────────────────────────────────────────────────

def search_wikipedia(query: str, lang: str = "ko") -> str:
    """위키백과에서 주제를 검색하고 본문 요약을 반환한다.

    "이게 뭔지", "역사·정의·배경"을 알아야 할 때 사용.
    실시간 뉴스나 최근 사건은 search_naver를 써라 (위키는 갱신이 느리다).

    Args:
        query: 검색어 (한국어 가능, 예: "한강 작가", "양자컴퓨터")
        lang: 'ko'=한국어 위키, 'en'=영어 위키 (한국어 항목이 빈약하면 영어 시도)

    Returns:
        제목 + 요약 + URL 형태의 텍스트. 항목이 없으면 안내 메시지.
    """
    # 1단계: 검색해서 가장 잘 맞는 페이지 제목 찾기
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    search_params = {
        "action":   "query",
        "list":     "search",
        "srsearch": query,
        "format":   "json",
        "srlimit":  1,
    }
    try:
        resp = (requests.get(search_url, params=search_params, timeout=10)
                .json().get("query", {}).get("search", []))
    except Exception as e:
        return f"위키백과 검색 실패: {e}"

    if not resp:
        return f"'{query}'에 대한 {lang} 위키백과 항목이 없습니다."

    title = resp[0]["title"]

    # 2단계: 해당 페이지의 요약(extract) 가져오기
    summary_url = (f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
                   f"{quote(title)}")
    try:
        s = requests.get(summary_url, timeout=10).json()
    except Exception as e:
        return f"요약 가져오기 실패: {e}"

    return (
        f"제목: {s.get('title', title)}\n"
        f"요약: {s.get('extract', '(요약 없음)')}\n"
        f"URL:  {s.get('content_urls', {}).get('desktop', {}).get('page', '')}"
    )


def search_naver(query: str, kind: str = "news", display: int = 10) -> str:
    """네이버 검색 API (한국 뉴스·블로그·웹문서·지식iN).

    "한국에서 지금 뭐라고 하나", "최근 보도", "여론·반응"이 필요할 때 사용.

    Args:
        query:   검색어 (한국어)
        kind:    'news'   = 한국 언론사 뉴스 (날짜순)
                 'blog'   = 블로그 (날짜순) — 시민·전문가 의견에 유용
                 'webkr'  = 한국어 웹문서
                 'kin'    = 지식iN — Q&A 패턴, 일반인 관심사 파악
        display: 가져올 결과 수 (1~100, 기본 10)

    Returns:
        "제목 / 요약 / 링크" 항목의 목록.
    """
    cid     = os.environ.get("NAVER_CLIENT_ID", "")
    secret  = os.environ.get("NAVER_CLIENT_SECRET", "")
    if not cid or not secret:
        return "NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 미설정 — .env 확인"

    url = f"https://openapi.naver.com/v1/search/{kind}.json"
    headers = {
        "X-Naver-Client-Id":     cid,
        "X-Naver-Client-Secret": secret,
    }
    # 뉴스·블로그·카페는 'date'(최신순) 지원, 나머지는 'sim'(정확도)만
    sort = "date" if kind in ("news", "blog", "cafearticle") else "sim"
    params = {"query": query, "display": display, "sort": sort}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        items = r.json().get("items", [])
    except Exception as e:
        return f"네이버 검색 실패: {e}"

    if not items:
        return "결과 없음"

    # 네이버 응답에는 <b>강조</b> 같은 HTML 태그가 섞여 있어 제거
    strip = lambda s: re.sub(r"<[^>]+>", "", s or "")
    return "\n\n".join(
        f"- {strip(it.get('title', ''))}\n"
        f"  {strip(it.get('description', ''))[:200]}\n"
        f"  {it.get('link', '')}"
        for it in items
    )


# ═══════════════════════════════════════════════════════════════════
# 2. Gemini 호출
# ═══════════════════════════════════════════════════════════════════

SYSTEM = """당신은 정보 수집 분석가입니다.

[행동 규칙 — 반드시 지킬 것]
1) 사용자에게 절대 되묻지 마세요. 질문이 모호하거나 추상적이어도
   가장 합리적으로 해석하여 직접 검색어를 만들고 도구를 호출하세요.
   예: "지방선거가 주식시장에 미칠 영향" → search_naver(query="지방선거 코스피 전망")
       "AI 규제는 어떻게 되나"        → search_naver(query="AI 기본법 규제 동향")
2) 한 질문에 보통 2~4번 도구를 호출해 자료를 충분히 모은 뒤 답하세요.
   - 정의·배경·역사  → search_wikipedia
   - 최근 보도·반응  → search_naver(kind="news")
   - 시민/전문가 의견 → search_naver(kind="blog")
3) 미래·전망·영향 같은 질문도 거부하지 말고, 관련 보도·전문가 분석을
   검색해서 그 내용을 정리해 주세요. (당신의 추측이 아닌, 자료의 인용)
4) 검색 결과가 정말 없을 때만 "자료 부족"이라 답하세요.

[답변 형식 — 한국어]
1. 결론 (1~3문장 핵심)
2. 배경 (Wikipedia 등에서 확인된 정의·맥락)
3. 최근 동향 (네이버 검색에서 확인된 보도/의견 요지)
4. 출처 (참고한 URL 모두 나열)
"""


def ask(question: str) -> str:
    """질문 한 개를 Gemini에게 던진다.
    tools=[함수들]만 넘기면 SDK가 자동으로:
      ① 함수 시그니처를 도구 스키마로 변환
      ② 모델이 호출 결정 → 실제 함수 실행 → 결과 다시 모델에 주입
      ③ 최종 답변까지 한 번에 반환

    ※ 질문을 검색용 키워드로 줄이는 작업도 ②에서 모델이 알아서 한다.
       예: "한강 작가가 누구이고 노벨문학상 수상 이후 무슨 일이 있었나?"
       → search_wikipedia(query="한강 (소설가)")
       → search_naver(query="한강 노벨문학상", kind="news")
       이 변환 과정을 보고 싶으면 파일 상단 DEBUG=True 로 변경.
    """
    resp = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=question,
        config=types.GenerateContentConfig(
            tools=[search_wikipedia, search_naver],
            temperature=0,
            system_instruction=SYSTEM,
        ),
    )

    # DEBUG=True면 Gemini가 호출한 함수와 인자(=변환된 검색어)를 출력
    if DEBUG:
        print("─" * 60)
        print("[디버그] Gemini가 호출한 함수와 인자")
        for turn in resp.automatic_function_calling_history or []:
            for part in turn.parts or []:
                if part.function_call:
                    fc = part.function_call
                    print(f"  🔧 {fc.name}({dict(fc.args)})")
                elif part.function_response:
                    preview = str(part.function_response.response)[:120]
                    print(f"     ↪ {preview}...")
        print("─" * 60)
        print()

    return resp.text


# ═══════════════════════════════════════════════════════════════════
# 메인
# ═══════════════════════════════════════════════════════════════════

EXAMPLES = [
    "한강 작가가 누구이고 노벨문학상 수상 이후 무슨 일이 있었나?",
    "스타링크가 뭐고 한국 진출 상황은 어떤가?",
    "양자컴퓨터가 무엇이고 한국 기업·연구의 최근 진전은?",
    "탄소국경조정제도(CBAM)가 무엇이고 한국 산업에 어떤 영향을 주나?",
    "AI 기본법이 무엇이고 한국에서 어떻게 논의되고 있나?",
]

if __name__ == "__main__":
    print("[예시 질문]")
    for i, q in enumerate(EXAMPLES, 1):
        print(f"  {i}. {q}")
    print()
    user_q = input("질문 (Enter 시 1번): ").strip() or EXAMPLES[0]
    print()
    print(ask(user_q))
