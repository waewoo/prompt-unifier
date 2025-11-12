# Specification: Security & Secrets Detection

## Goal
Implement comprehensive security scanning to prevent accidental commits of secrets (API keys, tokens, passwords) and detect security vulnerabilities in code and dependencies through automated pre-commit hooks and CI/CD pipeline integration.

## User Stories
- As a developer, I want the system to prevent me from committing secrets so that I don't accidentally expose sensitive credentials
- As a security engineer, I want automated security scanning in CI/CD so that vulnerabilities are detected before code reaches production
- As a team lead, I want visibility into security issues so that I can ensure the codebase meets security standards

## Context & Motivation

**Recent Incident:**
GitLab personal access token (`glpat-*`) was accidentally committed in TEST.md and multiple documentation files, requiring manual cleanup across several commits.

**Risks Without This Feature:**
- 🔴 **Critical:** Secrets leaked in public repositories
- 🔴 **Critical:** Unpatched vulnerabilities exploited in production
- 🟡 **High:** Time wasted on manual secret cleanup
- 🟡 **High:** Need to revoke and regenerate all exposed credentials

## Specific Requirements

### 1. Secrets Detection (Pre-commit)

**Tools Selection:**
- **Primary:** `detect-secrets` (Yelp) - Pattern-based secret detection
- **Secondary:** `gitleaks` - Git-specific secret scanning for CI

**Pre-commit Hook Configuration:**
```yaml
# .pre-commit-config.yaml addition
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
      exclude: ^(tests/fixtures/.*|\.secrets\.baseline)$
```

**Detection Patterns:**
- API keys and tokens (AWS, Azure, GCP, GitLab, GitHub)
- Private keys (SSH, PGP, RSA)
- Passwords in configuration files
- Database connection strings with credentials
- OAuth tokens and secrets
- JWT tokens
- Slack tokens, Discord webhooks
- Generic high-entropy strings (Base64, Hex)

**Baseline Management:**
```bash
# Generate initial baseline (one-time)
detect-secrets scan --baseline .secrets.baseline

# Audit baseline for false positives
detect-secrets audit .secrets.baseline

# Update baseline when adding legitimate test fixtures
detect-secrets scan --update .secrets.baseline
```

**Behavior:**
- Block commit if new secrets detected (not in baseline)
- Display clear error message with file location and secret type
- Provide guidance on how to fix (remove secret, add to baseline if legitimate)
- Exit code 1 on detection (fail the pre-commit hook)

### 2. SAST (Static Application Security Testing)

**Tool:** `bandit` - Python-specific SAST

**Configuration (pyproject.toml):**
```toml
[tool.bandit]
targets = ["src"]
exclude_dirs = ["/tests"]
skips = ["B404", "B603"]  # Skip specific checks if needed
severity = "medium"
confidence = "medium"

[tool.bandit.assert_used]
skips = ["*/test_*.py"]
```

**Pre-commit Hook:**
```yaml
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.5
  hooks:
    - id: bandit
      args: ['-c', 'pyproject.toml', '-r', 'src/']
```

**Security Checks:**
- SQL injection vulnerabilities
- Insecure deserialization (pickle, yaml.load)
- Use of dangerous functions (eval, exec, compile)
- Hardcoded passwords or secrets in code
- Weak cryptography (MD5, DES, weak random)
- Command injection vulnerabilities
- Path traversal risks
- Insecure file permissions

**Severity Levels:**
- **High:** Block commit (exit code 1)
- **Medium:** Block commit (exit code 1)
- **Low:** Warning only (informational)

### 3. Dependency Security Scanning

**Tools:**
- **Primary:** `safety` - CVE database for Python packages
- **Alternative:** `pip-audit` - More comprehensive, newer tool

**Pre-commit Hook (Optional - can be slow):**
```yaml
- repo: local
  hooks:
    - id: safety-check
      name: Safety vulnerability scan
      entry: poetry run safety check --json
      language: system
      pass_filenames: false
      stages: [manual]  # Run manually or in CI only
```

**CI/CD Integration (Required):**
```yaml
dependency-scan:
  stage: security
  script:
    - poetry run safety check --json --output safety-report.json
    - poetry run pip-audit --format json --output pip-audit-report.json
  artifacts:
    reports:
      dependency_scanning: safety-report.json
  allow_failure: false  # Block merge on critical vulnerabilities
```

**Scan Coverage:**
- Direct dependencies (poetry.lock)
- Transitive dependencies
- CVE severity: Critical, High, Medium, Low
- Known exploits in the wild

**Failure Criteria:**
- Critical severity: Block commit/merge
- High severity: Block commit/merge
- Medium severity: Warning (allow with review)
- Low severity: Informational only

### 4. GitLab CI Security Pipeline

**Pipeline Stages:**
```yaml
# .gitlab-ci.yml
stages:
  - security
  - test
  - build
  - deploy

variables:
  SECURE_LOG_LEVEL: "info"
```

**Jobs:**

#### 4.1 Secrets Detection (CI)
```yaml
secrets-scan:
  stage: security
  image: python:3.11
  before_script:
    - pip install detect-secrets gitleaks
  script:
    # Scan with detect-secrets
    - detect-secrets scan --baseline .secrets.baseline
    # Scan with gitleaks for git history
    - gitleaks detect --source . --no-git --verbose
  allow_failure: false
  only:
    - merge_requests
    - main
```

#### 4.2 SAST Scanning
```yaml
sast-scan:
  stage: security
  image: python:3.11
  before_script:
    - pip install poetry
    - poetry install --no-root
  script:
    - poetry run bandit -r src/ -f json -o bandit-report.json
    - poetry run bandit -r src/ -f screen  # Human-readable output
  artifacts:
    reports:
      sast: bandit-report.json
    paths:
      - bandit-report.json
    expire_in: 1 week
  allow_failure: false
```

#### 4.3 Dependency Scanning
```yaml
dependency-scan:
  stage: security
  image: python:3.11
  before_script:
    - pip install poetry safety pip-audit
    - poetry install --no-root
  script:
    # Safety scan
    - poetry run safety check --json --output safety-report.json || true
    - poetry run safety check  # Human-readable
    # pip-audit scan
    - poetry run pip-audit --format json --output pip-audit-report.json || true
    - poetry run pip-audit  # Human-readable
  artifacts:
    reports:
      dependency_scanning: safety-report.json
    paths:
      - safety-report.json
      - pip-audit-report.json
    expire_in: 1 week
  allow_failure: false
```

### 5. Developer Experience

**Setup Instructions:**
```bash
# Install pre-commit
poetry add --group dev pre-commit detect-secrets bandit safety pip-audit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Error Messages:**
- Clear indication of what was detected
- File path and line number
- Suggested remediation
- Link to documentation

**Example:**
```
[detect-secrets] Potential secret detected!
  File: config.yaml
  Line: 15
  Type: GitLab Personal Access Token

  ❌ BLOCKED: Commit contains potential secrets

  To fix:
  1. Remove the secret from the file
  2. Use environment variables or secure vaults
  3. If legitimate test data, add to .secrets.baseline

  See: docs/security.md for more information
```

### 6. Baseline and Exceptions

**Legitimate Secrets (Test Fixtures):**
Create `.secrets.baseline` with audited false positives:

```json
{
  "version": "1.4.0",
  "filters_used": [
    {
      "path": "detect_secrets.filters.heuristic.is_potential_uuid"
    }
  ],
  "results": {
    "tests/fixtures/sample_config.yaml": [
      {
        "type": "Secret Keyword",
        "filename": "tests/fixtures/sample_config.yaml",
        "hashed_secret": "abc123...",
        "is_verified": false,
        "line_number": 10
      }
    ]
  }
}
```

**Updating Baseline:**
```bash
# Scan and update baseline
detect-secrets scan --baseline .secrets.baseline

# Audit new findings
detect-secrets audit .secrets.baseline
# Press:
# 'y' - Real secret (should be removed)
# 'n' - False positive (add to baseline)
# 's' - Skip for now
```

### 7. Documentation Requirements

**Security Policy (SECURITY.md):**
- Reporting security vulnerabilities
- Response timeline
- Security contacts
- PGP key for encrypted reports

**Developer Guide (docs/security.md):**
- How pre-commit hooks work
- How to handle detected secrets
- How to add test fixtures to baseline
- Best practices for credential management
- How to use SSH keys instead of tokens

**CI/CD Guide:**
- How to read security reports
- How to fix failing security jobs
- Exemption process for false positives

## Out of Scope

❌ **Not Included:**
- DAST (Dynamic Application Security Testing) - No web application
- Container security scanning - No containers yet
- License compliance checking - Future feature
- Penetration testing - Manual process
- Runtime security monitoring - Not applicable for CLI tool
- Code signing - Future consideration
- Supply chain security (SBOM) - Future consideration

## Error Handling

**Pre-commit Failures:**
- Clear error messages with remediation steps
- Exit code 1 to block commit
- Logs saved to `.pre-commit.log` for debugging

**CI/CD Failures:**
- Job fails with clear error summary
- Artifacts preserved for analysis
- Link to security documentation
- Notification to security team (future)

**False Positives:**
- Documented process to add to baseline
- Require security review for baseline changes
- Audit trail in git history

## Success Metrics

**Goals:**
- ✅ 0 secrets committed after implementation
- ✅ 100% of commits scanned locally
- ✅ 100% of MRs scanned in CI
- ✅ < 5 minutes CI security scan time
- ✅ < 5 false positives per week
- ✅ 0 critical vulnerabilities unpatched > 7 days

**Monitoring:**
- Track secret detection events
- Track vulnerability detection and remediation time
- Track false positive rate
- Developer satisfaction survey

## Implementation Phases

### Phase 1: Pre-commit Secrets Detection
- Install and configure detect-secrets
- Create initial baseline
- Document usage for developers
- Test on existing codebase

### Phase 2: SAST Integration
- Configure bandit
- Add to pre-commit hooks
- Fix any existing issues
- Document common issues

### Phase 3: Dependency Scanning
- Add safety and pip-audit
- Run in CI (not pre-commit - too slow)
- Create vulnerability remediation process
- Set up regular scans

### Phase 4: GitLab CI Pipeline
- Create security stage
- Configure all security jobs
- Set up artifact collection
- Configure failure thresholds

### Phase 5: Documentation & Training
- Write security policy
- Create developer guide
- Train team on tools
- Establish security champion

## References

- [detect-secrets Documentation](https://github.com/Yelp/detect-secrets)
- [gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [bandit Documentation](https://bandit.readthedocs.io/)
- [safety Documentation](https://github.com/pyupio/safety)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitLab Security Best Practices](https://docs.gitlab.com/ee/user/application_security/)
- [Pre-commit Framework](https://pre-commit.com/)
