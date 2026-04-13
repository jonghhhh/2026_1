"""
╔══════════════════════════════════════════════════════════╗
║        네이버 검색 API 통합 수집기 (간략 버전)            ║
╚══════════════════════════════════════════════════════════╝

■ 사전 준비 (최초 1회만)
  ─────────────────────────────────────────────────────────
  1) https://developers.naver.com 접속 → 네이버 로그인
  2) 상단 메뉴 [Application] → [애플리케이션 등록]
  3) 애플리케이션 이름: 아무거나 (예: "검색연습")
  4) 사용 API: "검색" 선택
  5) 비로그인 오픈 API 서비스 환경: WEB 선택 → http://localhost 입력
  6) 등록 완료 → Client ID / Client Secret 확인·복사

  7) 이 파일과 같은 폴더에 .env 파일 생성:
     ┌─────────────────────────────────────────────┐
     │ NAVER_CLIENT_ID=여기에_복사한_ID_붙여넣기     │
     │ NAVER_CLIENT_SECRET=여기에_복사한_Secret      │
     └─────────────────────────────────────────────┘

  8) 필요한 패키지 설치 (터미널에서):
     pip install requests python-dotenv pandas openpyxl

■ 사용법 요약 (Jupyter에서 셀 단위로 실행)
  ─────────────────────────────────────────────────────────
  ① 단건 검색 (결과 1페이지)
     data = search("news", "인공지능")
     data = search("blog", "데이터분석", display=10, sort="date")

  ② 대량 수집 (페이지 자동 넘김)
     items = search_many("news", "인공지능", max_items=500)

  ③ 파일 저장 (확장자로 형식 자동 판별)
     save(items, "결과.json")     # JSON
     save(items, "결과.csv")      # CSV
     save(items, "결과.xlsx")     # Excel

■ 지원 엔드포인트 7종 (endpoint 파라미터에 넣을 값)
  ─────────────────────────────────────────────────────────
  "news"         뉴스          sort: sim(정확도) / date(최신)
  "blog"         블로그        sort: sim / date
  "cafearticle"  카페글        sort: sim / date
  "kin"          지식iN        sort: sim / date / count(답변수) / point(채택)
  "book"         책            sort: sim / date / count(판매량)
  "shop"         쇼핑          sort: sim / date / asc(저가순) / dsc(고가순)
  "local"        지역(장소)    sort: random / comment(리뷰수)

■ 주요 제약
  ─────────────────────────────────────────────────────────
  display : 한 번에 가져올 건수. 최대 100 (local만 최대 5)
  start   : 검색 시작 위치. 최대 1000
  일일 API 호출 한도: 25,000회
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 패키지 불러오기
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import os           # 환경변수 읽기
import re           # 정규표현식 (HTML 태그 제거용)
import json         # JSON 파일 저장
import time         # API 호출 간 대기
import datetime     # 파일명에 타임스탬프 넣기
import requests     # HTTP 요청 보내기 (핵심!)
import pandas as pd # DataFrame → CSV/Excel 변환
from dotenv import load_dotenv  # .env 파일에서 환경변수 읽기


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1단계: 인증 정보 로딩
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
load_dotenv()  # .env 파일의 내용을 환경변수로 등록

CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")      # 발급받은 ID
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")   # 발급받은 Secret

# 인증 정보가 없으면 여기서 중단
if not CLIENT_ID or not CLIENT_SECRET:
    raise EnvironmentError(
        ".env 파일에 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET을 설정하세요."
    )

# 네이버 API는 URL이 아니라 HTTP "헤더"로 인증함
# → 그래서 브라우저 주소창에 URL만 넣으면 작동하지 않음
HEADERS = {
    "X-Naver-Client-Id":     CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET,
}

BASE = "https://openapi.naver.com/v1/search"  # API 기본 주소


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 유틸: HTML 태그 제거
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 네이버 API 응답의 title, description에는
# <b>검색어</b> 같은 HTML 태그가 섞여 옴 → 깨끗이 제거
def strip_html(text):
    """'<b>인공</b>지능' → '인공지능' 으로 변환"""
    if not text:
        return ""
    text = re.sub(r"<.*?>", "", text)   # 모든 HTML 태그 제거
    for old, new in [("&amp;","&"), ("&lt;","<"), ("&gt;",">"),
                     ("&quot;",'"'), ("&#39;","'")]:
        text = text.replace(old, new)   # HTML 특수문자 복원
    return text.strip()


def clean(items):
    """검색 결과 리스트 전체에서 HTML 태그 일괄 제거"""
    return [
        {k: strip_html(v) if isinstance(v, str) else v
         for k, v in item.items()}
        for item in items
    ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 핵심 함수 ①: search() — 1회 호출
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def search(endpoint, query, display=10, start=1, sort="date"):
    """
    네이버 검색 API를 1번 호출하여 결과를 반환합니다.

    [매개변수]
      endpoint : "news" / "blog" / "cafearticle" / "kin" /
                 "book" / "shop" / "local"
      query    : 검색어 (예: "인공지능", "맛집 강남")
      display  : 가져올 건수 (1~100, local은 1~5)
      start    : 검색 시작 위치 (1~1000)
      sort     : 정렬 방식 (엔드포인트별 상이, 위 docstring 참조)

    [반환값]
      dict — {"total":전체건수, "items":[결과1, 결과2, ...], ...}

    [사용 예]
      >>> data = search("news", "인공지능", display=5)
      >>> for item in data["items"]:
      ...     print(strip_html(item["title"]))
    """
    # local은 display 최대 5, 나머지는 100
    if endpoint == "local":
        display = min(display, 5)
        if sort not in ("random", "comment"):
            sort = "random"
    else:
        display = min(display, 100)

    url = f"{BASE}/{endpoint}.json"       # 예: .../search/news.json
    params = {"query": query, "display": display,
              "start": start, "sort": sort}

    # GET 요청 전송 (헤더에 인증 정보 포함)
    resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()   # 에러 시 예외 발생 (401, 429 등)

    return resp.json()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 핵심 함수 ②: search_many() — 페이지 자동 넘김
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def search_many(endpoint, query, max_items=300, sort="date", delay=0.1):
    """
    search()를 반복 호출하여 여러 페이지를 자동으로 수집합니다.

    [매개변수]
      endpoint  : 검색 대상
      query     : 검색어
      max_items : 최대 수집 건수 (기본 300)
      sort      : 정렬 방식
      delay     : 호출 간 대기 초 (기본 0.1초, 429 에러 방지)

    [반환값]
      list[dict] — HTML 태그가 제거된 검색 결과 리스트

    [사용 예]
      >>> items = search_many("news", "인공지능", max_items=500)
      >>> print(f"수집 완료: {len(items)}건")
      >>> save(items, "ai_news.csv")
    """
    page_size = 5 if endpoint == "local" else 100  # 한 페이지 크기
    all_items = []    # 결과 누적
    start = 1         # 시작 위치

    while start <= 1000 and len(all_items) < max_items:
        try:
            data = search(endpoint, query, display=page_size,
                          start=start, sort=sort)
        except requests.exceptions.HTTPError as e:
            # 429 = 호출 한도 초과 → 5초 기다렸다 같은 페이지 재시도
            if e.response is not None and e.response.status_code == 429:
                print("  ⏳ 호출 한도 초과 → 5초 대기 후 재시도...")
                time.sleep(5)
                continue
            raise

        items = data.get("items", [])
        if not items:   # 더 이상 결과 없음
            break

        all_items.extend(items)
        total = data.get("total", 0)

        # 진행 상황 출력
        print(f"  [{start:>4}~{start+len(items)-1:>4}] "
              f"누적 {len(all_items):,}건 / 전체 {total:,}건")

        start += page_size   # 다음 페이지로
        if start > min(total, max_items):
            break
        time.sleep(delay)

    # 초과분 잘라내기 + HTML 태그 제거
    return clean(all_items[:max_items])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 핵심 함수 ③: save() — 파일 저장
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def save(items, filename):
    """
    검색 결과를 파일로 저장합니다. 확장자로 형식 자동 판별.

    [매개변수]
      items    : search() 또는 search_many()의 결과
      filename : 저장 파일명 (.json / .csv / .xlsx)

    [사용 예]
      >>> save(items, "뉴스_인공지능.json")
      >>> save(items, "뉴스_인공지능.csv")
      >>> save(items, "뉴스_인공지능.xlsx")
    """
    if filename.endswith(".json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    elif filename.endswith(".csv"):
        pd.DataFrame(items).to_csv(filename, index=False, encoding="utf-8-sig")
    elif filename.endswith(".xlsx"):
        pd.DataFrame(items).to_excel(filename, index=False, engine="openpyxl")
    else:
        print("⚠ .json / .csv / .xlsx 확장자만 지원합니다.")
        return
    print(f"✅ 저장 완료: {filename} ({len(items)}건)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실행 예시 (이 파일을 직접 실행했을 때만 동작)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":

    # ── 예시 1: 뉴스 5건 검색 ──
    print("=" * 50)
    print("예시 1: 뉴스 단건 검색")
    print("=" * 50)
    data = search("news", "인공지능", display=5, sort="date")
    for i, item in enumerate(data["items"], 1):
        print(f"  {i}. {strip_html(item['title'])}")
        print(f"     {item['originallink']}")
        print()

    # ── 예시 2: 블로그 100건 → CSV 저장 ──
    print("=" * 50)
    print("예시 2: 블로그 대량 수집 → CSV")
    print("=" * 50)
    items = search_many("blog", "데이터 저널리즘", max_items=100)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save(items, f"blog_결과_{ts}.csv")

    # ── 예시 3: 7개 엔드포인트 순회 ──
    print("\n" + "=" * 50)
    print("예시 3: 전체 엔드포인트 맛보기 (각 3건)")
    print("=" * 50)
    for ep in ["news","blog","cafearticle","kin","book","shop","local"]:
        print(f"\n▸ {ep}")
        data = search(ep, "경희대학교", display=3)
        for item in data["items"]:
            print(f"    - {strip_html(item.get('title',''))}")
