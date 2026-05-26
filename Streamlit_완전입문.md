# 🎈 Streamlit 입문 — RAG 챗봇을 통해 배우는 웹 앱 개발

> \*\*대상:\*\* Python은 알지만 웹 개발은 처음인 분  
> \*\*목표:\*\* Streamlit의 핵심 원리를 이해하고, 챗봇 코드의 각 UI 요소가 왜 그렇게 작동하는지 설명.

\---

## 목차

1. [Streamlit이란?](#1-streamlit이란)
2. [핵심 원리: 스크립트 재실행 모델](#2-핵심-원리-스크립트-재실행-모델)
3. [session\_state — 상태를 기억하는 방법](#3-session_state--상태를-기억하는-방법)
4. [주요 UI 컴포넌트 사전](#4-주요-ui-컴포넌트-사전)
5. [캐싱 — 느린 작업을 빠르게](#5-캐싱--느린-작업을-빠르게)
6. [레이아웃 구성법](#6-레이아웃-구성법)
7. [챗봇 코드 줄별 해석](#7-챗봇-코드-줄별-해석)
8. [자주 하는 실수와 해결법](#8-자주-하는-실수와-해결법)

\---

## 1\. Streamlit이란?

### 1.1 한 문장으로

> \*\*Python 함수를 호출하는 것만으로 웹 UI를 만드는 프레임워크\*\*

HTML, CSS, JavaScript를 전혀 몰라도 됩니다.

### 1.2 기존 방법과 비교

|방법|필요한 기술|복잡도|
|-|-|-|
|Flask + HTML/CSS/JS|Python + 웹 프론트엔드|★★★★☆|
|Django|Python + 웹 프레임워크 전반|★★★★★|
|Gradio|Python|★★☆☆☆|
|**Streamlit**|**Python만**|**★☆☆☆☆**|

### 1.3 설치와 실행

```bash
# 설치
pip install streamlit

# 실행
streamlit run app.py

# 브라우저에서 자동으로 http://localhost:8501 열림
```

### 1.4 가장 짧은 Streamlit 앱

```python
import streamlit as st

st.title("안녕하세요!")
st.write("이게 전부입니다.")

name = st.text\_input("이름을 입력하세요")
if name:
    st.success(f"{name}님, 환영합니다! 🎉")
```

이 5줄이 완전한 웹 앱입니다. `streamlit run hello.py`로 바로 실행됩니다.

\---

## 2\. 핵심 원리: 스크립트 재실행 모델

### 2.1 Streamlit의 가장 중요한 규칙

> \*\*사용자가 무언가를 할 때마다 Python 스크립트 전체가 처음부터 끝까지 다시 실행됩니다.\*\*

이것이 Streamlit을 이해하는 핵심입니다.

```
사용자가 버튼 클릭 → app.py 전체 재실행 → 화면 다시 그리기
사용자가 텍스트 입력 → app.py 전체 재실행 → 화면 다시 그리기
사용자가 슬라이더 조작 → app.py 전체 재실행 → 화면 다시 그리기
```

### 2.2 재실행 모델의 의미

**일반 Python 프로그램과 다른 점:**

```python
# 일반 Python: 한 번 실행하고 끝
count = 0
count += 1
print(count)  # 항상 1 출력

# Streamlit: 버튼 클릭마다 재실행
import streamlit as st
count = 0          # ← 재실행마다 0으로 초기화됨!
if st.button("클릭"):
    count += 1     # ← 이건 의미없음 (다음 재실행에서 다시 0이 됨)
st.write(count)    # 항상 0 또는 1
```

**해결책 → session\_state 사용** (3장에서 설명)

### 2.3 재실행 모델이 주는 이점

```python
# 이렇게 쓰면 슬라이더 값이 바뀔 때마다 자동으로 그래프가 업데이트됨
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

n = st.slider("포인트 수", 10, 1000, 100)  # 슬라이더

x = np.linspace(0, 10, n)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y)
st.pyplot(fig)  # 슬라이더를 움직이면 그래프가 즉시 업데이트!
```

별도의 이벤트 핸들러나 콜백 없이 자동으로 반응형 UI가 됩니다.

\---

## 3\. session\_state — 상태를 기억하는 방법

### 3.1 문제: 재실행마다 변수가 초기화됨

```python
# ❌ 동작하지 않음 (재실행마다 messages가 빈 리스트로 초기화됨)
messages = \[]

if st.button("메시지 추가"):
    messages.append("안녕")

st.write(messages)  # 항상 \[] 또는 \["안녕"] — 누적이 안 됨
```

### 3.2 해결: session\_state에 저장

```python
# ✅ 올바른 방법
import streamlit as st

# session\_state는 브라우저 탭이 열린 동안 유지되는 딕셔너리
if "messages" not in st.session\_state:
    st.session\_state.messages = \[]  # 처음 한 번만 초기화

if st.button("메시지 추가"):
    st.session\_state.messages.append("안녕")

st.write(st.session\_state.messages)  # \["안녕", "안녕", "안녕", ...] 누적됨!
```

### 3.3 session\_state 사용 패턴

```python
# 패턴 1: 없으면 초기화
if "count" not in st.session\_state:
    st.session\_state.count = 0

# 패턴 2: 딕셔너리처럼 접근
st.session\_state\["count"] += 1

# 패턴 3: 속성처럼 접근 (동일한 동작)
st.session\_state.count += 1

# 패턴 4: .get()으로 안전하게 꺼내기 (없으면 None 반환)
value = st.session\_state.get("key", "기본값")

# 패턴 5: .pop()으로 꺼내고 삭제 (챗봇의 pending\_question에서 사용)
pending = st.session\_state.pop("pending\_question", None)
```

### 3.4 챗봇에서 session\_state가 하는 일

```python
# 이 챗봇에서 session\_state에 저장하는 것들:

st.session\_state.messages
# = 화면에 표시할 대화 이력
# = \[{"role": "user", "content": "질문"}, {"role": "assistant", "content": "답변"}, ...]

st.session\_state.gemini\_history
# = Gemini API에 전달할 대화 이력
# = \[{"role": "user", "parts": "질문"}, {"role": "model", "parts": "답변"}, ...]
# Gemini는 "assistant" 대신 "model"을 씁니다.

st.session\_state.pending\_question
# = 사이드바 버튼 클릭으로 입력된 질문 (다음 재실행에서 처리)
```

\---

## 4\. 주요 UI 컴포넌트 사전

### 4.1 텍스트 표시

```python
st.title("제목")                    # 큰 제목 (h1)
st.header("섹션 제목")             # 중간 제목 (h2)
st.subheader("소제목")             # 작은 제목 (h3)
st.text("고정폭 텍스트")           # 코드처럼 보이는 텍스트
st.markdown("\*\*굵게\*\* \*기울임\*")   # 마크다운 지원
st.caption("작은 설명 텍스트")     # 회색 작은 글씨
st.code("print('hello')")          # 코드 블록
st.divider()                       # 수평선 구분자
```

### 4.2 입력 위젯

```python
# 텍스트 입력
name = st.text\_input("이름", placeholder="홍길동")
bio = st.text\_area("자기소개", height=150)

# 숫자
age = st.number\_input("나이", min\_value=0, max\_value=120, value=25)
score = st.slider("점수", 0, 100, 50)  # (label, min, max, default)

# 선택
choice = st.selectbox("선택", \["옵션1", "옵션2", "옵션3"])
checks = st.multiselect("복수 선택", \["A", "B", "C"])
agree = st.checkbox("동의합니다")
radio = st.radio("단일 선택", \["A", "B", "C"])

# 버튼
clicked = st.button("클릭하세요")
if clicked:
    st.write("클릭됨!")

# 채팅 전용 입력창 (화면 하단 고정)
msg = st.chat\_input("메시지를 입력하세요...")
```

### 4.3 알림 메시지

```python
st.success("✅ 성공!")           # 초록색 박스
st.error("❌ 오류!")             # 빨간색 박스
st.warning("⚠️ 경고!")          # 노란색 박스
st.info("ℹ️ 정보")              # 파란색 박스
st.exception(e)                  # 예외 상세 표시 (개발 시 유용)
```

### 4.4 로딩 표시

```python
# 스피너 (작업 중 표시)
with st.spinner("처리 중..."):
    time.sleep(3)  # 이 코드 실행 동안 스피너 표시
st.success("완료!")

# 진행 바 (0.0 \~ 1.0)
progress\_bar = st.progress(0, text="시작...")
for i in range(100):
    progress\_bar.progress((i + 1) / 100, text=f"{i+1}% 완료")
    time.sleep(0.01)
progress\_bar.empty()  # 완료 후 제거
```

### 4.5 채팅 말풍선

```python
# role: "user" → 오른쪽 말풍선, "assistant" → 왼쪽 말풍선
with st.chat\_message("user"):
    st.markdown("안녕하세요!")

with st.chat\_message("assistant"):
    st.markdown("안녕하세요! 무엇을 도와드릴까요?")
```

### 4.6 화면 새로고침

```python
st.rerun()
# 현재 실행을 중단하고 스크립트를 처음부터 다시 실행
# 주로 상태를 바꾼 뒤 즉시 화면을 업데이트할 때 사용
```

\---

## 5\. 캐싱 — 느린 작업을 빠르게

### 5.1 문제: 재실행마다 무거운 작업이 반복됨

```python
# ❌ 캐싱 없음: 사용자가 입력할 때마다 모델을 다시 로드!
def load\_model():
    return SomeBigModel()  # 30초 걸림

model = load\_model()  # 매번 30초...
```

### 5.2 @st.cache\_resource — 객체(리소스) 캐싱

```python
# ✅ 첫 실행에만 함수가 실행되고, 이후에는 캐시된 객체 반환
@st.cache\_resource
def load\_model():
    return SomeBigModel()  # 최초 1회만 30초

model = load\_model()  # 이후에는 즉시 반환
```

**언제 쓰나요?**

* 데이터베이스 연결
* ML 모델 로드
* API 클라이언트 객체
* **→ 이 챗봇의 Chroma DB 컬렉션 객체**

### 5.3 @st.cache\_data — 데이터(결과값) 캐싱

```python
# ✅ 같은 파라미터로 호출하면 계산 없이 이전 결과 반환
@st.cache\_data
def load\_csv(filepath):
    return pd.read\_csv(filepath)  # 첫 번째만 실제 파일 읽기

df = load\_csv("data.csv")  # 이후 호출은 캐시에서 즉시 반환
```

**언제 쓰나요?**

* DataFrame 로드
* API 응답 캐싱
* 변환 결과 저장

### 5.4 두 캐싱 데코레이터 비교

||`@st.cache\_resource`|`@st.cache\_data`|
|-|-|-|
|대상|객체, 연결, 클라이언트|데이터, 계산 결과|
|공유|모든 사용자/세션 공유|사용자별 복사본|
|예시|DB 연결, 모델|DataFrame, 변환값|

\---

## 6\. 레이아웃 구성법

### 6.1 사이드바

```python
# with 블록 안에 쓰면 모두 사이드바에 표시됨
with st.sidebar:
    st.header("설정")
    top\_k = st.slider("검색 수", 1, 10, 5)
    temperature = st.slider("창의성", 0.0, 1.0, 0.2)
    
    if st.button("초기화"):
        st.session\_state.messages = \[]
```

### 6.2 열(Column) 레이아웃

```python
col1, col2 = st.columns(2)       # 같은 너비 2열
col1, col2 = st.columns(\[2, 1])  # 2:1 비율

with col1:
    st.metric("정확도", "89.31%", "+2.1%")

with col2:
    st.metric("처리 속도", "1.2초", "-0.3초")
```

### 6.3 탭

```python
tab1, tab2, tab3 = st.tabs(\["💬 챗봇", "📊 통계", "⚙️ 설정"])

with tab1:
    st.write("챗봇 내용")

with tab2:
    st.write("통계 내용")

with tab3:
    st.write("설정 내용")
```

### 6.4 확장/접기 (Expander)

```python
with st.expander("🔍 검색된 문서 보기"):
    for i, hit in enumerate(hits, 1):
        st.markdown(f"\*\*문서 {i}\*\* (페이지 {hit\['page']}, 유사도 {hit\['score']})")
        st.text(hit\['text'])
        st.divider()
```

\---

## 7\. 챗봇 코드 줄별 해석

### 7.1 초기화 블록

```python
# ── session\_state 초기화 ──
if "messages" not in st.session\_state:
    st.session\_state.messages = \[]
```

**왜 `if "messages" not in`으로 시작하나요?**  
스크립트가 재실행될 때마다 이 코드가 실행됩니다.  
`if` 없이 `st.session\_state.messages = \[]`라고 쓰면
사용자가 입력할 때마다 대화 이력이 지워집니다.  
`if "messages" not in`으로 감싸면 **처음 한 번만** 초기화됩니다.

### 7.2 대화 이력 표시 블록

```python
for msg in st.session\_state.messages:
    with st.chat\_message(msg\["role"]):
        st.markdown(msg\["content"])
```

**왜 이걸 매번 다시 그리나요?**  
Streamlit은 재실행마다 화면을 처음부터 다시 그립니다.  
이 반복문이 저장된 모든 대화를 매번 화면에 다시 출력합니다.  
이것이 Streamlit 채팅 앱의 기본 패턴입니다.

### 7.3 사용자 입력 + 처리 블록

```python
user\_input = st.chat\_input("질문을 입력하세요...")
query = user\_input or pending  # 직접 입력 또는 버튼 클릭

if query:
    # 화면에 표시
    with st.chat\_message("user"):
        st.markdown(query)
    
    # 이력에 추가
    st.session\_state.messages.append({"role": "user", "content": query})
    
    # 답변 생성
    with st.chat\_message("assistant"):
        with st.spinner("검색 중..."):
            answer = generate\_answer(...)
        st.markdown(answer)
    
    # 이력에 추가
    st.session\_state.messages.append({"role": "assistant", "content": answer})
```

**흐름 정리:**  
`query` 감지 → 사용자 말풍선 출력 → 이력에 저장 → 답변 생성(스피너) → 답변 말풍선 출력 → 이력에 저장

**이 순서가 중요한 이유:**  
`st.chat\_input`에 값이 들어오는 순간 스크립트가 재실행됩니다.  
말풍선을 먼저 그리고 → 이력에 저장해야 다음 재실행 시 이력이 올바르게 표시됩니다.

### 7.4 사이드바 버튼 → pending 패턴

```python
# 사이드바에서
if st.button("예시 질문 1"):
    st.session\_state\["pending\_question"] = "예시 질문 1"

# 메인 영역에서
pending = st.session\_state.pop("pending\_question", None)
query = user\_input or pending
```

**왜 이렇게 복잡하게 하나요?**  
사이드바 버튼을 클릭하면 스크립트가 재실행됩니다.  
재실행 시 `st.chat\_input`에는 아무것도 없습니다.  
버튼 클릭으로 입력된 질문을 `session\_state`에 임시 저장했다가  
메인 로직에서 꺼내 쓰는 패턴입니다.  
`.pop()`을 쓰는 이유는 한 번만 처리하고 제거하기 위함입니다.

\---

## 8\. 자주 하는 실수와 해결법

### 실수 1: session\_state 없이 카운터 구현

```python
# ❌ 클릭해도 카운터가 오르지 않음
count = 0
if st.button("클릭"):
    count += 1
st.write(count)  # 항상 0 또는 1

# ✅ 올바른 방법
if "count" not in st.session\_state:
    st.session\_state.count = 0
if st.button("클릭"):
    st.session\_state.count += 1
st.write(st.session\_state.count)  # 누적됨!
```

### 실수 2: 캐싱 없이 무거운 작업 반복

```python
# ❌ 사용자 입력마다 모델을 다시 로드
model = load\_big\_model()  # 30초 × 매번...

# ✅ 캐싱으로 최초 1회만 로드
@st.cache\_resource
def load\_model():
    return load\_big\_model()
model = load\_model()  # 첫 번째만 30초, 이후는 즉시
```

### 실수 3: st.rerun() 남용

```python
# ❌ rerun을 너무 많이 쓰면 무한 루프 가능
if condition:
    st.session\_state.something = value
    st.rerun()  # 꼭 필요한 경우에만 사용

# ✅ 대부분의 경우 rerun 없이도 다음 상호작용 시 자동 반영됨
st.session\_state.something = value
# 다음에 사용자가 무언가 하면 자동으로 반영됨
```

### 실수 4: 대화 이력 형식 혼동

```python
# Streamlit 화면 표시용 형식
{"role": "user", "content": "질문"}       # role: user/assistant
{"role": "assistant", "content": "답변"}

# Gemini API 전달용 형식
{"role": "user", "parts": "질문"}          # role: user/model
{"role": "model", "parts": "답변"}         # ← "model" (assistant 아님!)
```

Gemini API는 "assistant" 대신 \*\*"model"\*\*을 씁니다. 혼동 주의!

\---

## 빠른 참고 카드

```
화면 표시      → st.title(), st.markdown(), st.write()
입력 위젯      → st.text\_input(), st.chat\_input(), st.button()
알림           → st.success(), st.error(), st.warning()
로딩           → st.spinner(), st.progress()
채팅 말풍선    → st.chat\_message("user" / "assistant")
상태 저장      → st.session\_state
캐싱 (객체)    → @st.cache\_resource
캐싱 (데이터)  → @st.cache\_data
화면 새로고침  → st.rerun()
사이드바       → with st.sidebar:
열 레이아웃    → col1, col2 = st.columns(2)
```

\---

*Streamlit 공식 문서:* [*docs.streamlit.io*](https://docs.streamlit.io)  
*갤러리(예제 모음):* [*streamlit.io/gallery*](https://streamlit.io/gallery)

