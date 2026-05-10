"""
═══════════════════════════════════════════════════════════════════
글로벌 뉴스 Top 5 브리핑: Gemini + 외신 RSS
                                             
═══════════════════════════════════════════════════════════════════

[무엇을 하는 코드인가]
  ① 세계 주요 외신 9개 매체의 RSS에서 최근 헤드라인을 모은다
  ② Gemini에게 "국제뉴스 5대 가치 기준"으로 평가시켜 Top 5 선정
  ③ 선정 이유 + 한국 독자 관점 요약을 한국어로 출력

[국제뉴스 5대 가치 기준 — 시스템 프롬프트에 그대로 사용]
  ① 한국 관련성   : 한국의 정치·경제·안보·사회·문화에 직접 영향
                   (예: 북핵, 미중 갈등, 반도체 공급망, 한일관계)
  ② 세계 영향성   : 국제 질서·경제·정치·인류 보편 문제에 파급력
                   (예: 미국 대선, 글로벌 금융위기, 기후위기, AI 패권)
  ③ 유명성·권위성 : 강대국·국제기구·유명인사 등 영향력 큰 행위자
                   (예: 미·중·일 정상, UN/WHO/IMF, 글로벌 CEO)
  ④ 갈등·위기·일탈 : 전쟁·외교 충돌·테러·재난·스캔들
  ⑤ 인간 흥미·자극 : 화제성·드라마성·감동 서사

[준비]
  pip install google-genai python-dotenv feedparser

  .env 파일:
    GEMINI_API_KEY=AIza...   ← https://aistudio.google.com/apikey 무료
"""

import feedparser
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()


# ═══════════════════════════════════════════════════════════════════
# 1. 데이터 소스 — 외신 RSS + Google News RSS
# ═══════════════════════════════════════════════════════════════════
# 두 종류를 합친 이유:
#   (A) 외신 매체 RSS — "이 매체가 오늘 무엇을 표지로 골랐나"
#       편집국의 의도가 반영된 1차 큐레이션. 매체별 프레임 비교에 유용.
#   (B) Google News 검색 RSS — "특정 키워드로 전 세계가 뭐라 하나"
#       매체 선정에 갇히지 않고, 5대 가치 기준 중 ①·④ 등을
#       키워드로 직접 보강.
# ───────────────────────────────────────────────────────────────────

# (A) ✅ 검증된 외신 매체 RSS — 영미·유럽·아시아·중동을 골고루 포함
#     각 매체의 시각·논조가 달라야 "지역 편향"과 "이념 편향"이 줄어듦.
MEDIA_FEEDS = [
    # 英 공영방송, 영어권 최대 국제뉴스 — 중도, 보편적 표준
    ("BBC World",       "https://feeds.bbci.co.uk/news/world/rss.xml"),
    # 英 진보 일간, 탐사보도·기후·인권 보도에 강함
    ("Guardian World",  "https://www.theguardian.com/world/rss"),
    # 美 권위지, 외교·국제정치 분석 깊이 (영향력 척도)
    ("NYT World",       "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    # 카타르 본사, 중동·아프리카·글로벌 사우스 시각의 대표
    ("Al Jazeera",      "https://www.aljazeera.com/xml/rss/all.xml"),
    # 美 공영 라디오, 차분한 해설·맥락 분석에 강점
    ("NPR",             "https://feeds.npr.org/1001/rss.xml"),
    # 獨 공영 국제방송, EU 내부 시각·30개 언어 송출
    ("Deutsche Welle",  "https://rss.dw.com/rdf/rss-en-all"),
    # 佛 국제방송, 프랑스·아프리카 프랑스어권 시각
    ("France 24",       "https://www.france24.com/en/rss"),
    # 홍콩 영자지, 중국 본토·아시아 이슈 1차 소스
    ("SCMP (HK)",       "https://www.scmp.com/rss/91/feed"),
    # 유엔 공식, 국제기구·평화·인권·개발 의제 (권위 출처)
    ("UN News",         "https://news.un.org/feed/subscribe/en/news/all/rss.xml"),
]

# (B) Google News 검색 — 키워드를 5대 가치 기준에 맞춰 전략적으로 설계
#     URL 형식:
#       https://news.google.com/rss/search?q={키워드}&hl=en&gl=US&ceid=US:en
#     hl/gl/ceid를 ko-KR로 바꾸면 한국어 결과가 나옴 (지금은 외신용 영문)
GOOGLE_QUERIES = [
    # ① 한국 관련성 보강 — 외신이 한국을 어떻게 보도하나
    ("Google: Korea",        "South Korea OR Korean"),
    # ④ 갈등·위기 보강 — 분쟁·위기 관련 외신 헤드라인
    ("Google: 분쟁",         "war OR crisis OR conflict"),
    # ② 세계 영향성 보강 — 글로벌 거시 이슈
    ("Google: 글로벌이슈",   "global OR international"),
]

def google_news_url(query: str) -> str:
    """Google News 검색 RSS URL 생성 (영문 결과)."""
    from urllib.parse import quote_plus
    return (f"https://news.google.com/rss/search?"
            f"q={quote_plus(query)}&hl=en&gl=US&ceid=US:en")

# 두 소스를 하나의 FEEDS 리스트로 통합 — 이후 처리는 동일
FEEDS = MEDIA_FEEDS + [
    (label, google_news_url(q)) for label, q in GOOGLE_QUERIES
]

# 소스당 가져올 최근 헤드라인 수.
# 12개 소스 × 8건 = 약 96건 → Gemini 한 번 호출로 처리 가능.
N_PER_FEED = 8


# ═══════════════════════════════════════════════════════════════════
# 2. RSS 수집 함수
# ═══════════════════════════════════════════════════════════════════

def collect_headlines() -> list[dict]:
    """모든 매체의 RSS를 순서대로 가져와 헤드라인 목록을 만든다.

    동기(synchronous) 방식 — 9개 매체면 5~10초 정도 걸림.
    더 빨리 만들고 싶으면 asyncio + httpx로 병렬화 가능 (RSS_Guide §9-3).
    """
    items = []
    for outlet, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            taken = 0
            for entry in feed.entries[:N_PER_FEED]:
                items.append({
                    "outlet":    outlet,
                    "title":     entry.get("title", "")[:200],
                    # 일부 매체는 summary가 길거나 HTML — 300자로 잘라 절약
                    "summary":   (entry.get("summary", "") or "")[:300],
                    "link":      entry.get("link", ""),
                    "published": entry.get("published", ""),
                })
                taken += 1
            print(f"  ✓ {outlet:20s} {taken}건")
        except Exception as e:
            print(f"  ✗ {outlet:20s} 실패: {e}")
    return items


# ═══════════════════════════════════════════════════════════════════
# 3. Gemini 프롬프트 — 5대 뉴스가치 기준 + 출력 형식
# ═══════════════════════════════════════════════════════════════════
# 핵심 설계:
#   - "역할(에디터)" 부여 → 모델이 진지하게 판단하도록
#   - 5대 기준에 구체 예시 포함 → 모델이 같은 기준을 일관되게 적용
#   - 출력 형식 고정 → 결과가 학생 보기 좋게 정렬됨
#   - "중복 회피" 명시 → 같은 사건 여러 매체 보도 시 1건만 선택
# ───────────────────────────────────────────────────────────────────

PROMPT = """당신은 한국 종합지의 국제뉴스 데스크 에디터입니다.
오늘 들어온 외신 헤드라인 중에서, 한국 독자에게 알릴 가치가 가장
큰 뉴스 5건을 선정하고 한국어로 브리핑해 주세요.

[국제뉴스 5대 가치 기준 — 종합적으로 판단]
① 한국 관련성:
   한국의 정치·경제·안보·사회·문화에 직접 영향을 주는가?
   (예: 북핵, 미중 갈등, 반도체 공급망, 한일관계, K-콘텐츠 해외 평가)

② 세계 영향성:
   국제 질서·경제·정치·기후·인류 보편 문제에 파급력이 큰가?
   (예: 미국 대선, 글로벌 금융위기, 기후위기, 팬데믹, AI 패권 경쟁)

③ 유명성·권위성:
   강대국·국제기구·세계적 유명인사 등 영향력 큰 행위자가 관련됐는가?
   (예: 미·중·일·EU 정상, UN/WHO/IMF, 글로벌 빅테크 CEO)

④ 갈등·위기·일탈성:
   전쟁·외교 충돌·테러·쿠데타·대형 재난·정치 스캔들 등 정상에서 벗어난 사건인가?

⑤ 인간 흥미·자극성:
   감동·충격·드라마·기이함 등 감정 몰입을 유발하는 요소가 있는가?

[선정 규칙]
- 위 5개 기준에 가중치 두지 말고 종합 판단. 적용된 기준은 명시.
- 같은 사건을 여러 매체가 보도한 경우 가장 정보가 풍부한 1건만 선택
  (중복 피하고 다양성 확보).
- 가십·연예성 단신은 ⑤만 강해도 제외 — 최소 2개 기준 부합해야 선정.
- 한국 관련성이 높은 사건은 우선순위.

[출력 형식 — 반드시 이 형식 그대로]
=== 오늘의 글로벌 뉴스 Top 5 ===

1. [매체명] 제목의 한국어 번역
   ▸ 적용 기준: ① 한국 관련성 (강), ④ 갈등·위기 (중)
   ▸ 한 줄 요지: 기사가 다루는 핵심 사실 1문장
   ▸ 왜 중요한가: 한국 독자 관점에서 1~2문장 해설
   ▸ 출처: [원문 URL]

(2~5번도 동일 형식)

=== 오늘 외신을 관통하는 흐름 (3줄) ===
- ...
- ...
- ...

[헤드라인 목록]
"""


# ═══════════════════════════════════════════════════════════════════
# 4. Gemini 호출 — 한 번에 평가 + 선정 + 요약
# ═══════════════════════════════════════════════════════════════════

def rank_and_brief(items: list[dict]) -> str:
    """수집한 헤드라인 전체를 Gemini에 한 번에 넘겨 Top 5 브리핑을 받는다."""
    # LLM이 읽기 좋은 형태로 헤드라인 목록을 합치기
    bundled = "\n".join(
        f"[{i}] ({it['outlet']}) {it['title']}\n"
        f"     요약: {it['summary']}\n"
        f"     링크: {it['link']}"
        for i, it in enumerate(items)
    )

    resp = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=PROMPT + bundled,
        config=types.GenerateContentConfig(
            temperature=0.3,        # 사실 판단 위주 — 낮게
            max_output_tokens=2500, # Top 5 + 흐름 정리에 충분
        ),
    )
    return resp.text


# ═══════════════════════════════════════════════════════════════════
# 메인
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("[1/2] 외신 RSS 수집 중...")
    print("=" * 60)
    headlines = collect_headlines()
    print(f"\n총 {len(headlines)}건 수집 완료.\n")

    if not headlines:
        print("수집된 헤드라인이 없습니다. 네트워크나 피드 URL을 확인하세요.")
        raise SystemExit(1)

    print("=" * 60)
    print("[2/2] Gemini 평가 — 5대 뉴스가치 기준으로 Top 5 선정 중...")
    print("=" * 60)
    print()
    print(rank_and_brief(headlines))

    # 학습 확장 아이디어:
    #   - FEEDS에 본인 관심 매체 추가 (예: NHK World, Reuters via RSSHub)
    #   - 일자별로 결과를 .md 파일로 저장 → 일일 브리핑 아카이브
    #   - cron으로 매일 아침 실행 → Telegram/Slack 봇으로 발송
    #   - 5대 기준에 가중치 슬라이더 추가 (예: 한국 관련성 ×2)
    #   - 매체별 프레임 비교 ("같은 사건을 BBC vs SCMP는 어떻게 다루나")
