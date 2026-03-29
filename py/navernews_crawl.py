# ============================================================================
# 네이버 뉴스 크롤러 (Naver News Crawler)
# ----------------------------------------------------------------------------
# 이 스크립트는 네이버 뉴스 검색 결과를 자동으로 수집(크롤링)하여
# 엑셀 파일(.xlsx)로 저장하는 프로그램입니다.
#
# [크롤링이란?]
#   웹사이트의 데이터를 프로그램으로 자동 수집하는 것을 말합니다.
#   사람이 브라우저에서 검색하고 기사를 클릭하는 과정을 코드가 대신 해줍니다.
#
# [동작 흐름]
#   1) 검색 키워드·날짜 등 조건을 설정
#   2) 네이버 내부 검색 API에 요청을 보내 기사 목록을 받아옴
#   3) 받아온 HTML에서 제목·언론사·날짜·본문요약·URL 등을 추출
#   4) 결과를 표(DataFrame)로 정리하여 엑셀로 저장
# ============================================================================

# --- 라이브러리 불러오기 (import) ---
# 라이브러리 = 다른 개발자가 미리 만들어둔 기능 모음. 설치 후 import로 가져와 사용.

import requests          # HTTP 요청을 보내는 라이브러리 (웹 서버에 데이터를 요청할 때 사용)
                         # 예: requests.get(url) → 해당 URL의 내용을 가져옴
from bs4 import BeautifulSoup  # HTML을 파싱(분석·분해)하는 라이브러리
                               # 예: 긴 HTML 텍스트에서 제목, 본문 등 원하는 부분만 뽑아냄
import urllib            # URL 인코딩 등 URL 관련 유틸리티
                         # 예: "인공지능" → "%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5" (URL에 한글 사용 불가하므로 변환)
import pandas as pd      # 데이터를 표(테이블) 형태로 다루는 라이브러리
                         # 예: 엑셀처럼 행·열로 된 DataFrame 객체를 제공
import time              # 시간 관련 기능 (대기 시간 추가 등)
                         # 예: time.sleep(1) → 1초 동안 멈춤
import re                # 정규표현식(Regular Expression) 라이브러리
                         # 예: 텍스트에서 "2026.01.01" 같은 날짜 패턴을 찾을 때 사용
from tqdm import tqdm    # 반복문(for)에 진행률 표시줄(progress bar)을 추가해주는 라이브러리
                         # 예: 수집 중 ████████░░ 80% 처럼 진행 상황을 보여줌

# ──────────────────────────────────────────────────────────────────────────────
# 언론사 이름 → 네이버 뉴스 내부 ID 매핑 딕셔너리
# ----------------------------------------------------------------------------
# [딕셔너리(dict)란?]
#   '키(key): 값(value)' 쌍으로 데이터를 저장하는 자료구조.
#   예: news_office['조선일보'] → '1001' 을 반환
#
# 네이버는 각 언론사에 고유 숫자 ID를 부여합니다.
# 특정 언론사 기사만 검색하고 싶을 때 이 ID를 사용합니다.
# ──────────────────────────────────────────────────────────────────────────────
news_office = {
    '조선일보': '1001', '중앙일보': '1002', '동아일보': '1003',
    'MBC': '1009', 'SBS': '1011', 'KBS': '1056',
    '한겨레': '1028', '경향신문': '1032', '한국일보': '1038',
    'JTBC': '1437', 'YTN': '1052', '연합뉴스': '1001',
}


def navernews_crawl(
    query: str = '인공지능',       # 검색할 키워드 (기본값: '인공지능')
    media: str = '전체',           # 특정 언론사 이름 또는 '전체' (기본값: '전체')
    date_from: int = 20260101,     # 검색 시작 날짜 (YYYYMMDD 형식, 예: 20260101 = 2026년 1월 1일)
    date_to: int = 20260301,       # 검색 종료 날짜 (YYYYMMDD 형식)
    sort: int = 1,                 # 정렬 방식: 0=관련도순, 1=최신순, 2=오래된순
    pages: int = 5,                # 수집할 페이지 수 (1페이지 = 기사 10개, 최대 400페이지)
) -> pd.DataFrame:
    """
    네이버 뉴스 검색 결과를 내부 JSON API로 수집한다.

    [JSON API란?]
      웹사이트가 내부적으로 데이터를 주고받는 통로.
      브라우저에서 검색하면 화면 뒤에서 이 API가 기사 데이터를 JSON 형식으로 전달합니다.
      JSON = JavaScript Object Notation, 데이터를 { "키": "값" } 형태로 표현하는 형식.

    Parameters (매개변수 = 함수에 전달하는 입력값)
    ----------
    query     : 검색 키워드
    media     : 언론사 이름(news_office 키 참고) 또는 '전체'
    date_from : 수집 시작일 (YYYYMMDD 정수)
    date_to   : 수집 종료일 (YYYYMMDD 정수)
    sort      : 정렬 방식 (0=관련도순, 1=최신순, 2=오래된순)
    pages     : 수집 페이지 수 (최대 400 · 1페이지=10건)

    Returns (반환값 = 함수가 실행 후 돌려주는 결과)
    -------
    pd.DataFrame  ← media, date, title, text, naver_url, media_url 컬럼을 가진 표
    """

    # ── ① URL 파라미터 준비 ──────────────────────────────────────────────────
    # [URL 파라미터란?]
    #   URL 뒤에 ?key=value&key2=value2 형태로 붙는 추가 정보.
    #   예: search.naver.com?query=인공지능&sort=1
    #   서버에게 "인공지능을 최신순으로 검색해줘"라고 요청하는 것.

    # urllib.parse.quote(): 한글 등 특수문자를 URL에서 사용할 수 있는 형태로 변환
    # 예: "인공지능" → "%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5"
    # 이유: URL에는 영문·숫자·일부 기호만 허용되므로 한글은 변환(인코딩)이 필요
    q        = urllib.parse.quote(query)
    df_str   = str(date_from)                       # 정수를 문자열로 변환 (예: 20260101 → '20260101')
    dt_str   = str(date_to)                         # 정수를 문자열로 변환 (예: 20260301 → '20260301')

    # 언론사 필터 설정
    # '전체'이면 → media_id를 비워서 모든 언론사 기사를 수집
    # 특정 언론사이면 → 해당 ID를 넣고 mynews='1'로 필터 활성화
    if media == '전체':
        media_id, mynews = '', '0'    # 필터 없음
    else:
        media_id = str(news_office.get(media, ''))  # dict.get(): 딕셔너리에서 키로 값을 조회 (없으면 '' 반환)
        mynews   = '1'                               # mynews=1: "특정 언론사만 보여줘" 플래그 활성화

    # 네이버 API가 요구하는 날짜 형식으로 변환
    # '20260101' → '2026.01.01' (슬라이싱으로 연/월/일 분리 후 점(.)으로 연결)
    # [슬라이싱이란?] 문자열의 일부를 잘라내는 것. 예: "20260101"[:4] → "2026"
    ds  = f"{df_str[:4]}.{df_str[4:6]}.{df_str[6:]}"   # 예: '2026.01.01'
    de  = f"{dt_str[:4]}.{dt_str[4:6]}.{dt_str[6:]}"   # 예: '2026.03.01'

    # [nso 파라미터란?]
    #   네이버 검색의 내부 옵션 문자열. "Naver Search Option"의 약자로 추정.
    #   so=r      → 정렬(sort) 옵션 (r=관련도)
    #   p=from~to → 기간(period) 범위
    #   a=all     → 전체(all) 유형
    #   %3A = ':', %2C = ',' 의 URL 인코딩 형태
    #   즉, 풀어쓰면: "so:r,p:from20260101to20260301,a:all"
    nso = f"so%3Ar%2Cp%3Afrom{df_str}to{dt_str}%2Ca%3Aall"

    # ── ② HTTP 요청 헤더(headers) 설정 ──────────────────────────────────────
    # [headers란?]
    #   HTTP 요청을 보낼 때 함께 전달하는 부가 정보.
    #   편지로 비유하면, 편지 봉투에 적는 "보낸이 정보"와 같은 것.
    #   서버는 이 정보를 보고 요청을 허용할지 거부할지 판단합니다.
    headers = {
        # [User-Agent란?]
        #   "나는 이런 브라우저/기기에서 접속하고 있어"라고 서버에 알려주는 정보.
        #   크롤링 프로그램은 기본적으로 "python-requests/2.x" 같은 값을 보내는데,
        #   많은 웹사이트가 이런 비-브라우저 요청을 차단합니다.
        #   그래서 실제 Chrome 브라우저의 User-Agent를 그대로 적어서
        #   "나는 일반 사용자입니다"라고 위장(spoofing)합니다.
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Safari/537.36"
        ),
        # [Referer란?]
        #   "이 요청은 어디 페이지에서 왔는가"를 알려주는 헤더.
        #   네이버 검색 결과 페이지에서 온 것처럼 설정하여
        #   API가 정상적인 요청으로 인식하도록 합니다.
        "Referer": f"https://search.naver.com/search.naver?where=news&query={q}"
    }

    all_results = []    # 수집한 기사 데이터를 담을 빈 리스트 (나중에 DataFrame으로 변환)
    seen_urls   = set() # 중복 제거용 집합(set). 이미 수집한 URL을 기록하여 같은 기사를 두 번 저장하지 않음.
                        # [set이란?] 중복을 허용하지 않는 자료구조. 'in' 연산이 매우 빠름.

    # ── ③ 페이지 반복 수집 ──────────────────────────────────────────────────
    # tqdm()으로 감싸면 반복 진행률이 화면에 표시됨 (예: 수집 중: 60%|██████░░░░| 3/5)
    for page in tqdm(range(1, pages + 1), desc="수집 중"):

        # [페이지네이션(pagination)]
        #   네이버는 한 페이지에 기사 10개씩 보여줌.
        #   start=1이면 1~10번째, start=11이면 11~20번째 기사를 요청.
        #   공식: start = (페이지번호 - 1) × 10 + 1
        start = (page - 1) * 10 + 1  # 1페이지→1, 2페이지→11, 3페이지→21 ...

        # 네이버 뉴스 내부 JSON API의 전체 URL 구성
        # 각 파라미터 설명:
        #   query       : 검색 키워드
        #   ssc         : 검색 범위 (tab.news.all = 뉴스 탭 전체)
        #   pd=3        : 기간 검색 모드 (3 = 사용자 지정 기간)
        #   photo=0     : 사진 필터 없음
        #   sort        : 정렬 방식
        #   nso         : 검색 옵션 (위에서 만든 기간·정렬 문자열)
        #   ds, de      : 시작일, 종료일
        #   start       : 시작 위치 (몇 번째 기사부터)
        #   news_office_checked : 언론사 ID (비어있으면 전체)
        #   mynews      : 언론사 필터 활성화 여부 (0=끔, 1=켬)
        target_url = (
            "https://s.search.naver.com/p/newssearch/3/api/tab/more"
            f"?query={q}&ssc=tab.news.all&pd=3&photo=0"
            f"&sort={sort}&nso={nso}&ds={ds}&de={de}"
            f"&start={start}&news_office_checked={media_id}"
            f"&mynews={mynews}&office_type=0&office_section_code=0"
        )

        # [requests.get()으로 HTTP GET 요청 보내기]
        #   서버에 "이 URL의 데이터를 주세요"라고 요청하는 것.
        #   headers : 위에서 만든 헤더(브라우저 위장 정보) 포함
        #   timeout=10 : 서버가 10초 안에 응답하지 않으면 포기 (무한 대기 방지)
        #                [timeout이란?] 최대 대기 시간. 서버가 느리거나 장애일 때
        #                프로그램이 영원히 멈추는 것을 방지합니다. 단위: 초(seconds)
        response = requests.get(target_url, headers=headers, timeout=10)

        # [HTTP 상태 코드(status_code)]
        #   서버가 "요청 처리 결과"를 숫자로 알려주는 것.
        #   200 = 성공 (OK), 404 = 페이지 없음, 403 = 접근 거부, 500 = 서버 오류
        #   200이 아니면 문제가 있으므로 해당 페이지를 건너뜀
        if response.status_code != 200:
            print(f"[경고] 페이지 {page} 요청 실패: HTTP {response.status_code}")
            continue  # continue = 이번 반복을 건너뛰고 다음 페이지로 이동

        # [JSON 파싱]
        #   서버가 보내준 텍스트 응답을 파이썬 딕셔너리로 변환.
        #   response.json()은 응답 본문이 JSON 형식일 때 사용.
        #   서버가 JSON 대신 HTML 오류 페이지를 보내면 파싱이 실패할 수 있으므로 try-except로 감싸줌.
        # [try-except란?]
        #   오류(예외)가 발생할 수 있는 코드를 안전하게 실행하는 방법.
        #   try 안에서 오류 발생 → except 블록으로 이동 (프로그램이 멈추지 않음)
        try:
            data = response.json()
        except Exception:
            print(f"[경고] 페이지 {page}: JSON 파싱 실패, 건너뜀.")
            continue

        # data.get('collection'): 딕셔너리에서 'collection' 키의 값을 안전하게 조회
        # .get()은 키가 없어도 오류 없이 None을 반환 (data['collection']은 키가 없으면 오류 발생)
        # 값이 없거나 빈 리스트이면 → 더 이상 검색 결과가 없다는 뜻 → 수집 종료
        if not data.get('collection'):
            print(f"[종료] 페이지 {page}: 데이터 없음. 수집 종료.")
            break  # break = 반복문(for) 자체를 완전히 종료

        # collection 안의 첫 번째 항목에서 HTML 문자열을 꺼냄
        # 네이버 API는 기사 목록을 HTML 형태로 담아서 JSON 안에 넣어 보내줌
        html = data['collection'][0].get('html', '')
        if not html:
            print(f"[종료] 페이지 {page}: HTML 없음. 수집 종료.")
            break

        # ── ④ HTML 파싱 (분석·분해) ────────────────────────────────────────
        # [BeautifulSoup이란?]
        #   HTML 텍스트를 트리(나무) 구조로 변환하여 원하는 요소를 쉽게 찾을 수 있게 해주는 도구.
        #   예: soup.select('a') → HTML에서 모든 <a> 태그(링크)를 찾아줌
        # 'html.parser': 파이썬 내장 HTML 분석기를 사용 (별도 설치 불필요)
        soup = BeautifulSoup(html, 'html.parser')

        # [CSS 선택자(selector)로 요소 찾기]
        #   soup.select_one('div.클래스명') → 해당 클래스를 가진 첫 번째 div 태그를 찾음
        #   soup.select('span.클래스명')    → 해당 클래스를 가진 모든 span 태그를 찾음
        #   [class*="xxx"] : 클래스 이름에 "xxx"가 포함된 요소를 찾음 (*= 는 "포함" 의미)

        # 2025년 이후 네이버 뉴스 검색 API는 SDS 컴포넌트 기반 HTML을 반환
        # (SDS = Samsung Design System 스타일의 UI 컴포넌트)
        # 기사 목록은 'fds-news-item-list-tab' 클래스의 div 안에 직속 div로 나열됨
        news_list = soup.select_one('div[class*="fds-news-item-list-tab"]')
        if not news_list:
            # fallback(대체 방법): 구형 HTML 구조일 경우 li.bx 태그로 시도
            # 네이버가 HTML 구조를 바꿀 수 있으므로 여러 방식을 시도하는 것
            news_items = soup.select('li.bx')
            if not news_items:
                # 그래도 못 찾으면 ul 태그 아래 직속 li들을 가져옴
                ul = soup.find('ul')
                news_items = ul.find_all('li', recursive=False) if ul else []
                # recursive=False: 직속 자식만 찾음 (손자, 증손자는 제외)
        else:
            # 직속 자식 div 중 headline(제목)을 포함한 것만 기사 아이템으로 사용
            # 광고나 빈 div를 제외하기 위한 필터링
            news_items = [
                div for div in news_list.find_all('div', recursive=False)
                if div.select('span[class*="text-type-headline"]')
            ]
            # ↑ 리스트 컴프리헨션(list comprehension): for와 if를 한 줄로 작성하는 문법
            #   풀어쓰면:
            #   news_items = []
            #   for div in news_list.find_all('div', recursive=False):
            #       if div.select('span[class*="text-type-headline"]'):
            #           news_items.append(div)

        if not news_items:
            print(f"[경고] 페이지 {page}: 기사 아이템을 찾을 수 없음.")
            break

        # ── ⑤ 각 기사 아이템에서 필드(항목) 추출 ─────────────────────────────
        for item in news_items:
            try:
                # ── 제목 추출 ────────────────────────────────────────────
                # 여러 CSS 선택자를 순서대로 시도 (or 연산자 사용)
                # 첫 번째가 None이면 두 번째 시도, 그것도 None이면 세 번째 시도
                title_el = (
                    item.select_one('span[class*="text-type-headline"]')  # SDS 신형 구조
                    or item.select_one('a.news_tit')                      # 구형 구조
                    or item.select_one('a[href]')                         # 최후의 수단: 아무 링크
                )
                # get_text(strip=True): 태그 안의 텍스트만 추출, 앞뒤 공백 제거
                title = title_el.get_text(strip=True) if title_el else ''

                # ── 언론사명 추출 ────────────────────────────────────────
                # SDS UI에서 언론사 이름은 'profile-info-title-text' 클래스의 span에 있음
                media_el = item.select_one(
                    'span[class*="profile-info-title-text"]'
                )
                if not media_el:
                    # 못 찾으면 다른 구조 시도
                    media_el = item.select_one(
                        'span[class*="profile-info-title"] span[class*="sds-comps-text"]'
                    )
                media_name = media_el.get_text(strip=True) if media_el else ''

                # ── 날짜 추출 ────────────────────────────────────────────
                # 방법 1: "2026.01.15" 같은 절대 날짜를 먼저 찾음
                # 방법 2: 없으면 "3일 전", "2주 전" 같은 상대 날짜를 사용
                date = ''
                for sp in item.select('span[class*="sds-comps-text"]'):
                    t = sp.get_text(strip=True)
                    # re.match(): 정규표현식으로 텍스트가 패턴과 일치하는지 확인
                    # r'\d{4}\.\d{2}\.\d{2}' = "숫자4개.숫자2개.숫자2개" 패턴 (예: 2026.01.15)
                    # \d = 숫자 한 개, {4} = 4번 반복, \. = 마침표(점) 문자 그대로
                    if re.match(r'\d{4}\.\d{2}\.\d{2}', t):
                        date = t
                        break
                if not date:
                    # 절대 날짜를 못 찾으면 상대 날짜("3일 전" 등) 찾기
                    for sp in item.select('span[class*="profile-info-subtext"]'):
                        t = sp.get_text(strip=True)
                        # re.search(): 텍스트 안에 패턴이 포함되어 있는지 검색
                        # (전|ago) = "전" 또는 "ago" 가 포함된 텍스트
                        if re.search(r'(전|ago)', t):
                            date = t
                            break

                # ── 본문 요약 추출 ───────────────────────────────────────
                # 검색 결과에 나오는 기사 미리보기 텍스트 (전체 본문 아님)
                text_el = (
                    item.select_one('span[class*="text-type-body1"]')     # SDS 신형
                    or item.select_one('span[class*="text-ellipsis"]')    # 중간형
                    or item.select_one('.api_txt_lines')                  # 구형
                )
                text = text_el.get_text(strip=True) if text_el else ''

                # ── URL 추출 ────────────────────────────────────────────
                # 각 기사에는 2가지 URL이 있을 수 있음:
                #   naver_url : 네이버 뉴스에서 보는 URL (n.news.naver.com)
                #   media_url : 원래 언론사 사이트의 URL
                naver_url, media_url = '', ''
                for a in item.select('a[href]'):  # 모든 <a> 링크 태그를 순회
                    href = a.get('href', '')       # href 속성값(URL) 가져오기
                    if href in ('#', ''):          # 빈 링크나 # 링크는 건너뜀
                        continue
                    if 'n.news.naver.com' in href and not naver_url:
                        naver_url = href           # 네이버 뉴스 URL 저장
                    elif href.startswith('http') and not media_url \
                            and 'naver' not in href:
                        media_url = href           # 원본 언론사 URL 저장

                # ── 중복 체크 ───────────────────────────────────────────
                # 같은 기사가 여러 페이지에 중복 노출될 수 있으므로
                # naver_url을 고유 키로 사용하여 이미 수집한 기사인지 확인
                # naver_url이 없는 경우 "제목|날짜" 조합을 보조 키로 사용
                dedup_key = naver_url if naver_url else f"{title}|{date}"
                if dedup_key in seen_urls:
                    continue                # 이미 수집한 기사 → 건너뜀
                if dedup_key:
                    seen_urls.add(dedup_key)  # set에 추가하여 다음번에 중복 감지 가능

                # 제목도 언론사도 없는 빈 행은 의미 없으므로 저장하지 않음
                if title or media_name:
                    all_results.append([
                        media_name, date, title, text, naver_url, media_url
                    ])
                    # append(): 리스트 끝에 새 항목을 추가하는 메서드

            except Exception as e:
                # 특정 기사 파싱에서 오류가 나도 전체 프로그램이 멈추지 않도록
                # 해당 기사만 건너뛰고 다음 기사로 계속 진행
                print(f"[파싱 오류] {e}")
                continue

        # [time.sleep(1): 1초 대기]
        #   서버에 너무 빠르게 연속 요청하면:
        #   1) 서버에 과부하를 줄 수 있음
        #   2) 크롤링 차단(IP 밴)을 당할 수 있음
        #   그래서 한 페이지 수집 후 1초씩 쉬어줌 ("예의 바른 크롤링")
        time.sleep(1)

    # ── ⑥ 결과를 DataFrame(표)으로 만들어 반환 ──────────────────────────────
    # DataFrame의 컬럼(열) 이름 정의
    cols = ['media', 'date', 'title', 'text', 'naver_url', 'media_url']

    if all_results:
        # 수집된 데이터가 있으면 → DataFrame 생성
        # DataFrame = 엑셀 시트처럼 행과 열로 구성된 표 형태 데이터 구조
        df   = pd.DataFrame(all_results, columns=cols)
        last = df['date'].iloc[-1] or '날짜 없음'   # iloc[-1]: 마지막 행의 값
        print(f"\n✅ {last}까지 총 {len(df)}건 수집 완료.")  # len(df): 전체 행 수
        return df
    else:
        # 수집된 데이터가 없으면 → 빈 DataFrame 반환
        print("\n❌ 수집된 데이터가 없습니다.")
        return pd.DataFrame(columns=cols)


def get_article_body(naver_url: str, headers: dict | None = None) -> str:
    """
    네이버 뉴스 본문 전체를 추출한다.

    [왜 필요한가?]
      위의 navernews_crawl()이 수집하는 건 검색 결과의 '요약'뿐입니다.
      기사 전체 본문이 필요하면 각 기사의 naver_url에 직접 접속하여
      HTML에서 본문 영역을 추출해야 합니다.

    Parameters
    ----------
    naver_url : 네이버 뉴스 기사 URL (예: https://n.news.naver.com/article/...)
    headers   : HTTP 요청 헤더 (없으면 기본값 사용)

    Returns
    -------
    str : 기사 본문 텍스트 (실패 시 빈 문자열 '')
    """
    if not naver_url:
        return ''
    if not headers:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 Chrome/135.0.0.0 Safari/537.36"
        }
    try:
        # 기사 페이지에 GET 요청
        resp = requests.get(naver_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return ''
        # 응답 HTML을 BeautifulSoup으로 파싱
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 네이버 뉴스 본문 영역을 여러 선택자로 시도
        # 네이버 뉴스 페이지 구조가 바뀔 수 있으므로 3가지 방법을 순서대로 시도:
        #   article#dic_area         : 현재(2025~) 가장 흔한 본문 영역
        #   div#articleBodyContents  : 구형 본문 영역
        #   div.newsct_article       : 또 다른 구형 본문 영역
        body = (
            soup.select_one('article#dic_area')
            or soup.select_one('div#articleBodyContents')
            or soup.select_one('div.newsct_article')
        )

        if body:
            # 본문 안에 섞여 있는 불필요한 요소 제거
            # script : 자바스크립트 코드
            # style  : CSS 스타일 코드
            # span.end_photo_org : 사진 출처 텍스트
            for tag in body.select('script, style, span.end_photo_org'):
                tag.decompose()  # decompose(): 해당 태그를 HTML에서 완전히 삭제

            # get_text(): HTML 태그를 제거하고 순수 텍스트만 추출
            # separator=' ' : 태그 사이에 공백 삽입 (붙어나오는 것 방지)
            # strip=True    : 앞뒤 공백 제거
            return body.get_text(separator=' ', strip=True)
        return ''
    except Exception:
        # 네트워크 오류, 파싱 오류 등 어떤 예외든 빈 문자열 반환 (프로그램 중단 방지)
        return ''


def add_article_bodies(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame의 각 기사 URL로 본문을 수집하여 'body' 컬럼을 추가한다.

    [동작 과정]
      1) df의 naver_url 컬럼을 하나씩 순회
      2) 각 URL에 대해 get_article_body()를 호출하여 본문 추출
      3) 추출된 본문들을 'body'라는 새 컬럼으로 DataFrame에 추가

    Parameters
    ----------
    df : navernews_crawl()이 반환한 DataFrame (naver_url 컬럼 필수)

    Returns
    -------
    pd.DataFrame : 'body' 컬럼이 추가된 DataFrame
    """
    bodies = []  # 각 기사의 본문을 담을 리스트
    # tqdm으로 진행률 표시하며 각 URL 순회
    for url in tqdm(df['naver_url'], desc="본문 수집"):
        bodies.append(get_article_body(url))  # 본문 추출 후 리스트에 추가
        time.sleep(0.5)  # 0.5초 대기 (서버 부하 방지 + 차단 방지)
    df['body'] = bodies  # DataFrame에 'body'라는 새 컬럼 추가
    ok = sum(1 for b in bodies if b)  # 본문이 비어있지 않은 건수 세기
    # ↑ 제너레이터 표현식: bodies 리스트에서 빈 문자열이 아닌 것만 세어 합산
    print(f"\n✅ 본문 수집 완료: {ok}/{len(df)}건 성공")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# 사용 예시 (이 파일을 직접 실행할 때만 아래 코드가 실행됨)
# ----------------------------------------------------------------------------
# [if __name__ == '__main__': 란?]
#   이 파일을 직접 실행하면 (python navernews_crawl.py) 아래 코드가 실행되고,
#   다른 파일에서 import할 때는 실행되지 않음.
#   즉, "메인 프로그램으로 실행될 때만 동작하는 코드"를 여기에 넣음.
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    xlsx_path = 'naver_news.xlsx'  # 결과를 저장할 엑셀 파일 경로

    # ── 1차: 검색 결과 수집 → 엑셀 저장 ─────────────────────────────────────
    df = navernews_crawl(
        query='인공지능',       # 검색어
        media='전체',           # 모든 언론사
        date_from=20260101,     # 2026년 1월 1일부터
        date_to=20260301,       # 2026년 3월 1일까지
        sort=1,                 # 최신순 정렬
        pages=2,                # 2페이지 (약 20건) 수집
    )
    print(df.head())  # head(): DataFrame의 처음 5행만 미리보기 출력
    # to_excel(): DataFrame을 엑셀 파일로 저장
    # index=False : 행 번호(0,1,2...)를 엑셀에 포함하지 않음
    # engine='openpyxl' : .xlsx 형식 저장에 사용하는 엔진(라이브러리)
    df.to_excel(xlsx_path, index=False, engine='openpyxl')
    print(f"1차 저장 완료: {xlsx_path}")

    # ── 2차: 본문 추가 → 엑셀 갱신 ──── 불필요하면 이 부분을 주석 처리(# 붙이기)
    # 각 기사의 전체 본문을 추가로 수집하여 엑셀을 업데이트
    df = add_article_bodies(df)
    df.to_excel(xlsx_path, index=False, engine='openpyxl')
    print(f"2차 저장 완료(본문 포함): {xlsx_path}")
