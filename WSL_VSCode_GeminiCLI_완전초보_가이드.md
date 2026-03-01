# WSL + VSCode + Gemini CLI 완전 초보자 설치·사용 가이드

> **대상**: 컴퓨터에 Python, Node.js 등 개발 도구가 전혀 없는 Windows 사용자  
> **목표**: WSL(리눅스 환경) 설치 → VSCode 연동 → Python/Node.js 설치 → Gemini CLI 실행까지  
> **소요 시간**: 약 30~40분  
> **작성**: 이종혁 (경희대 미디어학과) · 2025년 3월

---

## 목차

1. [전체 흐름 미리 보기](#1-전체-흐름-미리-보기)
2. [STEP 1: WSL2 설치 — Windows에서 리눅스 쓰기](#2-step-1-wsl2-설치--windows에서-리눅스-쓰기)
3. [STEP 2: VSCode 설치 및 WSL 연동](#3-step-2-vscode-설치-및-wsl-연동)
4. [STEP 3: Python 설치](#4-step-3-python-설치)
5. [STEP 4: Node.js 설치](#5-step-4-nodejs-설치)
6. [STEP 5: Gemini API 키 발급](#6-step-5-gemini-api-키-발급)
7. [STEP 6: Gemini CLI 설치 및 실행](#7-step-6-gemini-cli-설치-및-실행)
8. [STEP 7: Gemini CLI 기본 사용법](#8-step-7-gemini-cli-기본-사용법)
9. [STEP 8: VSCode + Gemini CLI 실전 워크플로우](#9-step-8-vscode--gemini-cli-실전-워크플로우)
10. [자주 묻는 질문 (FAQ)](#10-자주-묻는-질문-faq)
11. [유용한 명령어 치트시트](#11-유용한-명령어-치트시트)

---

## 1. 전체 흐름 미리 보기

```
[Windows PC]
    │
    ├── ① WSL2 설치 (Windows 안에 리눅스 환경 생성)
    │       └── Ubuntu (리눅스 배포판) 자동 설치
    │
    ├── ② VSCode 설치 (코드 편집기)
    │       └── WSL 확장 설치 → 리눅스 환경에서 직접 코딩
    │
    ├── ③ Python 설치 (WSL 안에서)
    │
    ├── ④ Node.js 설치 (WSL 안에서)
    │       └── npm (패키지 관리자) 자동 포함
    │
    ├── ⑤ Gemini API 키 발급 (Google AI Studio에서 무료)
    │
    └── ⑥ Gemini CLI 설치 & 실행
            └── 터미널에서 AI와 대화하며 코딩!
```

**왜 WSL인가?**  
프로그래밍 세계에서는 리눅스/맥 환경이 표준입니다. WSL을 쓰면 Windows를 포맷하지 않고도 리눅스를 사용할 수 있어, 실무에서 쓰이는 개발 환경을 그대로 경험할 수 있습니다.

---

## 2. STEP 1: WSL2 설치 — Windows에서 리눅스 쓰기

### 사전 확인

- **운영체제**: Windows 10 (빌드 19041 이상) 또는 Windows 11
- **확인 방법**: `Win + R` → `winver` 입력 → 버전 확인

### 설치 방법

#### 2-1. PowerShell을 관리자 권한으로 실행

1. 화면 하단 **시작 버튼** 우클릭 (또는 `Win + X`)
2. **"터미널(관리자)"** 또는 **"PowerShell(관리자)"** 클릭
3. "이 앱이 디바이스를 변경할 수 있도록 허용하시겠어요?" → **예** 클릭

#### 2-2. WSL 설치 명령어 입력

```powershell
wsl --install
```

이 한 줄이면 됩니다! 이 명령이 자동으로 처리하는 것들:
- Linux용 Windows 하위 시스템 활성화
- 가상 머신 플랫폼 활성화
- WSL2를 기본 버전으로 설정
- Ubuntu (최신 LTS 버전) 설치

#### 2-3. 컴퓨터 재시작

설치가 끝나면 **반드시 컴퓨터를 재시작**합니다.

#### 2-4. Ubuntu 초기 설정

재시작 후 Ubuntu 터미널 창이 자동으로 열립니다 (안 열리면 시작 메뉴에서 "Ubuntu" 검색하여 실행).

```
Enter new UNIX username: myname          ← 원하는 사용자 이름 입력
New password: ********                   ← 비밀번호 입력 (화면에 안 보이는 게 정상!)
Retype new password: ********            ← 비밀번호 다시 입력
```

> ⚠️ **비밀번호 입력 시 화면에 아무것도 안 보이는 게 정상입니다.** 리눅스의 보안 기능입니다. 그냥 입력하고 Enter를 누르세요.

#### 2-5. 설치 확인

Ubuntu 터미널에서:

```bash
# WSL 버전 확인 (PowerShell에서 실행)
wsl --list --verbose
```

결과에 `Ubuntu`와 `VERSION 2`가 보이면 성공입니다.

#### 2-6. Ubuntu 업데이트

처음 설치 후 반드시 한 번 해주세요:

```bash
sudo apt update && sudo apt upgrade -y
```

> `sudo`는 관리자 권한으로 실행하는 명령어입니다. 비밀번호를 물어보면 아까 설정한 비밀번호를 입력하세요.

### 💡 혹시 오류가 나면?

| 오류 | 해결 방법 |
|------|-----------|
| `0x800701bc` | PowerShell(관리자)에서 `wsl --update` 실행 후 재시작 |
| 가상화 관련 오류 | BIOS에서 가상화(Virtualization) 옵션 활성화 필요. 컴퓨터 제조사별로 방법이 다름 |
| WSL1으로 설치됨 | `wsl --set-default-version 2` 실행 후 재설치 |

---

## 3. STEP 2: VSCode 설치 및 WSL 연동

### 3-1. VSCode 다운로드 및 설치

1. 브라우저에서 [https://code.visualstudio.com](https://code.visualstudio.com) 접속
2. **"Download for Windows"** 클릭 → 설치 파일 실행
3. 설치 시 아래 옵션 **반드시 체크**:
   - ✅ `PATH에 추가` (Add to PATH)
   - ✅ `파일의 오른쪽 클릭 메뉴에 "Code로 열기" 추가`

### 3-2. WSL 확장(Extension) 설치

1. VSCode 실행
2. 왼쪽 사이드바에서 **확장(Extensions)** 아이콘 클릭 (네모 4개 모양, 또는 `Ctrl + Shift + X`)
3. 검색창에 **`WSL`** 입력
4. **"WSL"** (Microsoft 제작) → **Install** 클릭

### 3-3. VSCode에서 WSL 접속하기

**방법 A: VSCode에서 직접 연결**
1. VSCode 좌측 하단에 **파란색 `><` 아이콘** 클릭
2. **"WSL에 연결"** 또는 **"Connect to WSL"** 선택
3. 좌측 하단이 `WSL: Ubuntu`로 바뀌면 성공!

**방법 B: Ubuntu 터미널에서 VSCode 열기 (더 간편)**
```bash
# Ubuntu 터미널에서 현재 폴더를 VSCode로 열기
code .
```

> 처음 실행 시 "VS Code Server for Linux"가 자동 설치됩니다. 1~2분 정도 기다려주세요.

### 3-4. 추천 확장 프로그램 추가 설치

WSL에 연결된 상태에서 아래 확장들을 설치하세요:

| 확장 이름 | 용도 |
|-----------|------|
| Python | Python 개발 지원 |
| Pylance | Python 코드 자동완성 |
| Korean Language Pack | VSCode 한국어 메뉴 |
| Markdown All in One | 마크다운 미리보기 |

---

## 4. STEP 3: Python 설치

WSL의 Ubuntu에는 Python이 기본 포함되어 있을 수 있지만, 최신 버전과 pip(패키지 관리자)를 확실하게 설정해봅시다.

### 4-1. Ubuntu 터미널 열기

시작 메뉴에서 "Ubuntu"를 검색해 실행하거나, Windows Terminal에서 Ubuntu 탭을 선택합니다.

### 4-2. Python 설치 및 확인

```bash
# Python 설치 (이미 있을 수 있지만 확실하게)
sudo apt install python3 python3-pip python3-venv -y

# 설치 확인
python3 --version
# 출력 예: Python 3.12.3

pip3 --version
# 출력 예: pip 24.0 from ...
```

### 4-3. python3 대신 python으로 쓰기 (편의 설정)

```bash
# python 명령으로 python3 사용하도록 별칭 설정
echo "alias python=python3" >> ~/.bashrc
echo "alias pip=pip3" >> ~/.bashrc
source ~/.bashrc

# 확인
python --version
```

### 4-4. 간단한 테스트

```bash
python -c "print('Hello, Python!')"
# 출력: Hello, Python!
```

---

## 5. STEP 4: Node.js 설치

Gemini CLI를 실행하려면 **Node.js 20 이상**이 필요합니다.

### 5-1. nvm으로 Node.js 설치 (권장)

nvm(Node Version Manager)을 사용하면 Node.js 버전을 쉽게 관리할 수 있습니다.

```bash
# nvm 설치
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 터미널 새로고침 (중요!)
source ~/.bashrc

# nvm 설치 확인
nvm --version
# 출력 예: 0.40.1
```

### 5-2. Node.js LTS 버전 설치

```bash
# 최신 LTS(장기 지원) 버전 설치
nvm install --lts

# 설치 확인
node --version
# 출력 예: v22.13.1

npm --version
# 출력 예: 10.9.2
```

> **npm**은 Node.js의 패키지 관리자로, Node.js를 설치하면 자동으로 함께 설치됩니다. Gemini CLI도 npm으로 설치합니다.

### 💡 트러블슈팅

`nvm: command not found` 오류가 나면:
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
source ~/.bashrc
```

---

## 6. STEP 5: Gemini API 키 발급

Gemini CLI는 두 가지 인증 방식을 지원합니다:
- **방법 A: Google 로그인** (가장 간단, 무료 60회/분, 1000회/일)
- **방법 B: API 키** (더 유연, 환경변수로 관리)

### 방법 A: Google 로그인 (초보자 추천 ⭐)

API 키 없이 바로 사용 가능합니다. Gemini CLI를 처음 실행하면 브라우저가 열리고 Google 계정으로 로그인하면 됩니다. (STEP 6에서 자세히 설명)

**무료 쿼터:**
- 분당 60회 요청
- 일일 1,000회 모델 요청

### 방법 B: API 키 발급 (선택사항)

API 키가 필요한 경우 (자동화 스크립트, 더 세밀한 관리가 필요할 때):

#### 6-1. Google AI Studio 접속

1. 브라우저에서 [https://aistudio.google.com](https://aistudio.google.com) 접속
2. Google 계정으로 로그인

#### 6-2. API 키 생성

1. 왼쪽 메뉴에서 **"Get API Key"** (또는 **"API 키 가져오기"**) 클릭
2. 상단의 **"API 키 만들기"** (Create API Key) 버튼 클릭
3. 새 프로젝트 또는 기존 프로젝트 선택 → **"키 만들기"** 클릭
4. 생성된 API 키를 **복사**해서 안전한 곳에 저장

> ⚠️ **API 키는 비밀번호와 같습니다.** 절대 GitHub, 블로그, SNS에 공개하지 마세요!

#### 6-3. 환경변수로 API 키 등록

Ubuntu 터미널에서:

```bash
# .bashrc 파일에 환경변수 추가
echo 'export GEMINI_API_KEY="여기에_발급받은_API키_붙여넣기"' >> ~/.bashrc

# 적용
source ~/.bashrc

# 확인 (키가 출력되면 성공)
echo $GEMINI_API_KEY
```

---

## 7. STEP 6: Gemini CLI 설치 및 실행

### 7-1. Gemini CLI 설치

Ubuntu 터미널에서:

```bash
# 전역 설치 (권장)
npm install -g @google/gemini-cli
```

설치 확인:
```bash
gemini --version
```

> 설치 없이 바로 실행하려면 `npx @google/gemini-cli` 명령도 사용 가능합니다.

### 7-2. Gemini CLI 처음 실행

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

방향키로 원하는 테마를 선택하고 Enter를 누릅니다.

#### 인증 방법 선택

```
? How would you like to authenticate for this project?
❯ 1. Login with Google         ← 이것을 선택 (추천!)
  2. Use API Key
  3. Skip authentication
```

**"1. Login with Google"** 선택 → 브라우저가 자동으로 열림 → Google 계정 로그인 → "Sign in" 클릭

> 브라우저가 자동으로 안 열리면, 터미널에 표시된 URL을 복사해서 브라우저에 직접 붙여넣기 하세요.

인증 완료 후 터미널에 다음과 같이 표시되면 성공입니다:

```
╭─────────────────────────────────────────╮
│ ✦ Welcome to Gemini CLI!                │
│                                         │
│ /help for commands, /quit to exit       │
╰─────────────────────────────────────────╯

>
```

### 7-3. 첫 대화 해보기

```
> 안녕하세요! 저는 Gemini CLI를 처음 사용합니다.
```

Gemini가 한국어로 답변합니다!

---

## 8. STEP 7: Gemini CLI 기본 사용법

### 8-1. 핵심 슬래시 명령어

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

### 8-2. 파일 작업

```bash
# 현재 폴더의 파일 읽기·분석
> 이 폴더에 있는 Python 파일을 분석해줘

# 특정 파일 참조 (@ 기호 사용)
> @main.py 이 코드의 버그를 찾아줘

# 파일 생성·수정 요청
> hello.py 파일을 만들어줘. "Hello World"를 출력하는 코드로.
```

### 8-3. 코딩 활용 예시

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

### 8-4. 셸(터미널) 명령어 실행

Gemini CLI는 터미널 명령어를 직접 실행할 수도 있습니다:

```bash
# Gemini에게 명령어 실행 요청
> 현재 폴더의 파일 목록을 보여줘

# Gemini가 ls 또는 dir 명령어를 실행하고 결과를 보여줌
```

> Gemini가 명령어를 실행하기 전에 확인을 요청합니다. `y`를 눌러 승인하세요.

### 8-5. 대화 관리

```bash
# 이전 세션 이어서 하기
gemini --resume

# 특정 세션 재개
gemini --resume <session-id>
```

---

## 9. STEP 8: VSCode + Gemini CLI 실전 워크플로우

### 9-1. 프로젝트 폴더 만들고 시작하기

```bash
# Ubuntu 터미널에서
mkdir ~/my-project
cd ~/my-project

# VSCode로 이 폴더 열기
code .
```

### 9-2. VSCode 터미널에서 Gemini CLI 사용

1. VSCode에서 `` Ctrl + ` `` (백틱)으로 터미널 열기
2. 터미널이 WSL(Ubuntu)인지 확인 (우상단에 `bash` 또는 `Ubuntu` 표시)
3. `gemini` 입력하여 Gemini CLI 시작

### 9-3. 실전 예제: 데이터 분석 프로젝트

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
# 4. Gemini CLI 잠시 나가기 (Ctrl+C 또는 /quit)
# 5. 필요한 패키지 설치
pip install pandas matplotlib

# 6. 코드 실행
python analysis.py
```

### 9-4. GEMINI.md로 프로젝트 컨텍스트 설정

프로젝트 루트에 `GEMINI.md` 파일을 만들면 Gemini가 프로젝트 맥락을 이해합니다:

```markdown
# 프로젝트 정보

## 개요
이 프로젝트는 한국어 뉴스 데이터를 수집·분석하는 데이터 저널리즘 프로젝트입니다.

## 기술 스택
- Python 3.12
- pandas, beautifulsoup4, matplotlib
- 한국어 형태소 분석: konlpy

## 코딩 규칙
- 한국어 주석 사용
- 함수마다 docstring 작성
- 변수명은 영어 snake_case
```

이후 Gemini CLI를 실행하면 이 맥락을 자동으로 반영합니다.

---

## 10. 자주 묻는 질문 (FAQ)

### Q1. WSL과 Windows는 파일을 어떻게 공유하나요?

```bash
# WSL에서 Windows 파일 접근
cd /mnt/c/Users/내이름/Desktop    # Windows 바탕화면

# Windows 탐색기에서 WSL 파일 접근
\\wsl$\Ubuntu\home\내리눅스이름    # 탐색기 주소창에 입력
```

### Q2. Gemini CLI 무료 사용량은 얼마인가요?

Google 로그인 방식:
- **분당 60회** 요청
- **일일 1,000회** 모델 요청
- 완전 무료, 신용카드 불필요

### Q3. pip install할 때 permission 에러가 나요

```bash
# 가상환경 사용 (권장)
python -m venv myenv
source myenv/bin/activate
pip install pandas    # 가상환경 안에서는 에러 없음
```

### Q4. `gemini` 명령이 안 됩니다

```bash
# npm 전역 경로 확인
npm list -g @google/gemini-cli

# 재설치
npm install -g @google/gemini-cli

# 또는 npx로 바로 실행
npx @google/gemini-cli
```

### Q5. WSL을 종료하려면?

```bash
# Ubuntu 터미널에서 로그아웃
exit

# 또는 PowerShell에서 WSL 완전 종료
wsl --shutdown
```

### Q6. Gemini CLI에서 인터넷 검색도 되나요?

네! Gemini CLI는 웹 검색 및 URL 접근 기능을 지원합니다:
```bash
> 오늘 한국 뉴스 헤드라인을 검색해줘
> https://example.com 이 페이지 내용을 요약해줘
```

### Q7. Windows에서 직접 Gemini CLI를 설치할 수는 없나요?

가능합니다. Windows에 Node.js를 직접 설치한 뒤 `npm install -g @google/gemini-cli`를 실행하면 됩니다. 하지만 **WSL 환경을 추천하는 이유**는:
- 리눅스 기반 개발 도구와의 호환성이 좋음
- 실무 서버 환경(리눅스)과 동일한 경험
- Python, Node.js 버전 관리가 더 쉬움

---

## 11. 유용한 명령어 치트시트

### 리눅스(Ubuntu) 기본 명령어

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
| `clear` | 화면 지우기 | `clear` |
| `sudo` | 관리자 권한 실행 | `sudo apt install ...` |

### Python 관련

| 명령어 | 설명 |
|--------|------|
| `python --version` | Python 버전 확인 |
| `pip install 패키지명` | 패키지 설치 |
| `pip list` | 설치된 패키지 목록 |
| `python 파일.py` | Python 파일 실행 |
| `python -m venv 환경명` | 가상환경 생성 |
| `source 환경명/bin/activate` | 가상환경 활성화 |
| `deactivate` | 가상환경 비활성화 |

### Node.js 관련

| 명령어 | 설명 |
|--------|------|
| `node --version` | Node.js 버전 확인 |
| `npm --version` | npm 버전 확인 |
| `npm install -g 패키지명` | 글로벌 패키지 설치 |
| `nvm ls` | 설치된 Node.js 버전 목록 |
| `nvm use 버전` | 특정 버전 사용 |

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

---

## 부록: 전체 설치 한 번에 따라하기 (요약)

시간이 없는 분을 위해, 위 과정을 한 번에 정리합니다:

### A. Windows에서 (PowerShell 관리자)

```powershell
# 1. WSL 설치
wsl --install

# 2. 재시작 후 Ubuntu 사용자 이름/비밀번호 설정
```

### B. VSCode 설치

1. https://code.visualstudio.com 에서 다운로드·설치
2. 확장에서 "WSL" 설치

### C. Ubuntu 터미널에서

```bash
# 3. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 4. Python 설치
sudo apt install python3 python3-pip python3-venv -y
echo "alias python=python3" >> ~/.bashrc
echo "alias pip=pip3" >> ~/.bashrc

# 5. Node.js 설치 (nvm 경유)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install --lts

# 6. Gemini CLI 설치
npm install -g @google/gemini-cli

# 7. 실행!
gemini
```

### D. Gemini CLI 첫 실행

1. 테마 선택
2. "Login with Google" 선택
3. 브라우저에서 로그인
4. 코딩 시작! 🎉

---

> **문의**: 이종혁 교수 (경희대 미디어학과)  
> **참고 자료**:
> - WSL 공식 문서: https://learn.microsoft.com/ko-kr/windows/wsl/
> - Gemini CLI 공식: https://geminicli.com/docs/
> - Gemini CLI GitHub: https://github.com/google-gemini/gemini-cli
> - Google AI Studio: https://aistudio.google.com
