# macOS용 VSCode + Gemini CLI 완전 초보자 설치·사용 가이드

> **대상**: Mac 컴퓨터에 Python, Node.js 등 개발 도구가 전혀 없는 사용자  
> **목표**: Homebrew 설치 → VSCode 설정 → Python/Node.js 설치 → Gemini CLI 실행까지  
> **소요 시간**: 약 20~30분  
> **작성**: 이종혁 (경희대 미디어학과) · 2025년 3월

---

## 목차

1. [전체 흐름 미리 보기](#1-전체-흐름-미리-보기)
2. [STEP 1: 터미널 열기 — Mac의 명령창](#2-step-1-터미널-열기--mac의-명령창)
3. [STEP 2: Homebrew 설치 — Mac의 패키지 관리자](#3-step-2-homebrew-설치--mac의-패키지-관리자)
4. [STEP 3: VSCode 설치 및 설정](#4-step-3-vscode-설치-및-설정)
5. [STEP 4: Python 설치](#5-step-4-python-설치)
6. [STEP 5: Node.js 설치](#6-step-5-nodejs-설치)
7. [STEP 6: Gemini API 키 발급](#7-step-6-gemini-api-키-발급)
8. [STEP 7: Gemini CLI 설치 및 실행](#8-step-7-gemini-cli-설치-및-실행)
9. [STEP 8: Gemini CLI 기본 사용법](#9-step-8-gemini-cli-기본-사용법)
10. [STEP 9: VSCode + Gemini CLI 실전 워크플로우](#10-step-9-vscode--gemini-cli-실전-워크플로우)
11. [자주 묻는 질문 (FAQ)](#11-자주-묻는-질문-faq)
12. [유용한 명령어 치트시트](#12-유용한-명령어-치트시트)

---

## 1. 전체 흐름 미리 보기

```
[Mac]
  │
  ├── ① 터미널 열기 (Mac에 기본 내장)
  │
  ├── ② Homebrew 설치 (Mac용 패키지 관리자)
  │       └── 이후 모든 도구를 brew 명령으로 간편 설치
  │
  ├── ③ VSCode 설치 (코드 편집기)
  │       └── 터미널에서 code 명령으로 바로 실행
  │
  ├── ④ Python 설치
  │
  ├── ⑤ Node.js 설치 (Gemini CLI에 필요)
  │       └── npm (패키지 관리자) 자동 포함
  │
  ├── ⑥ Gemini API 키 발급 (Google AI Studio에서 무료)
  │
  └── ⑦ Gemini CLI 설치 & 실행
          └── 터미널에서 AI와 대화하며 코딩!
```

**Mac 사용자의 장점**: Mac은 Unix 기반 운영체제라서 Windows처럼 WSL을 따로 설치할 필요가 없습니다. 터미널이 바로 리눅스와 거의 동일한 환경이므로 설정이 더 간단합니다.

---

## 2. STEP 1: 터미널 열기 — Mac의 명령창

터미널은 Mac에 기본으로 설치되어 있습니다.

### 열기 방법 (3가지 중 택 1)

**방법 A: Spotlight 검색 (가장 빠름)**
1. `Cmd + Space` 누르기
2. "터미널" 또는 "Terminal" 입력
3. Enter

**방법 B: Finder에서 찾기**
1. Finder → 응용 프로그램 → 유틸리티 → 터미널

**방법 C: Launchpad**
1. Dock에서 Launchpad 클릭 → "기타" 폴더 → 터미널

### 터미널이 열리면

이런 화면이 나타납니다:
```
사용자이름@MacBook ~ %
```

여기에 명령어를 입력하게 됩니다. `%` 또는 `$` 기호가 프롬프트(입력 대기 표시)입니다.

### 내 Mac 정보 확인

```bash
# macOS 버전 확인
sw_vers

# 칩 종류 확인 (Apple Silicon인지 Intel인지)
uname -m
# arm64 → Apple Silicon (M1/M2/M3/M4)
# x86_64 → Intel
```

> 칩 종류에 따라 일부 설치 과정이 다를 수 있지만, 이 가이드는 **둘 다 동일하게** 진행됩니다.

---

## 3. STEP 2: Homebrew 설치 — Mac의 패키지 관리자

Homebrew는 Mac에서 개발 도구를 설치·관리하는 필수 프로그램입니다. "Mac의 앱스토어(개발자 버전)"이라고 생각하면 됩니다.

### 3-1. Homebrew 설치

터미널에 아래 명령어를 **한 줄로** 복사·붙여넣기하고 Enter:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

설치 중 물어보는 것들:
- **"Press RETURN to continue"** → Enter 누르기
- **비밀번호 입력** → Mac 로그인 비밀번호 입력 (화면에 안 보이는 게 정상!)

설치에 2~5분 정도 걸립니다.

### 3-2. Homebrew PATH 설정 (Apple Silicon Mac만 해당)

> Intel Mac은 이 단계를 건너뛰세요.

Apple Silicon Mac (M1/M2/M3/M4)에서는 설치 끝에 다음과 비슷한 안내가 나옵니다:

```
==> Next steps:
- Run these commands in your terminal to add Homebrew to your PATH:
```

아래 명령어를 실행하세요:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 3-3. 설치 확인

```bash
brew --version
# 출력 예: Homebrew 4.4.x
```

버전이 표시되면 성공입니다!

---

## 4. STEP 3: VSCode 설치 및 설정

### 4-1. VSCode 설치

**방법 A: Homebrew로 설치 (권장)**

```bash
brew install --cask visual-studio-code
```

**방법 B: 직접 다운로드**

1. [https://code.visualstudio.com](https://code.visualstudio.com) 접속
2. "Download for Mac" 클릭
3. 다운로드된 `.zip` 파일 더블클릭 → `Visual Studio Code.app`을 **응용 프로그램** 폴더로 드래그

### 4-2. 터미널에서 `code` 명령어 설정

VSCode 설치 후, 터미널에서 `code` 명령으로 바로 실행할 수 있도록 설정합니다:

1. VSCode 실행
2. `Cmd + Shift + P` (명령 팔레트 열기)
3. "shell command" 검색
4. **"Shell Command: Install 'code' command in PATH"** 선택

확인:
```bash
# 터미널을 새로 열고
code --version
```

### 4-3. 추천 확장 프로그램 설치

VSCode에서 `Cmd + Shift + X` (확장 패널)를 열고 설치:

| 확장 이름 | 용도 |
|-----------|------|
| Python | Python 개발 지원 |
| Pylance | Python 코드 자동완성 |
| Korean Language Pack | VSCode 한국어 메뉴 |
| Markdown All in One | 마크다운 미리보기 |

---

## 5. STEP 4: Python 설치

Mac에는 Python이 기본 포함되어 있을 수 있지만, 최신 버전을 확실하게 설치합니다.

### 5-1. Python 설치

```bash
# Homebrew로 Python 설치
brew install python

# 설치 확인
python3 --version
# 출력 예: Python 3.13.x

pip3 --version
# 출력 예: pip 24.x from ...
```

### 5-2. python3 대신 python으로 쓰기 (편의 설정)

Mac의 기본 쉘은 **zsh**이므로 `.zshrc` 파일에 설정합니다:

```bash
echo 'alias python=python3' >> ~/.zshrc
echo 'alias pip=pip3' >> ~/.zshrc
source ~/.zshrc

# 확인
python --version
```

### 5-3. 간단한 테스트

```bash
python -c "print('Hello, Python on Mac!')"
# 출력: Hello, Python on Mac!
```

---

## 6. STEP 5: Node.js 설치

Gemini CLI를 실행하려면 **Node.js 20 이상**이 필요합니다.

### 방법 A: Homebrew로 직접 설치 (가장 간단)

```bash
# Node.js LTS 버전 설치
brew install node@22

# 설치 확인
node --version
# 출력 예: v22.x.x

npm --version
# 출력 예: 10.x.x
```

### 방법 B: nvm으로 설치 (버전 관리가 필요한 경우)

```bash
# nvm 설치
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 쉘 설정 반영
source ~/.zshrc

# Node.js LTS 설치
nvm install --lts

# 확인
node --version
npm --version
```

> **npm**은 Node.js의 패키지 관리자로, Node.js를 설치하면 자동으로 함께 설치됩니다.

### 💡 트러블슈팅

`node: command not found` 오류가 나면:
```bash
# Homebrew로 설치한 경우
brew link node@22

# nvm으로 설치한 경우
source ~/.zshrc
nvm use --lts
```

---

## 7. STEP 6: Gemini API 키 발급

Gemini CLI는 두 가지 인증 방식을 지원합니다:
- **방법 A: Google 로그인** (가장 간단, 무료 60회/분, 1000회/일)
- **방법 B: API 키** (자동화·스크립트에 유용)

### 방법 A: Google 로그인 (초보자 추천 ⭐)

API 키 없이 바로 사용 가능합니다. Gemini CLI를 처음 실행하면 Safari/Chrome이 열리고 Google 계정으로 로그인하면 끝! (STEP 7에서 자세히 설명)

**무료 쿼터:**
- 분당 60회 요청
- 일일 1,000회 모델 요청

### 방법 B: API 키 발급 (선택사항)

#### 7-1. Google AI Studio 접속

1. 브라우저에서 [https://aistudio.google.com](https://aistudio.google.com) 접속
2. Google 계정으로 로그인

#### 7-2. API 키 생성

1. 왼쪽 메뉴에서 **"Get API Key"** (또는 **"API 키 가져오기"**) 클릭
2. 상단의 **"API 키 만들기"** (Create API Key) 버튼 클릭
3. 새 프로젝트 또는 기존 프로젝트 선택 → **"키 만들기"** 클릭
4. 생성된 API 키를 **복사**해서 안전한 곳에 저장

> ⚠️ **API 키는 비밀번호와 같습니다.** 절대 GitHub, 블로그, SNS에 공개하지 마세요!

#### 7-3. 환경변수로 API 키 등록

```bash
# .zshrc 파일에 환경변수 추가 (Mac 기본 쉘 = zsh)
echo 'export GEMINI_API_KEY="여기에_발급받은_API키_붙여넣기"' >> ~/.zshrc

# 적용
source ~/.zshrc

# 확인 (키가 출력되면 성공)
echo $GEMINI_API_KEY
```

> ⚠️ Mac에서는 `.bashrc`가 아닌 **`.zshrc`** 파일을 사용합니다. macOS Catalina(2019) 이후 기본 쉘이 zsh로 변경되었습니다.

---

## 8. STEP 7: Gemini CLI 설치 및 실행

### 8-1. Gemini CLI 설치

터미널에서:

```bash
# 전역 설치 (권장)
npm install -g @google/gemini-cli
```

설치 확인:
```bash
gemini --version
```

> permission 오류가 나면:
> ```bash
> sudo npm install -g @google/gemini-cli
> ```
> Mac 비밀번호를 입력하세요.

### 8-2. Gemini CLI 처음 실행

```bash
gemini
```

#### 테마 선택

```
? Select a theme:
❯ Default
  Minimal
  Solarized
  High Contrast
```

방향키(↑↓)로 선택하고 Enter를 누릅니다.

#### 인증 방법 선택

```
? How would you like to authenticate for this project?
❯ 1. Login with Google         ← 이것을 선택 (추천!)
  2. Use API Key
  3. Skip authentication
```

**"1. Login with Google"** 선택:
1. Safari 또는 Chrome이 자동으로 열림
2. Google 계정으로 로그인
3. "Sign in" 클릭
4. 터미널로 돌아오면 인증 완료

> 브라우저가 자동으로 안 열리면, 터미널에 표시된 URL을 복사해서 브라우저에 직접 붙여넣기 하세요.

인증 완료 후:

```
╭─────────────────────────────────────────╮
│ ✦ Welcome to Gemini CLI!                │
│                                         │
│ /help for commands, /quit to exit       │
╰─────────────────────────────────────────╯

>
```

### 8-3. 첫 대화 해보기

```
> 안녕하세요! 저는 Mac에서 Gemini CLI를 처음 사용합니다.
```

---

## 9. STEP 8: Gemini CLI 기본 사용법

### 9-1. 핵심 슬래시 명령어

Gemini CLI 프롬프트(`>`)에서 `/`로 시작하는 명령어를 사용합니다:

| 명령어 | 설명 |
|--------|------|
| `/help` | 전체 명령어 목록 보기 |
| `/chat` | 새 대화 시작 |
| `/quit` 또는 `/exit` | Gemini CLI 종료 |
| `/stats model` | 토큰 사용량·쿼터 확인 |
| `/init` | 현재 프로젝트에 GEMINI.md 파일 생성 |
| `/memory show` | 현재 컨텍스트 확인 |
| `/ide install` | VSCode 연동 설정 |

### 9-2. 파일 작업

```bash
# 현재 폴더의 파일 읽기·분석
> 이 폴더에 있는 Python 파일을 분석해줘

# 특정 파일 참조 (@ 기호 사용)
> @main.py 이 코드의 버그를 찾아줘

# 파일 생성·수정 요청
> hello.py 파일을 만들어줘. "Hello World"를 출력하는 코드로.
```

### 9-3. 코딩 활용 예시

```bash
# Python 코드 작성 요청
> 네이버 뉴스에서 헤드라인을 수집하는 Python 코드를 작성해줘

# 코드 설명 요청
> @scraper.py 이 코드를 초보자도 이해할 수 있게 설명해줘

# 오류 해결
> 이 에러를 해결해줘: ModuleNotFoundError: No module named 'pandas'

# 데이터 분석
> data.csv 파일을 읽어서 기본 통계를 보여주는 Python 코드를 작성해줘
```

### 9-4. 셸 명령어 실행

Gemini CLI는 터미널 명령어를 직접 실행할 수도 있습니다:

```bash
> 현재 폴더의 파일 목록을 보여줘
```

> Gemini가 명령어를 실행하기 전에 확인을 요청합니다. `y`를 눌러 승인하세요.

### 9-5. 대화 관리

```bash
# 이전 세션 이어서 하기
gemini --resume

# 세션 목록 확인
gemini --list
```

---

## 10. STEP 9: VSCode + Gemini CLI 실전 워크플로우

### 10-1. 프로젝트 폴더 만들고 시작하기

```bash
# 터미널에서
mkdir ~/my-project
cd ~/my-project

# VSCode로 이 폴더 열기
code .
```

### 10-2. VSCode 터미널에서 Gemini CLI 사용

1. VSCode에서 `` Ctrl + ` `` (백틱) 으로 터미널 열기
   - Mac에서는 `` Control + ` `` 입니다
2. 터미널이 `zsh`인지 확인 (기본값이므로 대부분 자동)
3. `gemini` 입력하여 Gemini CLI 시작

### 10-3. 실전 예제: 데이터 분석 프로젝트

```bash
# 1. 프로젝트 폴더 생성
mkdir ~/data-project && cd ~/data-project
code .

# 2. VSCode 터미널에서 Gemini CLI 시작
gemini

# 3. Gemini에게 요청
> pandas와 matplotlib을 사용해서 CSV 파일을 분석하고 
> 차트를 그리는 Python 코드를 만들어줘.
> 샘플 CSV 데이터도 같이 만들어줘.
```

Gemini가 파일을 생성하면:

```bash
# 4. Gemini CLI 나가기 (/quit)
# 5. 필요한 패키지 설치
pip install pandas matplotlib

# 6. 코드 실행
python analysis.py
```

### 10-4. GEMINI.md로 프로젝트 컨텍스트 설정

프로젝트 루트에 `GEMINI.md` 파일을 만들면 Gemini가 프로젝트 맥락을 이해합니다:

```markdown
# 프로젝트 정보

## 개요
이 프로젝트는 한국어 뉴스 데이터를 수집·분석하는 데이터 저널리즘 프로젝트입니다.

## 기술 스택
- Python 3.13
- pandas, beautifulsoup4, matplotlib
- 한국어 형태소 분석: konlpy

## 코딩 규칙
- 한국어 주석 사용
- 함수마다 docstring 작성
- 변수명은 영어 snake_case
```

이후 Gemini CLI를 실행하면 이 맥락을 자동으로 반영합니다.

---

## 11. 자주 묻는 질문 (FAQ)

### Q1. Gemini CLI 무료 사용량은 얼마인가요?

Google 로그인 방식:
- **분당 60회** 요청
- **일일 1,000회** 모델 요청
- 완전 무료, 신용카드 불필요

### Q2. pip install할 때 permission 에러가 나요

```bash
# 가상환경 사용 (권장)
python -m venv myenv
source myenv/bin/activate
pip install pandas    # 가상환경 안에서는 에러 없음

# 가상환경 나가기
deactivate
```

### Q3. `gemini` 명령이 안 됩니다

```bash
# npm 전역 경로 확인
npm list -g @google/gemini-cli

# 재설치
npm install -g @google/gemini-cli

# 또는 npx로 바로 실행 (설치 없이)
npx @google/gemini-cli
```

### Q4. `brew` 명령이 안 됩니다

```bash
# Apple Silicon Mac인 경우 PATH 재설정
eval "$(/opt/homebrew/bin/brew shellenv)"

# Intel Mac인 경우
eval "$(/usr/local/bin/brew shellenv)"
```

### Q5. zsh와 bash의 차이는?

macOS Catalina(2019) 이후 기본 쉘이 bash에서 **zsh**로 변경되었습니다.

| 항목 | bash | zsh (Mac 기본) |
|------|------|---------|
| 설정 파일 | `~/.bashrc`, `~/.bash_profile` | **`~/.zshrc`** |
| 프롬프트 | `$` | `%` |
| 사용법 | 거의 동일 | 거의 동일 |

이 가이드의 모든 설정은 **`.zshrc`** 기준입니다.

### Q6. Gemini CLI에서 인터넷 검색도 되나요?

네! Gemini CLI는 웹 검색 및 URL 접근 기능을 지원합니다:
```bash
> 오늘 한국 뉴스 헤드라인을 검색해줘
> https://example.com 이 페이지 내용을 요약해줘
```

### Q7. Apple Silicon과 Intel Mac에서 차이가 있나요?

이 가이드의 모든 과정은 **양쪽 모두 동일**합니다. 유일한 차이는 Homebrew 설치 경로입니다:
- Apple Silicon: `/opt/homebrew/`
- Intel: `/usr/local/`

하지만 Homebrew가 자동 처리하므로 별도로 신경 쓸 필요 없습니다.

### Q8. Windows 가이드와의 차이는?

| 항목 | Windows | Mac |
|------|---------|-----|
| 리눅스 환경 | WSL2 설치 필요 | 불필요 (Mac = Unix 기반) |
| 패키지 관리자 | apt (Ubuntu) | **Homebrew** |
| 쉘 설정 파일 | `.bashrc` | **`.zshrc`** |
| 터미널 | Ubuntu / Windows Terminal | **터미널.app** |
| 전체 난이도 | 중간 | **쉬움** |

---

## 12. 유용한 명령어 치트시트

### 터미널(zsh) 기본 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `ls` | 파일 목록 보기 | `ls -la` (숨김파일 포함) |
| `cd` | 폴더 이동 | `cd ~/my-project` |
| `mkdir` | 폴더 생성 | `mkdir new-folder` |
| `pwd` | 현재 위치 확인 | `pwd` |
| `cp` | 파일 복사 | `cp file1.txt file2.txt` |
| `mv` | 파일 이동/이름변경 | `mv old.txt new.txt` |
| `rm` | 파일 삭제 | `rm file.txt` |
| `cat` | 파일 내용 보기 | `cat hello.py` |
| `clear` | 화면 지우기 | `clear` (또는 `Cmd + K`) |
| `open` | Finder에서 열기 | `open .` (현재 폴더) |

### Homebrew

| 명령어 | 설명 |
|--------|------|
| `brew install 패키지` | 패키지 설치 |
| `brew install --cask 앱` | GUI 앱 설치 |
| `brew update` | Homebrew 업데이트 |
| `brew upgrade` | 설치된 패키지 업그레이드 |
| `brew list` | 설치된 패키지 목록 |
| `brew search 키워드` | 패키지 검색 |
| `brew uninstall 패키지` | 패키지 삭제 |

### Python

| 명령어 | 설명 |
|--------|------|
| `python --version` | Python 버전 확인 |
| `pip install 패키지명` | 패키지 설치 |
| `pip list` | 설치된 패키지 목록 |
| `python 파일.py` | Python 파일 실행 |
| `python -m venv 환경명` | 가상환경 생성 |
| `source 환경명/bin/activate` | 가상환경 활성화 |
| `deactivate` | 가상환경 비활성화 |

### Node.js

| 명령어 | 설명 |
|--------|------|
| `node --version` | Node.js 버전 확인 |
| `npm --version` | npm 버전 확인 |
| `npm install -g 패키지명` | 글로벌 패키지 설치 |

### Gemini CLI

| 명령어/단축키 | 설명 |
|---------------|------|
| `gemini` | Gemini CLI 시작 |
| `gemini --resume` | 마지막 세션 이어서 |
| `/help` | 도움말 |
| `/chat` | 새 대화 |
| `/quit` | 종료 |
| `/stats model` | 사용량 확인 |
| `/init` | GEMINI.md 생성 |
| `@파일명` | 파일 첨부 |
| `Ctrl + C` | 현재 응답 중단 |
| `↑` / `↓` | 이전 입력 탐색 |

### Mac 키보드 단축키 (VSCode)

| 단축키 | 설명 |
|--------|------|
| `Cmd + Shift + P` | 명령 팔레트 |
| `Cmd + Shift + X` | 확장 패널 |
| `` Control + ` `` | 터미널 열기/닫기 |
| `Cmd + S` | 저장 |
| `Cmd + P` | 파일 빠르게 열기 |
| `Cmd + B` | 사이드바 토글 |
| `Cmd + ,` | 설정 |

---

## 부록: 전체 설치 한 번에 따라하기 (요약)

터미널을 열고 아래 명령어를 순서대로 실행하세요:

```bash
# 1. Homebrew 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Apple Silicon Mac만 (M1/M2/M3/M4):
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

# 5. Gemini CLI 설치
npm install -g @google/gemini-cli

# 6. 실행!
gemini
```

Gemini CLI 첫 실행:
1. 테마 선택
2. "Login with Google" 선택
3. 브라우저에서 로그인
4. 코딩 시작! 🎉

---

> **문의**: 이종혁 교수 (경희대 미디어학과)  
> **참고 자료**:
> - Homebrew 공식: https://brew.sh
> - Gemini CLI 공식: https://geminicli.com/docs/
> - Gemini CLI GitHub: https://github.com/google-gemini/gemini-cli
> - Google AI Studio: https://aistudio.google.com
> - VSCode 공식: https://code.visualstudio.com
