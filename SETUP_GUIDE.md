# 🚀 GitHub PR 자동화 및 Claude 코드 리뷰 시스템 설정 가이드

이 문서는 GitHub Actions CI/CD 파이프라인과 Claude 자동 코드 리뷰 시스템을 설정하는 방법을 안내합니다.

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [사전 준비](#사전-준비)
3. [단계별 설정](#단계별-설정)
4. [검증 및 테스트](#검증-및-테스트)
5. [트러블슈팅](#트러블슈팅)

## 시스템 개요

### 아키텍처

```
개발자 → feature/* 브랜치 push
    ↓
수동 PR 생성
    ↓
GitHub Actions 자동 실행:
  • CI/CD (테스트, 린트, 타입 체크) [BLOCKING]
  • Claude 코드 리뷰              [ADVISORY]
    ↓
PR에 리뷰 코멘트 자동 게시
    ↓
개발자 수정 → Push → 재검증
    ↓
사람 리뷰어 최종 승인
    ↓
Main 브랜치로 Squash Merge
```

### 주요 기능

- ✅ **CI/CD Pipeline**: 자동 테스트, 린트, 타입 체크
- ✅ **Claude 코드 리뷰**: AI 기반 보안/품질/성능 분석
- ✅ **PR 템플릿**: 일관된 PR 작성
- ✅ **Branch Protection**: 품질 보증
- ✅ **한국어 지원**: 커밋 메시지, 리뷰 모두 한국어

## 사전 준비

### 1. 필수 계정 및 권한

- [ ] GitHub 저장소 관리자 권한
- [ ] Anthropic API 키 (Claude 리뷰용)
  - [Anthropic Console](https://console.anthropic.com)에서 생성
  - 최소 티어: Pay-as-you-go

### 2. 로컬 환경

- [ ] Git 설치
- [ ] GitHub CLI 설치 (선택사항)
  - Windows: `winget install GitHub.cli`
  - Mac: `brew install gh`
  - Linux: [공식 문서](https://github.com/cli/cli/blob/trunk/docs/install_linux.md)

## 단계별 설정

### Step 1: GitHub Secrets 설정 ⭐ 필수

1. GitHub 저장소로 이동
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** 클릭
4. Secret 추가:

```
Name: ANTHROPIC_API_KEY
Value: sk-ant-api03-xxxxxxxxxxxxx
```

**검증:**
- Secrets 목록에 `ANTHROPIC_API_KEY`가 보이는지 확인

### Step 2: Branch Protection 설정 ⭐ 필수

1. **Settings** → **Branches**
2. **Add branch protection rule**
3. Branch name pattern: `main`
4. 다음 옵션 활성화:

```
✅ Require a pull request before merging
  ✅ Require approvals (최소 1명)
  ✅ Dismiss stale pull request approvals when new commits are pushed

✅ Require status checks to pass before merging
  ✅ Require branches to be up to date before merging
  Status checks: (PR 생성 후 아래 항목들이 나타남)
    - backend-validation
    - frontend-validation

✅ Require conversation resolution before merging

✅ Do not allow bypassing the above settings (관리자도 규칙 준수)

Merge 방식:
✅ Allow squash merging (권장)
❌ Allow merge commits
❌ Allow rebase merging
```

5. **Create** 버튼 클릭

**검증:**
- Branch protection rules에 `main` 규칙이 생성되었는지 확인

### Step 3: Actions Permissions 설정 ⭐ 필수

1. **Settings** → **Actions** → **General**
2. **Actions permissions** 섹션:

```
✅ Allow all actions and reusable workflows
```

3. **Workflow permissions** 섹션:

```
✅ Read and write permissions
✅ Allow GitHub Actions to create and approve pull requests
```

4. **Save** 버튼 클릭

**검증:**
- Actions 탭에서 워크플로우가 활성화되었는지 확인

### Step 4: GitHub CLI 인증 (로컬 환경)

보안 강화를 위해 GitHub CLI 사용을 권장합니다.

```bash
# GitHub CLI 설치 확인
gh --version

# GitHub 인증 (브라우저 팝업)
gh auth login

# 인증 상태 확인
gh auth status
```

**출력 예시:**
```
✓ Logged in to github.com as your-username
✓ Git operations for github.com configured to use https protocol.
✓ Token: gho_************************************
```

**검증:**
- `gh pr list` 명령어가 정상 작동하는지 확인

## 검증 및 테스트

### 테스트 시나리오 1: CI/CD 파이프라인 검증

#### 1.1 성공 케이스

```bash
# 테스트 브랜치 생성
git checkout -b test/ci-pipeline

# 정상 코드 커밋
echo "# Test" >> README.md
git add README.md
git commit -m "test: CI/CD 파이프라인 검증"

# Push
git push -u origin test/ci-pipeline

# PR 생성 (GitHub UI 또는 gh CLI 사용)
gh pr create --title "test: CI/CD 검증" --body "CI/CD 파이프라인 테스트"
```

**예상 결과:**
- ✅ GitHub Actions에서 `backend-validation` 성공
- ✅ GitHub Actions에서 `frontend-validation` 성공
- ✅ GitHub Actions에서 `security-scan` 실행 (경고는 허용)
- ✅ PR 상태가 "All checks have passed"

#### 1.2 실패 케이스 (의도적)

```bash
# 테스트 브랜치 생성
git checkout -b test/ci-fail

# Backend: 린트 오류 추가
cat >> backend/app/test_error.py << EOF
def bad_function(  ):  # 불필요한 공백
    x=1+2  # 공백 없음
    return x
EOF

git add backend/app/test_error.py
git commit -m "test: CI 실패 테스트"
git push -u origin test/ci-fail

# PR 생성
gh pr create --title "test: CI 실패 검증" --body "CI 실패 동작 테스트"
```

**예상 결과:**
- ❌ `backend-validation` 실패 (black, flake8 오류)
- 🚫 PR 병합 차단 (Branch protection 규칙)
- ℹ️ 실패 원인이 Actions 로그에 명확히 표시

**정리:**
```bash
git checkout main
git branch -D test/ci-fail
git push origin --delete test/ci-fail
rm backend/app/test_error.py  # 실제로 파일이 있다면
```

### 테스트 시나리오 2: Claude 코드 리뷰 검증

#### 2.1 보안 취약점 테스트

```bash
# 테스트 브랜치 생성
git checkout -b test/security-review

# 의도적 보안 취약점 추가
mkdir -p backend/app/test
cat > backend/app/test/vulnerable_code.py << 'EOF'
from fastapi import APIRouter

router = APIRouter()

@router.get("/user/{user_id}")
async def get_user(user_id: str):
    # SQL Injection 취약점
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return {"query": query}

def store_password(password: str):
    # 평문 비밀번호 저장
    user_password = password
    return user_password
EOF

git add backend/app/test/vulnerable_code.py
git commit -m "test: 보안 취약점 리뷰 테스트"
git push -u origin test/security-review

# PR 생성
gh pr create --title "test: 보안 리뷰 검증" --body "Claude가 보안 취약점을 탐지하는지 테스트"
```

**예상 Claude 리뷰:**

```markdown
### 🔴 보안: SQL Injection 취약점

**파일:** `backend/app/test/vulnerable_code.py:8`

**문제:**
사용자 입력(`user_id`)이 f-string으로 직접 SQL 쿼리에 삽입되어
SQL Injection 공격에 취약합니다.

**영향:**
- 공격자가 임의의 SQL을 실행할 수 있음
- 데이터베이스 전체가 노출될 위험

**권장사항:**
```python
# ✅ 개선 코드 (안전)
from sqlalchemy import text
query = text("SELECT * FROM users WHERE id = :user_id")
result = await db.execute(query, {"user_id": user_id})
```

**우선순위:** Critical
```

**검증 포인트:**
- ✅ PR에 Claude 리뷰 코멘트가 자동으로 게시됨
- ✅ 🔴 보안 취약점 탐지 (SQL Injection)
- ✅ 🔴 평문 비밀번호 저장 경고
- ✅ 구체적인 개선 코드 제시
- ✅ 한국어 피드백

**정리:**
```bash
git checkout main
git branch -D test/security-review
git push origin --delete test/security-review
rm -rf backend/app/test/
```

#### 2.2 Claude 리뷰 실패 테스트

```bash
# Anthropic API 키를 잠시 무효화 (Settings → Secrets에서 삭제)
# 또는 테스트용 무효 키 입력

# PR 생성 시 Claude 리뷰가 실패하는지 확인
```

**예상 결과:**
- ⚠️ PR에 "Claude 코드 리뷰 실패" 코멘트 자동 게시
- ℹ️ 해결 방법 안내 (API 키 확인, 재시도 등)
- ✅ CI/CD는 정상 작동 (Claude 리뷰와 독립적)

### 테스트 시나리오 3: PR 템플릿 검증

```bash
# GitHub UI에서 새 PR 생성
# 또는
gh pr create
```

**예상 결과:**
- ✅ PR 본문에 템플릿이 자동으로 로드됨
- ✅ 체크리스트 항목들이 표시됨
- ✅ 한국어 텍스트가 올바르게 표시됨

### 테스트 시나리오 4: 통합 워크플로우

완전한 개발 워크플로우 테스트:

```bash
# 1. Feature 브랜치 생성
git checkout -b feature/test-workflow

# 2. 실제 기능 구현 (예: 간단한 API 추가)
cat > backend/app/test/health.py << 'EOF'
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}
EOF

git add backend/app/test/health.py
git commit -m "feat(api): 헬스 체크 엔드포인트 추가"

# 3. 로컬 검증
cd backend
./scripts/lint.sh --check  # 또는 --fix
./scripts/test.sh --cov
cd ..

cd frontend
./scripts/check.sh
cd ..

# 4. Push
git push -u origin feature/test-workflow

# 5. PR 생성
gh pr create \
  --title "feat(api): 헬스 체크 엔드포인트 추가" \
  --body "헬스 체크 API 추가 및 테스트"

# 6. Actions 탭에서 워크플로우 확인
# 7. PR에서 Claude 리뷰 확인
# 8. 필요시 수정 후 다시 push
# 9. 팀원 승인 요청
# 10. Squash merge
```

**검증 포인트:**
- ✅ 로컬 검사 통과
- ✅ CI/CD 파이프라인 통과
- ✅ Claude 리뷰 생성됨
- ✅ 사람 리뷰어 승인 가능
- ✅ Squash merge 성공
- ✅ 브랜치 자동 삭제

## 트러블슈팅

### 문제 1: Claude 리뷰가 실행되지 않음

**증상:**
- PR 생성 후 Claude 리뷰 코멘트가 게시되지 않음
- Actions 탭에서 "Claude Code Review" 워크플로우가 보이지 않음

**원인 및 해결:**

1. **Draft PR인 경우**
   ```
   Draft PR은 Claude 리뷰에서 자동으로 제외됩니다.
   → PR을 "Ready for review"로 변경
   ```

2. **ANTHROPIC_API_KEY가 설정되지 않음**
   ```bash
   # Settings → Secrets에서 확인
   # 없으면 추가
   ```

3. **Actions 권한 부족**
   ```
   Settings → Actions → General
   → "Read and write permissions" 활성화
   ```

4. **API 요청 한도 초과**
   ```
   Anthropic Console에서 사용량 확인
   → 요금제 업그레이드 또는 대기
   ```

### 문제 2: CI/CD가 계속 실패함

**증상:**
- `backend-validation` 또는 `frontend-validation` 실패
- PR 병합 차단

**해결:**

```bash
# 로컬에서 동일한 검사 실행
cd backend
./scripts/lint.sh --check  # 문제 확인
./scripts/lint.sh --fix    # 자동 수정
./scripts/test.sh          # 테스트 실행
cd ..

cd frontend
./scripts/check.sh         # 문제 확인
./scripts/check.sh --fix   # 자동 수정
cd ..

# 수정 후 재커밋
git add .
git commit -m "fix: CI 오류 수정"
git push
```

### 문제 3: Branch Protection이 작동하지 않음

**증상:**
- CI가 실패해도 PR 병합 가능
- 리뷰 없이 병합 가능

**해결:**

1. **Status checks가 required로 설정되지 않음**
   ```
   Settings → Branches → main
   → "Require status checks to pass before merging" 활성화
   → backend-validation, frontend-validation 체크
   ```

2. **관리자 bypass 허용됨**
   ```
   → "Do not allow bypassing the above settings" 활성화
   ```

3. **Status checks가 아직 실행되지 않음**
   ```
   → 첫 PR 생성 후 status checks가 나타남
   → 두 번째 PR부터 required로 설정 가능
   ```

### 문제 4: GitHub CLI 인증 실패

**증상:**
```bash
$ gh pr list
gh: command not found
# 또는
gh auth status
You are not logged into any GitHub hosts
```

**해결:**

```bash
# 1. GitHub CLI 설치 확인
gh --version

# 없으면 설치 (Windows)
winget install GitHub.cli

# 2. 인증
gh auth login

# 3. 인증 방법 선택
- GitHub.com
- HTTPS
- Login with a web browser

# 4. 인증 코드 입력 및 브라우저 승인

# 5. 확인
gh auth status
```

### 문제 5: Actions가 실행되지 않음

**증상:**
- PR 생성 후 Actions 탭에 워크플로우가 나타나지 않음
- "No workflow runs found" 메시지

**원인 및 해결:**

1. **워크플로우 파일 위치 오류**
   ```bash
   # 올바른 위치 확인
   ls -la .github/workflows/
   # 파일이 있어야 함:
   # - ci.yml
   # - claude-review.yml
   ```

2. **YAML 문법 오류**
   ```bash
   # 온라인 YAML validator 사용
   # 또는 yamllint 설치
   pip install yamllint
   yamllint .github/workflows/*.yml
   ```

3. **Actions가 비활성화됨**
   ```
   Settings → Actions → General
   → "Allow all actions and reusable workflows" 활성화
   ```

## 다음 단계

### 선택적 확장 기능

시스템이 안정화된 후 고려할 사항:

1. **Pre-commit Hooks**
   - 로컬에서 커밋 전 자동 검증
   - 개발자 경험 개선

2. **Codecov 통합**
   - 코드 커버리지 추적
   - PR에 커버리지 리포트 자동 게시

3. **Dependabot**
   - 의존성 자동 업데이트
   - 보안 패치 자동화

4. **성능 모니터링**
   - Lighthouse CI
   - Bundle size tracking

## 도움말 및 리소스

- **GitHub Actions 문서**: https://docs.github.com/actions
- **Anthropic API 문서**: https://docs.anthropic.com
- **Claude Code Agent 가이드**: `.claude/agents/pr-reviewer.md`
- **프로젝트 README**: `README.md`

## 문의

설정 중 문제가 발생하면:
1. 이 가이드의 트러블슈팅 섹션 확인
2. Actions 탭에서 워크플로우 로그 확인
3. 팀원에게 문의

---

**설정 완료 체크리스트:**

- [ ] ✅ GitHub Secrets 설정 (ANTHROPIC_API_KEY)
- [ ] ✅ Branch Protection 설정 (main 브랜치)
- [ ] ✅ Actions Permissions 설정
- [ ] ✅ GitHub CLI 인증 (로컬)
- [ ] ✅ 테스트 PR로 CI/CD 검증
- [ ] ✅ 테스트 PR로 Claude 리뷰 검증
- [ ] ✅ PR 템플릿 확인
- [ ] ✅ 통합 워크플로우 테스트

**모든 체크가 완료되면 시스템이 정상 작동합니다!** 🎉
