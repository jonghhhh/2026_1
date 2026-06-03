# =============================================================================
# silicon_sampling.py
# 실리콘 샘플링 기초 실습: Nemotron-Personas-Korea + Gemini API
# 경희대학교 미디어학과 AI 미디어 코딩 강의
# =============================================================================
#
# [사전 준비]
# 터미널에서 아래 명령어 실행:
#   pip install datasets google-generativeai pandas tqdm python-dotenv
#
# [Gemini API 키 발급]
#   https://aistudio.google.com → "Get API Key"
#   무료 티어: 분당 15회, 일 1,500회 (1,000명 실습에 충분)
#
# [API 키 설정]
#   이 파일과 같은 폴더에 .env 파일을 만들고 아래 한 줄을 적으세요:
#     GEMINI_API_KEY=여기에_발급받은_키_입력
#
# =============================================================================
#
# [Nemotron-Personas-Korea 변수 설명 — 총 26개]
#
#   ▶ 페르소나 서술 변수 (7개)
#     professional_persona  : 직업 및 업무 중심 페르소나
#     sports_persona        : 운동 습관 및 스포츠 활동 중심 페르소나
#     arts_persona          : 예술 활동 및 문화 소비 중심 페르소나
#     travel_persona        : 여행 스타일 중심 페르소나
#     culinary_persona      : 음식 취향 및 식생활 중심 페르소나
#     family_persona        : 가족 관계 및 생활 방식 중심 페르소나
#     persona               : 위 내용을 통합한 요약 페르소나
#
#   ▶ 페르소나 속성 변수 (6개)
#     cultural_background          : 문화적·지역적 배경
#     career_goals_and_ambitions   : 경력 목표 및 장기적 포부
#     skills_and_expertise         : 기술 및 전문성 설명
#     skills_and_expertise_list    : 기술 및 전문성 목록
#     hobbies_and_interests        : 취미 및 관심사 설명
#     hobbies_and_interests_list   : 취미 및 관심사 목록
#
#   ▶ 인구통계 변수 (13개)
#     uuid            : 고유 식별자
#     sex             : 성별
#     age             : 나이
#     marital_status  : 혼인 상태
#     education_level : 최종 학력
#     bachelors_field : 전공 분야
#     occupation      : 직업
#     military_status : 병역 상태
#     family_type     : 가구 형태
#     housing_type    : 주거 형태
#     province        : 시도
#     district        : 시군구
#     country         : 국가
#
# =============================================================================


# ─────────────────────────────────────────────────────────────────────────────
# ★ 설정 영역 (여기만 수정하면 됩니다!)
# ─────────────────────────────────────────────────────────────────────────────

# [필수] Gemini API 키
# 키는 같은 폴더의 .env 파일에서 GEMINI_API_KEY 값을 읽어옵니다.
# (.env 파일 예시)  GEMINI_API_KEY=AIza...
# → API 초기화 영역(2번)에서 .env를 로드합니다.

# 샘플 수: 테스트 시 10~50명으로 시작, 충분히 확인 후 1000으로 변경
N_SAMPLES = 50  # 처음엔 50으로 테스트!

# 재현 가능성: 같은 숫자 = 같은 샘플 (동료와 결과 비교할 때 중요)
RANDOM_SEED = 42

# Gemini 모델 선택 (2026년 6월 기준 사용 가능 모델)
# - "gemini-2.5-flash-lite" : 가장 저렴, 가장 빠름 (구 gemini-2.0-flash-lite의 후속)
# - "gemini-2.5-flash"      : 조금 더 똑똑함 (권장 균형점)
# - "gemini-2.5-pro"        : 가장 똑똑함 (느리고 비쌈)
# ⚠️ gemini-2.0-* 계열은 모두 서비스 종료(404)되어 사용 불가합니다.
MODEL_NAME = "gemini-2.5-flash-lite"

# API 호출 간 대기 시간 (초) - 너무 빠르면 오류 발생
SLEEP_SEC = 0.2

# 결과 저장 파일명 (CSV만 저장 — 그래프 PNG는 한글 폰트 문제로 생략)
OUTPUT_CSV = "silicon_sampling_results.csv"


# ─────────────────────────────────────────────────────────────────────────────
# ★★ 설문 문항 설정 (여기를 바꿔서 다른 설문 실험 가능!)
# ─────────────────────────────────────────────────────────────────────────────

# 설문 문항 텍스트
SURVEY_QUESTION = """
귀하는 현재 우리 사회의 빈부 격차가 어느 정도 심각하다고 생각하십니까?

① 전혀 심각하지 않다
② 별로 심각하지 않다
③ 약간 심각하다
④ 매우 심각하다
"""

# 선택지 목록 (파싱에 사용 - 위 문항의 보기와 일치해야 함!)
CHOICES = [
    "전혀 심각하지 않다",
    "별로 심각하지 않다",
    "약간 심각하다",
    "매우 심각하다",
]

# 설문 제목 (그래프 제목에 사용)
SURVEY_TITLE = "빈부 격차 심각성 인식"


# =============================================================================
# 여기서부터는 직접 수정 불필요 (코드 동작 영역)
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# 1. 라이브러리 임포트
# ─────────────────────────────────────────────────────────────────────────────
import os
import re
import time
import warnings

import pandas as pd
from tqdm import tqdm           # 진행 상황 표시줄
from datasets import load_dataset  # HuggingFace 데이터셋 로드
import google.generativeai as genai  # Gemini API
from dotenv import load_dotenv   # .env 파일에서 환경변수 로드

warnings.filterwarnings("ignore")  # 불필요한 경고 숨김


# ─────────────────────────────────────────────────────────────────────────────
# 2. API 초기화
# ─────────────────────────────────────────────────────────────────────────────

# .env 파일 로드 후 GEMINI_API_KEY 값 읽기
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "❌ GEMINI_API_KEY가 없습니다!\n"
        "   같은 폴더에 .env 파일을 만들고 아래 한 줄을 적으세요:\n"
        "     GEMINI_API_KEY=발급받은_키"
    )

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(
    MODEL_NAME,
    generation_config=genai.types.GenerationConfig(
        temperature=0.7,       # 응답 다양성 (0=항상같음, 1=매우다양)
        max_output_tokens=150, # 응답 길이 제한 (설문이니 짧게)
    )
)
print(f"✅ Gemini API 초기화 완료: {MODEL_NAME}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Nemotron 데이터셋 로드
# ─────────────────────────────────────────────────────────────────────────────

print("\n📦 Nemotron-Personas-Korea 로딩 중...")
print("   (처음 실행 시 자동 다운로드, 수분 소요 가능)")

dataset = load_dataset("nvidia/Nemotron-Personas-Korea")
df = dataset["train"].to_pandas()

print(f"✅ 로드 완료: 총 {len(df):,}명의 합성 한국인 페르소나")

# ─ 컬럼 이름 확인 (중요!) ─────────────────────────────────────────────────
print("\n" + "="*60)
print("📋 데이터셋 컬럼 목록 (필드명 확인용):")
print("="*60)
for i, col in enumerate(df.columns.tolist(), 1):
    print(f"  {i:2d}. {col}")

print("\n📄 데이터 샘플 (첫 1행 미리보기):")
print(df.iloc[0].to_string())
print("="*60)

# ─ 컬럼 매핑 ──────────────────────────────────────────────────────────────
# Nemotron-Personas-Korea 데이터셋의 실제 26개 변수를 그대로 사용합니다.
# 왼쪽: 코드에서 사용하는 이름 / 오른쪽: 실제 데이터의 컬럼명
COLUMN_MAP = {
    # ── 인구통계 변수 (13개) ──────────────────────────────────────────
    "uuid":            "uuid",              # 고유 식별자
    "sex":             "sex",               # 성별
    "age":             "age",               # 나이
    "marital_status":  "marital_status",    # 혼인 상태
    "education_level": "education_level",   # 최종 학력
    "bachelors_field": "bachelors_field",   # 전공 분야
    "occupation":      "occupation",        # 직업
    "military_status": "military_status",    # 병역 상태
    "family_type":     "family_type",       # 가구 형태
    "housing_type":    "housing_type",      # 주거 형태
    "province":        "province",          # 시도
    "district":        "district",          # 시군구
    "country":         "country",           # 국가

    # ── 페르소나 속성 변수 (6개) ──────────────────────────────────────
    "cultural_background":        "cultural_background",         # 문화적·지역적 배경
    "career_goals_and_ambitions": "career_goals_and_ambitions",  # 경력 목표 및 포부
    "skills_and_expertise":       "skills_and_expertise",        # 기술 및 전문성 (서술)
    "skills_and_expertise_list":  "skills_and_expertise_list",   # 기술 및 전문성 (목록)
    "hobbies_and_interests":      "hobbies_and_interests",       # 취미 및 관심사 (서술)
    "hobbies_and_interests_list": "hobbies_and_interests_list",  # 취미 및 관심사 (목록)

    # ── 페르소나 서술 변수 (7개) ──────────────────────────────────────
    "persona":              "persona",               # 통합 요약 페르소나
    "professional_persona": "professional_persona",  # 직업/업무 중심
    "sports_persona":       "sports_persona",        # 운동/스포츠 중심
    "arts_persona":         "arts_persona",          # 예술/문화 소비 중심
    "travel_persona":       "travel_persona",        # 여행 스타일 중심
    "culinary_persona":     "culinary_persona",      # 음식/식생활 중심
    "family_persona":       "family_persona",        # 가족 관계/생활 방식 중심
}

def get_field(row, key, default="정보 없음"):
    """
    페르소나 데이터에서 안전하게 필드값을 꺼냅니다.
    컬럼이 없거나 값이 비어있으면 default를 반환합니다.
    """
    col_name = COLUMN_MAP.get(key, key)
    val = row.get(col_name, default)
    if pd.isna(val) or str(val).strip() == "":
        return default
    return str(val)


# ─────────────────────────────────────────────────────────────────────────────
# 4. 1,000명 (또는 N_SAMPLES명) 샘플링
# ─────────────────────────────────────────────────────────────────────────────

# random_state를 고정하면 매번 같은 사람들이 뽑힘 → 결과 재현 가능
sample_df = df.sample(n=N_SAMPLES, random_state=RANDOM_SEED).reset_index(drop=True)
print(f"\n✅ {N_SAMPLES}명 샘플링 완료 (seed={RANDOM_SEED})")

# 샘플 기본 통계 출력
print("\n📊 샘플 인구학 분포 미리보기:")
for col in ["sex", "age", "education_level", "province"]:
    actual_col = COLUMN_MAP.get(col, col)
    if actual_col in sample_df.columns:
        print(f"\n  [{col}]")
        print(sample_df[actual_col].value_counts().head(5).to_string())


# ─────────────────────────────────────────────────────────────────────────────
# 5. 프롬프트 생성 함수
# ─────────────────────────────────────────────────────────────────────────────

# 페르소나 구성에 사용하는 변수 목록 (프롬프트 + 결과 CSV 저장에 동일하게 사용)
# ── 인구통계 변수 (구조화 정보) ──
PROMPT_DEMOGRAPHIC_FIELDS = [
    ("sex",             "성별"),
    ("age",             "나이"),
    ("province",        "시도"),
    ("district",        "시군구"),
    ("education_level", "최종 학력"),
    ("bachelors_field", "전공 분야"),
    ("occupation",      "직업"),
    ("marital_status",  "혼인 상태"),
    ("military_status", "병역 상태"),
    ("family_type",     "가구 형태"),
    ("housing_type",    "주거 형태"),
]
# ── 서사 변수 (인물 이야기) ──
PROMPT_NARRATIVE_FIELDS = [
    ("persona",                    "인물 요약"),
    ("cultural_background",        "문화적·지역적 배경"),
    ("professional_persona",       "직업·업무 스타일"),
    ("career_goals_and_ambitions", "경력 목표 및 포부"),
    ("skills_and_expertise",       "기술·전문성"),
    ("hobbies_and_interests",      "취미·관심사"),
    ("sports_persona",             "운동·스포츠 성향"),
    ("arts_persona",               "예술·문화 취향"),
    ("travel_persona",             "여행 스타일"),
    ("culinary_persona",           "음식·식생활"),
    ("family_persona",             "가족 관계·생활 방식"),
]


def build_prompt(persona_row, question):
    """
    한 명의 페르소나 정보를 자연어 프롬프트로 변환합니다.

    좋은 프롬프트의 조건:
    1. 구조화 정보 (통계적 특성) 포함
    2. 서사 정보 (인물 이야기) 포함  ← AI가 더 몰입하게 만듦
    3. 명확한 응답 형식 지시

    Args:
        persona_row: 데이터프레임의 한 행 (한 사람의 정보)
        question: 설문 문항 텍스트
    Returns:
        str: Gemini에게 보낼 프롬프트
    """

    # 구조화 정보 조합 (인구통계 변수)
    basic_lines = []
    for key, label in PROMPT_DEMOGRAPHIC_FIELDS:
        val = get_field(persona_row, key)
        suffix = "세" if key == "age" and val != "정보 없음" else ""
        basic_lines.append(f"- {label}: {val}{suffix}")
    basic_info = "\n".join(basic_lines)

    # 서사 정보: 통합 페르소나(persona)를 중심으로 속성 변수를 덧붙임
    # (있는 변수만 포함, 없으면 생략 → 프롬프트가 깔끔하게 유지됨)
    narrative_parts = []
    for key, label in PROMPT_NARRATIVE_FIELDS:
        val = get_field(persona_row, key)
        if val != "정보 없음":
            narrative_parts.append(f"[{label}] {val}")

    narrative = "\n".join(narrative_parts) if narrative_parts else "(서사 정보 없음)"

    # 최종 프롬프트 조합
    prompt = f"""당신은 다음과 같은 한국인입니다.

[기본 정보]
{basic_info}

[인물 소개]
{narrative}

위 인물의 관점에서, 아래 설문 문항에 솔직하게 답해주세요.
반드시 번호(①②③④ 중 하나)와 해당 텍스트를 포함해서 답하세요.

{question}
"""
    return prompt


# ─────────────────────────────────────────────────────────────────────────────
# 6. 응답 파싱 함수
# ─────────────────────────────────────────────────────────────────────────────

def parse_response(text, choices):
    """
    AI의 자유 응답 텍스트에서 선택지를 추출합니다.

    3단계 안전망:
    1단계: 보기 텍스트 직접 매칭 (가장 긴 것부터 시도)
    2단계: 번호 기호 매칭 ①②③④
    3단계: 숫자 매칭 1,2,3,4
    실패: "모름/무응답" 반환

    Args:
        text: AI 응답 텍스트
        choices: 선택지 리스트 (CHOICES 변수)
    Returns:
        str: 선택된 보기 텍스트 또는 "모름/무응답"
    """

    # 1단계: 텍스트 직접 매칭 (긴 것부터 → 짧은 것의 부분 매칭 오류 방지)
    for choice in sorted(choices, key=len, reverse=True):
        if choice in text:
            return choice

    # 2단계: 번호 기호 매칭
    number_symbols = {"①": 0, "②": 1, "③": 2, "④": 3, "⑤": 4}
    for symbol, idx in number_symbols.items():
        if symbol in text and idx < len(choices):
            return choices[idx]

    # 3단계: 일반 숫자 매칭 (응답 텍스트의 맥락 숫자 제외 위해 조심스럽게)
    pattern = r'(?<!\d)([1-' + str(len(choices)) + r'])(?!\d)'
    match = re.search(pattern, text)
    if match:
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(choices):
            return choices[idx]

    # 모두 실패
    return "모름/무응답"


# ─────────────────────────────────────────────────────────────────────────────
# 7. 메인 실행: AI에게 설문 물어보기
# ─────────────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"🤖 {N_SAMPLES}명의 페르소나에게 설문 시작!")
print(f"   예상 소요 시간: 약 {N_SAMPLES * SLEEP_SEC:.0f}초")
print(f"{'='*60}\n")

results = []  # 결과를 저장할 리스트

for idx, row in tqdm(sample_df.iterrows(), total=N_SAMPLES, desc="설문 진행"):

    # 기본값 설정 (오류 발생 시 사용)
    raw_text = ""
    parsed_answer = "모름/무응답"

    try:
        # 프롬프트 생성
        prompt = build_prompt(row, SURVEY_QUESTION)

        # Gemini API 호출
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # 응답 파싱
        parsed_answer = parse_response(raw_text, CHOICES)

    except Exception as e:
        # API 오류 발생 시 기록하고 계속 진행
        raw_text = f"[오류] {str(e)}"

    # 결과 저장: 페르소나 구성에 사용한 "모든 변수"(인구통계 + 서사)를 함께 기록
    # → 나중에 어떤 변수가 응답에 영향을 줬는지 추적/분석 가능
    record = {"persona_id": idx, "uuid": get_field(row, "uuid")}
    for key, _label in PROMPT_DEMOGRAPHIC_FIELDS:   # 인구통계 변수
        record[key] = get_field(row, key)
    for key, _label in PROMPT_NARRATIVE_FIELDS:     # 서사 변수
        record[key] = get_field(row, key)
    record["raw_response"] = raw_text[:300]         # AI 응답 원문 앞 300자
    record["parsed_answer"] = parsed_answer         # 파싱된 선택지
    results.append(record)

    # API 과부하 방지 대기
    time.sleep(SLEEP_SEC)


# ─────────────────────────────────────────────────────────────────────────────
# 8. 결과 저장
# ─────────────────────────────────────────────────────────────────────────────

result_df = pd.DataFrame(results)
result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print(f"\n✅ 결과 저장 완료!")
print(f"   파일: {os.path.abspath(OUTPUT_CSV)}")
print(f"   행: {len(result_df):,}개 (한 행 = 한 명의 응답)")


# ─────────────────────────────────────────────────────────────────────────────
# 9. 응답 분포 계산
# ─────────────────────────────────────────────────────────────────────────────

# 각 선택지별 응답 수 집계
answer_counts = result_df["parsed_answer"].value_counts()

# 선택지 순서 유지 + 없는 선택지는 0으로 채움
all_labels = CHOICES + ["모름/무응답"]
answer_counts = answer_counts.reindex(all_labels, fill_value=0)

# 터미널에 텍스트 분포 출력
print(f"\n{'='*60}")
print(f"📊 응답 분포 요약: {SURVEY_TITLE}")
print(f"{'='*60}")
total_valid = answer_counts[CHOICES].sum()  # 유효 응답 수
for label in all_labels:
    count = answer_counts[label]
    pct = (count / N_SAMPLES * 100) if N_SAMPLES > 0 else 0
    bar = "█" * int(pct / 2)   # 간단한 텍스트 막대그래프
    print(f"  {label:<20} {bar:<25} {count:4d}명 ({pct:5.1f}%)")

print(f"\n  유효 응답: {total_valid}명 / 전체: {N_SAMPLES}명")
no_answer = answer_counts.get("모름/무응답", 0)
print(f"  모름/무응답: {no_answer}명 ({no_answer/N_SAMPLES*100:.1f}%)")


# ─────────────────────────────────────────────────────────────────────────────
# 10. [심화] 인구집단별 분포 비교
# ─────────────────────────────────────────────────────────────────────────────

# 성별(sex)이 있는 경우에만 실행
if "sex" in result_df.columns and result_df["sex"].nunique() > 1:

    print(f"\n{'='*60}")
    print("📊 [심화] 성별별 응답 분포 비교")
    print("="*60)

    for sex_val in result_df["sex"].unique():
        sub = result_df[result_df["sex"] == sex_val]
        print(f"\n  [{sex_val}] (N={len(sub)}명)")
        counts = sub["parsed_answer"].value_counts().reindex(CHOICES, fill_value=0)
        for choice, cnt in counts.items():
            pct = cnt / len(sub) * 100
            print(f"    {choice:<20} {cnt:3d}명 ({pct:.1f}%)")


# ─────────────────────────────────────────────────────────────────────────────
# 11. AI 응답 원문 샘플 출력 (디버깅 / 이해용)
# ─────────────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print("🔍 AI 응답 원문 샘플 (5개)")
print("="*60)
for _, row_r in result_df.head(5).iterrows():
    print(f"\n  페르소나: {row_r.get('sex','?')} / {row_r.get('age','?')}세 / {row_r.get('province','?')} {row_r.get('district','')}")
    print(f"  파싱 결과: 【{row_r['parsed_answer']}】")
    print(f"  AI 원문:  {row_r['raw_response'][:150]}...")
    print("  " + "-"*50)


# ─────────────────────────────────────────────────────────────────────────────
# 완료 메시지
# ─────────────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print("🎉 실리콘 샘플링 실습 완료!")
print(f"{'='*60}")
print(f"  결과 CSV : {OUTPUT_CSV}")
print()
print("  💡 다음 단계:")
print("     1. SURVEY_QUESTION을 바꿔서 다른 문항 실험해보기")
print("     2. N_SAMPLES=1000으로 올려서 전체 실행")
print("     3. 실제 여론조사 수치와 비교해보기")
print()
print("  📌 확장 가능성:")
print("     이 코드는 실리콘 샘플링 기초 플랫폼입니다.")
print("     향후 KSIS, NBS 등 실제 여론조사와 연동하여")
print("     AI 응답과 실측 분포의 충실도(JS 발산)를")
print("     정량 측정하는 연구로 확장할 수 있습니다.")
