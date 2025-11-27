# Implementation Tasks: Security & Secrets Detection

## Task Group 1: Setup & Dependencies

### Task 1.1: Add Security Dependencies
**Description:** Add all required security scanning tools to project dependencies

**Steps:**
1. Add detect-secrets to dev dependencies
2. Add bandit to dev dependencies
3. Add pip-audit to dev dependencies
4. Add gitleaks to CI docker image (not Poetry dependency)
5. Update poetry.lock

**Commands:**
```bash
poetry add --group dev detect-secrets bandit pip-audit
poetry lock
```

**Acceptance Criteria:**
- ✅ All tools in pyproject.toml [tool.poetry.group.dev.dependencies]
- ✅ poetry.lock updated
- ✅ `poetry install` succeeds
- ✅ All tools executable: `poetry run detect-secrets --version`

**Files Modified:**
- `pyproject.toml`
- `poetry.lock`

---

### Task 1.2: Configure Bandit in pyproject.toml
**Description:** Add bandit configuration for SAST scanning

**Configuration:**
```toml
[tool.bandit]
targets = ["src"]
exclude_dirs = ["/tests", "/agent-os"]
skips = []
severity = "medium"
confidence = "medium"

[tool.bandit.assert_used]
skips = ["*/test_*.py", "*/conftest.py"]
```

**Acceptance Criteria:**
- ✅ Configuration in pyproject.toml
- ✅ `poetry run bandit -r src/` runs successfully
- ✅ Excludes test directories
- ✅ Reports medium+ severity issues

**Files Modified:**
- `pyproject.toml`

---

## Task Group 2: Pre-commit Hooks Setup

### Task 2.1: Configure detect-secrets Pre-commit Hook
**Description:** Add detect-secrets to pre-commit configuration

**Steps:**
1. Add detect-secrets hook to `.pre-commit-config.yaml`
2. Configure with baseline file
3. Add exclude patterns for test fixtures
4. Test hook activation

**Configuration:**
```yaml
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        name: Detect secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: |
          (?x)^(
              tests/fixtures/.*|
              \.secrets\.baseline|
              poetry\.lock
          )$
```

**Acceptance Criteria:**
- ✅ Hook configured in `.pre-commit-config.yaml`
- ✅ Hook runs on `pre-commit run --all-files`
- ✅ Detects test secrets in test files
- ✅ Excludes legitimate patterns

**Files Modified:**
- `.pre-commit-config.yaml`

---

### Task 2.2: Create Initial Secrets Baseline
**Description:** Scan repository and create baseline for existing legitimate secrets

**Steps:**
1. Run detect-secrets scan to generate baseline
2. Audit baseline for false positives
3. Mark test fixtures as intentional
4. Commit baseline file

**Commands:**
```bash
# Generate baseline
poetry run detect-secrets scan --baseline .secrets.baseline

# Audit findings
poetry run detect-secrets audit .secrets.baseline
```

**Acceptance Criteria:**
- ✅ `.secrets.baseline` file created
- ✅ All test fixtures marked as intentional
- ✅ No real secrets in baseline
- ✅ Baseline committed to repository

**Files Created:**
- `.secrets.baseline`

---

### Task 2.3: Configure Bandit Pre-commit Hook
**Description:** Add bandit SAST scanning to pre-commit

**Configuration:**
```yaml
  - repo: https://github.com/PyCQA/bandit
    rev: '1.7.5'
    hooks:
      - id: bandit
        name: Bandit security linter
        args: ['-c', 'pyproject.toml', '-r', 'src/']
        pass_filenames: false
```

**Acceptance Criteria:**
- ✅ Hook configured in `.pre-commit-config.yaml`
- ✅ Runs on `pre-commit run bandit`
- ✅ Uses pyproject.toml configuration
- ✅ Scans only src/ directory

**Files Modified:**
- `.pre-commit-config.yaml`

---

### Task 2.4: Test Pre-commit Hooks
**Description:** Verify all security hooks work correctly

**Test Cases:**
1. **Test secrets detection:**
   - Create file with fake API key
   - Try to commit
   - Verify hook blocks commit

2. **Test SAST:**
   - Add `eval()` usage in code
   - Try to commit
   - Verify bandit detects it

3. **Test baseline exception:**
   - Add secret to test fixture
   - Add to baseline
   - Verify commit succeeds

**Acceptance Criteria:**
- ✅ Secrets hook blocks real secrets
- ✅ Secrets hook allows baselined items
- ✅ Bandit detects security issues
- ✅ Clean code passes all hooks

**Files Modified:**
- None (testing only)

---

## Task Group 3: GitLab CI Pipeline

### Task 3.1: Create Security Stage in GitLab CI
**Description:** Add security scanning stage to .gitlab-ci.yml

**Configuration:**
```yaml
stages:
  - security
  - test
  - build

variables:
  SECURE_LOG_LEVEL: "info"
```

**Acceptance Criteria:**
- ✅ Security stage added to pipeline
- ✅ Runs before test stage
- ✅ Variables configured

**Files Modified:**
- `.gitlab-ci.yml`

---

### Task 3.2: Add Secrets Detection Job (CI)
**Description:** Create GitLab CI job for secrets scanning

**Job Configuration:**
```yaml
secrets-scan:
  stage: security
  image: python:3.11-slim
  before_script:
    - pip install detect-secrets
  script:
    - detect-secrets scan --baseline .secrets.baseline
  allow_failure: false
  only:
    - merge_requests
    - main
  cache:
    paths:
      - .pip-cache
```

**Acceptance Criteria:**
- ✅ Job runs on MRs and main
- ✅ Uses .secrets.baseline
- ✅ Fails pipeline if secrets found
- ✅ Caches dependencies

**Files Modified:**
- `.gitlab-ci.yml`

---

### Task 3.3: Add SAST Job (CI)
**Description:** Create bandit scanning job for CI

**Job Configuration:**
```yaml
sast-scan:
  stage: security
  image: python:3.11-slim
  before_script:
    - pip install poetry
    - poetry config virtualenvs.create false
    - poetry install --no-root --only main,dev
  script:
    - poetry run bandit -r src/ -f json -o bandit-report.json
    - poetry run bandit -r src/ -f screen
  artifacts:
    reports:
      sast: bandit-report.json
    paths:
      - bandit-report.json
    expire_in: 1 week
    when: always
  allow_failure: false
  only:
    - merge_requests
    - main
```

**Acceptance Criteria:**
- ✅ Scans src/ directory
- ✅ Generates JSON report
- ✅ Saves artifacts
- ✅ Fails on security issues

**Files Modified:**
- `.gitlab-ci.yml`

---

### Task 3.4: Add Dependency Scanning Job (CI)
**Description:** Create job for vulnerability scanning of dependencies

**Job Configuration:**
```yaml
dependency-scan:
  stage: security
  image: python:3.11-slim
  before_script:
    - pip install poetry pip-audit
    - poetry config virtualenvs.create false
    - poetry install --no-root
  script:
    - echo "Running pip-audit scan..."
    - poetry run pip-audit --format json --output pip-audit-report.json || true
    - poetry run pip-audit || true
  artifacts:
    reports:
      dependency_scanning: pip-audit-report.json
    paths:
      - pip-audit-report.json
    expire_in: 1 week
    when: always
  allow_failure: false
  only:
    - merge_requests
    - main
```

**Acceptance Criteria:**
- ✅ Runs pip-audit
- ✅ Generates JSON reports
- ✅ Fails on critical vulnerabilities
- ✅ Saves artifacts

**Files Modified:**
- `.gitlab-ci.yml`

---

### Task 3.5: Test GitLab CI Pipeline
**Description:** Verify entire security pipeline works end-to-end

**Test Cases:**
1. Create MR with clean code → all jobs pass
2. Create MR with secret → secrets-scan fails
3. Create MR with `eval()` → sast-scan fails
4. Verify artifacts are generated
5. Verify reports visible in GitLab UI

**Acceptance Criteria:**
- ✅ Pipeline runs all security jobs
- ✅ Security issues block merge
- ✅ Reports available in GitLab
- ✅ Artifacts downloadable

**Files Modified:**
- None (testing only)

---

## Task Group 4: Documentation

### Task 4.1: Create Security Policy (SECURITY.md)
**Description:** Document security vulnerability reporting process

**Content Sections:**
1. Reporting vulnerabilities
2. Response timeline (24h acknowledgment, 7d fix for critical)
3. Security contacts
4. Disclosure policy
5. PGP key (if applicable)
6. Supported versions

**Acceptance Criteria:**
- ✅ SECURITY.md file created
- ✅ Clear reporting instructions
- ✅ Contact information provided
- ✅ Follows industry standards

**Files Created:**
- `SECURITY.md`

---

### Task 4.2: Create Developer Security Guide
**Description:** Document how to use security tools and handle issues

**File:** `docs/security.md`

**Content Sections:**
1. Overview of security tools
2. Pre-commit hooks setup and usage
3. How to handle detected secrets
4. How to add test fixtures to baseline
5. How to fix bandit issues
6. Best practices for credentials
7. SSH keys vs tokens
8. Common errors and solutions

**Acceptance Criteria:**
- ✅ `docs/security.md` created
- ✅ All tools documented
- ✅ Examples for common scenarios
- ✅ Troubleshooting guide

**Files Created:**
- `docs/security.md`

---

### Task 4.3: Update Main README with Security Section
**Description:** Add security information to main README

**Section to Add:**
```markdown
## Security

This project uses automated security scanning to detect:
- Secrets and credentials
- Code security vulnerabilities (SAST)
- Dependency vulnerabilities

### For Developers

Security checks run automatically:
- **Pre-commit:** Secrets and SAST scanning
- **CI/CD:** Full security scan on every MR

See [docs/security.md](docs/security.md) for details.

### Reporting Security Issues

Please report security vulnerabilities to [security contact].
See [SECURITY.md](SECURITY.md) for details.
```

**Acceptance Criteria:**
- ✅ Security section in README.md
- ✅ Links to security docs
- ✅ Clear for new developers

**Files Modified:**
- `README.md`

---

### Task 4.4: Document CI/CD Security Pipeline
**Description:** Add documentation for CI/CD security jobs

**File:** `docs/ci-security.md`

**Content:**
1. Overview of security pipeline
2. Each job explained
3. How to read security reports
4. How to fix failing jobs
5. Baseline update process
6. Exemption process for false positives

**Acceptance Criteria:**
- ✅ `docs/ci-security.md` created
- ✅ All jobs documented
- ✅ Remediation guides
- ✅ Screenshots of reports

**Files Created:**
- `docs/ci-security.md`

---

## Task Group 5: Testing & Validation

### Task 5.1: Test Secrets Detection with Real Scenarios
**Description:** Verify secrets detection works for common secret types

**Test Cases:**
1. GitLab token (glpat-*)
2. GitHub token (ghp_*)
3. AWS credentials (AKIA*)
4. SSH private key
5. Database URL with password
6. API key in environment variable
7. Base64 encoded credentials
8. High entropy random strings

**Acceptance Criteria:**
- ✅ All secret types detected
- ✅ Clear error messages
- ✅ File and line number shown
- ✅ Remediation suggested

**Files Modified:**
- None (testing only)

---

### Task 5.2: Test SAST Detection
**Description:** Verify bandit detects common security issues

**Test Cases:**
1. SQL injection (string concatenation)
2. `eval()` usage
3. `exec()` usage
4. `pickle.loads()` without validation
5. `yaml.load()` without SafeLoader
6. Weak random (`random` instead of `secrets`)
7. Hardcoded password
8. Shell injection

**Acceptance Criteria:**
- ✅ All issues detected
- ✅ Severity correctly assigned
- ✅ Code location shown
- ✅ Fix suggestions provided

**Files Modified:**
- None (testing only)

---

### Task 5.3: Test Dependency Scanning
**Description:** Verify vulnerability detection in dependencies

**Test Cases:**
1. Add package with known vulnerability
2. Verify pip-audit detects it
3. Check severity classification
4. Verify CI job fails appropriately

**Acceptance Criteria:**
- ✅ Known vulnerabilities detected
- ✅ CVE IDs shown
- ✅ Severity accurate
- ✅ Fix version suggested

**Files Modified:**
- None (testing only)

---

### Task 5.4: End-to-End Pipeline Test
**Description:** Test complete workflow from commit to merge

**Scenario:**
1. Create feature branch
2. Make changes
3. Run pre-commit hooks
4. Push to GitLab
5. CI runs security scan
6. Review security reports
7. Merge if clean

**Acceptance Criteria:**
- ✅ Pre-commit blocks local issues
- ✅ CI catches additional issues
- ✅ Reports accessible in GitLab
- ✅ Merge blocked if issues found
- ✅ Merge succeeds when clean

**Files Modified:**
- None (testing only)

---

## Task Group 6: Cleanup & Finalization

### Task 6.1: Scan Existing Codebase
**Description:** Run all security tools on current code and fix issues

**Steps:**
1. Run detect-secrets on all files
2. Audit and baseline legitimate secrets
3. Run bandit on src/
4. Fix any security issues found
5. Update vulnerable dependencies

**Acceptance Criteria:**
- ✅ No real secrets in codebase
- ✅ All bandit issues resolved or baselined
- ✅ No critical vulnerabilities
- ✅ All tests still pass

**Files Modified:**
- Various (based on findings)

---

### Task 6.2: Update .gitignore
**Description:** Ensure security tool outputs are not committed

**Additions:**
```gitignore
# Security scanning outputs
bandit-report.json
pip-audit-report.json
.secrets.baseline.tmp
```

**Acceptance Criteria:**
- ✅ Security outputs in .gitignore
- ✅ No reports committed accidentally
- ✅ Baseline file IS committed

**Files Modified:**
- `.gitignore`

---

### Task 6.3: Create Verification Document
**Description:** Document testing and validation of security feature

**File:** `agent-os/specs/2025-11-12-security-secrets-detection/verifications/implementation-verification.md`

**Content:**
1. All tasks completed checklist
2. Test results for each security tool
3. Sample security reports
4. Known false positives baseline
5. Performance metrics (scan times)
6. Lessons learned

**Acceptance Criteria:**
- ✅ Verification doc created
- ✅ All tests documented
- ✅ Screenshots included
- ✅ Metrics collected

**Files Created:**
- `agent-os/specs/.../verifications/implementation-verification.md`

---

## Summary

**Total Tasks:** 23 tasks across 6 groups

**Dependencies:**
- Group 1 → Group 2 (need dependencies to configure hooks)
- Group 2 → Group 3 (hooks before CI)
- Group 1-3 → Group 4 (implementation before docs)
- All → Group 5 (everything implemented before testing)
- All → Group 6 (finalization last)

**Estimated Complexity:** M (Medium)

**Success Criteria:**
- ✅ All pre-commit hooks working
- ✅ GitLab CI pipeline with security stage
- ✅ Complete documentation
- ✅ Zero secrets in codebase
- ✅ All tests passing
- ✅ Security scan time < 5 minutes
