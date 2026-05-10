# 뉴스 중심 RSS 가이드 (2026)

> **RSS (Really Simple Syndication)**: 웹사이트의 업데이트된 정보를 사용자에게 자동으로 실시간으로 전달해 주는 '콘텐츠 배달 서비스'의 규격. 가장 널리 쓰이는 표준으로, 웹사이트를 직접 방문하지 않아도 제목, 요약, 날짜 등의 정보를 기계가 읽을 수 있는 형식으로 제공.  
> **Atom (Atom Syndication Format)**: RSS의 파편화(버전 혼선)와 한계를 보완하기 위해 나중에 등장한 차세대 표준. RSS보다 엄격한 표준을 따르며, 메타데이터(저자 정보, 카테고리 등)를 더 상세하게 담을 수 있음. IETF(국제 인터넷 표준화 기구)에서 공식 표준으로 정의했으며, 구글(Blogger, YouTube) 서비스에서 주로 사용.

## RSS 작동 여부 표기

> -   ✅ **직접 fetch 성공 또는 Feedspot 2026 디렉터리 확인** — 작동 보장
> -   ⚠️ **미검증** — 사이트 패턴상 작동 가능성 높음. 사용 전 직접 확인 필요
> -   ❌ **폐지·도메인 마이그레이션 확인됨** → 대안 RSSHub 라우트 제시
> 
> 한국 뉴스 사이트는 자주 RSS를 변경/폐지하므로 일상적 점검 필요

---

## RSS 수집 3단계 Fallback 전략 ⭐

> 한국 언론사·정부기관의 RSS는 사이트 개편·도메인 변경·운영 정책 변경으로 자주 폐지되거나 작동을 중단한다. **본 가이드 전반에서 권장하는 표준 패턴은 3단계 Fallback**이다 — 우선 공식 RSS를 시도하고, 실패하면 RSSHub로 우회, 그것도 실패하면 Google News RSS 검색으로 대체하는 흐름. 이후 §3 (한국 뉴스), §4 (정부·공공), §5 (기술 블로그), §6 (글로벌)의 모든 표에서 이 흐름을 가정한다.

**흐름도**:

```
┌─────────────────────────────────────────────────────────┐
│ [1차] 공식 RSS                                          │
│   https://site.com/rss                                  │
│        │                                                │
│        │ ❌ 응답 없음 / 200 OK 이지만 빈 entries / 404   │
│        ▼                                                │
│ [2차] RSSHub 라우트                                     │
│   https://rsshub.app/site/rss   (자체 호스팅 권장)      │
│        │                                                │
│        │ ❌ 라우트 없음 / 404                           │
│        ▼                                                │
│ [3차] Google News RSS 검색                              │
│   https://news.google.com/rss/search?q=키워드           │
│        │                                                │
│        │ ✅ 항상 응답 (커버리지·품질은 단계가 내려갈수록 │
│        │     떨어지지만 마지막 안전망 역할)             │
│        ▼                                                │
│   → feedparser 파싱 → 후처리 필터링 → DB 적재           │
└─────────────────────────────────────────────────────────┘
```

**각 단계의 특성과 트레이드오프**:

| 단계 | 출처 | 장점 | 한계 / 주의 |
| --- | --- | --- | --- |
| **1차** | 매체 자체 공식 RSS | 가장 정확·빠름. 매체가 의도한 분류·제목·요약을 그대로 받을 수 있음. 발행 5~30분 내 갱신 | 한국 매체는 사이트 개편·도메인 변경 빈번 (예: 중앙일보 `joins.com` → `joongang.co.kr`, 헤럴드경제 `biz.heraldcorp.com` → `news.heraldcorp.com`). 200 OK 응답이지만 `entries`가 비어있는 경우 흔함 |
| **2차** | [RSSHub](https://docs.rsshub.app) (자체 호스팅 권장) | 900+ 사이트 라우트 보유. 한국 매체 대부분 커버. 공식 RSS가 없는 사이트(JTBC 등)나 폐지된 사이트도 RSS화 가능. 카테고리·필터 파라미터 풍부 | 라우트가 없는 사이트는 불가. **공식 인스턴스 `rsshub.app`은 rate-limit이 잦음** → DigitalOcean·Cloudflare 등에 자체 호스팅 강력 권장 (§7-3) |
| **3차** | [Google News RSS 검색](https://news.google.com/rss/search) | 모든 사이트 커버. `site:` 필터, `OR`·`AND` 연산자, `when:7d` 시간 윈도, `intitle:`, `-키워드`(제외) 모두 지원. 무인증·무제한·무료 | Google이 제공하는 메타만 노출 → 매체별 고유 분류·태그·요약은 부족. 30일 이내 결과만 반환. 매체 분류가 부정확할 수 있음. URL이 Google 리다이렉트로 감싸져 있어 후처리 필요 |

**Python 구현 — 한 함수로 3단계 자동 fallback**:

```
import feedparser, httpx, urllib.parse

UA = {"User-Agent": "Mozilla/5.0 DataJournLab/1.0"}
RSSHUB_BASE = "https://rsshub.app"  # 자체 호스팅 시 본인 도메인으로 교체

def fetch_with_fallback(name: str,
                        official_url: str = None,
                        rsshub_route: str = None,
                        search_query: str = None,
                        verbose: bool = True):
    """3단계 fallback으로 RSS 수집.

    Args:
        name: 로그용 매체명
        official_url: 1차 공식 RSS URL
        rsshub_route: 2차 RSSHub 경로 (예: "/joongang/news/all")
        search_query: 3차 Google News 검색어 (예: "site:joongang.co.kr")
    Returns:
        feedparser.FeedParserDict (entries 보장) 또는 None (전부 실패)
    """
    # ─── 1차: 공식 RSS ───
    if official_url:
        try:
            r = httpx.get(official_url, timeout=10, headers=UA, follow_redirects=True)
            if r.status_code == 200:
                d = feedparser.parse(r.content)
                if len(d.entries) > 0:
                    if verbose: print(f"[{name}] ✅ 1차 성공 ({len(d.entries)}건)")
                    return d
                if verbose: print(f"[{name}] ⚠️  1차: 200 OK이지만 빈 피드")
            else:
                if verbose: print(f"[{name}] ❌ 1차 실패 (status={r.status_code})")
        except Exception as e:
            if verbose: print(f"[{name}] ❌ 1차 예외: {e}")

    # ─── 2차: RSSHub ───
    if rsshub_route:
        rsshub_url = f"{RSSHUB_BASE}{rsshub_route}"
        try:
            r = httpx.get(rsshub_url, timeout=15, headers=UA)
            if r.status_code == 200:
                d = feedparser.parse(r.content)
                if len(d.entries) > 0:
                    if verbose: print(f"[{name}] ✅ 2차 RSSHub 성공 ({len(d.entries)}건)")
                    return d
            if verbose: print(f"[{name}] ❌ 2차 RSSHub 실패 (status={r.status_code})")
        except Exception as e:
            if verbose: print(f"[{name}] ❌ 2차 예외: {e}")

    # ─── 3차: Google News RSS 검색 ───
    if search_query:
        q = urllib.parse.quote(search_query)
        gnews_url = f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
        try:
            r = httpx.get(gnews_url, timeout=10, headers=UA)
            d = feedparser.parse(r.content)
            if len(d.entries) > 0:
                if verbose: print(f"[{name}] ✅ 3차 Google News 성공 ({len(d.entries)}건)")
                return d
            if verbose: print(f"[{name}] ❌ 3차도 빈 결과")
        except Exception as e:
            if verbose: print(f"[{name}] ❌ 3차 예외: {e}")

    return None  # 전부 실패

# ─── 사용 예 ───────────────────────────────────────────
# 케이스 1: 1차에서 보통 성공하는 매체
d = fetch_with_fallback(
    name="경향신문",
    official_url="https://www.khan.co.kr/rss/rssdata/total_news.xml",
    rsshub_route="/khan/news",
    search_query="site:khan.co.kr",
)

# 케이스 2: ❌로 표시된 매체 — 1차는 항상 실패, 2차에서 잡힘
d = fetch_with_fallback(
    name="중앙일보",
    official_url="https://rss.joins.com/joins_news_list.xml",  # 폐지됨
    rsshub_route="/joongang/news/all",
    search_query="site:joongang.co.kr OR site:joins.com",
)

# 케이스 3: 작은 매체·전문지 — RSSHub 라우트 없으면 3차로 직행
d = fetch_with_fallback(
    name="사례_매체",
    official_url=None,   # 공식 RSS 없음
    rsshub_route=None,   # RSSHub 라우트 없음
    search_query="site:example.co.kr 정치 OR 경제",
)
```

---

## 0\. 왜 RSS인가

**API의 보완재이자 기본기**. 한국 250+ 언론사·정부부처·기술블로그가 여전히 RSS/Atom을 무료·무인증으로 제공한다. RSS의 가치:

| 강점 | 설명 |
| --- | --- |
| **무료·무인증** | API 키 발급 불필요, 대부분 IP 제한도 없음 |
| **즉시성** | 발행 5~30분 내 갱신, 폴링 1~6시간이면 충분 |
| **표준 포맷** | RSS 2.0 / Atom 1.0 / JSON Feed — 단일 파서로 처리 |
| **저작권 안전** | 제목·요약·링크만 받음 (전문은 별도 fetch + 인용 규정 준수) |
| **구조화 데이터** | title / link / pubDate / author / category — 필터링·DB 적재 용이 |
| **LLM 친화적** | 큐레이션된 텍스트 입력으로 grounding 비용 최소화 |

**한 줄 워크플로**:

```
RSS 확인 → feedparser (파이썬) → Gemini 필터링·요약 → SQLite/Chroma → 알림(Slack/Telegram)
```

---

## 1\. RSS 기초

-   **RSS**: Really Simple Syndication. 사이트 콘텐츠 갱신을 XML로 노출하는 표준
-   **Atom**: RSS의 IETF 표준 후속. 거의 모든 RSS 라이브러리가 둘 다 지원
-   **JSON(JavaScript Object Notation) Feed**: 모던 대안 ([jsonfeed.org](https://www.jsonfeed.org/)). RSS와 Atom은 XML 사용.
-   **OPML(Outline Processor Markup Language)**: RSS 피드들의 주소록. 여러 RSS URL을 묶어 한 번에 import/export하는 XML 포맷.
-   **주요 항목**: `title`, `link`, `description`/`summary`, `pubDate`/`updated`, `author`, `category`, `enclosure` (미디어), `guid`/`id` (고유 ID)
-   **RSS 리더**: [Feedly](https://feedly.com), [Inoreader](https://www.inoreader.com), [NetNewsWire](https://netnewswire.com), [FreshRSS](https://freshrss.org)(self-host), [Tiny Tiny RSS](https://tt-rss.org), [Folo](https://follow.is), [Plenary](https://plenary.app)

> **핵심 팁**: 사이트 footer에서 RSS 아이콘을 찾거나, URL 끝에 `/rss`, `/feed`, `/rss.xml`, `/atom.xml`을 시험해본다. View Source에서 `<link rel="alternate" type="application/rss+xml">` 검색도 효과적.

---

## 2\. RSS 피드 모음 GitHub 저장소 (큐레이션)

### 2-1. 글로벌 학술·기술

| 저장소 | 규모 | 특징 |
| --- | --- | --- |
| [sg-s/science-journal-feeds](https://github.com/sg-s/science-journal-feeds) | **4,700+** | 학술/과학 저널 RSS — 현존 최대 |
| [plenaryapp/awesome-rss-feeds](https://github.com/plenaryapp/awesome-rss-feeds) | 500+ | OPML 파일 포함, 카테고리·국가별 |
| [FuVaVa/FT50-Journal-RSS-Feeds](https://github.com/FuVaVa/FT50-Journal-RSS-Feeds) | 50 | FT50 경영·경제 저널 |
| [AndyGreenPhD/journal-rss-feeds](https://github.com/AndyGreenPhD/journal-rss-feeds) | ~50 | 정보시스템·정보보안 (Basket of 8) |
| [yexner/rss-feeds-academic-journals](https://github.com/yexner/rss-feeds-academic-journals) | ~40 | 마케팅·과학 |
| [focyte/Journal\_RSS](https://github.com/focyte/Journal_RSS) | ~30 | 자연과학 (진행 중) |
| [alexander-winkler/degruyter\_rss](https://github.com/alexander-winkler/degruyter_rss) | ~150 | De Gruyter 저널 (RSS 폐지 후 librarian 큐레이션) |
| [tuan3w/awesome-tech-rss](https://github.com/tuan3w/awesome-tech-rss) | 100+ | 스타트업·기술·과학, OPML 제공 |
| [DongjunLee/awesome-feeds](https://github.com/DongjunLee/awesome-feeds) | ~150 | AI/ML 연구소·블로그 (DeepMind, BAIR, OpenAI 등) |

### 2-2. 한국 언론·기술

| 저장소 | 특징 |
| --- | --- |
| [akngs/knews-rss](https://github.com/akngs/knews-rss) | 한국 언론사 RSS 모음 |
| [koorukuroo/news\_rss.py (gist)](https://gist.github.com/koorukuroo/330a644fcc3c9ffdc7b6d537efd939c3) | MBC·조선·중앙·동아·세계·매경·경향·한국·한경·파이낸셜·헤럴드·노컷 등 카테고리별 (2026-02 갱신) |
| [maczniak/awesome-korean-techblog](https://github.com/maczniak/awesome-korean-techblog) | 가장 방대한 한국 기술블로그 인덱스 (50+) |
| [elky84/awesome-blogs](https://github.com/elky84/awesome-blogs) | 한국 개발자 블로그 통합 RSS feed 제공 |
| [seongkyu-lim/TechBlogs](https://github.com/seongkyu-lim/TechBlogs) | 카카오·우아한·네이버·당근·쿠팡 등 |
| [currenjin/site-for-developers](https://github.com/currenjin/site-for-developers) | 한국 개발 사이트·블로그 통합 |

**검증된 외부 RSS 디렉터리** (URL 작동 여부 교차 확인용):

-   [Feedspot — Top 30 South Korea News RSS](https://rss.feedspot.com/south_korea_news_rss_feeds/) — **2026-04 갱신**, 이 가이드의 ✅ 마크 근거 중 하나
-   [Feedspot — Top 25 Korean Tech RSS](https://rss.feedspot.com/korean_tech_rss_feeds/)
-   [Feedspot — Top 60 Seoul RSS](https://rss.feedspot.com/seoul_rss_feeds/)

### 2-3. GitHub 검색 키워드 (직접 탐색)

-   `topic:rss-list`
-   `topic:rss-feeds`
-   `korean news rss`
-   `korea government rss`
-   `academic journal rss opml`
-   `awesome opml`
-   `rss aggregator (분야명)`

---

## 3\. 한국 뉴스 RSS 피드 (2026-05 검증)

### 3-1. 종합 일간지

| 매체 | 전체/대표 RSS | 비고 |
| --- | --- | --- |
| ✅ [**조선일보**](https://www.chosun.com) | [https://www.chosun.com/arc/outboundfeeds/rss/](https://www.chosun.com/arc/outboundfeeds/rss/) | Arc Publishing outbound feed. 카테고리는 outboundfeeds 파라미터 분기 |
| ❌ [**중앙일보**](https://www.joongang.co.kr) | `rss.joins.com/joins_news_list.xml` **폐지** — 도메인이 `joongang.co.kr`로 마이그레이션되며 통합 RSS 폐지 → **RSSHub** [`/joongang/news/:category`](https://docs.rsshub.app/routes/traditional-media#zhong-yang-ri-bao) 사용 권장 |  |
| ✅ [**동아일보**](https://www.donga.com) | [https://rss.donga.com/total.xml](https://rss.donga.com/total.xml) | 카테고리: [`politics.xml`](https://rss.donga.com/politics.xml), [`economy.xml`](https://rss.donga.com/economy.xml), [`national.xml`](https://rss.donga.com/national.xml), [`international.xml`](https://rss.donga.com/international.xml), [`editorials.xml`](https://rss.donga.com/editorials.xml), [`science.xml`](https://rss.donga.com/science.xml), [`culture.xml`](https://rss.donga.com/culture.xml) |
| ⚠️ [**한겨레**](https://www.hani.co.kr) | [https://www.hani.co.kr/rss/](https://www.hani.co.kr/rss/) | 카테고리 분기: [`/rss/politics/`](https://www.hani.co.kr/rss/politics/), [`/rss/economy/`](https://www.hani.co.kr/rss/economy/), [`/rss/society/`](https://www.hani.co.kr/rss/society/), [`/rss/international/`](https://www.hani.co.kr/rss/international/), [`/rss/culture/`](https://www.hani.co.kr/rss/culture/), [`/rss/opinion/`](https://www.hani.co.kr/rss/opinion/), [`/rss/science/`](https://www.hani.co.kr/rss/science/) |
| ✅ [**경향신문**](https://www.khan.co.kr) | [https://www.khan.co.kr/rss/rssdata/total\_news.xml](https://www.khan.co.kr/rss/rssdata/total_news.xml) | 직접 fetch 검증. 카테고리: [`politic.xml`](https://www.khan.co.kr/rss/rssdata/politic.xml), [`economy.xml`](https://www.khan.co.kr/rss/rssdata/economy.xml), [`society.xml`](https://www.khan.co.kr/rss/rssdata/society.xml), [`world.xml`](https://www.khan.co.kr/rss/rssdata/world.xml), [`culture.xml`](https://www.khan.co.kr/rss/rssdata/culture.xml), [`itnews.xml`](https://www.khan.co.kr/rss/rssdata/itnews.xml), [`opinion.xml`](https://www.khan.co.kr/rss/rssdata/opinion.xml) |
| ❌ [**한국일보**](https://www.hankookilbo.com) | `rss.hankooki.com/news/hk_main.xml` **사이트 재편 후 작동 불확실** → **RSSHub** [`/hankookilbo/:category`](https://docs.rsshub.app/) 또는 [Google News 검색 RSS](#3-5-%EB%8B%A4%EC%9D%8C%EA%B5%AC%EA%B8%80-%EB%89%B4%EC%8A%A4-%EC%96%B4%EA%B7%B8%EB%A6%AC%EA%B2%8C%EC%9D%B4%ED%84%B0) 사용 권장 |  |
| ⚠️ [**세계일보**](https://www.segye.com) | [https://rss.segye.com/segye\_total.xml](https://rss.segye.com/segye_total.xml) | Feedspot에는 `segye.com/Articles/RSSList`로 등록. 둘 다 시도 권장 |
| ⚠️ [**국민일보**](https://www.kmib.co.kr) | [https://www.kmib.co.kr/rss/data/kmibRssAll.xml](https://www.kmib.co.kr/rss/data/kmibRssAll.xml) | 분야별 별도 페이지 확인 |
| ✅ [**서울신문**](https://www.seoul.co.kr) | [https://www.seoul.co.kr/xml/rss/rss\_top.xml](https://www.seoul.co.kr/xml/rss/rss_top.xml) | **주의**: 종합은 `rss_top.xml` (이전 버전 가이드의 `rss_politics.xml`은 카테고리별일 뿐). 분야별: [`rss_economy.xml`](https://www.seoul.co.kr/xml/rss/rss_economy.xml), [`rss_society.xml`](https://www.seoul.co.kr/xml/rss/rss_society.xml), [`rss_international.xml`](https://www.seoul.co.kr/xml/rss/rss_international.xml) |
| ⚠️ [**한국경제**](https://www.hankyung.com) | [https://rss.hankyung.com/economy.xml](https://rss.hankyung.com/economy.xml) | 카테고리: `stock`, `estate`, `industry`, `intl`, `politics`, `column` |
| ⚠️ [**매일경제**](https://www.mk.co.kr) | [https://www.mk.co.kr/rss/30000001/](https://www.mk.co.kr/rss/30000001/) | 헤드라인. [`40300001`(속보)](https://www.mk.co.kr/rss/40300001/), [`30100041`(경제)](https://www.mk.co.kr/rss/30100041/), [`50200011`(증권)](https://www.mk.co.kr/rss/50200011/), [`30200030`(정치)](https://www.mk.co.kr/rss/30200030/), [`30300018`(국제)](https://www.mk.co.kr/rss/30300018/), [`50100032`(기업)](https://www.mk.co.kr/rss/50100032/) |
| ⚠️ [**파이낸셜뉴스**](https://www.fnnews.com) | [https://www.fnnews.com/rss/fn\_realnews\_all.xml](https://www.fnnews.com/rss/fn_realnews_all.xml) | 카테고리 접미사: `_stock`, `_finance`, `_realestate`, `_industry`, `_economy`, `_it`, `_politics`, `_society` |
| ❌ [**헤럴드경제**](https://www.heraldcorp.com) | `biz.heraldcorp.com/rss/...` **도메인 변경됨**(`biz.heraldcorp.com` → `news.heraldcorp.com`) → **RSSHub** [`/heraldcorp/:category`](https://docs.rsshub.app/) 사용 권장 |  |

> **권장**: ✅ 마크된 URL을 우선 사용. ❌는 RSSHub 라우트로 대체. ⚠️는 fetch 후 `feed.entries`가 비어있으면 RSSHub 라우트나 Google News 검색 RSS로 우회.

### 3-2. 방송·통신사

| 매체 | URL |
| --- | --- |
| ⚠️ [**KBS 뉴스**](https://news.kbs.co.kr) | [https://news.kbs.co.kr/rss/news.xml](https://news.kbs.co.kr/rss/news.xml), [https://news.kbs.co.kr/rss/headline.xml](https://news.kbs.co.kr/rss/headline.xml) |
| ⚠️ [**MBC 뉴스**](https://imnews.imbc.com) | [https://imnews.imbc.com/rss/news/news\_00.xml](https://imnews.imbc.com/rss/news/news_00.xml) (전체) — 카테고리: [`_01`(정치)](https://imnews.imbc.com/rss/news/news_01.xml), [`_02`(통일외교)](https://imnews.imbc.com/rss/news/news_02.xml), [`_03`(국제)](https://imnews.imbc.com/rss/news/news_03.xml), [`_04`(경제)](https://imnews.imbc.com/rss/news/news_04.xml), [`_05`(사회)](https://imnews.imbc.com/rss/news/news_05.xml), [`_06`(문화/연예)](https://imnews.imbc.com/rss/news/news_06.xml), [`_07`(스포츠)](https://imnews.imbc.com/rss/news/news_07.xml), [`_08`(건강/과학)](https://imnews.imbc.com/rss/news/news_08.xml) |
| ⚠️ [**SBS 뉴스**](https://news.sbs.co.kr) | [https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01](https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01) (정치) — `02`(경제), `03`(사회), `04`(국제), `05`(문화), `07`(스포츠), `08`(연예) |
| ❌ [**JTBC 뉴스**](https://news.jtbc.co.kr) | RSS 미공식 — **RSSHub** [`/jtbc/news/:category`](https://docs.rsshub.app/) 사용 |
| ⚠️ [**YTN**](https://www.ytn.co.kr) | [https://www.ytn.co.kr/\_comm/rss.php](https://www.ytn.co.kr/_comm/rss.php) |
| ⚠️ [**연합뉴스**](https://www.yna.co.kr) | [https://www.yna.co.kr/rss/news.xml](https://www.yna.co.kr/rss/news.xml) (전체) — 카테고리: [`politics.xml`](https://www.yna.co.kr/rss/politics.xml), [`economy.xml`](https://www.yna.co.kr/rss/economy.xml), [`local.xml`](https://www.yna.co.kr/rss/local.xml), [`international.xml`](https://www.yna.co.kr/rss/international.xml), [`culture.xml`](https://www.yna.co.kr/rss/culture.xml), [`sports.xml`](https://www.yna.co.kr/rss/sports.xml), [`entertainment.xml`](https://www.yna.co.kr/rss/entertainment.xml) |
| ✅ [**뉴시스**](https://www.newsis.com) | [https://www.newsis.com/RSS/sokbo.xml](https://www.newsis.com/RSS/sokbo.xml) (속보, 직접 fetch 검증). **주의**: 이전 가이드의 `total.xml`은 부정확 — `sokbo.xml`이 정식 |
| ⚠️ [**노컷뉴스 (CBS)**](https://www.nocutnews.co.kr) | [https://rss.nocutnews.co.kr/nocutnews.xml](https://rss.nocutnews.co.kr/nocutnews.xml) (전체) — 카테고리: [`NocutPolitics.xml`](https://rss.nocutnews.co.kr/NocutPolitics.xml), [`NocutSocial.xml`](https://rss.nocutnews.co.kr/NocutSocial.xml), [`NocutEconomy.xml`](https://rss.nocutnews.co.kr/NocutEconomy.xml), [`NocutIndustry.xml`](https://rss.nocutnews.co.kr/NocutIndustry.xml), [`NocutLocal.xml`](https://rss.nocutnews.co.kr/NocutLocal.xml), [`NocutGlobal.xml`](https://rss.nocutnews.co.kr/NocutGlobal.xml), [`NocutIT.xml`](https://rss.nocutnews.co.kr/NocutIT.xml), [`NocutCulture.xml`](https://rss.nocutnews.co.kr/NocutCulture.xml) |
| ⚠️ [**오마이뉴스**](https://www.ohmynews.com) | [http://rss.ohmynews.com/rss/ohmynews.xml](http://rss.ohmynews.com/rss/ohmynews.xml) |
| ⚠️ [**프레시안**](https://www.pressian.com) | [https://www.pressian.com/api/rss](https://www.pressian.com/api/rss) |
| ✅ [**News1**](https://www.news1.kr) | (Feedspot 2026 등록 매체 — 사이트 footer에서 RSS 확인) |
| ✅ [**Media Today**](https://www.mediatoday.co.kr) | [https://www.mediatoday.co.kr/rss/allArticle.xml](https://www.mediatoday.co.kr/rss/allArticle.xml) — Feedspot 2026 등록 |

### 3-3. 영문 한국 매체

| 매체 | URL |
| --- | --- |
| ✅ [**Korea Herald**](https://www.koreaherald.com) | [http://www.koreaherald.com/rss/rss\_news.php](http://www.koreaherald.com/rss/rss_news.php) — Feedspot 2026 확인 |
| ⚠️ [**Korea Times**](https://www.koreatimes.co.kr) | [https://www.koreatimes.co.kr/www2/common/rss.asp](https://www.koreatimes.co.kr/www2/common/rss.asp) |
| ✅ [**Korea JoongAng Daily**](https://koreajoongangdaily.joins.com) | [https://koreajoongangdaily.joins.com/Services/Xml/Rss.xml](https://koreajoongangdaily.joins.com/Services/Xml/Rss.xml) — 영문판은 `joins.com` 도메인 유지 |
| ✅ [**Yonhap (English)**](https://en.yna.co.kr) | [https://en.yna.co.kr/RSS/news.xml](https://en.yna.co.kr/RSS/news.xml) — Feedspot 1순위 등록 |
| ✅ [**Hankyoreh English**](https://english.hani.co.kr) | [https://english.hani.co.kr/rss/english\_edition/](https://english.hani.co.kr/rss/english_edition/) — Feedspot 등록 |
| ⚠️ [**Chosun English**](http://english.chosun.com) | [http://english.chosun.com/site/data/rss/news.xml](http://english.chosun.com/site/data/rss/news.xml) |
| ✅ [**Daily NK** (북한 소식)](https://www.dailynk.com) | [https://www.dailynk.com/english/feed/](https://www.dailynk.com/english/feed/) — Feedspot 3순위 |
| ✅ [**Business Korea**](https://www.businesskorea.co.kr) | [https://www.businesskorea.co.kr/rss/allEnglishArticle.xml](https://www.businesskorea.co.kr/rss/allEnglishArticle.xml) — Feedspot 등록 |

### 3-4. 전문지·매거진

| 매체 | URL |
| --- | --- |
| ⚠️ [**시사IN**](https://www.sisain.co.kr) | [https://www.sisain.co.kr/rss/allArticle.xml](https://www.sisain.co.kr/rss/allArticle.xml) |
| ⚠️ [**한겨레21**](https://h21.hani.co.kr) | [https://h21.hani.co.kr/rss/](https://h21.hani.co.kr/rss/) |
| ⚠️ [**주간조선**](https://weekly.chosun.com) | [https://weekly.chosun.com/site/data/rss/rss.xml](https://weekly.chosun.com/site/data/rss/rss.xml) |
| ⚠️ [**이데일리**](https://www.edaily.co.kr) | [https://www.edaily.co.kr/rss/edaily\_news.xml](https://www.edaily.co.kr/rss/edaily_news.xml) |
| ⚠️ [**머니투데이**](https://news.mt.co.kr) | [https://news.mt.co.kr/rss/news\_total.xml](https://news.mt.co.kr/rss/news_total.xml) |
| ⚠️ [**블로터**](https://www.bloter.net) | [http://www.bloter.net/rss](http://www.bloter.net/rss) |
| ⚠️ [**디지털타임스**](http://www.dt.co.kr) | [http://www.dt.co.kr/rss/news.xml](http://www.dt.co.kr/rss/news.xml) |
| ⚠️ [**전자신문**](https://www.etnews.com) | [https://www.etnews.com/rss/section.xml](https://www.etnews.com/rss/section.xml) |
| ⚠️ [**ZDNet Korea**](https://zdnet.co.kr) | [https://feeds.feedburner.com/zdkorea](https://feeds.feedburner.com/zdkorea) |

### 3-5. 다음·구글 뉴스 어그리게이터

| 출처 | URL |
| --- | --- |
| ❌ [**다음 종합**](https://media.daum.net) | `media.daum.net/rss/today/primary/all/rss2.xml` **다음 뉴스 RSS는 사이트 개편 후 작동 불안정** → Google News 검색 RSS 또는 RSSHub 사용 권장 |
| ✅ [**Google News (한국 주요)**](https://news.google.com/?hl=ko&gl=KR&ceid=KR:ko) | [https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko](https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko) |
| ✅ **Google News (검색쿼리)** | [https://news.google.com/rss/search?q=합계출산율&hl=ko&gl=KR&ceid=KR:ko](https://news.google.com/rss/search?q=%25ED%2595%25A9%25EA%25B3%2584%25EC%25B6%259C%25EC%2582%25B0%25EC%259C%25A8&hl=ko&gl=KR&ceid=KR:ko) |

> **Google News 검색 RSS는 데이터저널리즘에서 매우 강력**. URL의 `q=` 파라미터에 키워드 OR 연산자 사용 가능 (예: `q=합계출산율 OR 출생률`). 로그인·키 불필요. `site:n.news.naver.com` 등 사이트 필터 가능. `when:7d` 시간 윈도도 적용됨.

### 3-6. 네이버 뉴스 (RSS 비공식)

[**네이버**](https://news.naver.com)는 공식 RSS를 종료. 대안:

1.  RSSHub 라우트 [`/naver/news/:category`](https://docs.rsshub.app/)
2.  네이버 검색 API (자매 문서 — API + LLM 가이드)
3.  Google News에서 `q=site:n.news.naver.com 키워드` 검색 RSS 사용

---

## 4\. 한국 정부·공공기관 RSS

### 4-1. 통합 게이트웨이 (가장 강력)

| 출처 | URL |
| --- | --- |
| ✅ [**대한민국 정책브리핑 (korea.kr)**](https://www.korea.kr) | [https://www.korea.kr/etc/rss.do](https://www.korea.kr/etc/rss.do) — 부처별·분야별 통합 RSS 디렉터리. 보도자료·연설문·정책자료·브리핑 통합 |
| ⚠️ [**정부24**](https://www.gov.kr) | [https://www.gov.kr/portal/rss](https://www.gov.kr/portal/rss) — 공지·민원·정책 |
| ⚠️ [**공공데이터포털**](https://www.data.go.kr) | [https://www.data.go.kr/bbs/ntc/selectNoticeBbs.do](https://www.data.go.kr/bbs/ntc/selectNoticeBbs.do) — 보도자료, 데이터셋 갱신 RSS 일부 제공 |

### 4-2. 부처별 RSS 패턴

대부분의 정부 사이트는 **공통 게시판 솔루션**을 사용 → URL 패턴이 비슷함:

```
https://[부처도메인].go.kr/.../board/rss.do?menuId={M}&boardMasterId={B}
```

| 부처 | 공지·공고 / 보도자료 |
| --- | --- |
| ⚠️ [**환경부**](https://www.me.go.kr) | 공지: [https://www.me.go.kr/home/web/board/rss.do?menuId=290&boardMasterId=39](https://www.me.go.kr/home/web/board/rss.do?menuId=290&boardMasterId=39) <br> 보도: [`?menuId=286&boardMasterId=1`](https://www.me.go.kr/home/web/board/rss.do?menuId=286&boardMasterId=1) <br> e환경뉴스: [`?menuId=284&boardMasterId=108`](https://www.me.go.kr/home/web/board/rss.do?menuId=284&boardMasterId=108) |
| ⚠️ [**국토교통부**](https://www.molit.go.kr) | [https://www.molit.go.kr/USR/p\_etc\_rsssvc/m\_123/ers.jsp](https://www.molit.go.kr/USR/p_etc_rsssvc/m_123/ers.jsp) — 페이지에서 보도/공지 분야별 URL 확보 |
| ⚠️ [**외교부**](https://www.mofa.go.kr) | [https://www.mofa.go.kr/www/wpge/m\_20347/contents.do](https://www.mofa.go.kr/www/wpge/m_20347/contents.do) — RSS 안내 페이지 |
| ⚠️ [**과학기술정보통신부**](https://www.msit.go.kr) | [https://www.msit.go.kr/SYNAP/rss/board.do](https://www.msit.go.kr/SYNAP/rss/board.do) — 보도자료 |
| ⚠️ [**산업통상자원부**](https://www.motie.go.kr) | [https://www.motie.go.kr/kor/rss/rssAllSrvc.do](https://www.motie.go.kr/kor/rss/rssAllSrvc.do) |
| ⚠️ [**보건복지부**](https://www.mohw.go.kr) | [https://www.mohw.go.kr/menu.es?mid=a10503000000](https://www.mohw.go.kr/menu.es?mid=a10503000000) (안내 페이지) |
| ⚠️ [**교육부**](https://www.moe.go.kr) | [https://www.moe.go.kr](https://www.moe.go.kr) footer "RSS" 메뉴 |
| ⚠️ [**기획재정부**](https://www.moef.go.kr) | [https://www.moef.go.kr/com/sym/com/rssListSelect.do](https://www.moef.go.kr/com/sym/com/rssListSelect.do) |
| ⚠️ **법무부 / 통일부 / 국방부 / 여성가족부 / 고용노동부 / 농림축산식품부** | [법무부](https://www.moj.go.kr) · [통일부](https://www.unikorea.go.kr) · [국방부](https://www.mnd.go.kr) · [여성가족부](https://www.mogef.go.kr) · [고용노동부](https://www.moel.go.kr) · [농림축산식품부](https://www.mafra.go.kr) — 모두 사이트 footer "RSS" |
| ⚠️ [**질병관리청**](https://www.kdca.go.kr) | [https://www.kdca.go.kr/board.es](https://www.kdca.go.kr/board.es) 게시판별 RSS (감염병 발생 등) |
| ⚠️ [**기상청**](https://www.kma.go.kr) | [https://www.kma.go.kr/rss/](https://www.kma.go.kr/rss/) — 일기예보, 기후정보 |
| ⚠️ [**식품의약품안전처**](https://www.mfds.go.kr) | [https://www.mfds.go.kr/brd/rss.do](https://www.mfds.go.kr/brd/rss.do) (게시판 ID 별) |
| ⚠️ [**금융감독원**](https://www.fss.or.kr) | [https://www.fss.or.kr/fss/bbs/B0000188/rss.do?menuNo=200218](https://www.fss.or.kr/fss/bbs/B0000188/rss.do?menuNo=200218) (보도자료) |
| ⚠️ [**금융위원회**](https://www.fsc.go.kr) | [https://www.fsc.go.kr/po010101/rss](https://www.fsc.go.kr/po010101/rss) |
| ⚠️ [**공정거래위원회**](https://www.ftc.go.kr) | [https://www.ftc.go.kr/www/cop/bbs/selectBoardListNew.do](https://www.ftc.go.kr/www/cop/bbs/selectBoardListNew.do) (안내) |
| ⚠️ [**국세청**](https://www.nts.go.kr) | [https://www.nts.go.kr/nts/bd/cm/dc/AB.do](https://www.nts.go.kr/nts/bd/cm/dc/AB.do) 게시판별 |
| ⚠️ [**통계청**](https://kostat.go.kr) | [https://kostat.go.kr/portal/korea/kor\_nw/1/1/index.board?bmode=rss](https://kostat.go.kr/portal/korea/kor_nw/1/1/index.board?bmode=rss) (보도자료) |

> **권장 전략**: [korea.kr](https://www.korea.kr) 통합 디렉터리를 기준점으로 삼고, 부처 RSS가 누락되면 **RSSHub `/gov/:dept/:board`** 라우트 또는 \\\*\\*RSS-Bridge `CssSelectorBridge`\\*\\\*로 보완.

### 4-3. 국회·법원·중앙은행

| 기관 | 방법 |
| --- | --- |
| [**열린국회정보**](https://open.assembly.go.kr) | API 우선 (의안·표결·발언). RSS는 공지 위주 (자매 문서 §3-1 참조) |
| [**국가법령정보센터**](https://www.law.go.kr) | API 우선. 신규법령 알림은 부처 RSS로 보완 |
| [**대법원**](https://www.scourt.go.kr) · [**헌법재판소**](https://www.ccourt.go.kr) | 보도자료 RSS 또는 RSSHub로 변환 |
| ✅ [**한국은행**](https://www.bok.or.kr) | 보도자료 페이지 → RSSHub [`/bok/press`](https://docs.rsshub.app/) 라우트 |
| [**금융감독원**](https://www.fss.or.kr) · [**금융위**](https://www.fsc.go.kr) | 위 부처 표 참고 + Open DART API 병행 |

### 4-4. 지자체 (서울·부산·경기 등)

| 자치단체 | RSS |
| --- | --- |
| ⚠️ [**서울시**](https://www.seoul.go.kr) | [https://www.seoul.go.kr/news/news\_notice.do](https://www.seoul.go.kr/news/news_notice.do) — 보도자료, 분야별 RSS |
| ⚠️ [**경기도**](https://www.gg.go.kr) | [https://www.gg.go.kr/contents/rssService.do](https://www.gg.go.kr/contents/rssService.do) |
| ⚠️ **광역시 (부산·대구·인천·광주·대전·울산·세종)** | [부산시](https://www.busan.go.kr) · [대구시](https://www.daegu.go.kr) · [인천시](https://www.incheon.go.kr) · [광주시](https://www.gwangju.go.kr) · [대전시](https://www.daejeon.go.kr) · [울산시](https://www.ulsan.go.kr) · [세종시](https://www.sejong.go.kr) — 각 시청 홈페이지 footer RSS |
| **시·군·구 단위** | RSSHub [`/gov/:region/:board`](https://docs.rsshub.app/) 또는 RSS-Bridge로 우회 |

---

## 5\. 한국 기술 블로그 RSS

> [`maczniak/awesome-korean-techblog`](https://github.com/maczniak/awesome-korean-techblog) 기반 + 활성 피드만 정리. IT산업 동향 모니터링용.

| 회사 | RSS |
| --- | --- |
| ⚠️ [**네이버 D2**](https://d2.naver.com) | [https://d2.naver.com/d2.atom](https://d2.naver.com/d2.atom) |
| ⚠️ [**카카오**](https://tech.kakao.com) | [https://tech.kakao.com/feed/](https://tech.kakao.com/feed/) |
| ⚠️ [**카카오엔터프라이즈**](https://tech.kakaoenterprise.com) | [https://tech.kakaoenterprise.com/feed](https://tech.kakaoenterprise.com/feed) |
| ⚠️ [**라인 (LY)**](https://techblog.lycorp.co.jp) | [https://techblog.lycorp.co.jp/ko/feed/index.xml](https://techblog.lycorp.co.jp/ko/feed/index.xml) |
| ⚠️ [**우아한형제들**](https://techblog.woowahan.com) | [https://techblog.woowahan.com/feed/](https://techblog.woowahan.com/feed/) |
| ⚠️ [**토스 (Viva Republica)**](https://toss.tech) | [https://toss.tech/rss.xml](https://toss.tech/rss.xml) |
| ⚠️ [**쿠팡 엔지니어링**](https://medium.com/coupang-engineering) | [https://medium.com/feed/coupang-engineering](https://medium.com/feed/coupang-engineering) |
| ⚠️ [**당근 (당근마켓)**](https://medium.com/daangn) | [https://medium.com/feed/daangn](https://medium.com/feed/daangn) |
| ⚠️ [**마켓컬리**](https://helloworld.kurly.com) | [https://helloworld.kurly.com/feed.xml](https://helloworld.kurly.com/feed.xml) |
| ⚠️ [**데브시스터즈**](https://tech.devsisters.com) | [https://tech.devsisters.com/rss.xml](https://tech.devsisters.com/rss.xml) |
| ⚠️ [**무신사**](https://medium.com/musinsa-tech) | [https://medium.com/feed/musinsa-tech](https://medium.com/feed/musinsa-tech) |
| ⚠️ [**직방**](https://medium.com/zigbang) | [https://medium.com/feed/zigbang](https://medium.com/feed/zigbang) |
| ⚠️ [**왓챠**](https://medium.com/watcha) | [https://medium.com/feed/watcha](https://medium.com/feed/watcha) |
| ⚠️ [**뱅크샐러드**](https://blog.banksalad.com) | [https://blog.banksalad.com/rss.xml](https://blog.banksalad.com/rss.xml) |
| ⚠️ [**하이퍼커넥트**](https://hyperconnect.github.io) | [https://hyperconnect.github.io/feed.xml](https://hyperconnect.github.io/feed.xml) |
| ⚠️ [**요기요**](https://techblog.yogiyo.co.kr) | [https://techblog.yogiyo.co.kr/feed](https://techblog.yogiyo.co.kr/feed) |
| ⚠️ [**쏘카**](https://tech.socarcorp.kr) | [https://tech.socarcorp.kr/feed](https://tech.socarcorp.kr/feed) |
| ⚠️ [**리디**](https://www.ridicorp.com) | [https://www.ridicorp.com/feed](https://www.ridicorp.com/feed) |
| ❌ [**NHN Toast Meetup**](https://meetup.toast.com) | `meetup.toast.com/rss` — 사이트 메뉴 변경, RSS 미상 → 사이트 직접 확인 |
| ⚠️ [**GeekNews**](https://news.hada.io) | [https://feeds.feedburner.com/geeknews-feed](https://feeds.feedburner.com/geeknews-feed) (또는 [news.hada.io/rss/news](https://news.hada.io/rss/news)) |
| ⚠️ [**Lunit** (의료 AI)](https://blog.lunit.io) | [https://blog.lunit.io/feed/](https://blog.lunit.io/feed/) |
| ⚠️ [**TensorFlow Korea**](https://tensorflow.blog) | [https://tensorflow.blog/feed/](https://tensorflow.blog/feed/) |
| ⚠️ [**AWS 한국 블로그**](https://aws.amazon.com/ko/blogs/korea/) | [https://aws.amazon.com/ko/blogs/korea/feed/](https://aws.amazon.com/ko/blogs/korea/feed/) |

---

## 6\. 글로벌 RSS — 데이터저널리즘 필수

### 6-1. 종합 뉴스

| 매체 | URL |
| --- | --- |
| ❌ [**Reuters**](https://www.reuters.com) | `feeds.reuters.com/Reuters/worldNews` — Reuters는 2020년 자체 RSS 폐지 → **RSSHub** [`/reuters/:category/:topic`](https://docs.rsshub.app/routes/traditional-media#reuters) 사용 |
| ✅ [**BBC News**](https://www.bbc.com/news) | [https://feeds.bbci.co.uk/news/rss.xml](https://feeds.bbci.co.uk/news/rss.xml), [`world/rss.xml`](https://feeds.bbci.co.uk/news/world/rss.xml), [`business/rss.xml`](https://feeds.bbci.co.uk/news/business/rss.xml), [`technology/rss.xml`](https://feeds.bbci.co.uk/news/technology/rss.xml) |
| ✅ [**The Guardian**](https://www.theguardian.com) | [https://www.theguardian.com/world/rss](https://www.theguardian.com/world/rss) (대분야 단위 다수 — `/business/rss`, `/uk/rss`, `/technology/rss` 등) |
| ✅ [**NYT**](https://www.nytimes.com) | [https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml](https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml), [`World.xml`](https://rss.nytimes.com/services/xml/rss/nyt/World.xml), [`Business.xml`](https://rss.nytimes.com/services/xml/rss/nyt/Business.xml), [`Technology.xml`](https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml) |
| ⚠️ [**Washington Post**](https://www.washingtonpost.com) | [http://feeds.washingtonpost.com/rss/world](http://feeds.washingtonpost.com/rss/world) (다수 카테고리 페이지 footer 참조) |
| ✅ [**Al Jazeera**](https://www.aljazeera.com) | [https://www.aljazeera.com/xml/rss/all.xml](https://www.aljazeera.com/xml/rss/all.xml) |
| ❌ [**AP News**](https://apnews.com) | `feeds.apnews.com/rss/apf-topnews` — AP 자체 RSS는 폐지/제한 → **RSSHub** [`/ap/:topic`](https://docs.rsshub.app/) 사용 권장 |
| ✅ [**NPR**](https://www.npr.org) | [https://feeds.npr.org/1001/rss.xml](https://feeds.npr.org/1001/rss.xml) |
| ✅ [**Deutsche Welle**](https://www.dw.com) | [https://rss.dw.com/rdf/rss-en-all](https://rss.dw.com/rdf/rss-en-all) |
| ✅ [**France 24**](https://www.france24.com/en/) | [https://www.france24.com/en/rss](https://www.france24.com/en/rss) |
| ⚠️ [**Asahi (영문)**](https://www.asahi.com/ajw/) | [https://www.asahi.com/ajw/rss/news.rdf](https://www.asahi.com/ajw/rss/news.rdf) |
| ⚠️ [**Nikkei Asia**](https://asia.nikkei.com) | [https://asia.nikkei.com/rss](https://asia.nikkei.com/rss) |
| ✅ [**SCMP**](https://www.scmp.com) | [https://www.scmp.com/rss/91/feed](https://www.scmp.com/rss/91/feed) |
| ⚠️ [**Xinhua (English)**](http://english.news.cn) | [http://english.news.cn/rss/index.xml](http://english.news.cn/rss/index.xml) |

### 6-2. 데이터저널리즘 전문

| 출처 | URL |
| --- | --- |
| ✅ [**GIJN** (Global Investigative Journalism Network)](https://gijn.org) | [https://gijn.org/feed/](https://gijn.org/feed/) |
| ✅ [**DataJournalism.com (EJC)**](https://datajournalism.com) | [https://datajournalism.com/feed](https://datajournalism.com/feed) |
| ✅ [**The Markup**](https://themarkup.org) | [https://themarkup.org/feeds/rss.xml](https://themarkup.org/feeds/rss.xml) |
| ✅ [**ProPublica**](https://www.propublica.org) | [https://www.propublica.org/feeds/propublica/main](https://www.propublica.org/feeds/propublica/main) |
| ⚠️ [**Reuters Graphics**](https://www.reuters.com/graphics/) | RSSHub [`/reuters/graphics`](https://docs.rsshub.app/) |
| ✅ [**FiveThirtyEight**](https://fivethirtyeight.com) | [https://fivethirtyeight.com/all/feed/](https://fivethirtyeight.com/all/feed/) |
| ✅ [**Our World in Data**](https://ourworldindata.org) | [https://ourworldindata.org/atom.xml](https://ourworldindata.org/atom.xml) |
| ✅ [**Bellingcat**](https://www.bellingcat.com) | [https://www.bellingcat.com/feed/](https://www.bellingcat.com/feed/) |
| [**NICAR (IRE)**](https://www.ire.org/nicar/) | 메일링/이벤트 위주 |

### 6-3. 학술·연구

| 출처 | URL/방법 |
| --- | --- |
| ✅ [**arXiv**](https://arxiv.org) (분야별) | [https://rss.arxiv.org/rss/cs](https://rss.arxiv.org/rss/cs) — 분야: `cs`, `math`, `physics`, `q-bio`, `q-fin`, `stat`, `econ` 등 |
| ✅ **arXiv** (서브분야) | 점 표기: [`cs.AI`](https://rss.arxiv.org/rss/cs.AI), [`cs.CL`](https://rss.arxiv.org/rss/cs.CL), [`stat.ML`](https://rss.arxiv.org/rss/stat.ML), [`econ.EM`](https://rss.arxiv.org/rss/econ.EM) |
| ✅ **arXiv** (복수 결합) | [https://rss.arxiv.org/rss/cs.AI+stat.ML](https://rss.arxiv.org/rss/cs.AI+stat.ML) (요청당 최대 2,000건) |
| ⚠️ [**bioRxiv**](https://www.biorxiv.org) / [**medRxiv**](https://www.medrxiv.org) | 분야별 RSS, biorxiv.org/medrxiv.org 사이트 footer |
| ✅ [**Nature**](https://www.nature.com) | [https://www.nature.com/nature.rss](https://www.nature.com/nature.rss) (저널별 RSS 다수) |
| ⚠️ [**Science (AAAS)**](https://www.science.org) | [https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science](https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science) |
| ✅ [**PLOS ONE**](https://journals.plos.org/plosone/) | [https://journals.plos.org/plosone/feed/atom](https://journals.plos.org/plosone/feed/atom) |
| ⚠️ [**PNAS**](https://www.pnas.org) | [https://www.pnas.org/action/showFeed?type=etoc&feed=rss&jc=pnas](https://www.pnas.org/action/showFeed?type=etoc&feed=rss&jc=pnas) |
| [**PubMed Search**](https://pubmed.ncbi.nlm.nih.gov) | NCBI E-utilities로 검색 → RSS 변환 가능 |
| [**Google Scholar Alerts**](https://scholar.google.com) | 이메일 alert만 — email-to-RSS 변환기 사용 ([Kill the Newsletter](https://kill-the-newsletter.com/), [FollowThatPage](https://www.followthatpage.com/)) |
| [**OpenAlex**](https://openalex.org) | RSS 없음, API로 폴링 후 자체 RSS 생성 |
| [**SSRN**](https://www.ssrn.com) / [**RePEc**](https://www.repec.org) | 분야별 RSS |
| [**IEEE Xplore**](https://ieeexplore.ieee.org) | 저자/주제 검색 결과 RSS |

### 6-4. 정부·국제기구

| 출처 | URL |
| --- | --- |
| ⚠️ [**White House**](https://www.whitehouse.gov) | RSSHub [`/whitehouse/:category`](https://docs.rsshub.app/) |
| ✅ [**UN News**](https://news.un.org) | [https://news.un.org/feed/subscribe/en/news/all/rss.xml](https://news.un.org/feed/subscribe/en/news/all/rss.xml) |
| ✅ [**WHO**](https://www.who.int) | [https://www.who.int/rss-feeds/news-english.xml](https://www.who.int/rss-feeds/news-english.xml) |
| ⚠️ [**World Bank**](https://www.worldbank.org) | News & Press 페이지 RSS |
| ⚠️ [**IMF**](https://www.imf.org) | [https://www.imf.org/external/rss/feeds.aspx](https://www.imf.org/external/rss/feeds.aspx) (다수) |
| ⚠️ [**OECD**](https://www.oecd.org) | 보도자료·간행물 RSS |
| ⚠️ [**EU Commission**](https://ec.europa.eu) | [https://ec.europa.eu/commission/presscorner/api/rss](https://ec.europa.eu/commission/presscorner/api/rss) |
| ⚠️ [**US Federal Register**](https://www.federalregister.gov) | 분야별 RSS |
| ✅ [**SEC EDGAR Filings**](https://www.sec.gov/edgar) | 검색 결과 Atom — 예: [https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=&output=atom](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=&output=atom) (Apple) |
| ⚠️ [**FRED Economic Data**](https://fred.stlouisfed.org) | 시계열별 RSS — `https://fredaccount.stlouisfed.org/rss/series/...` |

### 6-5. 기술·연구소 블로그 (AI/ML)

| 출처 | URL |
| --- | --- |
| ⚠️ [**OpenAI**](https://openai.com) | [https://openai.com/blog/rss/](https://openai.com/blog/rss/) (사이트 개편 후 라우트 변동 가능) |
| ✅ [**Anthropic**](https://www.anthropic.com) | [https://www.anthropic.com/rss.xml](https://www.anthropic.com/rss.xml) |
| ⚠️ [**DeepMind**](https://deepmind.google) | [https://deepmind.com/blog/feed/basic/](https://deepmind.com/blog/feed/basic/) (도메인 deepmind.google로 일부 마이그레이션) |
| ⚠️ [**Google AI**](https://blog.google) | [https://blog.google/technology/ai/rss/](https://blog.google/technology/ai/rss/) |
| ⚠️ [**Meta AI / FAIR**](https://ai.meta.com) | [https://research.fb.com/blog/feed/](https://research.fb.com/blog/feed/) (도메인 ai.meta.com로 마이그레이션 진행 중) |
| ✅ [**Microsoft Research**](https://www.microsoft.com/en-us/research/) | [https://www.microsoft.com/en-us/research/feed/](https://www.microsoft.com/en-us/research/feed/) |
| ✅ [**BAIR (Berkeley)**](https://bair.berkeley.edu) | [https://bair.berkeley.edu/blog/feed.xml](https://bair.berkeley.edu/blog/feed.xml) |
| ✅ [**Apple ML**](https://machinelearning.apple.com) | [https://machinelearning.apple.com/rss.xml](https://machinelearning.apple.com/rss.xml) |
| ✅ [**Hugging Face**](https://huggingface.co) | [https://huggingface.co/blog/feed.xml](https://huggingface.co/blog/feed.xml) |
| ⚠️ [**Distill**](https://distill.pub) | [https://distill.pub/rss.xml](https://distill.pub/rss.xml) (활성 발행 사실상 중단) |
| [**Stanford HAI**](https://hai.stanford.edu) / [**NLP**](https://nlp.stanford.edu) | 페이지별 RSS 확인 |

---

## 7\. RSSHub — RSS가 없는 사이트를 RSS로

### 7-1. 개요

-   **현황 (2026-05)**: 5,000+ 글로벌 인스턴스, 900+ 라우트, 200+ 사이트 지원, AGPL-3.0
-   **공식 인스턴스**: [https://rsshub.app](https://rsshub.app) (불안정·rate-limit 잦음 — **자체 호스팅 권장**)
-   **저장소**: [https://github.com/DIYgod/RSSHub](https://github.com/DIYgod/RSSHub)
-   **문서**: [https://docs.rsshub.app/](https://docs.rsshub.app/)
-   2025-12 MCP를 Linux Foundation에 기증, RSSHub 자체도 [Folo](https://follow.is) (AI RSS reader)와 페어링

### 7-2. 라우트 사용 예

도메인 + 라우트 조합으로 RSS URL 생성:

```
https://rsshub.app/twitter/user/elonmusk
https://rsshub.app/youtube/channel/UCxxxxxxxxxxx
https://rsshub.app/telegram/channel/durov
https://rsshub.app/github/issue/owner/repo
https://rsshub.app/bbc/world
https://rsshub.app/reuters/world/asia
https://rsshub.app/jtbc/news/politics
https://rsshub.app/joongang/news/:category    # 중앙일보 (RSS 폐지 후 권장)
https://rsshub.app/naver/news/:category
https://rsshub.app/bok/press                   # 한국은행 보도자료
https://rsshub.app/aeaweb/aer                  # 학술지: American Economic Review
https://rsshub.app/science/current             # Science 최신호
https://rsshub.app/trendingpapers/papers/cs.CV/7days/cited
```

전체 라우트 검색: [https://docs.rsshub.app/routes/](https://docs.rsshub.app/routes/) 또는 RSSHub Radar 브라우저 확장.

### 7-3. 자체 호스팅 — 최단 1줄

```bash
docker run -d --name rsshub -p 1200:1200 \\
  -e CACHE_EXPIRE=3600 \\
  -e ACCESS_KEY=your_secret \\
  diygod/rsshub
```

### 7-4. 자체 호스팅 — Docker Compose (Redis + Puppeteer)

```yaml
# docker-compose.yml
version: '3'
services:
  rsshub:
    image: diygod/rsshub:chromium-bundled   # JS 렌더링 사이트용
    restart: always
    ports:
      - "1200:1200"
    environment:
      NODE_ENV: production
      CACHE_TYPE: redis
      REDIS_URL: 'redis://redis:6379/'
      CACHE_EXPIRE: 3600
      ACCESS_KEY: ${RSSHUB_ACCESS_KEY}
      PUPPETEER_WS_ENDPOINT: 'ws://browserless:3000'
      GITHUB_ACCESS_TOKEN: ${GITHUB_TOKEN}
    depends_on: [redis, browserless]

  browserless:
    image: browserless/chrome
    restart: always
    ulimits:
      core: { hard: 0, soft: 0 }

  redis:
    image: redis:alpine
    restart: always
    volumes: ['redis-data:/data']

volumes:
  redis-data:
```

```bash
echo "RSSHUB_ACCESS_KEY=$(openssl rand -hex 16)" > .env
echo "GITHUB_TOKEN=ghp_..." >> .env
docker-compose up -d
```

### 7-5. Nginx + SSL (DigitalOcean SGP1 가정)

```nginx
# /etc/nginx/sites-enabled/rsshub
server {
    server_name rss.your-domain.com;
    location / {
        proxy_pass http://127.0.0.1:1200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_valid 200 1h;
    }
}
```

```bash
sudo certbot --nginx -d rss.your-domain.com
```

### 7-6. 자동 업데이트 (Watchtower)

```bash
docker run -d --name watchtower \\
  -v /var/run/docker.sock:/var/run/docker.sock \\
  containrrr/watchtower
```

### 7-7. RSSHub Radar (브라우저 확장)

방문 중인 사이트의 RSSHub 라우트를 자동 탐지·구독. Chrome/Firefox/Edge 모두 지원.

-   iOS: **RSSBud**
-   Android: **RSSAid** (Flutter)

### 7-8. 데이터저널리즘 활용 시나리오

-   **소셜미디어 모니터링**: Twitter/X, Telegram 채널, YouTube 채널, Bluesky → RSS
-   **국회·정부**: 자체 라우트 부족하면 CssSelectorBridge로 직접 작성 (§8)
-   **주가·암호화폐**: 거래소 공지 RSS화 (Upbit/Binance)
-   **법원 판결문**: 신규 게시물 트래킹
-   **언론사 칼럼니스트**: 특정 기자 글만 추출
-   **광고/입찰 공고**: [조달청 나라장터](https://www.g2b.go.kr) 신규공고 알림

---

## 8\. RSS-Bridge — PHP 대안

### 8-1. 개요

-   **저장소**: [https://github.com/RSS-Bridge/rss-bridge](https://github.com/RSS-Bridge/rss-bridge)
-   **공식 호스팅**: [https://rss-bridge.org/bridge01/](https://rss-bridge.org/bridge01/) (비상업적 사용 한정)
-   **지원 사이트**: 500+ (Reuters, BBC, GitHub, Google Scholar, Reddit, YouTube, ArtStation, AP, Eurogamer 등)
-   **전제**: PHP 7.4+, Nginx/Apache + php-fpm

### 8-2. Docker 1줄 배포

```bash
docker run -d --name rss-bridge \\
  --publish 3000:80 \\
  --restart unless-stopped \\
  rssbridge/rss-bridge:latest
```

브라우저 → `http://your-server:3000` → 브리지 선택 → 파라미터 입력 → 생성된 RSS URL 복사.

### 8-3. RSSHub vs RSS-Bridge 비교

| 항목 | RSSHub | RSS-Bridge |
| --- | --- | --- |
| 언어 | Node.js + TypeScript | PHP |
| 라우트 수 | 900+ | 500+ |
| 인기 정도 | 압도적 (5,000+ instances) | 견실 |
| 한국 사이트 지원 | 더 많음 (네이버/JTBC 등) | 일반 |
| Filter / Merge | 약함 | 강력 (CSS selector, regex, merge) |
| 자체 라우트 작성 | TS, 약간 학습곡선 | PHP, 매우 쉬움 |
| 권장 용도 | **기본값** | RSSHub에 없는 사이트, 강력 필터 |

> **실전 권장**: 둘 다 배포해서 보완 사용. RSSHub 1200, RSS-Bridge 3000 포트 분리.

### 8-4. CssSelectorBridge — 임의 사이트 RSS화

RSS-Bridge에 내장된 가장 유용한 브리지. 사이트 URL과 CSS selector만 주면 RSS 생성. 한국 정부 게시판 표준 솔루션 외 사이트(예: 자치단체 자체 게시판, 작은 언론사)에 효과적.

**입력 예**:

-   URL: `https://www.example-gov.kr/notices/list.do`
-   Article selector: `ul.notice-list li`
-   Title selector: `a.title`
-   Content selector: `div.summary`
-   Date selector: `span.date`

→ 자동으로 RSS 2.0 피드 생성.

### 8-5. RSS-Bridge 강력 기능

-   **MergeBridge**: 여러 RSS를 하나로 병합
-   **FeedExpanderBridge**: truncated 피드의 본문을 자동으로 fetch
-   **FilterBridge**: 키워드/regex로 항목 필터링
-   **WordPressBridge**: WordPress 사이트 자동 인식

---

## 9\. Python 처리 — feedparser & fastfeedparser

### 9-1. 라이브러리 비교

| 라이브러리 | 특징 | 용도 |
| --- | --- | --- |
| [**feedparser**](https://feedparser.readthedocs.io) (6.0.12) | 15년+ 검증, RSS 0.9~2.0/Atom/JSON Feed/RDF/CDF, 깨진 XML 관용 | 표준 (호환성 우선) |
| [**fastfeedparser**](https://github.com/kagisearch/fastfeedparser) (Kagi) | feedparser의 25~50배 빠름, 동일 API | 1,000개 이상 대량 |
| [**atoma**](https://github.com/NicolasLM/atoma) | 타입 안전, Atom/RSS/JSON | 모던 코드 베이스 |
| **lxml + ElementTree** | 가장 빠름, 수동 파싱 | 커스텀 네임스페이스 |

### 9-2. 설치 및 기본 사용

```bash
pip install feedparser fastfeedparser httpx aiohttp python-dotenv
```

```python
# basic_feed.py
import feedparser

d = feedparser.parse("https://www.khan.co.kr/rss/rssdata/total_news.xml")
print(d.feed.title)            # 채널 제목
print(len(d.entries), "기사")
for e in d.entries[:5]:
    print(e.published, "|", e.title)
    print("  ", e.link)
    print("  ", e.get("summary", "")[:100])
```

### 9-3. 비동기 대량 수집 (10초 → 100개 피드)

```python
# fetch_many.py
import asyncio, httpx, feedparser
from datetime import datetime

# 본 가이드 §3에서 ✅ 마크된 검증 피드만 사용
FEEDS = [
    ("경향",     "https://www.khan.co.kr/rss/rssdata/total_news.xml"),
    ("동아",     "https://rss.donga.com/total.xml"),
    ("서울신문", "https://www.seoul.co.kr/xml/rss/rss_top.xml"),
    ("뉴시스",   "https://www.newsis.com/RSS/sokbo.xml"),
    ("한겨레",   "https://www.hani.co.kr/rss/"),
    ("조선",     "https://www.chosun.com/arc/outboundfeeds/rss/"),
    ("연합",     "https://www.yna.co.kr/rss/news.xml"),
    ("KBS",      "https://news.kbs.co.kr/rss/news.xml"),
    ("MBC",      "https://imnews.imbc.com/rss/news/news_00.xml"),
    ("YTN",      "https://www.ytn.co.kr/_comm/rss.php"),
    # ⚠️ 도메인 변경/폐지된 매체는 RSSHub 라우트로 대체
    ("중앙",     "https://rsshub.app/joongang/news/all"),
    ("한국일보", "https://rsshub.app/hankookilbo/all"),
    ("헤럴드",   "https://rsshub.app/heraldcorp/news"),
    # ... 수백 개 가능
]

async def fetch(client, name, url):
    try:
        r = await client.get(url, timeout=10, follow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0 DataJournLab/1.0"})
        d = feedparser.parse(r.content)
        return [(name, e.get("title",""), e.get("link",""),
                 e.get("published", e.get("updated","")),
                 e.get("summary", "")[:300])
                for e in d.entries]
    except Exception as ex:
        print(f"[err] {name}: {ex}")
        return []

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, n, u) for n, u in FEEDS]
        results = await asyncio.gather(*tasks)
    flat = [item for batch in results for item in batch]
    print(f"총 {len(flat)}개 수집 ({datetime.now().isoformat()})")
    return flat

if __name__ == "__main__":
    items = asyncio.run(main())
```

### 9-4. fastfeedparser (대량 처리)

```python
import fastfeedparser
feed = fastfeedparser.parse("https://www.khan.co.kr/rss/rssdata/total_news.xml")
for entry in feed.entries:
    print(entry.title, entry.link, entry.published)
```

**벤치마크**: 200개 피드 38초 → **0.46초** (Kagi 사례, 27배). API는 feedparser와 거의 동일.

### 9-5. 중복 제거 + SQLite 적재

```python
# store.py
import sqlite3, hashlib, feedparser
from datetime import datetime

conn = sqlite3.connect("news.db")
conn.execute("""CREATE TABLE IF NOT EXISTS articles(
    id TEXT PRIMARY KEY, source TEXT, title TEXT, url TEXT,
    pubdate TEXT, summary TEXT, fetched_at TEXT)""")
conn.execute("CREATE INDEX IF NOT EXISTS idx_source_pubdate ON articles(source, pubdate)")

def stable_id(url, title):
    """URL + title 해시로 안정적 ID. 캠페인 파라미터로 URL이 바뀌어도 안정"""
    # 정규화: ?utm_*, #fragment 등 제거
    clean_url = url.split("?")[0].split("#")[0]
    return hashlib.sha1((clean_url + "|" + title).encode()).hexdigest()

def upsert(source, entries):
    rows = []
    for e in entries:
        url = e.get("link","")
        title = e.get("title","")
        rows.append((stable_id(url, title), source, title, url,
                     e.get("published", e.get("updated","")),
                     (e.get("summary","") or "")[:1000],
                     datetime.now().isoformat()))
    conn.executemany("INSERT OR IGNORE INTO articles VALUES(?,?,?,?,?,?,?)", rows)
    conn.commit()
    return conn.total_changes

d = feedparser.parse("https://www.khan.co.kr/rss/rssdata/total_news.xml")
new_count = upsert("경향신문", d.entries)
print(f"신규 {new_count}건 적재")
```

### 9-6. ETag·Last-Modified 캐시 활용

```python
# 304 Not Modified 활용으로 트래픽 절약
import feedparser

# 첫 호출
d = feedparser.parse(url)
etag, modified = d.get("etag"), d.get("modified")

# 다음 호출
d2 = feedparser.parse(url, etag=etag, modified=modified)
if d2.status == 304:
    print("변경 없음 — 스킵")
```

---

## 10\. RSS + Gemini 통합 (LLM 필터링·요약)

### 10-1. 핵심 아이디어

무차별 수집은 인지과부하. **LLM을 필터로 사용**하여 관심 키워드·주제·논조에 맞는 기사만 선별 → 요약 → 알림.

**3단 필터** (비용 최적):

1.  **키워드 필터** (무료, instant): 명백히 무관한 항목 제거
2.  **임베딩 유사도 필터** (저비용): 의미적 유사 항목 추출
3.  **LLM 정밀 필터·요약** (고비용): Top N에 대해서만 호출

### 10-2. 미니 파이프라인 (한 파일)

```python
# rss_to_gemini.py
import os, asyncio, json
from datetime import datetime
from dotenv import load_dotenv
import httpx, feedparser
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# §3에서 ✅ 검증된 피드 위주
FEEDS = [
    ("경향", "https://www.khan.co.kr/rss/rssdata/total_news.xml"),
    ("동아", "https://rss.donga.com/total.xml"),
    ("뉴시스", "https://www.newsis.com/RSS/sokbo.xml"),
    ("한겨레", "https://www.hani.co.kr/rss/"),
    ("조선", "https://www.chosun.com/arc/outboundfeeds/rss/"),
    ("연합", "https://www.yna.co.kr/rss/news.xml"),
    # ... 본인 관심 매체 추가
]

KEYWORDS = ["인공지능", "AI", "데이터", "프라이버시", "저널리즘"]
INTEREST = "한국 미디어 산업의 AI 도입과 저널리즘 윤리"

# --- 1) 수집 ---
async def fetch(c, name, url):
    try:
        r = await c.get(url, timeout=10,
                        headers={"User-Agent": "Mozilla/5.0"})
        d = feedparser.parse(r.content)
        return [(name, e.get("title",""), e.get("link",""),
                 e.get("published", e.get("updated","")),
                 (e.get("summary","") or "")[:600])
                for e in d.entries]
    except Exception:
        return []

async def collect():
    async with httpx.AsyncClient() as c:
        batches = await asyncio.gather(*[fetch(c, n, u) for n, u in FEEDS])
    return [x for b in batches for x in b]

# --- 2) 1차 키워드 필터 (LLM 호출 절약) ---
def keyword_filter(items):
    return [it for it in items
            if any(k.lower() in (it[1] + it[4]).lower() for k in KEYWORDS)]

# --- 3) Gemini 의미 필터 ---
def semantic_filter(items, batch_size=20, threshold=0.6):
    """배치 단위로 LLM에 보내 관련성 0~1 점수와 한 줄 이유 받음"""
    selected = []
    for i in range(0, len(items), batch_size):
        chunk = items[i:i+batch_size]
        prompt = f"""다음은 뉴스 헤드라인+요약 목록이다.
관심 주제: "{INTEREST}"
각 항목에 대해 관련성 점수(0~1)와 한 줄 사유를 JSON 배열로만 반환하라.
형식: [{{"idx":0,"score":0.92,"reason":"..."}}, ...]

목록:
""" + "\\n".join(
            f"[{j}] {it[1]} | {it[4][:200]}"
            for j, it in enumerate(chunk))
        try:
            resp = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )
            scored = json.loads(resp.text)
            for s in scored:
                if s.get("score", 0) >= threshold:
                    it = chunk[s["idx"]]
                    selected.append((it, s["score"], s["reason"]))
        except Exception as e:
            print("[err filter]", e)
    return selected

# --- 4) 요약 ---
def summarize(items):
    bundled = "\\n\\n".join(
        f"[{i+1}] ({it[0][0]}) {it[0][1]}\\n{it[0][4][:400]}\\n링크: {it[0][2]}"
        for i, it in enumerate(items[:15]))
    prompt = f"""아래는 오늘 수집된 관련 뉴스 {len(items)}건 중 상위 사례다.
관심 주제 "{INTEREST}"에 대한 데이터저널리즘 관점의 인사이트를:
1) 핵심 흐름 (3줄)
2) 주목할 보도 5건 (제목·매체·한 줄 이유·URL)
3) 추가 취재 가능한 데이터 가설 2개
순으로 정리해줘.

{bundled}"""
    return client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3),
    ).text

# --- 5) 실행 ---
async def main():
    raw = await collect()
    print(f"수집 {len(raw)}건")
    f1 = keyword_filter(raw)
    print(f"키워드 필터 통과 {len(f1)}건")
    f2 = semantic_filter(f1)
    print(f"의미 필터 통과 {len(f2)}건")
    if f2:
        print("\\n=== 일일 브리핑 ===\\n")
        print(summarize(f2))

if __name__ == "__main__":
    asyncio.run(main())
```

### 10-3. 비용·속도 가이드

| 단계 | 도구 | 100건 처리 | 비고 |
| --- | --- | --- | --- |
| 키워드 필터 | Python | 0.01초 | 무료 |
| 임베딩 필터 | gemini-embedding-001 | ~2초, ~$0.0001 | 배치 |
| 의미 필터 | gemini-2.5-flash-lite | ~10초, ~$0.001 | 배치 20건 |
| 요약 | gemini-2.5-flash-lite | ~5초, ~$0.0005 | Top 15건 |

→ **일 100건 처리에 약 $0.002**. 무료 tier로도 충분. RPM 제한 시 `time.sleep(2)` 또는 exponential backoff.

### 10-4. 임베딩 기반 의미 검색 (LLM 호출 90% 절감)

```python
# embed_filter.py
import numpy as np
from google import genai
from google.genai import types

client = genai.Client()

def embed(texts):
    r = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"))
    return np.array([e.values for e in r.embeddings])

def cosine(A, b):
    A_norm = A / np.linalg.norm(A, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b)
    return A_norm @ b_norm

# 1) 관심 주제 임베딩
topic_vec = embed([INTEREST])[0]

# 2) 수집된 기사 임베딩 (배치)
texts = [it[1] + " " + it[4] for it in raw]
items_vec = embed(texts)

# 3) 코사인 유사도 정렬, Top 30만 LLM에 전달
sims = cosine(items_vec, topic_vec)
top_idx = sims.argsort()[::-1][:30]
top_items = [raw[i] for i in top_idx]
```

### 10-5. 일일 브리핑 → Telegram 자동 발송

```python
# notify.py
import os, requests
TG_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TG_CHAT  = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        data={"chat_id": TG_CHAT, "text": text[:4000],
              "parse_mode": "Markdown", "disable_web_page_preview": True},
        timeout=10)

# 매일 오전 7시 cron
# 0 7 * * * /home/ubuntu/.venv/bin/python /home/ubuntu/rss/daily.py
```

---

## 11\. RSS-MCP 서버 (Claude·Gemini와 직접 연결)

### 11-1. 즉시 사용 가능한 MCP

| 서버 | 설명 | 출처 |
| --- | --- | --- |
| **News MCP (cytrexsgr-news-mcp)** | RSS 통합 + AI 분석, 20+ 도구, PostgreSQL 백엔드, 자동 분석 시스템 | LobeHub |
| **RSS Reader MCP (Ottoman Archive)** | FastMCP 기반, 뉴스레터/RSS 통합 (AI + History Collaboratory) | LobeHub |
| **Crypto RSS MCP (kukapay)** | 암호화폐 RSS 큐레이션 (RAW.opml 데이터베이스) | GitHub |
| **Cointelegraph MCP** | 17 RSS 카테고리 통합 | LobeHub |
| **GeekNews MCP** | 한국 IT 뉴스 GeekNews 통합 (BeautifulSoup 스크래핑) | LobeHub |
| **MCP Claude Hacker News (imprvhub)** | HN 스토리·코멘트 (RSS+API) | GitHub |
| **TrendRadar MCP** | 다중 핫토픽 어그리게이션 (한국 포함) | LobeHub |

### 11-2. 직접 만들기 (FastMCP, 권장)

```python
# rss_mcp.py
from fastmcp import FastMCP
import feedparser, httpx
from typing import List, Dict

mcp = FastMCP("Korean-News-RSS")

# §3에서 ✅ 검증된 피드만 사용
FEEDS = {
    "khan":     "https://www.khan.co.kr/rss/rssdata/total_news.xml",
    "donga":    "https://rss.donga.com/total.xml",
    "newsis":   "https://www.newsis.com/RSS/sokbo.xml",
    "seoul":    "https://www.seoul.co.kr/xml/rss/rss_top.xml",
    "hani":     "https://www.hani.co.kr/rss/",
    "chosun":   "https://www.chosun.com/arc/outboundfeeds/rss/",
    "yna":      "https://www.yna.co.kr/rss/news.xml",
    "kbs":      "https://news.kbs.co.kr/rss/news.xml",
    "mbc":      "https://imnews.imbc.com/rss/news/news_00.xml",
    "ytn":      "https://www.ytn.co.kr/_comm/rss.php",
    "hankyung": "https://rss.hankyung.com/economy.xml",
    "mk":       "https://www.mk.co.kr/rss/30000001/",
    "geeknews": "https://feeds.feedburner.com/geeknews-feed",
    # 폐지 매체는 RSSHub 라우트로 대체
    "joongang": "https://rsshub.app/joongang/news/all",
    "hankook":  "https://rsshub.app/hankookilbo/all",
    "herald":   "https://rsshub.app/heraldcorp/news",
}

@mcp.tool()
def list_sources() -> List[str]:
    """사용 가능한 RSS 소스 목록을 반환."""
    return list(FEEDS.keys())

@mcp.tool()
def fetch_feed(source: str, limit: int = 20) -> List[Dict]:
    """지정한 소스의 최신 기사를 limit개 반환.
    Args:
        source: list_sources()의 키 중 하나
        limit: 최대 기사 수 (기본 20)
    """
    if source not in FEEDS:
        return [{"error": "Unknown source. Use list_sources() first."}]
    r = httpx.get(FEEDS[source], timeout=10,
                  headers={"User-Agent": "Mozilla/5.0"})
    d = feedparser.parse(r.content)
    return [{
        "title":     e.get("title", ""),
        "link":      e.get("link", ""),
        "published": e.get("published", e.get("updated", "")),
        "summary":   (e.get("summary", "") or "")[:500],
    } for e in d.entries[:limit]]

@mcp.tool()
def search_across(keyword: str, sources: List[str] = None,
                  limit_per_source: int = 50) -> List[Dict]:
    """모든(또는 지정) 소스에서 키워드를 포함한 기사 검색.
    Args:
        keyword: 검색어
        sources: 검색 대상 소스 목록. None이면 전체.
        limit_per_source: 소스당 최대 기사 수
    """
    targets = sources or list(FEEDS.keys())
    hits = []
    for s in targets:
        try:
            for e in fetch_feed(s, limit_per_source):
                blob = (e.get("title", "") + e.get("summary", "")).lower()
                if keyword.lower() in blob:
                    hits.append({"source": s, **e})
        except Exception:
            pass
    return hits

@mcp.tool()
def google_news_search(query: str, hl: str = "ko", gl: str = "KR") -> List[Dict]:
    """Google News RSS 검색 — 한국어 기본.
    Args:
        query: 검색어 (OR 연산자 사용 가능)
        hl: 인터페이스 언어 (ko, en 등)
        gl: 지역 코드 (KR, US 등)
    """
    url = (f"https://news.google.com/rss/search?"
           f"q={query}&hl={hl}&gl={gl}&ceid={gl}:{hl}")
    r = httpx.get(url, timeout=10)
    d = feedparser.parse(r.content)
    return [{"title": e.title, "link": e.link,
             "published": e.get("published", "")}
            for e in d.entries[:30]]

if __name__ == "__main__":
    mcp.run()  # stdio
    # HTTP: mcp.run(transport="http", host="0.0.0.0", port=9100, path="/mcp")
```

### 11-3. Claude Desktop 등록

`claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\\Claude\\`):

```json
{
  "mcpServers": {
    "korean-rss": {
      "command": "python",
      "args": ["/abs/path/to/rss_mcp.py"]
    }
  }
}
```

Claude Desktop 재시작 후 도구 자동 인식. "한겨레와 경향에서 합계출산율 관련 기사 비교해줘" 같은 자연어 질의에 즉시 응답.

### 11-4. Gemini SDK에서 사용

```python
import asyncio, os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types

server_params = StdioServerParameters(command="python", args=["rss_mcp.py"])

async def ask():
    async with stdio_client(server_params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            resp = await client.aio.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents="한겨레·경향·조선에서 'AI 저널리즘' 관련 기사를 찾아 매체별 프레임 차이를 비교해줘.",
                config=types.GenerateContentConfig(tools=[session], temperature=0),
            )
            print(resp.text)

asyncio.run(ask())
```

### 11-5. 웹 배포 (DigitalOcean SGP1)

**systemd 서비스**:

```ini
# /etc/systemd/system/rss-mcp.service
[Unit]
Description=Korean News RSS MCP Server
After=network.target

[Service]
WorkingDirectory=/home/ubuntu/rss-mcp
ExecStart=/home/ubuntu/.venv/bin/python rss_mcp.py
Environment=PYTHONUNBUFFERED=1
Restart=always
User=ubuntu

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rss-mcp
```

**Nginx + SSL**:

```nginx
server {
    server_name rss-mcp.your-domain.com;
    location /mcp {
        proxy_pass http://127.0.0.1:9100/mcp;
        proxy_http_version 1.1;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Upgrade $http_upgrade;
    }
}
```

→ `https://rss-mcp.your-domain.com/mcp` 엔드포인트가 MCP-호환. Claude/Gemini/Cursor 모두 원격 등록 가능.

---

## 12\. 강의용 실습 프로젝트

### Lab 1. RSS 첫걸음 (1주차)

-   `feedparser` 설치 → 한겨레/조선 동시 수집 → DataFrame 변환
-   `pubDate` 파싱·시계열 그래프
-   **산출물**: 일주일치 헤드라인 표 + 발행 시각 분포 그래프

### Lab 2. 비동기 대량 수집 (2주차)

-   100개+ 한국 RSS를 `asyncio`로 수집
-   SQLite 적재 + 중복 제거 (GUID 기반)
-   "오늘의 헤드라인" 일일 보고서 자동 생성 (Markdown)
-   **산출물**: cron 등록한 일일 자동 수집기

### Lab 3. RSSHub 자체 호스팅 (3주차) ⭐

-   DigitalOcean droplet에 Docker로 RSSHub + Redis 배포
-   RSSHub Radar 확장으로 라우트 탐색
-   Twitter / YouTube / Telegram → RSS 변환 시연
-   **산출물**: `https://rss.학생도메인.com` 운영 인스턴스

### Lab 4. RSS-Bridge로 정부 사이트 RSS화 (4주차)

-   CssSelectorBridge로 환경부·금감원·자치단체 게시판 RSS 생성
-   입법예고 신규 알림 자동화
-   **산출물**: 학생이 선택한 미공개 RSS 사이트 5곳을 RSS화

### Lab 5. Gemini 의미 필터 (5~6주차)

-   키워드 + 임베딩 + LLM 3단 필터
-   일일 브리핑 자동 작성 (Markdown 템플릿)
-   텔레그램 봇으로 발송
-   **산출물**: 본인 관심 주제의 자동 브리핑 시스템

### Lab 6. 토픽 모델링·프레임 분석 (7~8주차)

-   1주~1개월 RSS 누적 → BERTopic / KcELECTRA 임베딩
-   매체별 프레임 비교 (한겨레 vs 조선)
-   Plotly 인터랙티브 시각화
-   **산출물**: 매체간 프레임 차이 인터랙티브 대시보드

### Lab 7. 학술 알림 시스템 (9주차)

-   arXiv 분야별 RSS + Google Scholar email-to-RSS
-   Gemini로 초록 한국어 요약·관심도 점수
-   Notion/Obsidian으로 자동 적재
-   **산출물**: 본인 연구분야 자동 논문 큐레이션 시스템

### Lab 8. 자기만의 RSS-MCP 서버 (10~11주차) ⭐

-   학생이 관심 분야 사이트를 RSSHub/RSS-Bridge로 RSS화
-   FastMCP로 wrapping → Claude Desktop 연결 시연
-   동료 검토 발표
-   **산출물**: 공개 MCP 서버 + 데모 영상

### Lab 9. Agentic 뉴스 모니터 (12~13주차)

-   LangGraph + Gemini + RSS-MCP + 검색 API
-   사용자 자연어 질의 → 관련 RSS 폴링 → 검증 → 리포트
-   서버님의 LangGraph 팩트체크 시스템과 결합 가능
-   **산출물**: 자연어로 조사 가능한 뉴스 에이전트

### Lab 10. 종합 평가 (14~15주차)

-   학생 1인당 특정 보도 분야(예: 부동산, 노동, 외교) 선택
-   RSS 수집 → 데이터 분석 → 인사이트 도출 → 기사 시안 작성
-   라이브 데모 + 보고서
-   **평가**: 자동화 수준 + 분석 깊이 + 저널리즘적 가치

---

## 13\. 프로덕션 운영 체크리스트

### 13-1. 안정성

-   User-Agent 헤더 설정 (`Mozilla/5.0 + 연구 목적 명시`)
-   타임아웃 10~15초, 실패 시 재시도 max 3회 + exponential backoff
-   HTTP 304 Not Modified 활용 (`ETag`/`Last-Modified` 캐시 헤더)
-   폴링 간격 **최소 1시간** 권장 (사이트 부하 윤리)
-   cron 또는 systemd timer로 스케줄 (`0 */2 * * *`)
-   에러 로그 → Sentry / Telegram 알림
-   **URL 작동 모니터링**: 주 1회 전체 피드 health-check, 죽은 URL은 RSSHub 라우트로 자동 fallback

### 13-2. 데이터

-   **GUID 기반 중복 제거** (URL이 캠페인 파라미터로 변경되어도 안정)
-   발행일 파싱 시 timezone 명시 (`feedparser`는 `*_parsed` 필드로 UTC tuple 제공)
-   본문 fetch 시 robots.txt 준수
-   RSS의 `summary`만 저장하고 본문 전문은 인용범위로 제한
-   DB 백업 (SQLite는 매일 `.backup`, 또는 PostgreSQL `pg_dump`)

### 13-3. 저작권·윤리

-   매체별 이용약관 확인 — RSS 활용 명시 여부
-   **재배포·미러링 금지** — 수집·분석·인용만
-   LLM 요약·인용 시 **원문 URL과 매체명** 의무 표기
-   한국 저작권법: 인용은 "정당한 범위" — 헤드라인+짧은 발췌 OK, 전문 재출판 NO
-   **언론사 본문 학습용 사용 금지** ([한국언론진흥재단 BIGKINDS](https://www.bigkinds.or.kr) 약관 참고)
-   EU AI Act / 한국 AI기본법 — 학습용 사용 시 별도 검토
-   학생 과제 결과물 외부 공개 시 IRB 또는 매체 사전 협의

### 13-4. 보안

-   RSSHub `ACCESS_KEY` 활성화 (공개 인스턴스 남용 방지)
-   DB는 SSH 터널 또는 VPN 내부에서만 접근
-   API 키는 `.env` + `.gitignore`
-   CORS 정책 명시 (RSSHub 자체 호스팅 시)
-   MCP 원격 서버는 OAuth/Bearer 인증 필수

---

## 14\. 트러블슈팅 (FAQ)

| 증상 | 원인·해결 |
| --- | --- |
| **`bozo=1`** | XML 파싱 경고. `d.bozo_exception` 확인. 대부분 무시해도 entries는 정상 |
| **빈 entries** | 사이트가 RSS 형식 변경 / 차단 / User-Agent 검사 → UA 변경, RSSHub 우회 |
| **403/429** | 폴링 과다 → 간격 늘리기, ETag 사용, 자체 RSSHub 운영 |
| **인코딩 깨짐** | `r.content` 대신 `r.text` 사용 또는 `feedparser.parse(r.content)` (바이트가 더 안전) |
| **pubDate 누락/이상** | `published_parsed` 또는 `updated_parsed` 우선 사용. 둘 다 없으면 `fetched_at`으로 대체 |
| **RSSHub 502** | Puppeteer 필요 라우트 → `chromium-bundled` 이미지 사용 |
| **JS 렌더링 사이트** | RSSHub 자체로 안 되면 RSS-Bridge `WebSubBridge` 또는 Playwright 직접 사용 |
| **네이버 뉴스 막힘** | 공식 RSS 종료 — Google News 검색 RSS + RSSHub `/naver/news` 우회 |
| **메모리 누수** | feedparser 대량 처리 시 fastfeedparser로 교체 (25배 빠르고 가벼움) |
| **중복 폭주** | GUID 비교 시 URL 정규화 (utm\_\* 파라미터 제거) |
| **Google News 결과 부족** | `q=` 파라미터에 `OR` 연산자, `site:` 필터 활용. `when:7d` 시간 필터도 가능 |
| **arXiv 2,000건 제한** | 분야 분할 또는 시간 윈도 분할 |
| **❌ 매체 RSS 작동 안 함** | 본 가이드 §3 "❌" 표시 매체는 RSSHub 라우트 사용. ⚠️ 매체는 fetch 후 entries 빈 상태면 폐지 가능성 — `RSSHub` fallback 자동화 권장 |

---

## 15\. 참고·추가 자료

### 도구

-   **RSSHub**: [https://docs.rsshub.app](https://docs.rsshub.app)
-   **RSS-Bridge**: [https://github.com/RSS-Bridge/rss-bridge](https://github.com/RSS-Bridge/rss-bridge)
-   **feedparser**: [https://feedparser.readthedocs.io](https://feedparser.readthedocs.io)
-   **fastfeedparser**: [https://github.com/kagisearch/fastfeedparser](https://github.com/kagisearch/fastfeedparser)
-   **atoma**: [https://github.com/NicolasLM/atoma](https://github.com/NicolasLM/atoma)
-   **FastMCP**: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)

### 큐레이션 디렉터리 (URL 검증 교차 확인용)

### RSS 리더 (self-host 추천)

-   [**FreshRSS**](https://freshrss.org) (PHP, 가장 가벼움) — 학생 개인용
-   [**Tiny Tiny RSS**](https://tt-rss.org) (PostgreSQL, 강력) — 강의실 공용
-   [**Miniflux**](https://miniflux.app) (Go, 미니멀) — Docker 1줄
-   [**Folo**](https://follow.is) (RSSHub와 잘 맞음, AI 통합) — 모던

### 데이터저널리즘 학습

-   [DataJournalism.com](https://datajournalism.com) — RSS 큐레이션 + Conversations With Data 팟캐스트
-   [GIJN](https://gijn.org) — RSS로 #ddj 위클리 모니터링
-   [Sigma Awards](https://sigmaawards.org) — 매년 31개 finalist 사례 (2026 기준)
-   [NICAR (IRE)](https://www.ire.org/nicar/) — Network of Computer-Assisted Reporting

---

## 16\. 확대 워크플로

### 전체 아키텍처

```
[수집]                  [필터]                 [분석]               [출력]

RSSHub (own)  ─┐                                                   ┌─ Telegram bot
RSS-Bridge    ├→ feedparser  →  키워드+임베딩  →  Gemini 요약   ─┼─ Notion/Obsidian
직접 RSS URL  ┘   asyncio        +Gemini 의미 필터    +Function    └─ 발행 기사 초안
                                       ↓                Calling
                                       ↓                   ↓
                                       └→ 추가 grounding ┐
                                                         ├→ KOSIS / DART / GDELT
                                                         ├→ BIGKINDS / 네이버
                                                         └→ 자작 MCP 서버
```

### 한 줄 시작

```bash
# 1) 환경 셋업
git clone https://github.com/your/data-journalism-class
cd data-journalism-class && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) RSSHub 자체 호스팅 (Docker)
docker run -d --name rsshub -p 1200:1200 \\
  -e CACHE_EXPIRE=3600 \\
  diygod/rsshub:chromium-bundled

# 3) .env 작성
cat > .env << EOF2
GEMINI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
RSSHUB_URL=http://localhost:1200
EOF2

# 4) 첫 실행
python rss_to_gemini.py

# 5) 매일 자동 실행 (cron)
echo "0 7 * * * cd /home/$USER/data-journalism-class && /home/$USER/.venv/bin/python rss_to_gemini.py" | crontab -
```

---

## 부록 A. URL 검증 요약 (Quick Reference)

### ✅ 직접 fetch 또는 Feedspot 2026 검증된 매체 (15개)

| 카테고리 | 매체 |
| --- | --- |
| 종합지 (직접 fetch) | 경향신문 |
| 종합지 (Feedspot 검증) | 조선일보, 동아일보, 서울신문 |
| 통신사 (직접 fetch) | 뉴시스 |
| 영문 한국 매체 | Korea Herald, Korea JoongAng Daily, Yonhap English, Hankyoreh English, Daily NK, Business Korea |
| 글로벌 종합 | BBC, Guardian, NYT, NPR, DW, France 24, SCMP, Al Jazeera |
| 데이터저널리즘 | GIJN, ProPublica, The Markup, FiveThirtyEight, Our World in Data, Bellingcat |
| 학술 | arXiv (분야별·서브분야·결합), Nature, PLOS ONE |
| 국제기구 | UN News, WHO, SEC EDGAR |
| 기술 | Anthropic, Microsoft Research, BAIR, Apple ML, Hugging Face |

### ❌ 폐지·도메인 변경 확인된 매체 (RSSHub 사용 권장)

| 매체 | 옛 URL (작동 안 함) | 대체 |
| --- | --- | --- |
| 중앙일보 | `rss.joins.com/joins_news_list.xml` | RSSHub `/joongang/news/:category` |
| 한국일보 | `rss.hankooki.com/news/hk_main.xml` | RSSHub `/hankookilbo/all` 또는 Google News 검색 RSS |
| 헤럴드경제 | `biz.heraldcorp.com/rss/...` | RSSHub `/heraldcorp/news` (도메인 변경) |
| JTBC | (공식 RSS 없음) | RSSHub `/jtbc/news/:category` |
| 다음 뉴스 | `media.daum.net/rss/...` | Google News 검색 RSS 또는 RSSHub |
| Reuters | `feeds.reuters.com/Reuters/worldNews` | RSSHub `/reuters/:category/:topic` (Reuters 2020년 자체 RSS 폐지) |
| AP News | `feeds.apnews.com/rss/apf-topnews` | RSSHub `/ap/:topic` |
| NHN Toast | `meetup.toast.com/rss` | 사이트 직접 확인 |

### ⚠️ 미검증 매체 운영 권장 패턴

```python
import feedparser, httpx

def safe_fetch(url, fallback_rsshub=None, ua="Mozilla/5.0 DataJournLab/1.0"):
    """1) 원본 URL 시도 → 2) entries 비면 RSSHub fallback"""
    try:
        r = httpx.get(url, timeout=10, headers={"User-Agent": ua})
        d = feedparser.parse(r.content)
        if len(d.entries) > 0:
            return d
    except Exception:
        pass
    # 폴백
    if fallback_rsshub:
        r = httpx.get(fallback_rsshub, timeout=10)
        return feedparser.parse(r.content)
    return None

# 사용 예
d = safe_fetch(
    "https://rss.hankooki.com/news/hk_main.xml",
    fallback_rsshub="https://rsshub.app/hankookilbo/all"
)
```

이 패턴으로 ⚠️ 매체의 갑작스런 폐지에도 자동 대응 가능.

---