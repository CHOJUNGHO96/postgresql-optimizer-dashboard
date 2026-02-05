# ⚡ Quick Start - GitHub Actions & Claude Review

시스템을 빠르게 설정하고 실행하기 위한 체크리스트

## 🎯 5분 설정 가이드

### 1️⃣ GitHub Secrets 설정 (2분)

```
1. GitHub 저장소 페이지 이동
2. Settings → Secrets and variables → Actions 클릭
3. "New repository secret" 클릭
4. 입력:
   Name: ANTHROPIC_API_KEY
   Value: [Anthropic Console에서 발급받은 API 키]
5. "Add secret" 클릭
```

✅ **확인**: Secrets 목록에 `ANTHROPIC_API_KEY`가 보이면 성공

---

### 2️⃣ Branch Protection 설정 (2분)

```
1. Settings → Branches 클릭
2. "Add branch protection rule" 클릭
3. Branch name pattern: main
4. 체크:
   ☑️ Require a pull request before merging
   ☑️ Require approvals (1)
   ☑️ Require status checks to pass before merging
   ☑️ Require conversation resolution before merging
5. "Create" 클릭
```

⚠️ **주의**: Status checks (backend-validation, frontend-validation)는 첫 PR 실행 후 설정 가능

---

### 3️⃣ Actions Permissions 설정 (1분)

```
1. Settings → Actions → General 클릭
2. "Actions permissions" 섹션:
   ☑️ Allow all actions and reusable workflows
3. "Workflow permissions" 섹션:
   ☑️ Read and write permissions
4. "Save" 클릭
```

✅ **확인**: 설정이 저장되면 완료

---

## 🧪 테스트 (5분)

### 간단한 테스트 PR 생성

```bash
# 1. 테스트 브랜치 생성
git checkout -b test/github-actions

# 2. 작은 변경 추가
echo "# Test" >> README.md

# 3. 커밋
git add README.md
git commit -m "test: GitHub Actions 및 Claude 리뷰 테스트"

# 4. Push
git push -u origin test/github-actions

# 5. PR 생성 (GitHub UI 또는 gh CLI)
gh pr create \
  --title "test: CI/CD 및 Claude 리뷰 검증" \
  --body "자동화 시스템 테스트"
```

### 예상 결과

1. **Actions 탭**에서 워크플로우 실행 확인:
   - ✅ `CI/CD Pipeline` 실행 중
   - ✅ `Claude Code Review` 실행 중

2. **PR 페이지**에서 확인:
   - ✅ PR 템플릿 자동 로드
   - ✅ 잠시 후 Claude 리뷰 코멘트 게시
   - ✅ CI/CD 체크 결과 표시

3. **성공 시**:
   - ✅ 모든 체크 통과 (green checkmark)
   - 🤖 Claude 리뷰 코멘트 확인 가능
   - ✅ PR 병합 가능 상태

---

## 📋 설정 체크리스트

완료한 항목에 체크하세요:

### 필수 설정
- [ ] ✅ Anthropic API 키 발급 받음
- [ ] ✅ GitHub Secrets에 `ANTHROPIC_API_KEY` 추가
- [ ] ✅ Branch Protection 규칙 생성 (main 브랜치)
- [ ] ✅ Actions Permissions 설정 완료
- [ ] ✅ 테스트 PR 생성하여 검증

### 선택 설정
- [ ] Codecov 통합 (커버리지 추적)
- [ ] Dependabot 활성화 (의존성 업데이트)
- [ ] CODEOWNERS 파일 생성 (필수 리뷰어)

---

## 🔗 문서 링크

더 자세한 정보가 필요하면:

- **📖 전체 설정 가이드**: [`SETUP_GUIDE.md`](./SETUP_GUIDE.md)
- **👨‍💻 개발자 가이드**: [`DEVELOPER_GUIDE.md`](./DEVELOPER_GUIDE.md)
- **📝 구현 요약**: [`IMPLEMENTATION_SUMMARY.md`](./IMPLEMENTATION_SUMMARY.md)
- **📚 프로젝트 README**: [`README.md`](./README.md)

---

## 🆘 문제 해결

### Claude 리뷰가 안 나타남

**원인**: ANTHROPIC_API_KEY가 설정되지 않음

**해결**:
```
Settings → Secrets → ANTHROPIC_API_KEY 확인
없으면 추가, 있으면 값이 올바른지 확인
```

### CI/CD가 실패함

**원인**: 코드 품질 검사 실패

**해결**:
```bash
# 로컬에서 검증
cd backend && ./scripts/lint.sh --fix
cd frontend && ./scripts/check.sh --fix

# 재커밋
git add .
git commit -m "fix: CI 오류 수정"
git push
```

### Actions가 실행 안 됨

**원인**: Actions 권한 부족

**해결**:
```
Settings → Actions → General
→ "Allow all actions" 활성화
→ "Read and write permissions" 활성화
```

---

## 📞 도움말

- **설정 중 문제**: `SETUP_GUIDE.md` 트러블슈팅 섹션 참조
- **개발 질문**: `DEVELOPER_GUIDE.md` 참조
- **팀 문의**: 팀 리드 또는 시니어 개발자

---

## ✅ 완료!

모든 항목을 완료했다면 시스템이 정상 작동합니다.

**다음 단계**:
1. 팀원들에게 새 워크플로우 공유
2. `DEVELOPER_GUIDE.md` 읽고 일상 개발 시작
3. 첫 실제 Feature PR 생성!

**Happy Coding! 🚀**
