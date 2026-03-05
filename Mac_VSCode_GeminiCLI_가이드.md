# macOS용 VSCode + Gemini CLI 설치 가이드

> **대상**: Mac 사용자, 개발 환경이 전혀 없는 초보자  
> **목표**: Homebrew 설치 → VSCode 설정 → Python/Node.js 설치 → Gemini CLI 실행  
> **소요 시간**: 약 20~30분

> **Mac 사용자의 장점**: Mac은 Unix 기반이라 Windows처럼 WSL을 따로 설치할 필요가 없습니다. 설정이 더 간단합니다.

---

## 전체 순서

```
Homebrew 설치 → VSCode 설치 → Python/Node.js 설치 → Gemini CLI 실행
```

---

## STEP 1: 터미널 열기

터미널은 Mac에 기본으로 설치되어 있습니다. 아래 방법 중 하나로 실행하세요:

- **방법 1**: `Cmd + Space` → 검색창에 `터미널` 또는 `Terminal` 입력 → Enter
- **방법 2**: Finder → 응용 프로그램 → 유틸리티 → 터미널 클릭
- **방법 3**: Dock에서 Launchpad 클릭 → "기타" 폴더 → 터미널 클릭

터미널이 열리면 아래처럼 표시됩니다:
```
사용자이름@MacBook ~ %
```
> `%` 기호가 "입력 대기 중"을 뜻합니다. 여기에 명령어를 타이핑합니다.

내 Mac 칩 확인 (참고용):
```bash
uname -m
# arm64  → Apple Silicon (M1/M2/M3/M4)
# x86_64 → Intel
```

---

## STEP 2: Homebrew 설치

Homebrew는 Mac용 패키지 관리자입니다. 이후 모든 도구를 `brew` 명령으로 설치합니다.

**① 설치**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
설치 중 "Press RETURN to continue" → Enter, 비밀번호 요청 시 Mac 로그인 비밀번호 입력

**② PATH 설정 (Apple Silicon M1/M2/M3/M4만 해당)**
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```
> Intel Mac은 이 단계 건너뛰기

**③ 확인**
```bash
brew --version
# Homebrew 4.x.x 가 출력되면 성공
```

---

## STEP 3: VSCode 설치

**① Homebrew로 설치**
```bash
brew install --cask visual-studio-code
```

**② 터미널에서 `code` 명령 활성화**
1. VSCode 실행
2. `Cmd + Shift + P` → "shell command" 검색
3. **"Shell Command: Install 'code' command in PATH"** 선택

**③ 확인**
```bash
code --version
```

---

## STEP 4: Python 설치

```bash
# 설치
brew install python

# python3 대신 python으로 쓰기
echo 'alias python=python3' >> ~/.zshrc
echo 'alias pip=pip3' >> ~/.zshrc
source ~/.zshrc

# 확인
python --version
```

---

## STEP 5: Node.js 설치

Gemini CLI 실행에 **Node.js 20 이상** 필요합니다.

```bash
# 설치
brew install node@22

# 확인
node --version   # v22.x.x
npm --version
```

> `node: command not found` 오류 시: `brew link node@22`

---

## STEP 6: Gemini CLI 설치 및 실행

**① 설치**
```bash
npm install -g @google/gemini-cli
```
> permission 오류 시: `sudo npm install -g @google/gemini-cli`

**② 실행**
```bash
gemini
```

**③ 첫 실행 설정**
1. 테마 선택 (아무거나 선택)
2. 인증 방식 선택 → 아래 두 가지 중 하나 선택

---

### 🔑 인증 방법 선택

> ⚠️ **학교 제메일(@khu.ac.kr)은 Google Workspace 계정이라 Gemini CLI 로그인이 안 될 수 있습니다.**  
> **개인 Gmail** 또는 **API 키** 방식을 사용하세요.

#### 방법 A: 개인 Gmail로 로그인 (추천 ⭐)

인증 선택 화면에서 **"1. Login with Google"** 선택  
→ 브라우저에서 **개인 Gmail 계정**으로 로그인  
→ 무료 사용량: 분당 60회, 일 1,000회 (신용카드 불필요)

#### 방법 B: API 키 사용 (개인 메일도 안 될 때)

**① Google AI Studio에서 키 발급**
1. [https://aistudio.google.com](https://aistudio.google.com) 접속 → **개인 Gmail**로 로그인
2. 왼쪽 메뉴 **"Get API Key"** → **"API 키 만들기"** 클릭
3. 생성된 키 복사 후 안전한 곳에 저장

> ⚠️ API 키는 비밀번호와 같습니다. GitHub, SNS에 절대 공개하지 마세요.

**② 환경변수로 등록**
```bash
echo 'export GEMINI_API_KEY="발급받은_키_붙여넣기"' >> ~/.zshrc
source ~/.zshrc

# 확인
echo $GEMINI_API_KEY
```

**③ Gemini CLI 실행 시 API 키 선택**
```
? How would you like to authenticate?
  1. Login with Google
❯ 2. Use API Key          ← 이것 선택
```
환경변수가 등록되어 있으면 자동으로 키를 읽어옵니다.

---

아래 화면이 보이면 성공!

```
╭─────────────────────────────────╮
│ ✦ Welcome to Gemini CLI!        │
│   /help for commands            │
╰─────────────────────────────────╯
>
```

---

## 기본 사용법

### 대화하기
```
> 안녕하세요!
> 파이썬으로 Hello World 출력하는 코드 짜줘
```

### 파일 참조
```
> @main.py 이 코드 설명해줘
> @data.csv 읽어서 분석하는 코드 만들어줘
```

### 주요 명령어

| 명령어 | 설명 |
|--------|------|
| `/help` | 전체 명령어 보기 |
| `/quit` | 종료 |
| `/stats model` | 사용량 확인 |
| `Ctrl+C` | 응답 중단 |

---

## 빠른 설치 요약

```bash
# 1. Homebrew 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Apple Silicon(M칩)만:
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# 2. VSCode 설치
brew install --cask visual-studio-code

# 3. Python 설치
brew install python
echo 'alias python=python3' >> ~/.zshrc
echo 'alias pip=pip3' >> ~/.zshrc
source ~/.zshrc

# 4. Node.js 설치
brew install node@22

# 5. Gemini CLI 설치 및 실행
npm install -g @google/gemini-cli
gemini
```

---

## 자주 묻는 질문

**Q. pip install 시 permission 오류가 나면?**
```bash
python -m venv myenv
source myenv/bin/activate
pip install 패키지명
```

**Q. `gemini` 명령이 안 되면?**
```bash
npx @google/gemini-cli   # 설치 없이 바로 실행
```

**Q. `brew` 명령이 안 되면?**
```bash
# Apple Silicon
eval "$(/opt/homebrew/bin/brew shellenv)"
# Intel
eval "$(/usr/local/bin/brew shellenv)"
```

**Q. Windows 가이드와 뭐가 다른가요?**

| 항목 | Windows | Mac |
|------|---------|-----|
| 리눅스 환경 | WSL2 설치 필요 | 불필요 |
| 패키지 관리자 | apt | Homebrew |
| 쉘 설정 파일 | `.bashrc` | `.zshrc` |
| 전체 난이도 | 중간 | 쉬움 |

---

> 참고: [Homebrew 공식](https://brew.sh) · [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
