# PostgreSQL Optimizer Dashboard

PostgreSQL 성능 최적화를 위한 AI 기반 대시보드 시스템

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [시작하기](#시작하기)
- [개발 워크플로우](#개발-워크플로우)
- [프로젝트 구조](#프로젝트-구조)
- [배포](#배포)

## 개요

PostgreSQL 데이터베이스의 성능을 분석하고 최적화하는 AI 기반 대시보드입니다. 쿼리 분석, 스키마 검증, 헬스 모니터링 기능을 제공하며, Claude AI를 활용한 자동 쿼리 최적화 기능을 포함합니다.

## 주요 기능

### 🔍 쿼리 분석
- **EXPLAIN 분석**: PostgreSQL EXPLAIN 결과 시각화
- **직접 입력 분석**: EXPLAIN JSON을 직접 입력하여 분석
- **AI 기반 최적화**: Claude AI를 활용한 쿼리 최적화 제안

### 🏗️ 스키마 검증
- 데이터베이스 스키마 구조 분석
- 인덱스 최적화 제안
- 관계 무결성 검증

### 📊 헬스 모니터링
- 데이터베이스 성능 메트릭
- 실시간 모니터링 대시보드
- 알림 및 경고 시스템

### 🤖 AI 통합
- Claude (Anthropic) 모델 통합
- Gemini (Google) 모델 지원
- GLM (智谱AI) 모델 지원
- 최적화 이력 추적

## 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Architecture**: Clean Architecture
  - Domain: 순수 비즈니스 로직
  - Application: Use cases
  - Infrastructure: DB, 외부 API
  - Presentation: 컨트롤러
- **Database**: PostgreSQL with SQLAlchemy (Async)
- **Migration**: Alembic
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **State Management**: React Query (TanStack Query)
- **Styling**: Tailwind CSS
- **Charts**: Recharts

### DevOps & CI/CD
- **CI/CD**: GitHub Actions
- **Code Quality**: Black, isort, Flake8, ESLint
- **Code Review**: Claude AI 자동 리뷰
- **Container**: Docker, Docker Compose

## 시작하기

### 사전 요구사항

- Python 3.11+
- Node.js 20+
- PostgreSQL 13+
- Docker & Docker Compose (선택사항)

### 설치 및 실행

#### 1. 저장소 클론

```bash
git clone https://github.com/your-org/postgresql-optimizer-dashboard.git
cd postgresql-optimizer-dashboard
```

#### 2. Backend 설정

```bash
cd backend

# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 데이터베이스 정보 및 API 키 입력

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

Backend API: http://localhost:8000
API 문서: http://localhost:8000/docs

#### 3. Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 API URL 입력

# 개발 서버 실행
npm run dev
```

Frontend: http://localhost:5173

#### 4. Docker로 실행 (선택사항)

```bash
docker-compose up -d
```

## 🔄 개발 워크플로우

### PR 생성

1. **Feature 브랜치 생성**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **개발 및 커밋** (한국어 Conventional Commits)
   ```bash
   git add .
   git commit -m "feat(scope): 기능 설명"
   ```

   **커밋 메시지 형식:**
   - `feat(scope)`: 새로운 기능
   - `fix(scope)`: 버그 수정
   - `refactor(scope)`: 리팩토링
   - `docs(scope)`: 문서 업데이트
   - `test(scope)`: 테스트 추가/수정
   - `chore(scope)`: 빌드/설정 변경

3. **PR 생성**
   - GitHub에서 수동으로 PR 생성
   - 또는 Claude Code에서 git-pr-creator 에이전트 사용
   - PR 템플릿이 자동으로 로드됨

### 자동화된 검증

PR 생성 시 자동으로 실행:

#### 1. CI/CD Pipeline (필수 통과)

**Backend 검증:**
- ✅ Black: 코드 포맷 체크
- ✅ isort: import 정렬 체크
- ✅ Flake8: 린트 검사
- ✅ MyPy: 타입 체크 (선택적)
- ✅ Pytest: 테스트 실행 및 커버리지

**Frontend 검증:**
- ✅ ESLint: 린트 검사
- ✅ TypeScript: 타입 체크
- ✅ Build: 빌드 테스트
- ✅ Tests: 프론트엔드 테스트

**보안 스캔 (권고):**
- ⚠️ Python 의존성 취약점 스캔
- ⚠️ Node.js 의존성 취약점 스캔
- ⚠️ Secret Scanning (Gitleaks)

#### 2. Claude 코드 리뷰 (권고)

**리뷰 우선순위:**
1. 🔴 **보안 취약점** (Critical)
   - SQL Injection, XSS, 인증/인가 우회
   - 민감 정보 노출, CSRF
2. 🟡 **코드 품질** (High)
   - SOLID 원칙, Clean Architecture
   - 중복 코드, 복잡도, 네이밍
3. 🟢 **성능 문제** (Medium)
   - N+1 query, 비효율적 알고리즘
   - 불필요한 렌더링
4. ℹ️ **테스트** (Low)
   - 테스트 누락, Edge case

**특징:**
- Advisory 모드: PR 병합 차단 안 함
- 한국어 피드백
- 구체적인 코드 예시 제공

### 리뷰 및 병합

1. **Claude 리뷰 확인 및 수정**
   - PR에 자동으로 게시된 Claude 리뷰 확인
   - Critical/High 이슈는 수정 권장

2. **팀원 리뷰 요청**
   - 최소 1명의 팀원 승인 필요
   - 모든 conversation 해결 필요

3. **CI/CD 체크 확인**
   - 모든 required 체크 통과 필요
   - ✅ 모든 체크가 green이어야 병합 가능

4. **Squash Merge**
   - Squash merge to main
   - 커밋 히스토리 정리

## 🛠️ 로컬 개발 환경 설정

### 보안 설정

**GitHub CLI 인증** (권장):
```bash
# GitHub CLI 설치 확인
gh --version

# GitHub 인증
gh auth login

# 인증 상태 확인
gh auth status
```

### 코드 품질 도구

#### Backend (Python)

```bash
cd backend

# 포맷팅 (자동 수정)
black .
isort .

# 린트 검사
flake8 app/ --max-line-length=100

# 타입 체크
mypy app/ --ignore-missing-imports

# 테스트 실행
pytest

# 커버리지 포함 테스트
pytest --cov=app --cov-report=html
```

**자동화 스크립트:**
```bash
# 모든 검사 실행 (수정 포함)
./scripts/lint.sh --fix

# 검사만 실행 (CI와 동일)
./scripts/lint.sh --check
```

#### Frontend (TypeScript/React)

```bash
cd frontend

# 린트 검사 (자동 수정)
npm run lint -- --fix

# 타입 체크
npm run type-check

# 빌드 테스트
npm run build

# 테스트 실행
npm test

# 개발 서버
npm run dev
```

### Pre-commit Hooks (선택사항)

로컬에서 커밋 전 자동 검증:

```bash
# pre-commit 설치
pip install pre-commit

# Hooks 설치
pre-commit install

# 모든 파일에 대해 실행
pre-commit run --all-files
```

## 프로젝트 구조

```
postgresql-optimizer-dashboard/
├── backend/
│   ├── app/
│   │   ├── domain/              # 순수 비즈니스 로직
│   │   ├── application/         # Use cases
│   │   ├── infrastructure/      # DB, 외부 API
│   │   └── presentation/        # 컨트롤러 (FastAPI)
│   ├── alembic/                 # DB 마이그레이션
│   ├── tests/                   # 테스트
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React 컴포넌트
│   │   ├── hooks/               # Custom hooks
│   │   ├── api/                 # API 클라이언트
│   │   ├── types/               # TypeScript 타입
│   │   └── utils/               # 유틸리티
│   ├── public/
│   └── package.json
├── .github/
│   ├── workflows/
│   │   ├── ci.yml               # CI/CD 파이프라인
│   │   └── claude-review.yml    # Claude 자동 리뷰
│   └── pull_request_template.md # PR 템플릿
├── .claude/
│   └── agents/
│       └── pr-reviewer.md       # PR 리뷰어 에이전트
└── docker-compose.yml
```

## 배포

### 환경 변수 설정

**Backend (.env):**
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
GLM_API_KEY=your_glm_api_key
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000
```

### GitHub Repository 설정

#### 1. Secrets 설정
Repository Settings → Secrets and variables → Actions

필수 Secrets:
- `ANTHROPIC_API_KEY`: Claude API 키 (코드 리뷰용)

선택 Secrets:
- 배포 관련 키 (AWS, GCP 등)

#### 2. Branch Protection
Repository Settings → Branches → main

권장 설정:
- ✅ Require status checks to pass before merging
  - `backend-validation`
  - `frontend-validation`
- ✅ Require at least 1 approval from reviewers
- ✅ Require conversation resolution before merging
- ✅ Require linear history (Squash merge)

#### 3. Actions Permissions
Repository Settings → Actions → General

권장 설정:
- ✅ Allow all actions and reusable workflows
- ✅ Read and write permissions for GITHUB_TOKEN

## 📚 추가 리소스

- [FastAPI 문서](https://fastapi.tiangolo.com)
- [React Query 문서](https://tanstack.com/query/latest)
- [Tailwind CSS 문서](https://tailwindcss.com)
- [SQLAlchemy 문서](https://www.sqlalchemy.org)
- [Anthropic Claude API](https://docs.anthropic.com)

## 🤝 기여하기

1. 이 저장소를 Fork
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'feat: Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 있습니다.

## 👥 팀

- **개발팀**: [Your Team Name]
- **문의**: [Contact Email]

## 🔧 트러블슈팅

### CI/CD 실패

**문제:** Backend validation 실패
```bash
# 로컬에서 동일한 검사 실행
cd backend
black --check .
isort --check-only .
flake8 app/
pytest
```

**문제:** Frontend validation 실패
```bash
# 로컬에서 동일한 검사 실행
cd frontend
npm run lint
npm run type-check
npm run build
```

### Claude 리뷰 실패

**문제:** Anthropic API 키 오류
1. Repository Settings → Secrets 확인
2. [Anthropic Console](https://console.anthropic.com)에서 API 키 상태 확인
3. API 키 재생성 및 Secret 업데이트

**문제:** API 요청 한도 초과
1. Anthropic Console에서 사용량 확인
2. 요금제 업그레이드 고려
3. 또는 Draft PR로 작성 후 ready로 전환하여 리뷰 실행

### 데이터베이스 마이그레이션 오류

```bash
# 마이그레이션 상태 확인
cd backend
alembic current

# 최신 마이그레이션으로 업그레이드
alembic upgrade head

# 마이그레이션 히스토리 확인
alembic history

# 특정 버전으로 다운그레이드 (주의!)
alembic downgrade <revision>
```

---

**Happy Coding! 🚀**
