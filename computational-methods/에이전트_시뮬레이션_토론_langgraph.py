# ── 필요한 패키지 설치 ─────────────────────────────────────
# pip install langgraph langchain-google-genai python-dotenv
# ============================================================
# 실습 5: 5인 페르소나 토론 + "찬반 태도 변화 추적" (LangGraph)
# ============================================================
#
# [바탕] 강의자료 "생성 에이전트 사회 시뮬레이션" Part 2 — 대화형(미시) 시뮬레이션
# [핵심 원리] "에이전트 1명 = LLM 호출 하나"
#            누가 언제 말하는지(=오케스트레이션)는 LangGraph 그래프가 통제한다.
#
# ★ 이 코드의 목적: 정치성향이 다른 5명이 한 이슈를 토론하는 동안,
#   각자의 '찬반 태도(0~10점)'가 라운드마다 어떻게 변하는지를 추적·기록한다.
#   (의견이 한쪽으로 수렴하는가? 양극화되는가? 누가 흔들리고 누가 고집하는가?)
#
# 정치성향 스펙트럼: 극보수 → 보수 → 중도 → 진보 → 극진보
# 이슈(주제)와 라운드 수는 실행할 때 직접 입력받는다.
#
# 그래프 구조 (5명이 한 바퀴 돌면 사회자가 라운드를 세고 계속/종료 판단):
#   START → 극보수 → 보수 → 중도 → 진보 → 극진보 → 사회자
#                                                      │
#                          (라운드 남음? continue) ←───┤
#                          (다 채움? end → END)    ────┘
#
# ※ Chuang(2024) 교훈: LLM은 기본값이 너무 "착해서" 금방 합의해 버린다.
#    → 페르소나에 '고집/편향/정체성'을 명시해야 태도 변화가 현실적이 된다.
# ============================================================


# ── 환경 설정 ──────────────────────────────────────────────
import os
import re                                    # 답변에서 '찬반 점수'를 뽑아낼 때 사용
import operator                              # 리스트 누적(add) 리듀서에 사용
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()                                # .env 파일을 읽어 환경변수로 등록
os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]  # 라이브러리가 찾는 이름으로 복사
print("✅ 환경 설정 완료\n")


# ── 패키지 임포트 ──────────────────────────────────────────
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI


# ── LLM(두뇌) 초기화 ───────────────────────────────────────
# temperature=0.9 : 토론은 다양한 의견이 나와야 하므로 창의성을 높게 둔다.
# 모델은 저렴한 flash-lite 사용. 품질을 더 높이려면 "gemini-2.5-flash"로 교체.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.9)


# ── 찬반 점수 척도 (전 구간 공통 기준) ─────────────────────
# 0 = 강하게 반대 … 5 = 중립 … 10 = 강하게 찬성
SCALE_NOTE = "0=강하게 반대, 3=반대, 5=중립, 7=찬성, 10=강하게 찬성"


# ============================================================
# 1단계: 5명의 페르소나 정의  ★시뮬레이션의 질을 좌우하는 가장 중요한 부분★
# ============================================================
# - 인구통계(나이/성별/직업/지역)를 서로 다르게 → 다양성 확보
# - 정치성향을 극보수~극진보로 분산 → 스펙트럼 전체를 대표
# - "입장을 잘 안 바꾼다" 같은 고집을 명시 → 너무 빨리 합의하는 것 방지(Chuang 교훈)
# ★ 파이썬 dict는 입력한 순서를 기억한다 → 아래 순서가 곧 발언 순서가 된다.
PERSONAS = {
    "[극보수] 68세 박갑수": (
        "당신은 68세 남성, 퇴역 군인 출신으로 지방 소도시에 삽니다. "
        "전통적 가치·국가 안보·사회 질서를 최우선으로 여기며, 급진적 변화를 강하게 경계합니다. "
        "권위와 위계를 존중하고, 자신의 신념을 거의 바꾸지 않습니다. "
        "단호하고 직설적인 말투를 씁니다."
    ),
    "[보수] 52세 김영희": (
        "당신은 52세 여성, 중소기업을 운영하며 수도권에 삽니다. "
        "시장경제·재정건전성·개인의 자유와 책임을 중시하고, 세금 인상과 큰 정부에 회의적입니다. "
        "현실적 비용과 효율을 근거로 신중하게 주장합니다. "
        "차분하고 실무적인 말투를 씁니다."
    ),
    "[중도] 39세 이준호": (
        "당신은 39세 남성, 공무원이며 광역시에 삽니다. "
        "어느 한쪽에 치우치기보다 실용성과 균형, 점진적 개혁을 선호합니다. "
        "양측 주장의 장단점을 견주어 절충안을 모색하며, 설득력 있는 근거에는 입장을 조정할 수 있습니다. "
        "신중하고 균형 잡힌 말투를 씁니다."
    ),
    "[진보] 30세 정수민": (
        "당신은 30세 여성, 사회복지사이며 대도시에 삽니다. "
        "분배 정의·사회복지 확대·약자 보호를 중시하고, 불평등 해소를 위한 국가의 역할을 강조합니다. "
        "데이터와 공정성을 근거로 상대 논리의 허점을 짚습니다. "
        "열정적이고 따뜻한 말투를 씁니다."
    ),
    "[극진보] 24세 한가람": (
        "당신은 24세 청년 활동가이자 대학생으로 대도시에 삽니다. "
        "기후위기·노동권·구조적 불평등의 근본적 개혁을 급진적으로 주장합니다. "
        "기존 체제와 점진주의에 비판적이며, 강한 신념으로 타협을 쉽게 받아들이지 않습니다. "
        "단호하고 도전적인 말투를 씁니다."
    ),
}


# ============================================================
# 2단계: 공유 상태(State) 정의 — 토론 전체가 함께 쓰는 메모장
# ============================================================
class DebateState(TypedDict):
    topic: str                                   # 토론 이슈 (실행 시 입력)
    transcript: Annotated[list, operator.add]    # 발언 기록(문자열들) — 누적
    stances: Annotated[list, operator.add]       # ★찬반 점수 기록 — 누적 (추적의 핵심)
    round: int                                   # 현재까지 끝난 라운드 수
    max_rounds: int                              # 목표 라운드 수 (실행 시 입력)

# ★ Annotated[list, operator.add] 의 의미 (헷갈리는 부분!):
#   노드가 {"stances": [한 건]} 을 반환하면, 기존 리스트에 '이어붙이기(+)' 된다.
#   → 매 발언마다 (라운드, 이름, 점수) 한 건씩 쌓여, 토론이 끝나면 전체 변화 이력이 된다.
#   stances 한 건의 형식: {"round": 1, "name": "[보수] ...", "score": 6}


# ── 도우미: LLM 답변에서 '찬반: X' 점수를 숫자로 뽑아낸다 ───
def parse_score(text: str):
    """답변 맨 끝의 '찬반: 7' 같은 표기를 찾아 0~10 사이 숫자로 돌려준다. 없으면 None."""
    # 정규식: '찬반' 뒤의 콜론(일반:/전각：)과 공백을 건너뛰고 숫자(소수 가능)를 잡는다
    m = re.search(r"찬반\s*[:：]\s*(\d+(?:\.\d+)?)", text)
    if not m:
        return None
    score = float(m.group(1))
    return max(0.0, min(10.0, score))            # 0~10 범위를 벗어나면 잘라준다


# ============================================================
# 3단계: 페르소나 발언 노드 — "공장(factory)" 함수로 5개를 찍어낸다
# ============================================================
# 노드 5개의 내용이 거의 같으므로, 매번 복붙하지 않고
# "노드를 만들어 돌려주는 함수"를 한 번 정의해 재사용한다. → 클로저/팩토리 패턴.
def make_persona_node(name: str, persona: str):
    def node(state: DebateState) -> dict:
        # 지금 진행 중인 라운드 번호 (사회자가 +1 하기 전이므로 +1 해서 라벨링)
        cur_round = state["round"] + 1

        # (a) 최근 발언 몇 개만 맥락으로 전달 (전체를 다 넣으면 토큰 낭비)
        recent = state["transcript"][-6:]            # 뒤에서 6줄
        context = "\n".join(recent) if recent else "(아직 발언 없음. 당신이 첫 발언자입니다.)"

        # (b) 프롬프트 조립: 너는 누구다 + 주제 + 대화맥락 + 지시 + ★점수 출력 형식★
        prompt = (
            f"당신은 토론 참가자 '{name}'입니다.\n"
            f"[당신의 정체성과 성향]\n{persona}\n\n"
            f"[토론 주제]\n{state['topic']}\n\n"
            f"[지금까지의 대화]\n{context}\n\n"
            f"위 흐름에 반응하여, 당신의 성향에 충실하게 의견을 2~3문장으로 말하세요. "
            f"다른 참가자에게 동의/반박해도 됩니다. 설득력 있는 근거에는 입장을 바꿀 수도 있습니다.\n"
            f"그리고 반드시 '마지막 줄'에 이 주제에 대한 당신의 현재 찬반 입장을 "
            f"다음 형식으로 0~10 숫자 하나로 표시하세요 → 찬반: X\n"
            f"(척도: {SCALE_NOTE})"
        )

        # (c) LLM 호출 = "이 페르소나의 머리"가 한 번 생각하는 것
        answer = llm.invoke(prompt).content.strip()

        # (d) 답변에서 찬반 점수를 뽑는다. 못 뽑으면 직전 점수 유지(없으면 5=중립)
        score = parse_score(answer)
        if score is None:
            prev = [s["score"] for s in state["stances"] if s["name"] == name]
            score = prev[-1] if prev else 5.0

        # (e) 화면에 진행 상황 출력 (점수 변화가 보이도록)
        print(f"  {name}  (찬반 {score:.0f}/10)\n    → {answer}\n")

        # (f) 발언과 점수를 함께 반환 → 둘 다 누적된다
        return {
            "transcript": [f"[{cur_round}R] {name}: {answer}"],
            "stances": [{"round": cur_round, "name": name, "score": score}],
        }

    return node


# ============================================================
# 4단계: 사회자 노드 — 한 바퀴(라운드)가 끝날 때 라운드를 센다
# ============================================================
def moderator(state: DebateState) -> dict:
    new_round = state["round"] + 1
    print(f"───────── {new_round}라운드 종료 ─────────\n")
    return {"round": new_round}


# ============================================================
# 5단계: 조건부 분기 함수 — 계속할지 멈출지 결정
# ============================================================
def should_continue(state: DebateState) -> str:
    # 이 함수가 돌려주는 '문자열'에 따라 다음에 갈 노드가 결정된다.
    return "continue" if state["round"] < state["max_rounds"] else "end"


# ============================================================
# 6단계: 그래프 조립 — 노드를 발언 순서대로 한 줄로 잇는다
# ============================================================
graph = StateGraph(DebateState)

# (1) 페르소나 노드 5개 등록. dict 순서 = 극보수→보수→중도→진보→극진보
names = list(PERSONAS.keys())
for name in names:
    graph.add_node(name, make_persona_node(name, PERSONAS[name]))
graph.add_node("moderator", moderator)

# (2) START → 첫 번째(극보수)로 진입
graph.add_edge(START, names[0])

# (3) 페르소나들을 차례로 연결: 극보수→보수→중도→진보→극진보
#     zip(names, names[1:]) = (극보수,보수),(보수,중도)...(진보,극진보) 쌍을 만든다
for cur, nxt in zip(names, names[1:]):
    graph.add_edge(cur, nxt)

# (4) 마지막 페르소나(극진보) → 사회자
graph.add_edge(names[-1], "moderator")

# (5) ★조건부 엣지: 사회자 다음 분기. continue면 다시 처음(극진보 한바퀴 더), end면 종료
graph.add_conditional_edges(
    "moderator",
    should_continue,
    {"continue": names[0], "end": END},
)

# (6) 컴파일
app = graph.compile()
print("✅ 토론 그래프 컴파일 완료\n")


# ============================================================
# 7단계: 찬반 변화 추적 표를 그려주는 함수
# ============================================================
def print_stance_table(stances: list):
    """누적된 stances 기록을 '페르소나 × 라운드' 표로 정리해 변화를 보여준다."""
    rounds = sorted({s["round"] for s in stances})     # 등장한 라운드 번호들(중복 제거·정렬)

    # 헤더 출력
    header = "페르소나".ljust(20) + "".join(f"R{r}".rjust(6) for r in rounds) + "   변화"
    print(header)
    print("-" * len(header))

    for name in names:
        # 이 페르소나의 라운드별 점수를 딕셔너리로 모은다 {라운드: 점수}
        by_round = {s["round"]: s["score"] for s in stances if s["name"] == name}
        cells = "".join(
            (f"{by_round[r]:.0f}".rjust(6) if r in by_round else "-".rjust(6))
            for r in rounds
        )
        # 첫 점수 → 마지막 점수의 변화량(Δ)과 방향 화살표
        seq = [by_round[r] for r in rounds if r in by_round]
        if len(seq) >= 2:
            delta = seq[-1] - seq[0]
            arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "—")
            change = f"  {arrow}{abs(delta):.0f}"
        else:
            change = "   —"
        print(name.ljust(20) + cells + change)

    print("-" * len(header))
    print("※ 점수 0=강한 반대 … 5=중립 … 10=강한 찬성 / ▲상승(찬성쪽) ▼하락(반대쪽)")


# ============================================================
# 8단계: 실행 — 이슈와 라운드 수를 '직접 입력'받아 토론 시작
# ============================================================
if __name__ == "__main__":
    print("=" * 64)
    print("🗣️  5인 페르소나 토론 — 찬반 태도 변화 추적")
    print("   참가자: 극보수 · 보수 · 중도 · 진보 · 극진보")
    print("=" * 64)

    # 이슈(주제)를 별도로 입력받는다
    topic = input("\n토론 이슈를 입력하세요: ").strip()

    # 라운드 수도 여기서 입력받는다. 숫자가 아니면 기본 3라운드.
    raw = input("토론 라운드 수를 입력하세요 (예: 3): ").strip()
    max_rounds = int(raw) if raw.isdigit() and int(raw) > 0 else 3

    print(f"\n[이슈] {topic}")
    print(f"[라운드] {max_rounds}\n")
    print("=" * 64 + "\n")

    # invoke: START부터 END까지 그래프를 실행. 초기 상태를 넣어준다.
    result = app.invoke(
        {
            "topic": topic,
            "transcript": [],
            "stances": [],
            "round": 0,
            "max_rounds": max_rounds,
        },
        # recursion_limit: 그래프가 도는 총 스텝 수 상한(무한루프 안전장치).
        # 라운드마다 노드 6개(페르소나5+사회자)가 도므로 넉넉히 잡는다.
        config={"recursion_limit": max_rounds * 6 + 10},
    )

    # ★ 핵심 결과: 찬반 태도 변화 추적 표
    print("=" * 64)
    print("📊 찬반 태도 변화 추적 (라운드별 점수)")
    print("=" * 64)
    print_stance_table(result["stances"])


# ============================================================
# 학습 포인트 정리
# ============================================================
# 1. "에이전트 1명 = LLM 호출 하나" — 페르소나 노드 안의 llm.invoke()가 그 한 명의 머리다.
# 2. 매 발언에서 '찬반: X' 점수를 함께 받아 parse_score로 숫자화 → 태도를 '측정'한다.
# 3. Annotated[list, operator.add]로 점수 기록이 '누적'되어, 라운드별 변화를 추적할 수 있다.
# 4. 페르소나에 '고집/유연성'을 다르게 넣으면(극단=잘 안 바뀜, 중도=조정 가능),
#    점수 변화 패턴이 달라진다 → 수렴/양극화 실험으로 확장 가능(Chuang 2024).
# 5. 누가 언제 말하는지(오케스트레이션)는 LangGraph의 엣지/조건부엣지가 통제한다.
