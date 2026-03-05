# WSL + VSCode + Gemini CLI 설치 가이드

> **대상**: Windows 사용자, 개발 환경이 전혀 없는 초보자  
> **목표**: WSL 설치 → VSCode 연동 → Gemini CLI 실행  
> **소요 시간**: 약 30분

---

## 전체 순서

```
WSL2 설치 → VSCode 설치 → Python/Node.js 설치 → Gemini CLI 실행
```

---

## STEP 1: WSL2 + Ubuntu 24.04 LTS 설치

WSL은 Windows 안에서 리눅스를 쓸 수 있게 해주는 도구입니다.

> **Ubuntu 버전 선택**: **Ubuntu 24.04 LTS (Noble Numbat)** 를 설치합니다.  
> LTS(Long Term Support)는 5년간 보안 업데이트를 보장하는 안정 버전입니다.  
> `wsl --install`만 입력하면 최신 버전이 자동 설치되지만, 아래처럼 **버전을 명시**하는 것이 더 안전합니다.

**① PowerShell을 관리자 권한으로 실행**  
시작 버튼 우클릭 → "터미널(관리자)" 클릭

**② 명령어 입력 (Ubuntu 24.04 버전 지정)**
```
wsl --install -d Ubuntu-24.04
```
→ Ubuntu 24.04 LTS 설치됨

**③ 컴퓨터 재시작**

**④ Ubuntu 초기 설정**

재시작 후 검은 창(Ubuntu 터미널)이 자동으로 열립니다.  
자동으로 열리지 않으면 아래 방법 중 하나로 직접 실행하세요:

- **방법 1**: 시작 메뉴(윈도우 키) → 검색창에 `Ubuntu` 입력 → Ubuntu 앱 클릭
- **방법 2**: 시작 메뉴 → 앱 목록에서 `Ubuntu 24.04 LTS` 찾아서 클릭
- **방법 3**: PowerShell에서 `wsl` 입력 후 Enter


아래처럼 사용자 이름과 비밀번호를 설정하라고 요청합니다:

```
Enter new UNIX username: hong       ← 영문 소문자로 원하는 이름 입력 (예: hong)
New password:                       ← 비밀번호 입력 (입력해도 화면에 아무것도 안 나옴)
Retype new password:                ← 비밀번호 한 번 더 입력
```

> ⚠️ 비밀번호를 입력할 때 화면에 아무것도 표시되지 않는 게 **정상**입니다.  
> 리눅스의 보안 기능으로, 그냥 입력하고 Enter를 누르면 됩니다.

설정이 끝나면 아래처럼 프롬프트가 나타납니다. 이제 명령어를 입력할 수 있는 상태입니다:
```
hong@DESKTOP:~$
```
> 이 `$` 기호가 "입력 대기 중"을 뜻합니다. 여기에 명령어를 타이핑합니다.

**⑤ 설치된 버전 확인**

아래 명령어를 입력하고 Enter를 누르세요:

```bash
lsb_release -a
```

> `bash`는 터미널에서 명령어를 실행하는 프로그램 이름입니다.  
> 코드 블록에 `bash`라고 표시된 것은 "Ubuntu 터미널(검은 창)에서 입력하세요"라는 뜻입니다.

아래처럼 출력되면 성공입니다:
```
Description:    Ubuntu 24.04.x LTS
Release:        24.04
Codename:       noble
```

**⑥ Ubuntu 업데이트**
```bash
sudo apt update && sudo apt upgrade -y
```

| 오류 | 해결 |
|------|------|
| `0x800701bc` | `wsl --update` 후 재시작 |
| 가상화 오류 | BIOS에서 Virtualization 활성화 |
| Ubuntu 버전 목록 확인 | `wsl --list --online` 실행 |

---

## STEP 2: VSCode 설치 및 WSL 연동

**① VSCode 설치**  
[https://code.visualstudio.com](https://code.visualstudio.com) → Download → 설치  
설치 시 **"PATH에 추가"** 반드시 체크

**② WSL 확장 설치**  
VSCode 실행 → `Ctrl+Shift+X` → "WSL" 검색 → Install

**③ WSL 연결 확인**  
Ubuntu 터미널에서:
```bash
code .
```
VSCode 좌측 하단에 `WSL: Ubuntu` 표시되면 성공

---

## STEP 3: Python 설치

```bash
# 설치
sudo apt install python3 python3-pip python3-venv -y

# python3 대신 python으로 쓰기
echo "alias python=python3" >> ~/.bashrc
echo "alias pip=pip3" >> ~/.bashrc
source ~/.bashrc

# 확인
python --version
```

---

## STEP 4: Node.js 설치

Gemini CLI 실행에 **Node.js 20 이상** 필요합니다.

```bash
# nvm 설치
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc

# Node.js 설치
nvm install --lts

# 확인
node --version   # v22.x.x
npm --version
```

> `nvm: command not found` 오류 시:  
> `source ~/.nvm/nvm.sh` 후 재시도

---

## STEP 5: Gemini CLI 설치 및 실행

**① 설치**
```bash
npm install -g @google/gemini-cli
```

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
echo 'export GEMINI_API_KEY="발급받은_키_붙여넣기"' >> ~/.bashrc
source ~/.bashrc

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
# PowerShell(관리자)에서
wsl --install -d Ubuntu-24.04
# → 재시작 후 Ubuntu 24.04 LTS 계정 설정

# Ubuntu 터미널에서
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv -y
echo "alias python=python3" >> ~/.bashrc && source ~/.bashrc
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install --lts
npm install -g @google/gemini-cli

# 실행
gemini
```

---

## 자주 묻는 질문

**Q. Windows 파일을 WSL에서 열려면?**
```bash
cd /mnt/c/Users/내이름/Desktop
```

**Q. WSL에서 Windows 탐색기로 파일 보려면?**  
탐색기 주소창에 `\\wsl$\Ubuntu` 입력

**Q. pip install 시 permission 오류가 나면?**
```bash
python -m venv myenv
source myenv/bin/activate
pip install 패키지명
```

**Q. `gemini` 명령이 안 되면?**
```bash
npx @google/gemini-cli   # 이걸로 대신 실행
```

---

> 참고: [WSL 공식 문서](https://learn.microsoft.com/ko-kr/windows/wsl/) · [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
