"""
============================================================
text_clustering
한국어 문서를 SBERT/Gemini 임베딩으로 벡터화한 뒤,
K-means로 클러스터링하고 Gemini로 주제명을 도출하는 실습.

[설치]
  pip install google-genai sentence-transformers scikit-learn matplotlib python-dotenv

[실행]
  # Gemini API를 쓰려면 .env에 GEMINI_API_KEY=... 설정 (없으면 자동으로 SBERT 사용)
  python 01_text_clustering.py

[3단계 파이프라인]
  1) 임베딩  : 모든 문서를 벡터화 → embeddings.json 저장 (재실행 시 캐시 재사용)
  2) K 선택  : embeddings.json 로드 → 엘보우·실루엣 그림 표시/저장 → 연구자가 K 입력
  3) 클러스터링 분석 : K-means 실행 → 각 클러스터 멤버를 중심거리 기준으로 순위 매김
                      → clusters.json 저장

[출력]
  - embeddings.json      : 입력 문서와 임베딩 벡터 (단계 2/3의 입력)
  - k_selection.png      : K 후보별 엘보우·실루엣 그래프
  - clusters.json        : 클러스터별 결과 (멤버에 rank = 중심거리 순위 포함)
============================================================
"""

# ------------------------------------------------------------
# (A) 라이브러리 임포트
# ------------------------------------------------------------
import os
import json
import time
import platform
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score

# matplotlib 한글 폰트 설정 (한글 깨짐 방지)
def _setup_korean_font():
    system = platform.system()
    if system == "Windows":
        matplotlib.rcParams["font.family"] = "Malgun Gothic"
        return
    if system == "Darwin":
        matplotlib.rcParams["font.family"] = "AppleGothic"
        return

    # Linux / WSL: 시스템 폰트 파일을 직접 matplotlib에 등록해야 잡힘
    from matplotlib import font_manager as fm

    candidates = []
    # 1) fontconfig가 추천하는 한글 폰트 경로
    try:
        import subprocess
        r = subprocess.run(
            ["fc-match", "-f", "%{file}", ":lang=ko"],
            capture_output=True, text=True, timeout=2,
        )
        if r.returncode == 0 and r.stdout.strip():
            candidates.append(r.stdout.strip())
    except Exception:
        pass
    # 2) 흔한 설치 경로 후보 (NanumGothic, Noto Sans CJK)
    candidates += [
        os.path.expanduser("~/.local/share/fonts/NanumGothic.ttf"),
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]

    for path in candidates:
        if path and os.path.exists(path):
            fm.fontManager.addfont(path)
            family = fm.FontProperties(fname=path).get_name()
            matplotlib.rcParams["font.family"] = family
            return
    print("  [경고] 한글 폰트를 찾지 못함. 그래프의 한글이 깨질 수 있음.")


_setup_korean_font()
matplotlib.rcParams["axes.unicode_minus"] = False


# ============================================================
# 1. 분석 대상 문서 리스트
#    실전에서는 CSV/DB에서 불러오면 됨. 여기서는 18개 한국어 문서.
#    의도적으로 6개 주제(정치/경제/기술/스포츠/부동산/환경)를 섞어놓음.
# ============================================================
DOCUMENTS = [
    # --- 정치 ---
    "여당은 부동산 정책 실패를 인정하고 새로운 공급 대책을 발표했다. 야당은 책임자 처벌을 요구했다.",
    "대통령은 신년 기자회견에서 외교 정책 기조를 설명하고 한미동맹 강화를 강조했다.",
    "국회는 검찰 개혁 법안을 본회의에 상정했으나 여야 충돌로 표결이 무산되었다.",

    # --- 경제·금융 ---
    "코스피 지수가 2700선을 회복했다. 외국인 매수세가 유입되며 시장 회복 신호가 나타났다.",
    "한국은행은 기준금리를 동결하기로 결정했다. 인플레이션 우려가 여전하다는 판단이다.",
    "원달러 환율이 1380원대로 올라서며 수출 기업에는 호재, 수입 기업에는 부담으로 작용한다.",

    # --- AI·기술 ---
    "OpenAI가 GPT-5를 공개했다. 추론 성능이 대폭 향상되었고 멀티모달 처리도 가능해졌다.",
    "구글은 Gemini 모델의 새 버전을 발표하며 코딩 성능에서 경쟁사를 앞섰다고 주장했다.",
    "딥페이크 영상 탐지 기술이 빠르게 발전하지만 생성 기술의 발전 속도가 더 빠르다.",

    # --- 스포츠 ---
    "손흥민이 토트넘에서 시즌 20호 골을 기록했다. 프리미어리그 득점 순위 3위에 올랐다.",
    "한국 야구 대표팀이 WBC 본선 진출을 확정했다. 류현진의 호투가 결정적이었다.",
    "KBO 정규시즌이 개막했다. 디펜딩 챔피언 LG 트윈스가 첫 경기에서 승리를 거뒀다.",

    # --- 부동산 ---
    "제주도 부동산 시장이 침체에서 벗어날 조짐을 보인다. 중국 자본의 재유입이 관측된다.",
    "서울 아파트 매매가가 3주 연속 상승했다. 강남권 재건축 단지가 상승을 주도했다.",
    "전세 사기 피해자 구제 특별법이 시행되었으나 실효성에 대한 비판이 이어지고 있다.",

    # --- 환경·재난 ---
    "올해 여름 폭염이 역대 최고 기록을 경신했다. 기후변화의 영향이라는 분석이 지배적이다.",
    "동해안에서 진도 4.2 규모의 지진이 발생했다. 인명 피해는 보고되지 않았다.",
    "미세먼지 농도가 '나쁨' 수준으로 올라가며 시민들의 외출 자제 권고가 발령됐다.",
]


# ============================================================
# 2. 임베딩 함수 — 두 가지 옵션
# ============================================================
# .env 파일 로드. API 키 읽기
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def embed_with_gemini(texts, batch_size=50):
    """
    Gemini Embedding API로 텍스트를 벡터화한다.
    - task_type='CLUSTERING' 을 반드시 지정해야 클러스터링용으로 최적화된 벡터가 나옴.
    - output_dimensionality=768로 차원을 줄여 메모리·속도 향상 (Matryoshka 학습).
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    vectors = []

    # API는 한 번에 많은 문서를 받을 수 있지만, 안전하게 batch_size 단위로 나눠 호출
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.models.embed_content(
            model="gemini-embedding-001",
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="CLUSTERING",
                output_dimensionality=768,
            ),
        )
        vectors.extend([e.values for e in resp.embeddings])
        time.sleep(0.3)  # rate limit 회피용 짧은 대기

    return np.array(vectors)


def embed_with_sbert(texts, model_name="intfloat/multilingual-e5-large"):
    """
    오픈소스 SBERT 모델로 임베딩 (API 키 불필요, 로컬 GPU/CPU에서 실행).
    - multilingual-e5-large : 100개 언어 지원, 한국어 성능 우수
    - 대체: 'jhgan/ko-sroberta-multitask' (한국어 전용, 더 가볍지만 약간 낮음)
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)

    # E5 계열 모델은 입력 앞에 'passage: ' 접두사를 붙여야 최적 성능
    if "e5" in model_name.lower():
        texts = [f"passage: {t}" for t in texts]

    # normalize_embeddings=True → 출력 벡터가 단위벡터로 나옴 (코사인 유사도 = 내적)
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return vectors


# ============================================================
# 3. 최적 K 탐색: 엘보우 + 실루엣
# ============================================================

def find_optimal_k(X, k_range=(2, 11), chart_path="k_selection.png"):
    """
    K 후보별로 두 가지 지표를 계산한다.

    [엘보우 (Elbow)]
      - K가 커질수록 inertia(클러스터 내 분산 합)는 단조 감소.
      - 감소율이 급격히 꺾이는 '팔꿈치' 지점이 좋은 K 후보.

    [실루엣 (Silhouette)]
      - 각 점이 자기 클러스터에 잘 맞고 다른 클러스터와는 멀리 떨어져 있는지 측정.
      - -1 ~ +1 범위, 값이 클수록 좋음.

    두 지표가 시사하는 K가 일치하면 자신감 있게 채택,
    다르면 후보 K들에 대해 대표 문서를 직접 확인해 결정.
    """
    ks = list(range(k_range[0], k_range[1]))
    inertias, silhouettes = [], []

    print(f"\n  K 후보 탐색 (K = {ks[0]} ~ {ks[-1]})")
    print(f"  {'K':>3} | {'inertia':>10} | {'silhouette':>11}")
    print("  " + "-" * 35)

    for k in ks:
        # n_init=20 : 무작위 초기화를 20번 시도해 가장 좋은 결과 선택 (안정성 ↑)
        km = KMeans(n_clusters=k, n_init=20, random_state=42)
        labels = km.fit_predict(X)

        inertia = km.inertia_
        sil = silhouette_score(X, labels)
        inertias.append(inertia)
        silhouettes.append(sil)
        print(f"  {k:>3} | {inertia:>10.3f} | {sil:>11.4f}")

    # ---- 그래프 그리기 ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(ks, inertias, "o-", color="steelblue", linewidth=2)
    ax1.set_xlabel("K (클러스터 수)")
    ax1.set_ylabel("Inertia (WCSS)")
    ax1.set_title("엘보우 (Elbow Method) — 꺾이는 지점이 좋은 K")
    ax1.grid(alpha=0.3)

    ax2.plot(ks, silhouettes, "o-", color="darkorange", linewidth=2)
    ax2.set_xlabel("K (클러스터 수)")
    ax2.set_ylabel("Silhouette Score")
    ax2.set_title("실루엣 점수 — 최고점이 좋은 K")
    ax2.grid(alpha=0.3)

    # 실루엣 최고점 표시
    best_idx = int(np.argmax(silhouettes))
    ax2.axvline(ks[best_idx], color="red", linestyle="--", alpha=0.6,
                label=f"max @ K={ks[best_idx]}")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(chart_path, dpi=120, bbox_inches="tight")
    print(f"\n  그래프 저장: {chart_path}")
    print("  창을 닫으면 K 입력 단계로 진행합니다.")
    plt.show()       # 그래프 창을 띄워 연구자가 직접 확인
    plt.close("all")

    # 실루엣 최고 K를 '추천값'으로 함께 반환 (사용자 입력의 기본값으로 사용)
    return ks[best_idx], ks


def ask_k_from_user(suggested_k, valid_ks):
    """
    연구자가 엘보우/실루엣 그래프를 직접 보고 K를 입력하도록 한다.
    - 엔터만 누르면 추천 K(실루엣 최대)를 채택.
    - 유효 범위를 벗어나거나 정수가 아니면 다시 묻는다.
    """
    while True:
        raw = input(
            f"\n  사용할 K를 입력하세요 (가능 범위 {valid_ks[0]}~{valid_ks[-1]}, "
            f"엔터=추천값 {suggested_k}): "
        ).strip()
        if raw == "":
            return suggested_k
        try:
            k = int(raw)
        except ValueError:
            print("  [재입력] 정수를 입력해 주세요.")
            continue
        if k not in valid_ks:
            print(f"  [재입력] {valid_ks[0]}~{valid_ks[-1]} 범위의 값이어야 합니다.")
            continue
        return k


# ============================================================
# 4. Gemini로 클러스터 주제 명명
# ============================================================

def name_cluster_with_gemini(rep_docs):
    """
    대표 문서를 Gemini에 보내 클러스터 주제를 JSON으로 받아온다.
    JSON 응답을 강제하기 위해 response_mime_type='application/json' 지정.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    joined = "\n---\n".join(rep_docs)

    prompt = f"""다음은 같은 클러스터로 묶인 대표 문서들이다.
공통 주제를 도출해 아래 JSON 형식으로만 응답하라.

{{
  "topic_name": "15자 이내 주제명",
  "description": "2~3문장 설명",
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"]
}}

문서:
{joined}
"""
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return json.loads(resp.text)


# ============================================================
# 5. 단계별 파이프라인 함수
# ============================================================

EMBEDDINGS_PATH = "embeddings.json"
CLUSTERS_PATH = "clusters.json"
CHART_PATH = "k_selection.png"


def stage1_build_embeddings(documents, use_gemini, path=EMBEDDINGS_PATH):
    """
    [1단계] 문서 임베딩 → embeddings.json 저장.
    동일한 문서 목록의 캐시가 있으면 임베딩을 재계산하지 않고 재사용한다.
    """
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cached = json.load(f)
        if cached.get("documents") == list(documents):
            print(f"[1/3] 캐시 재사용: {path} (문서 {len(documents)}개)")
            return

    print(f"[1/3] 문서 {len(documents)}개 임베딩")
    if use_gemini:
        print("      → Gemini Embedding API 사용")
        X = embed_with_gemini(documents)
        model_name = "gemini-embedding-001"
    else:
        print("      → SBERT (multilingual-e5-large) 사용")
        X = embed_with_sbert(documents)
        model_name = "intfloat/multilingual-e5-large"

    payload = {
        "model": model_name,
        "use_gemini": use_gemini,
        "dim": int(X.shape[1]),
        "n_docs": len(documents),
        "documents": list(documents),
        "embeddings": X.tolist(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"      저장: {path}  (shape={X.shape})")


def stage2_select_k(embeddings_path=EMBEDDINGS_PATH, chart_path=CHART_PATH,
                    k_range=(2, 11)):
    """
    [2단계] embeddings.json 로드 → 엘보우·실루엣 분석 그림 표시/저장
            → 연구자가 K 입력.
    반환: (정규화된 X, 문서 리스트, 선택한 K)
    """
    print(f"\n[2/3] {embeddings_path} 로드 → K 탐색")
    with open(embeddings_path, encoding="utf-8") as f:
        data = json.load(f)
    X = np.array(data["embeddings"], dtype=float)
    documents = data["documents"]

    # L2 정규화: 모든 벡터를 단위 구로 보내 KMeans의 유클리드 거리가 코사인 거리와 동치가 되게 함
    X = normalize(X, norm="l2")
    print(f"      입력 shape: {X.shape}")

    suggested_k, valid_ks = find_optimal_k(X, k_range=k_range, chart_path=chart_path)
    print(f"      → 실루엣 기준 추천 K = {suggested_k}")
    best_k = ask_k_from_user(suggested_k, valid_ks)
    print(f"      → 선택한 K = {best_k}")
    return X, documents, best_k


def stage3_cluster_and_analyze(X, documents, k, use_gemini,
                               clusters_path=CLUSTERS_PATH):
    """
    [3단계] K-means 실행 → 각 클러스터 멤버를 중심거리 기준으로 정렬해 'rank' 부여
            → clusters.json 저장.

    KMeans는 sklearn에서 유클리드 거리만 지원하지만, 입력이 이미 L2 정규화된 단위벡터라
    유클리드 최소화는 코사인 유사도 최대화와 동치다 (||a-b||^2 = 2 - 2*cos(a,b)).
    """
    print(f"\n[3/3] K={k}으로 K-means 실행 + 결과 분석")
    km = KMeans(n_clusters=k, n_init=30, random_state=42)
    labels = km.fit_predict(X)

    clusters = []
    for c in sorted(set(labels)):
        idx = np.where(labels == c)[0]              # 이 클러스터 멤버 인덱스
        center = X[idx].mean(axis=0)                # 중심(centroid) 벡터
        dists = np.linalg.norm(X[idx] - center, axis=1)
        order = np.argsort(dists)                   # 중심에 가까운 순

        members = []
        for rank, pos in enumerate(order, start=1):
            doc_id = int(idx[pos])
            members.append({
                "rank": rank,                              # 1 = 중심에 가장 가까움 (대표성 ↑)
                "doc_id": doc_id,
                "distance_to_center": float(dists[pos]),
                "text": documents[doc_id],
            })

        cluster_info = {
            "cluster_id": int(c),
            "size": int(len(idx)),
            "members": members,
        }

        if use_gemini:
            try:
                rep_docs = [m["text"] for m in members[:3]]  # 상위 3개 = 가장 전형적인 문서
                topic = name_cluster_with_gemini(rep_docs)
                cluster_info["topic_name"] = topic["topic_name"]
                cluster_info["description"] = topic["description"]
                cluster_info["keywords"] = topic["keywords"]
            except Exception as e:
                cluster_info["topic_error"] = str(e)

        clusters.append(cluster_info)

    payload = {"k": int(k), "n_docs": len(documents), "clusters": clusters}
    with open(clusters_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"      저장: {clusters_path}")

    # ---- 콘솔 출력 ----
    print("=" * 70)
    for cl in clusters:
        print(f"\n[Cluster {cl['cluster_id']}]  n={cl['size']}")
        if "topic_name" in cl:
            print(f"  ▸ 주제명: {cl['topic_name']}")
            print(f"  ▸ 설명  : {cl['description']}")
            print(f"  ▸ 키워드: {', '.join(cl['keywords'])}")
        elif "topic_error" in cl:
            print(f"  (주제 도출 실패: {cl['topic_error']})")

        print("  ▸ 대표 문서 (rank = 중심에 가까운 순):")
        for m in cl["members"][:3]:
            t = m["text"]
            preview = t[:60] + ("..." if len(t) > 60 else "")
            print(f"    {m['rank']}. (d={m['distance_to_center']:.4f}) {preview}")

    print("\n" + "=" * 70)
    print(f"저장 완료: {CHART_PATH}, {clusters_path}")


# ============================================================
# 6. 메인 — 세 단계를 순서대로 실행
# ============================================================

def main():
    use_gemini = True  # True: Gemini Embedding API 사용 / False: 로컬 SBERT 사용

    # 1) 임베딩: 동일 문서면 캐시 재사용, 아니면 새로 계산해 embeddings.json 저장
    stage1_build_embeddings(DOCUMENTS, use_gemini=use_gemini)

    # 2) embeddings.json 다시 읽어와 K 분석/선택 (그림 저장 + 사용자 입력)
    X, documents, best_k = stage2_select_k()

    # 3) 클러스터링 결과 분석 → clusters.json (멤버에 중심거리 순위 'rank' 포함)
    stage3_cluster_and_analyze(X, documents, best_k, use_gemini=use_gemini)


if __name__ == "__main__":
    main()
