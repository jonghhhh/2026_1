# 🗳️ RAG 챗봇 + 배포

> \*\*대상:\*\* RAG·ChatBot·Streamlit·Hugging Face Spaces를 처음 접하는 학습자  
> \*\*목표:\*\* 챗봇이 어떻게 작동하는지 이해하고, Hugging Face Spaces에 배포

\---

## 목차

1. [전체 구조 한눈에 보기](#1-전체-구조-한눈에-보기)
2. [RAG란 무엇인가](#2-rag란-무엇인가)
3. [이 챗봇의 기술 스택](#3-이-챗봇의-기술-스택)
4. [로컬 실행 (개발 환경)](#4-로컬-실행-개발-환경)
5. [Hugging Face Spaces 배포](#5-hugging-face-spaces-배포)
6. [주요 설정값 조정 가이드](#6-주요-설정값-조정-가이드)
7. [자주 묻는 질문](#7-자주-묻는-질문)

\---

## 1\. 전체 구조 한눈에 보기

```
사용자 질문 입력
      │
      ▼
\[Streamlit UI] ──── 화면에 말풍선 형태로 대화 표시
      │
      ▼
\[Gemini Embedding] ── 질문을 768차원 숫자 벡터로 변환
      │
      ▼
\[Chroma 벡터 DB] ──── 비슷한 내용의 문서 조각(청크) 5개 검색
      │
      ▼
\[Gemini 2.5 Flash-Lite] ── 검색 결과 + 이전 대화 + 질문 → 답변 생성
      │
      ▼
화면에 답변 + 출처 페이지 표시
```

**비유로 이해하기**

> 도서관 사서(RAG 챗봇)에게 질문하면,
> 사서는 키워드로 책장(벡터 DB)에서 관련 페이지를 찾아오고,
> 그 페이지만 보면서 대답합니다.
> 사서가 기억에 의존하지 않고 \*\*항상 원문을 확인\*\*하므로
> 오답(환각, hallucination)이 훨씬 줄어듭니다.

\---

## 2\. RAG란 무엇인가

### 2.1 왜 RAG가 필요한가?

일반 LLM의 두 가지 한계:

|문제|설명|예시|
|-|-|-|
|**지식 단절 (Knowledge Cutoff)**|학습 데이터 이후의 내용은 모름|2026년 선거법 개정 내용|
|**환각 (Hallucination)**|모르는 내용을 그럴듯하게 지어냄|존재하지 않는 조항 번호 인용|

RAG는 이 두 문제를 **외부 문서 검색**으로 해결합니다.

### 2.2 RAG 3단계

```
① 준비 단계 (최초 1회)
   원본 문서 → 청크 분할 → 임베딩 → 벡터 DB 저장

② 검색 단계 (질문마다)
   사용자 질문 → 임베딩 → 벡터 DB에서 유사 청크 검색

③ 생성 단계 (질문마다)
   검색된 청크 + 질문 → LLM → 출처 포함 답변
```

### 2.3 임베딩(Embedding)이란?

텍스트를 숫자 벡터로 변환하는 기술입니다.

```
"선거 보도 공정성"  →  \[0.12, -0.45, 0.78, ...]  (768개 숫자)
"선거 뉴스 균형"    →  \[0.11, -0.43, 0.76, ...]  (비슷한 숫자!)
"오늘 날씨 맑음"    →  \[-0.89, 0.23, -0.11, ...]  (완전히 다른 숫자)
```

의미가 비슷한 문장은 **비슷한 벡터**를 가지므로, 코사인 유사도로 관련성을 측정할 수 있습니다.

### 2.4 비대칭 임베딩 (이 챗봇의 핵심 기법)

같은 임베딩 모델이라도 **역할에 따라 다른 task\_type**을 지정해야 합니다.

```python
# ✅ 올바른 사용
embed\_text("선거 보도 기준...", task\_type="retrieval\_document")  # 문서 저장 시
embed\_text("선거 보도 기준이 뭔가요?", task\_type="retrieval\_query")   # 질문 검색 시
```

## 3\. 이 챗봇의 기술 스택

### 3.1 구성 요소 설명

|구성 요소|역할|왜 이걸 선택했나|
|-|-|-|
|**Streamlit**|웹 UI|Python만으로 대화형 앱 구현, 설치 쉬움|
|**Gemini Embedding 001**|텍스트 → 벡터 변환|768차원 Matryoshka, 한국어 우수|
|**Chroma DB**|벡터 저장·검색|로컬 파일 기반, 별도 서버 불필요|
|**Gemini 2.5 Flash-Lite**|답변 생성|빠르고 저렴, 한국어 품질 우수|
|**Hugging Face Spaces**|무료 배포|GitHub 연동, 무료 CPU 인스턴스 제공|

### 3.2 데이터 흐름 상세

```
\[원본 TXT 파일]
    │  read\_text()
    ▼
\[전체 텍스트]  →  re.split("\[페이지 N]")  →  \[페이지별 텍스트 목록]
                                                    │
                                    RecursiveCharacterTextSplitter
                                                    │
                                              \[청크 목록]
                                    {"text": "...", "page": 23}
                                                    │
                                    embed\_text(task\_type="retrieval\_document")
                                                    │
                                              \[벡터 목록]
                                                    │
                                    chromadb.PersistentClient.add()
                                                    │
                                          \[Chroma DB 파일]
                                          (disk에 저장됨)
```

\---

## 4\. 로컬 실행 (개발 환경)

### 4.1 필요한 것

* Python 3.10 이상
* Gemini API 키 ([Google AI Studio](https://aistudio.google.com)에서 무료 발급)

### 4.2 설치 순서

```bash
# 1. 패키지 설치
pip install streamlit google-generativeai chromadb \\
            langchain-text-splitters python-dotenv

# 2. 파일 배치
#    같은 폴더에 아래 파일들이 있어야 합니다:
#    ├── rag챗봇\_배포.py
#    └── 2026\_공정선거보도\_안내서\_중앙선거관리위원회.txt

# 3. .env 파일 생성 (API 키 저장)
echo "GEMINI\_API\_KEY=AIza...본인키..." > .env

# 4. 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속하면 챗봇이 열립니다.

> 💡 \*\*첫 실행 시 주의:\*\*  
> DB 구축에 약 2\~3분이 걸립니다. 화면에 진행 바가 표시됩니다.  
> 이후 실행 시에는 저장된 DB를 즉시 로드하므로 5초 이내에 시작됩니다.

### 4.3 requirements.txt

배포를 위해 이 파일도 만들어두세요:

```
streamlit>=1.35.0
google-generativeai>=0.8.0
chromadb>=0.5.0
langchain-text-splitters>=0.2.0
python-dotenv>=1.0.0
```

\---

## 5\. Hugging Face Spaces 배포

> Hugging Face Spaces는 \*\*무료로 AI 앱을 배포\*\*할 수 있는 플랫폼입니다.  
> GitHub처럼 파일을 올리면 자동으로 앱이 실행됩니다.

### 5.1 Hugging Face 계정 만들기

1. [huggingface.co](https://huggingface.co) 접속 → **Sign Up**
2. 이메일 인증 완료

### 5.2 새 Space 만들기

1. 로그인 후 우측 상단 프로필 → **New Space** 클릭
2. 설정 입력:

|항목|값|
|-|-|
|**Space name**|`election-rag-chatbot` (원하는 이름)|
|**License**|MIT|
|**SDK**|**Streamlit** ← 반드시 선택!|
|**Space hardware**|CPU basic · Free|
|**Visibility**|Public 또는 Private|

3. **Create Space** 클릭

### 5.3 API 키 등록 (Secrets)

> 코드에 API 키를 직접 쓰면 절대 안 됩니다! Secrets를 사용하세요.

1. Space 페이지 → **Settings** 탭
2. **Repository secrets** 섹션 → **New secret** 클릭
3. 입력:

   * **Name:** `GEMINI\_API\_KEY`
   * **Value:** `AIza...본인키...`
4. **Save** 클릭

앱 코드에서 `st.secrets\["GEMINI\_API\_KEY"]`로 자동으로 읽어옵니다.

### 5.4 파일 업로드

Space에 올려야 할 파일 목록:

```
Space 루트
├── RAG챗봇\_배포.py              ← 챗봇 메인 코드
├── requirements.txt                ← 패키지 목록
└── 2026\_공정선거보도\_안내서\_중앙선거관리위원회.txt  ← 원본 문서
```

**방법 A: 웹 UI로 업로드 (쉬움)**

1. Space 페이지 → **Files** 탭 → **Add file** → **Upload files**
2. 위 세 파일을 드래그 앤 드롭
3. **Commit changes** 클릭 → 자동으로 앱 빌드 시작

**방법 B: Git으로 업로드 (추천)**

```bash
# Space를 로컬에 클론
git clone https://huggingface.co/spaces/본인아이디/election-rag-chatbot
cd election-rag-chatbot

# 파일 복사
cp app.py requirements.txt 2026\_공정선거보도\_안내서\_중앙선거관리위원회.txt ./

# 커밋 \& 푸시
git add .
git commit -m "Add RAG chatbot"
git push
```

### 5.5 빌드 확인

파일을 올리면 Space가 자동으로 빌드를 시작합니다.

* **Building** (파란색) → 빌드 중 (1\~3분)
* **Running** (초록색) → 앱 실행 중 ✅
* **Error** (빨간색) → Logs 탭에서 오류 확인

> ⚠️ \*\*Chroma DB 영구 저장 주의\*\*  
> Hugging Face Spaces의 무료 인스턴스는 \*\*재시작 시 파일이 초기화\*\*됩니다.  
> 따라서 앱이 재시작될 때마다 DB를 다시 구축합니다 (약 2\~3분 소요).  
> 이를 피하려면 DB 파일을 Space에 미리 커밋하거나, 유료 Persistent Storage를 사용하세요.

### 5.6 미리 빌드한 DB를 Space에 포함시키기 (권장)

로컬에서 DB를 먼저 구축한 뒤 통째로 업로드하면 배포 후 즉시 사용 가능합니다.

```bash
# 1. 로컬에서 DB 구축 (app.py를 한 번 실행하면 chroma\_election\_db/ 폴더 생성됨)
streamlit run app.py
# → 질문 한 번 하면 DB가 구축됨
# → Ctrl+C로 종료

# 2. DB 폴더를 Space에 포함시켜 커밋
git add chroma\_election\_db/
git commit -m "Add pre-built Chroma DB"
git push
```

\---

## 6\. 주요 설정값 조정 가이드

`app.py` 상단의 설정값을 바꾸면 챗봇 동작을 튜닝할 수 있습니다.

### 6.1 청킹 설정

```python
CHUNK\_SIZE = 500    # 청크 크기
CHUNK\_OVERLAP = 50  # 청크 간 겹침
```

|CHUNK\_SIZE|효과|
|-|-|
|200\~300|작고 정밀한 청크 → 특정 조항 검색에 유리|
|500 (기본)|균형잡힌 청크 (권장)|
|800\~1000|큰 청크 → 문맥이 풍부하지만 노이즈 증가|

### 6.2 검색 설정

```python
TOP\_K = 5  # 검색할 청크 수
```

* `TOP\_K = 3` → 빠르지만 컨텍스트가 적음
* `TOP\_K = 5` → 균형 (기본값)
* `TOP\_K = 8` → 풍부한 컨텍스트, 응답 시간 증가

### 6.3 생성 모델 temperature

```python
generation\_config={"temperature": 0.2}
```

|temperature|적합한 상황|
|-|-|
|0.0\~0.3|사실 기반 Q\&A (이 챗봇처럼 정확성 중요한 경우)|
|0.5\~0.7|일반적인 도우미|
|0.9\~1.0|창의적 글쓰기, 브레인스토밍|

\---

## 7\. 자주 묻는 질문

**Q: DB 구축이 너무 오래 걸립니다.**  
A: 무료 Gemini API는 분당 요청 수 제한이 있습니다. `RATE\_LIMIT\_SLEEP = 0.15`를 `0.3`으로 늘려보세요. 또는 로컬에서 미리 DB를 구축한 뒤 Space에 업로드하는 방법을 권장합니다.

**Q: "GEMINI\_API\_KEY를 찾을 수 없습니다" 오류가 납니다.**  
A: 로컬이면 `.env` 파일에 키가 있는지, Spaces라면 Settings → Secrets에 `GEMINI\_API\_KEY`가 등록됐는지 확인하세요.

**Q: 이전 대화 내용을 기억하지 못합니다.**  
A: 브라우저 탭을 새로고침하면 `session\_state`가 초기화됩니다. 같은 탭에서 계속 대화하면 이전 내용을 기억합니다.

**Q: 답변이 "제공된 자료에서는 확인할 수 없습니다"라고만 합니다.**  
A: 질문이 원본 문서 범위 밖이거나, 검색이 잘 안 된 경우입니다. 질문을 더 구체적으로 바꿔보거나, `TOP\_K`를 늘려보세요.

**Q: Hugging Face Space가 자꾸 잠듭니다 (sleeping).**  
A: 무료 Space는 일정 시간 사용이 없으면 잠듭니다. 첫 접속 시 깨어나는 데 30초\~1분 걸립니다. 유료 플랜을 사용하면 항상 켜둘 수 있습니다.

