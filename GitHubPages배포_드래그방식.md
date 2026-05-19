# GitHub Pages 배포 (드래그 방식 간략판)

## 1. GitHub 가입·로그인

**github.com** → 우측 상단 **Sign up** → 이메일·비밀번호·사용자명 입력 → 이메일 인증.

사용자명은 영문으로. 나중에 사이트 주소에 들어갑니다.

## 2. 저장소 만들기

우측 상단 **+** → **New repository**

- **Repository name**: 영문으로 (예: `news-project`)
- **Public** 선택
- **Add a README file** ✅ 체크
- **Create repository** 클릭

## 3. 파일 드래그 업로드

저장소 화면에서 **Add file** → **Upload files**

`export/` 폴더를 열고 **그 안의 내용물**을 드래그:

```
index.html
index.css
index.js
assets/  (폴더 통째로)
```

업로드 끝나면 페이지 하단 초록 버튼 **Commit changes** 한 번 클릭. (이게 "저장" 역할)

## 4. Pages 켜기

저장소 상단 **Settings** → 좌측 **Pages**

- **Source**: Deploy from a branch
- **Branch**: `main` / `(root)`
- **Save**

1~5분 대기. 상단에 주소가 표시됩니다.

```
https://사용자명.github.io/저장소명/
```

## 5. 접속 확인

위 주소 클릭. 페이지가 뜨면 끝.

---

## 안 보일 때

| 증상 | 해결 |
|---|---|
| 404 | 5분 더 대기 후 새로고침 |
| 빈 화면 | 파일명이 정확히 `index.html`인지 확인 |
| 사진/그래프 안 보임 | F12 → Console 탭에서 에러 확인 |
| 바뀐 게 반영 안 됨 | Ctrl+Shift+R 강제 새로고침 |

## 파일 수정 후 다시 올릴 때

**Add file → Upload files**로 같은 이름 파일 다시 드래그하면 자동 덮어쓰기. **Commit changes** 한 번 더 누르면 끝.