"""
============================================================
image_clustering
CLIP으로 이미지를 임베딩하고 K-means로 클러스터링한 뒤,
Gemini Vision으로 각 클러스터의 시각적 주제를 도출하는 실습.

[설치]
  pip install torch transformers pillow requests google-genai \
              scikit-learn matplotlib python-dotenv

[실행]
  # Gemini Vision으로 주제 명명하려면 .env에 GEMINI_API_KEY=... 설정
  python Sbert_clustering_image.py

[3단계 파이프라인]
  1) 임베딩  : 이미지 다운로드 + CLIP 임베딩 → embeddings_image.json (캐시 재사용)
  2) K 선택  : embeddings_image.json 로드 → 엘보우·실루엣 그림 표시/저장 → 연구자가 K 입력
  3) 클러스터링 분석 : K-means → 각 클러스터 멤버를 중심거리 기준으로 순위 매김
                      → clusters_image.json + cluster_grid_image.png 저장

[출력]
  - embeddings_image.json   : 이미지 소스와 CLIP 임베딩 (단계 2/3의 입력)
  - k_selection_image.png   : K 후보별 엘보우·실루엣 그래프
  - cluster_grid_image.png  : 클러스터별 대표 이미지 그리드
  - clusters_image.json     : 클러스터별 결과 (멤버에 rank = 중심거리 순위 포함)
============================================================
"""

# ------------------------------------------------------------
# (A) 라이브러리 임포트
# ------------------------------------------------------------
import os
import io
import json
import time
import platform
import subprocess
import sys

import requests
import numpy as np
from PIL import Image

import torch
from transformers import CLIPModel, CLIPProcessor

import matplotlib
matplotlib.use("Agg")   # GUI 없는 환경(WSL·서버·headless)에서 plt.show() 블로킹 방지
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


def _open_file(path):
    """PNG 등을 시스템 기본 뷰어로 비동기 열기 (실패해도 계속 진행)."""
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(os.path.abspath(path))
        elif system == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


# .env 로드 + Gemini API 키
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


# ============================================================
# 1. 분석 대상 이미지 리스트
#    - 웹 URL과 로컬 경로를 자유롭게 섞어 넣을 수 있음.
#    - 아래 예시는 Unsplash의 공개 이미지로, 의도적으로 5가지 주제를 섞어둠.
#    - 실전에서는 폴더를 탐색해 자동으로 채울 수도 있음:
#         IMAGES = [str(p) for p in Path("./photos").glob("*.jpg")]
# ============================================================
IMAGES = [
    # --- 자연 풍경 (산/숲/바다) ---
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600",
    "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=600",
    "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=600",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600",

    # --- 도시·고층빌딩 ---
    "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=600",
    "https://images.unsplash.com/photo-1449034446853-66c86144b0ad?w=600",
    "https://images.unsplash.com/photo-1444723121867-7a241cacace9?w=600",

    # --- 음식 ---
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600",
    "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=600",
    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600",

    # --- 동물 (반려동물) ---
    "https://images.unsplash.com/photo-1543852786-1cf6624b9987?w=600",
    "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=600",
    "https://images.unsplash.com/photo-1535268647677-300dbf3d78d1?w=600",

    # --- 자동차 ---
    "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=600",
    "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=600",
    "https://images.unsplash.com/photo-1542362567-b07e54358753?w=600",

    # 로컬 파일도 혼용 가능 (필요시 주석 해제)
    # "./photos/my_image.jpg",
]


# ============================================================
# 2. 이미지 로드 (URL/로컬 모두 처리)
# ============================================================

def load_image(source):
    """URL이면 다운로드, 파일 경로면 디스크에서 로드. PIL Image 반환."""
    if source.startswith(("http://", "https://")):
        # User-Agent를 설정해 차단 회피
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(source, headers=headers, timeout=20)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content))
    else:
        img = Image.open(source)
    # CLIP은 RGB 3채널 이미지를 가정 (PNG의 RGBA, 흑백 L 모드 등을 모두 RGB로 변환)
    return img.convert("RGB")


# ============================================================
# 3. CLIP 이미지 임베딩
# ============================================================

def embed_images_with_clip(sources, model_name="openai/clip-vit-base-patch32",
                           batch_size=16):
    """
    CLIP 모델로 이미지를 벡터화한다.

    - 'openai/clip-vit-base-patch32': 가볍고 빠른 기본 모델 (512차원)
    - 'openai/clip-vit-large-patch14': 더 강력하지만 무거움 (768차원)
    - 한국어 caption 매칭까지 필요하면 'koclip', 'AIDC-AI/Marco-CLIP-Multi' 등 고려

    반환: (벡터 행렬, 성공한 이미지 경로 리스트, PIL 이미지 리스트)
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Device: {device}")
    if device == "cpu":
        # CPU 스레드를 최대한 활용해 추론 속도 향상
        torch.set_num_threads(os.cpu_count() or 4)
        print(f"  CPU 스레드: {torch.get_num_threads()}")

    # 모델·전처리기 로드 (첫 실행 시 HuggingFace 캐시 다운로드, 이후 로컬 재사용)
    print(f"  모델 로드: {model_name} ...")
    model = CLIPModel.from_pretrained(model_name).to(device).eval()
    processor = CLIPProcessor.from_pretrained(model_name)

    # ---- 모든 이미지 로드 (실패한 것은 제외) ----
    images, valid_sources = [], []
    for src in sources:
        try:
            img = load_image(src)
            images.append(img)
            valid_sources.append(src)
        except Exception as e:
            print(f"  로드 실패: {src[:60]}... ({e})")

    print(f"  로드 성공: {len(images)} / {len(sources)}")

    # ---- 배치 단위 임베딩 ----
    all_vecs = []
    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]
        # processor가 리사이즈·정규화·텐서화를 한 번에 처리
        inputs = processor(images=batch, return_tensors="pt").to(device)
        with torch.no_grad():  # 추론이므로 그래디언트 계산 불필요 → 메모리·속도 향상
            features = model.get_image_features(**inputs)
        # 일부 transformers 버전은 텐서가 아닌 output 객체를 반환 → 안전하게 풀어냄
        if not isinstance(features, torch.Tensor):
            for attr in ("image_embeds", "pooler_output"):
                t = getattr(features, attr, None)
                if t is not None:
                    features = t
                    break
            else:
                features = features.last_hidden_state[:, 0]
        # L2 정규화: 코사인 유사도 계산을 단순 내적으로 만듦
        features = features / features.norm(dim=-1, keepdim=True)
        all_vecs.append(features.cpu().numpy())

    X = np.concatenate(all_vecs, axis=0)
    return X, valid_sources, images


# ============================================================
# 4. 최적 K 탐색 (엘보우 + 실루엣)
#    - 텍스트 버전과 동일한 로직이지만 그림 파일명만 다름.
# ============================================================

def find_optimal_k(X, k_range=(2, 9), chart_path="k_selection_image.png"):
    """
    K 후보별 엘보우·실루엣 점수 계산 → 그래프 표시+저장.
    반환: (실루엣 최대 K, 유효 K 리스트)
    """
    ks = list(range(k_range[0], k_range[1]))
    inertias, silhouettes = [], []

    print(f"\n  K 후보 탐색 (K = {ks[0]} ~ {ks[-1]})")
    print(f"  {'K':>3} | {'inertia':>10} | {'silhouette':>11}")
    print("  " + "-" * 35)
    for k in ks:
        km = KMeans(n_clusters=k, n_init=20, random_state=42)
        labels = km.fit_predict(X)
        inertias.append(km.inertia_)
        sil = silhouette_score(X, labels)
        silhouettes.append(sil)
        print(f"  {k:>3} | {km.inertia_:>10.3f} | {sil:>11.4f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(ks, inertias, "o-", color="steelblue", lw=2)
    ax1.set_xlabel("K (클러스터 수)")
    ax1.set_ylabel("Inertia (WCSS)")
    ax1.set_title("엘보우 (Elbow Method) — 꺾이는 지점이 좋은 K")
    ax1.grid(alpha=0.3)

    ax2.plot(ks, silhouettes, "o-", color="darkorange", lw=2)
    ax2.set_xlabel("K (클러스터 수)")
    ax2.set_ylabel("Silhouette Score")
    ax2.set_title("실루엣 점수 — 최고점이 좋은 K")
    ax2.grid(alpha=0.3)

    best_idx = int(np.argmax(silhouettes))
    ax2.axvline(ks[best_idx], color="red", linestyle="--", alpha=0.6,
                label=f"max @ K={ks[best_idx]}")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(chart_path, dpi=120, bbox_inches="tight")
    plt.close("all")
    print(f"\n  그래프 저장: {chart_path}")
    _open_file(chart_path)   # 시스템 기본 뷰어로 자동 열기 (비동기, 실패 무시)

    return ks[best_idx], ks


def ask_k_from_user(suggested_k, valid_ks):
    """
    엘보우/실루엣 그래프를 보고 K를 입력받는다.
    - 엔터만 누르면 추천 K(실루엣 최대)를 채택.
    - 파이프·리다이렉트 등 비대화형 환경이면 추천 K를 자동 선택.
    """
    if not sys.stdin.isatty():
        print(f"  비대화형 실행 감지 → 추천 K={suggested_k} 자동 선택")
        return suggested_k

    print(f"\n  그래프 파일을 확인한 뒤 K를 입력하세요.")
    while True:
        try:
            raw = input(
                f"  K 입력 (범위 {valid_ks[0]}~{valid_ks[-1]}, 엔터=추천값 {suggested_k}): "
            ).strip()
        except EOFError:
            print(f"  입력 종료 → 추천 K={suggested_k} 자동 선택")
            return suggested_k
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
# 5. 클러스터 대표 이미지 그리드 저장
# ============================================================

def save_cluster_grid(reps_pil, cluster_sizes, save_path="cluster_grid_image.png"):
    """
    클러스터별 대표 이미지를 한 장의 PNG에 격자(grid)로 배치한다.
    - reps_pil      : {cluster_id: [PIL.Image, ...]} (중심 가까운 순)
    - cluster_sizes : {cluster_id: int}
    """
    n_clusters = len(reps_pil)
    n_cols = max(len(v) for v in reps_pil.values())
    fig, axes = plt.subplots(n_clusters, n_cols,
                             figsize=(2.2 * n_cols, 2.2 * n_clusters))
    if n_clusters == 1:
        axes = np.array([axes])

    for row, c in enumerate(sorted(reps_pil.keys())):
        for col in range(n_cols):
            ax = axes[row, col] if n_cols > 1 else axes[row]
            ax.axis("off")
            if col < len(reps_pil[c]):
                ax.imshow(reps_pil[c][col])
                if col == 0:
                    ax.set_ylabel(f"C{c}\n(n={cluster_sizes[c]})",
                                  rotation=0, labelpad=30,
                                  fontsize=11, fontweight="bold")
    plt.suptitle("클러스터별 대표 이미지", fontsize=14, y=1.01)
    plt.tight_layout()
    plt.savefig(save_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  그리드 이미지 저장: {save_path}")
    _open_file(save_path)


# ============================================================
# 7. Gemini Vision으로 클러스터 주제 명명
# ============================================================

def name_image_cluster_with_gemini(image_paths):
    """
    대표 이미지 N장을 Gemini에 보내 공통 시각·주제 특징을 JSON으로 받음.
    멀티모달 LLM이라 이미지를 직접 보고 의미를 추출할 수 있다는 점이 핵심.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    # 이미지를 bytes로 로드해 prompt parts에 첨부
    parts = []
    for p in image_paths:
        img = load_image(p)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        parts.append(types.Part.from_bytes(
            data=buf.getvalue(),
            mime_type="image/jpeg",
        ))

    parts.append(types.Part.from_text(text="""위 이미지들은 K-means로 한 클러스터에 묶였다.
이 클러스터의 공통 시각·주제 특징을 도출해 아래 JSON 형식으로만 답하라.

{
  "topic_name": "15자 이내 주제명",
  "visual_features": "공통 색감·구도·소재 등 시각 특징 (1~2문장)",
  "subject": "주제·맥락 (1~2문장)",
  "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"]
}"""))

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=parts,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return json.loads(resp.text)


# ============================================================
# 8. 단계별 파이프라인 함수
# ============================================================

EMBEDDINGS_PATH = "embeddings_image.json"
CLUSTERS_PATH = "clusters_image.json"
CHART_PATH = "k_selection_image.png"
GRID_PATH = "cluster_grid_image.png"


def stage1_build_embeddings(sources, path=EMBEDDINGS_PATH):
    """
    [1단계] 이미지 다운로드 + CLIP 임베딩 → embeddings_image.json 저장.
    동일한 소스 목록의 캐시가 있으면 임베딩을 재계산하지 않고 재사용한다.
    """
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cached = json.load(f)
        if cached.get("sources_input") == list(sources):
            print(f"[1/3] 캐시 재사용: {path} (입력 {len(sources)}개)")
            return

    print(f"[1/3] 이미지 {len(sources)}개 CLIP 임베딩")
    X, valid_sources, _ = embed_images_with_clip(sources)
    # CLIP 출력은 이미 L2 정규화되어 있지만 안전하게 한 번 더
    X = normalize(X, norm="l2")

    payload = {
        "model": "openai/clip-vit-base-patch32",
        "dim": int(X.shape[1]),
        "n_images": len(valid_sources),
        "sources_input": list(sources),   # 원본 입력 (캐시 키)
        "sources": valid_sources,         # 임베딩 행과 1:1 매칭되는 유효 소스
        "embeddings": X.tolist(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"      저장: {path}  (shape={X.shape})")


def stage2_select_k(embeddings_path=EMBEDDINGS_PATH, chart_path=CHART_PATH):
    """
    [2단계] embeddings_image.json 로드 → 엘보우·실루엣 분석 그림 표시/저장
            → 연구자가 K 입력.
    반환: (정규화된 X, 소스 리스트, 선택한 K)
    """
    print(f"\n[2/3] {embeddings_path} 로드 → K 탐색")
    with open(embeddings_path, encoding="utf-8") as f:
        data = json.load(f)
    X = np.array(data["embeddings"], dtype=float)
    sources = data["sources"]

    # L2 정규화: 코사인 거리 효과 (KMeans는 유클리드만 지원)
    X = normalize(X, norm="l2")
    print(f"      입력 shape: {X.shape}")

    max_k = min(9, len(sources) - 1)
    suggested_k, valid_ks = find_optimal_k(X, k_range=(2, max_k), chart_path=chart_path)
    print(f"      → 실루엣 기준 추천 K = {suggested_k}")
    best_k = ask_k_from_user(suggested_k, valid_ks)
    print(f"      → 선택한 K = {best_k}")
    return X, sources, best_k


def stage3_cluster_and_analyze(X, sources, k, use_gemini,
                               clusters_path=CLUSTERS_PATH,
                               grid_path=GRID_PATH,
                               n_reps_for_grid=4):
    """
    [3단계] K-means 실행 → 각 클러스터 멤버를 중심거리 기준으로 정렬해 'rank' 부여
            → clusters_image.json + cluster_grid_image.png 저장.

    KMeans는 sklearn에서 유클리드 거리만 지원하지만, 입력이 이미 L2 정규화된 단위벡터라
    유클리드 최소화는 코사인 유사도 최대화와 동치다 (||a-b||^2 = 2 - 2*cos(a,b)).
    """
    print(f"\n[3/3] K={k}으로 K-means 실행 + 결과 분석")
    km = KMeans(n_clusters=k, n_init=30, random_state=42)
    labels = km.fit_predict(X)

    clusters = []
    reps_pil = {}        # 그리드용: cluster_id → [PIL]
    cluster_sizes = {}

    for c in sorted(set(labels)):
        idx = np.where(labels == c)[0]
        center = X[idx].mean(axis=0)
        dists = np.linalg.norm(X[idx] - center, axis=1)
        order = np.argsort(dists)

        members = []
        for rank, pos in enumerate(order, start=1):
            image_id = int(idx[pos])
            members.append({
                "rank": rank,                              # 1 = 중심에 가장 가까움
                "image_id": image_id,
                "distance_to_center": float(dists[pos]),
                "source": sources[image_id],
            })

        cluster_info = {
            "cluster_id": int(c),
            "size": int(len(idx)),
            "members": members,
        }

        # 그리드 + Gemini Vision용 대표 이미지 로드 (상위 N개)
        rep_sources = [m["source"] for m in members[:n_reps_for_grid]]
        rep_pils = []
        for src in rep_sources:
            try:
                rep_pils.append(load_image(src))
            except Exception as e:
                print(f"  [경고] 대표 이미지 로드 실패: {src[:60]} ({e})")
        reps_pil[int(c)] = rep_pils
        cluster_sizes[int(c)] = int(len(idx))

        if use_gemini:
            try:
                topic = name_image_cluster_with_gemini(rep_sources[:3])
                cluster_info["topic_name"] = topic["topic_name"]
                cluster_info["visual_features"] = topic["visual_features"]
                cluster_info["subject"] = topic["subject"]
                cluster_info["keywords"] = topic["keywords"]
                time.sleep(0.5)
            except Exception as e:
                cluster_info["topic_error"] = str(e)

        clusters.append(cluster_info)

    # ---- clusters_image.json ----
    payload = {"k": int(k), "n_images": len(sources), "clusters": clusters}
    with open(clusters_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"      저장: {clusters_path}")

    # ---- 콘솔 출력 ----
    print("=" * 70)
    for cl in clusters:
        print(f"\n[Cluster {cl['cluster_id']}]  n={cl['size']}")
        if "topic_name" in cl:
            print(f"  ▸ 주제명    : {cl['topic_name']}")
            print(f"  ▸ 시각특징  : {cl['visual_features']}")
            print(f"  ▸ 주제맥락  : {cl['subject']}")
            print(f"  ▸ 키워드    : {', '.join(cl['keywords'])}")
        elif "topic_error" in cl:
            print(f"  (주제 도출 실패: {cl['topic_error']})")

        print("  ▸ 대표 이미지 (rank = 중심에 가까운 순):")
        for m in cl["members"][:3]:
            print(f"    {m['rank']}. (d={m['distance_to_center']:.4f}) {m['source'][:75]}")

    # ---- 클러스터 그리드 ----
    save_cluster_grid(reps_pil, cluster_sizes, save_path=grid_path)

    print("\n" + "=" * 70)
    print(f"저장 완료: {CHART_PATH}, {grid_path}, {clusters_path}")


# ============================================================
# 9. 메인 — 세 단계를 순서대로 실행
# ============================================================

def main():
    use_gemini = True  # True: Gemini Vision으로 주제 명명 / False: 명명 생략

    # 1) 임베딩: 동일 소스면 캐시 재사용, 아니면 새로 CLIP 임베딩 후 embeddings_image.json 저장
    stage1_build_embeddings(IMAGES)

    # 2) embeddings_image.json 다시 읽어와 K 분석/선택 (그림 저장 + 사용자 입력)
    X, sources, best_k = stage2_select_k()

    # 3) 클러스터링 결과 분석 → clusters_image.json (멤버에 중심거리 순위 rank 포함)
    stage3_cluster_and_analyze(X, sources, best_k, use_gemini=use_gemini)


if __name__ == "__main__":
    main()
