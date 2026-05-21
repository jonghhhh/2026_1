"""
=====================================================================
공정선거보도 안내서 RAG 챗봇
=====================================================================
인터넷선거보도심의위원회의 「2026 공정선거보도 안내서」 (105쪽)를
RAG (Retrieval-Augmented Generation) 방식으로 질의응답하는 챗봇.

[기술 스택]
- 임베딩 모델 : Gemini Embedding 001 (768차원, Matryoshka 절단)
- 벡터 DB     : Chroma (로컬 영구 저장, 코사인 유사도)
- 청킹 방식   : LangChain RecursiveCharacterTextSplitter
- 생성 모델   : Gemini 2.5 Flash Lite

[강의안 핵심 개념 반영]
- 비대칭 임베딩 (task_type 짝맞춤):
    문서 저장 시 retrieval_document ↔ 질문 검색 시 retrieval_query
- 페이지 단위 사전 분리 후 재귀적 청킹 → 출처 인용 정확도 향상
- 프롬프트로 출처 표기 강제 + "모르면 모른다고" 답하기 유도

[준비 사항]
1) 패키지 설치:
     pip install google-generativeai chromadb langchain-text-splitters python-dotenv

2) 같은 폴더에 `.env` 파일 생성 후 한 줄 저장:
     GEMINI_API_KEY=AIza...본인_키...

3) 같은 폴더에 입력 문서가 있어야 함:
     공정선거보도_안내서_RAG용.txt

[실행]
   python 공정선거보도_RAG.py

   첫 실행 시  : Chroma DB를 빌드 (약 2~3분 소요) → 빌드 완료 메시지 후 질문 입력
   이후 실행 시: 빌드된 DB를 즉시 로드 → 바로 질문 가능

[DB 재빌드]
   ./chroma_election_db 폴더를 삭제한 뒤 다시 실행하면 새로 빌드됩니다.
=====================================================================
"""

import os
import re
import sys
import time
from pathlib import Path

# === 외부 라이브러리 ===
from dotenv import load_dotenv               # .env 파일 로드
import google.generativeai as genai           # Gemini API
import chromadb                               # 벡터 DB
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =====================================================================
#  설정값  ─  필요시 이 부분만 조정하면 됩니다
# =====================================================================
TXT_PATH = "2026_공정선거보도_안내서_중앙선거관리위원회.txt"   # 입력 문서 경로
DB_PATH = "./chroma_election_db"             # Chroma 영구 저장 경로
COLLECTION_NAME = "election_guide"           # Chroma 컬렉션 이름

EMBED_MODEL = "gemini-embedding-001"         # 임베딩 모델명
GEN_MODEL = "gemini-2.5-flash-lite"          # 답변 생성 모델명
EMBED_DIM = 768                              # 임베딩 차원 (Matryoshka 절단)

CHUNK_SIZE = 500                             # 청크 크기 (한국어 기준 권장값)
CHUNK_OVERLAP = 50                           # 청크 간 겹침 (맥락 보존)
TOP_K = 5                                    # 검색해서 가져올 청크 수
RATE_LIMIT_SLEEP = 0.1                       # API 호출 간격 (무료 tier 보호)


# =====================================================================
#  1. 환경 설정 ─ .env 파일에서 API 키를 읽어와 Gemini 클라이언트 구성
# =====================================================================
def setup_env():
    """`.env`의 GEMINI_API_KEY를 로드해 Gemini SDK에 등록합니다."""
    load_dotenv()                            # 같은 폴더의 .env 파일 자동 로드
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        # 키가 없으면 안내 메시지 출력 후 종료
        print("❌ .env 파일에 GEMINI_API_KEY가 없습니다.")
        print("   같은 폴더에 .env 파일을 만들고 다음 한 줄을 추가하세요:")
        print("   GEMINI_API_KEY=AIza...본인_키...")
        sys.exit(1)

    genai.configure(api_key=api_key)


# =====================================================================
#  2. 문서 로드 + 청킹
# =====================================================================
def load_and_chunk(txt_path: str):
    """
    공정선거보도 안내서 TXT를 페이지 단위로 먼저 분할한 뒤,
    각 페이지 내부에서 RecursiveCharacterTextSplitter로 작은 청크를 만듭니다.

    [페이지 단위 사전 분리의 이점]
    1) 각 청크의 출처 페이지가 메타데이터로 자동 부착됨 → 답변에 정확한 페이지 인용 가능
    2) 페이지 경계를 가로지르는 청크가 생기지 않음 → 의미 혼합 방지

    [재귀적 청킹 (RecursiveCharacterTextSplitter)]
    문서를 큰 단위(단락) → 작은 단위(줄·문장·어절) 순으로 분할 시도.
    의미 단위를 가능한 한 보존하면서 chunk_size를 맞춤.

    Returns
    -------
    list[dict]  ─  [{"text": 청크 내용, "page": 페이지 번호}, ...]
    """
    # 입력 파일 존재 확인
    if not Path(txt_path).exists():
        print(f"❌ 입력 파일이 없습니다: {txt_path}")
        sys.exit(1)

    text = Path(txt_path).read_text(encoding="utf-8")

    # [페이지 N] 마커를 기준으로 분할 (캡처 그룹으로 페이지 번호도 함께 추출)
    # 결과 구조: [서문, '1', 페이지1 본문, '2', 페이지2 본문, ...]
    parts = re.split(r'\n*\[페이지 (\d+)\]\n*', text)

    # 재귀적 청킹 도구 준비
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        # 우선순위 높은 구분자부터 시도: 단락 → 줄 → 문장 → 어절
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []
    # parts에서 인덱스 1,3,5,... = 페이지 번호 / 2,4,6,... = 본문
    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        page_text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if not page_text:
            continue

        # 페이지 내부 텍스트를 재귀적으로 청킹
        for chunk in splitter.split_text(page_text):
            chunk = chunk.strip()
            if len(chunk) >= 30:    # 너무 짧은 청크(노이즈)는 제외
                chunks.append({"text": chunk, "page": page_num})

    return chunks


# =====================================================================
#  3. Gemini Embedding 호출  ─  비대칭 임베딩의 핵심
# =====================================================================
def embed_text(text: str, task_type: str):
    """
    Gemini Embedding 모델 호출.

    task_type (강의안 4.1.1절 참고 — 비대칭 임베딩)
    ------------------------------------------------
    • 'retrieval_document' : 문서를 벡터 DB에 *저장*할 때
    • 'retrieval_query'    : 사용자 질문을 *검색*할 때

    저장되는 문서는 보통 서술문, 사용자 질문은 보통 의문문이라
    표면 구조가 다릅니다. task_type을 짝맞춰야 모델이 두 종류를
    같은 의미 공간에서 가깝게 매핑해 줍니다.

    짝이 안 맞으면 검색 정확도가 미묘하게 떨어집니다.
    """
    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type=task_type,
        output_dimensionality=EMBED_DIM      # Matryoshka 절단으로 차원 축소
    )
    return result["embedding"]               # 길이 EMBED_DIM의 리스트


# =====================================================================
#  4. Chroma DB 빌드  (이미 있으면 그대로 로드)
# =====================================================================
def build_index():
    """
    빌드 단계:
      ① TXT 로드 → ② 페이지별 청킹 → ③ 청크별 임베딩 → ④ Chroma에 저장

    이미 빌드된 DB(`COLLECTION_NAME` 컬렉션에 데이터가 차 있는 상태)가
    있으면 그대로 로드해 빠르게 시작합니다.
    """
    # 영구 저장 클라이언트 (디스크에 SQLite로 저장됨)
    client = chromadb.PersistentClient(path=DB_PATH)

    # 이미 빌드된 컬렉션이 있는지 확인
    try:
        col = client.get_collection(COLLECTION_NAME)
        if col.count() > 0:
            print(f"✅ 기존 DB 발견: {col.count()}개 청크. 빌드를 건너뜁니다.\n")
            return col
        # 비어 있으면 삭제 후 재생성
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass    # 컬렉션이 없으면 아래에서 새로 만듦

    # 컬렉션 생성 — 코사인 유사도 기반 인덱스
    col = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}    # 텍스트 임베딩 표준
    )

    # --- 1단계: 청킹 ---
    print("📄 [1/2] 문서 로드 및 청킹")
    chunks = load_and_chunk(TXT_PATH)
    print(f"   → 총 {len(chunks)}개 청크 생성")
    print(f"   → 첫 청크 미리보기: {chunks[0]['text'][:80]}... (페이지 {chunks[0]['page']})")

    # --- 2단계: 임베딩 + 저장 ---
    eta_min = len(chunks) * 0.6 / 60         # 대략 청크당 0.6초 가정
    print(f"\n🔢 [2/2] Gemini 임베딩 + Chroma 저장 (약 {eta_min:.1f}분 예상)")

    for i, ch in enumerate(chunks, 1):
        try:
            # 문서 저장용 임베딩 (task_type=retrieval_document)
            vec = embed_text(ch["text"], task_type="retrieval_document")
            col.add(
                ids=[f"doc_{i:04d}"],        # 고유 ID
                embeddings=[vec],            # 임베딩 벡터
                documents=[ch["text"]],      # 원본 텍스트
                metadatas=[{"page": ch["page"]}]    # 페이지 메타데이터
            )
        except Exception as e:
            # rate limit 등 일시적 오류 → 잠시 쉬고 다음으로
            print(f"   ⚠️  청크 {i} 임베딩 실패: {e}")
            time.sleep(2)
            continue

        # 진행 상황 표시
        if i % 20 == 0 or i == len(chunks):
            print(f"   진행: {i}/{len(chunks)}")
        time.sleep(RATE_LIMIT_SLEEP)         # rate limit 회피용 짧은 대기

    print(f"\n✅ 빌드 완료! {col.count()}개 청크가 {DB_PATH} 에 저장되었습니다.\n")
    return col


# =====================================================================
#  5. 검색 + 답변 생성
# =====================================================================
def search(collection, query: str, top_k: int = TOP_K):
    """
    사용자 질문을 임베딩한 뒤 가장 가까운 청크 top_k개를 Chroma에서 검색.

    질문 임베딩은 반드시 task_type='retrieval_query'로 호출 (저장 시
    'retrieval_document'와 짝맞춤). 짝이 안 맞으면 검색 정확도 저하.
    """
    q_vec = embed_text(query, task_type="retrieval_query")

    results = collection.query(
        query_embeddings=[q_vec],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # 결과를 보기 좋게 정리
    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        hits.append({
            "text": doc,
            "page": meta["page"],
            "score": 1 - dist                # 코사인 거리 → 유사도로 변환
        })
    return hits


def answer(collection, query: str) -> str:
    """
    질문 → 검색 → 컨텍스트 구성 → Gemini Flash로 답변 생성.

    프롬프트 설계 핵심 (강의안 8장 참고):
      1) 각 주장 끝에 [페이지 N] 출처를 표기하도록 강제
      2) 자료에 없는 내용은 "제공된 자료로는 답할 수 없습니다"
      3) temperature 낮춤(0.2) → 사실 기반 답변, 환각 억제
    """
    # 1) 관련 청크 검색
    hits = search(collection, query)

    # 2) 컨텍스트 구성 — 각 청크에 [문서 N] (페이지 N) 라벨 부착
    context_parts = [
        f"[문서 {i}] (페이지 {h['page']})\n{h['text']}"
        for i, h in enumerate(hits, 1)
    ]
    context = "\n\n".join(context_parts)

    # 3) 프롬프트 작성
    prompt = f"""다음 문서들은 인터넷선거보도심의위원회의 「2026 공정선거보도 안내서」에서 발췌한 자료입니다.
이 자료만 참고하여 질문에 답해 주세요.

규칙:
1. 답변의 각 주장 끝에 [페이지 N] 형식으로 출처를 표기하세요.
2. 주어진 문서에 없는 내용은 추측하지 말고 "제공된 자료로는 답할 수 없습니다"라고 답하세요.
3. 답변은 한국어로 작성하세요.

{context}

질문: {query}

답변:"""

    # 4) Gemini 2.5 Flash로 답변 생성 (temperature 낮음 → 사실 기반)
    model = genai.GenerativeModel(GEN_MODEL)
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.2}
    )

    # 5) 검색된 페이지를 정리해서 답변 끝에 첨부
    source_pages = sorted({h["page"] for h in hits})
    return response.text + f"\n\n📚 참고한 페이지: {source_pages}"


# =====================================================================
#  6. 대화 루프  ─  질문 입력 → 답변 출력 반복
# =====================================================================
def chat_loop(collection):
    """ 사용자가 종료할 때까지 질문-답변을 반복 """
    print("=" * 60)
    print("💬 질문을 입력하세요  (종료: 'exit' / 'quit' / 빈 줄)")
    print("=" * 60)
    print("\n예시 질문:")
    print("  • 특정 후보자의 홍보자료를 그대로 게재하면 어떻게 되나요?")
    print("  • 여론조사 결과를 보도할 때 어떤 표현을 피해야 하나요?")
    print("  • 인터넷선거보도심의위원회는 어떻게 구성되나요?")
    print("  • 선거기간 중 특별제한 기간이 있나요?")
    print()

    while True:
        # 사용자 입력 받기 (Ctrl+C나 Ctrl+D 시 안전 종료)
        try:
            query = input("❓ 질문 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 종료합니다.")
            break

        # 종료 조건
        if not query or query.lower() in {"exit", "quit", "q"}:
            print("👋 종료합니다.")
            break

        # 답변 생성
        try:
            print("\n🔍 검색 중...\n")
            response = answer(collection, query)
            print("💡 답변:")
            print(response)
            print()
        except Exception as e:
            # API 오류·rate limit 등은 잡아서 출력만, 루프는 유지
            print(f"⚠️  오류 발생: {e}\n")


# =====================================================================
#  7. 메인 진입점
# =====================================================================
def main():
    print("\n🚀 공정선거보도 안내서 RAG 챗봇 시작\n")
    setup_env()                              # ① .env에서 API 키 로드
    collection = build_index()               # ② DB 빌드 또는 로드
    chat_loop(collection)                    # ③ 질문 입력 받기


if __name__ == "__main__":
    main()
