# 🚀 개발자 빠른 참조 가이드

일상적인 개발 작업을 위한 명령어 및 워크플로우 빠른 참조

## 📚 목차

- [일일 개발 워크플로우](#일일-개발-워크플로우)
- [로컬 검증 명령어](#로컬-검증-명령어)
- [PR 체크리스트](#pr-체크리스트)
- [Git 컨벤션](#git-컨벤션)
- [트러블슈팅 빠른 해결](#트러블슈팅-빠른-해결)

## 일일 개발 워크플로우

### 1. 새 기능 시작

```bash
# Main 브랜치 최신화
git checkout main
git pull origin main

# Feature 브랜치 생성
git checkout -b feature/<kebab-case-name>

# 예시
git checkout -b feature/add-query-optimizer
git checkout -b feature/fix-schema-validation
```

### 2. 개발 중

```bash
# 자주 커밋하기 (한국어 Conventional Commits)
git add <파일들>
git commit -m "feat(scope): 기능 설명"

# 예시
git commit -m "feat(api): 쿼리 최적화 엔드포인트 추가"
git commit -m "fix(frontend): 차트 렌더링 오류 수정"
git commit -m "refactor(db): 리포지토리 계층 구조 개선"
```

### 3. PR 생성 전 로컬 검증

```bash
# Backend 검증
cd backend
./scripts/lint.sh --check    # 검사만
./scripts/lint.sh --fix      # 자동 수정
./scripts/test.sh            # 테스트
./scripts/test.sh --cov      # 커버리지 포함
cd ..

# Frontend 검증
cd frontend
./scripts/check.sh           # 검사
./scripts/check.sh --fix     # 자동 수정
npm test                     # 테스트
cd ..
```

### 4. PR 생성

```bash
# 브랜치 Push
git push -u origin feature/<branch-name>

# GitHub UI에서 PR 생성
# 또는 GitHub CLI 사용
gh pr create \
  --title "feat(scope): 기능 설명" \
  --body "상세 설명"

# Draft PR로 생성 (Claude 리뷰 제외)
gh pr create --draft

# Ready로 전환 시
gh pr ready
```

### 5. 리뷰 및 수정

```bash
# CI/CD 결과 확인
gh pr checks

# Claude 리뷰 확인 (PR 웹 페이지)
# 필요시 수정

git add .
git commit -m "fix(scope): 리뷰 피드백 반영"
git push  # 자동으로 재검증됨
```

### 6. 병합 후 정리

```bash
# 로컬 main 업데이트
git checkout main
git pull origin main

# 작업 브랜치 삭제
git branch -d feature/<branch-name>
```

## 로컬 검증 명령어

### Backend (Python)

```bash
cd backend

# 빠른 검사 (CI와 동일)
./scripts/lint.sh --check

# 자동 수정
./scripts/lint.sh --fix

# 개별 도구 실행
black .                     # 포맷팅
isort .                     # Import 정렬
flake8 app/                 # 린트
mypy app/                   # 타입 체크

# 테스트
pytest                      # 모든 테스트
pytest tests/test_api.py    # 특정 테스트
pytest -k "optimizer"       # 패턴 매칭
pytest -v                   # Verbose
pytest --cov=app            # 커버리지

# 서버 실행
uvicorn app.main:app --reload
```

### Frontend (TypeScript/React)

```bash
cd frontend

# 빠른 검사
./scripts/check.sh

# 자동 수정
./scripts/check.sh --fix

# 개별 도구 실행
npm run lint                # ESLint
npm run lint -- --fix       # ESLint 자동 수정
npm run type-check          # TypeScript
npm run build               # 빌드

# 테스트
npm test                    # 테스트 실행
npm test -- --coverage      # 커버리지

# 개발 서버
npm run dev
```

### 전체 프로젝트 검증

```bash
# 한 번에 모든 검사 실행
cd backend && ./scripts/lint.sh --check && ./scripts/test.sh && cd ..
cd frontend && ./scripts/check.sh && cd ..

# 또는 병렬 실행 (Linux/Mac)
(cd backend && ./scripts/lint.sh --check) & \
(cd frontend && ./scripts/check.sh) & \
wait
```

## PR 체크리스트

PR 생성 전 반드시 확인:

### 코드 품질
- [ ] 로컬에서 모든 검사 통과
  - [ ] Backend: `./scripts/lint.sh --check`
  - [ ] Frontend: `./scripts/check.sh`
- [ ] 새 코드에 대한 테스트 추가
- [ ] 기존 테스트 영향 없음 확인
- [ ] 불필요한 주석/console.log 제거

### 커밋 메시지
- [ ] 한국어 Conventional Commits 형식
- [ ] 의미 있는 커밋 메시지
- [ ] Co-Authored-By 포함 (Claude 사용 시)

### PR 설명
- [ ] 변경사항 요약 작성
- [ ] 변경 유형 체크
- [ ] 관련 이슈 링크
- [ ] 스크린샷 첨부 (UI 변경 시)

### 주의사항
- [ ] Breaking changes 명시
- [ ] 환경 변수 변경사항 기록
- [ ] DB 마이그레이션 필요 여부

## Git 컨벤션

### 브랜치 네이밍

```
feature/<kebab-case>   # 새 기능
fix/<kebab-case>       # 버그 수정
refactor/<kebab-case>  # 리팩토링
docs/<kebab-case>      # 문서
test/<kebab-case>      # 테스트
chore/<kebab-case>     # 기타

# 예시
feature/add-query-cache
fix/schema-validation-error
refactor/clean-architecture
```

### 커밋 메시지 형식

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `refactor`: 리팩토링
- `docs`: 문서 변경
- `test`: 테스트 추가/수정
- `style`: 코드 포맷팅 (로직 변경 없음)
- `perf`: 성능 개선
- `chore`: 빌드/설정 변경

**Scope:**
- `api`: Backend API
- `db`: 데이터베이스
- `frontend`: Frontend
- `ui`: UI 컴포넌트
- `auth`: 인증/인가
- `test`: 테스트

**예시:**
```bash
git commit -m "feat(api): Claude AI 모델 통합"
git commit -m "fix(frontend): 차트 데이터 로딩 오류 수정"
git commit -m "refactor(db): 리포지토리 패턴 적용"
git commit -m "docs(readme): 설치 가이드 추가"
git commit -m "test(api): 쿼리 최적화 테스트 추가"
```

### PR 제목

커밋 메시지와 동일한 형식:

```
feat(api): 쿼리 최적화 AI 분석 기능 추가
fix(frontend): EXPLAIN 결과 파싱 오류 수정
refactor(backend): Clean Architecture 적용
```

## 트러블슈팅 빠른 해결

### CI/CD 실패

**Black 포맷 오류:**
```bash
cd backend
black .
git add .
git commit -m "style: black 포맷 적용"
git push
```

**isort 오류:**
```bash
cd backend
isort .
git add .
git commit -m "style: import 정렬"
git push
```

**Flake8 린트 오류:**
```bash
cd backend
flake8 app/
# 오류 수정 후
git add .
git commit -m "fix: 린트 오류 수정"
git push
```

**ESLint 오류:**
```bash
cd frontend
npm run lint -- --fix
git add .
git commit -m "fix: ESLint 오류 수정"
git push
```

**TypeScript 타입 오류:**
```bash
cd frontend
npm run type-check
# 오류 수정 후
git add .
git commit -m "fix: 타입 오류 수정"
git push
```

**테스트 실패:**
```bash
# Backend
cd backend
pytest -v  # Verbose로 실패 원인 확인
# 테스트 수정 또는 코드 수정

# Frontend
cd frontend
npm test
# 테스트 수정 또는 코드 수정
```

### Claude 리뷰 관련

**Claude가 오탐(False Positive) 지적:**
- ℹ️ Advisory 모드이므로 무시 가능
- 사람 리뷰어에게 설명
- 필요시 코드 주석으로 의도 명시

**Claude 리뷰가 실행 안 됨:**
```bash
# Draft PR인지 확인
gh pr ready  # Ready로 전환

# 또는 PR을 닫았다가 다시 열기
gh pr close <PR번호>
gh pr reopen <PR번호>
```

**Claude 리뷰가 너무 길어짐:**
- Diff가 5000줄 이상이면 요약만 표시됨
- PR을 작게 나누는 것을 권장

### Git 관련

**잘못된 브랜치에서 작업:**
```bash
# 변경사항 임시 저장
git stash

# 올바른 브랜치로 이동
git checkout -b feature/correct-branch

# 변경사항 복원
git stash pop
```

**커밋 메시지 수정:**
```bash
# 마지막 커밋 메시지 수정
git commit --amend -m "올바른 메시지"

# Push된 경우 (주의: force push)
git push --force-with-lease
```

**PR에 불필요한 커밋 포함:**
```bash
# Interactive rebase로 커밋 정리
git rebase -i HEAD~<커밋 개수>

# Squash 또는 drop으로 정리
# 저장 후 force push
git push --force-with-lease
```

## 유용한 Alias

`.gitconfig` 또는 `.bash_profile`에 추가:

```bash
# Git aliases
alias gs='git status'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gco='git checkout'
alias gb='git branch'
alias gd='git diff'

# 프로젝트 특화
alias be-lint='cd backend && ./scripts/lint.sh --check && cd ..'
alias be-fix='cd backend && ./scripts/lint.sh --fix && cd ..'
alias be-test='cd backend && ./scripts/test.sh && cd ..'

alias fe-check='cd frontend && ./scripts/check.sh && cd ..'
alias fe-fix='cd frontend && ./scripts/check.sh --fix && cd ..'

alias all-check='be-lint && fe-check'
alias all-fix='be-fix && fe-fix'
```

## 도움말

### 명령어 도움말

```bash
# Scripts 도움말
./backend/scripts/lint.sh --help
./backend/scripts/test.sh --help
./frontend/scripts/check.sh --help

# GitHub CLI 도움말
gh pr --help
gh pr create --help
gh pr checks --help
```

### 문서 링크

- **전체 README**: `README.md`
- **설정 가이드**: `SETUP_GUIDE.md`
- **PR 리뷰 기준**: `.claude/agents/pr-reviewer.md`

### 문의

- 워크플로우 질문: 팀 리드에게 문의
- CI/CD 오류: GitHub Actions 로그 확인
- Claude 리뷰 피드백: 팀 시니어 개발자와 상의

---

**개발 즐거운 하루 되세요! 🚀**
