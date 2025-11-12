# CI/CD Security Pipeline Documentation

This document explains the security scanning jobs in the GitLab CI/CD pipeline, how to read security reports, and how to fix failing security jobs.

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [Security Jobs](#security-jobs)
3. [Reading Security Reports](#reading-security-reports)
4. [Fixing Failing Jobs](#fixing-failing-jobs)
5. [Baseline Management](#baseline-management)
6. [Exemption Process](#exemption-process)

## Pipeline Overview

The security stage runs **before** all other stages to catch issues early:

```
security → lint → typecheck → test
```

All security jobs:
- Run on **merge requests** and **main** branch
- Have `allow_failure: false` - **blocking** merge if they fail
- Generate **artifacts** (JSON reports) preserved for 1 week
- Use Python 3.11-slim image for efficiency

## Security Jobs

### 1. secrets-scan

**Purpose:** Detect secrets (API keys, tokens, passwords) in code

**Tool:** detect-secrets v1.5.0

**Configuration:**
```yaml
secrets-scan:
  stage: security
  image: python:3.11-slim
  script:
    - detect-secrets scan --baseline .secrets.baseline
  allow_failure: false
```

**What it checks:**
- GitLab/GitHub personal access tokens
- AWS credentials (AKIA*, SECRET_ACCESS_KEY)
- SSH private keys
- Database connection strings with passwords
- API keys (Stripe, Slack, Discord, etc.)
- JWT tokens
- High-entropy Base64/Hex strings

**Baseline:** Uses `.secrets.baseline` to allow legitimate test fixtures

**Runtime:** ~10-30 seconds

---

### 2. sast-scan (Static Application Security Testing)

**Purpose:** Find security vulnerabilities in Python code

**Tool:** Bandit v1.8.6

**Configuration:**
```yaml
sast-scan:
  stage: security
  script:
    - poetry run bandit -r src/ -f json -o bandit-report.json
    - poetry run bandit -r src/ -f screen
  artifacts:
    reports:
      sast: bandit-report.json
```

**What it checks:**
- SQL injection vulnerabilities (B608)
- Use of dangerous functions: eval(), exec(), compile() (B307)
- Insecure deserialization: pickle, yaml.load() (B301)
- Hardcoded passwords (B105, B106)
- Weak cryptography: MD5, DES (B303, B304)
- Command injection (B602, B603)
- Path traversal (B108)
- Insecure file permissions (B103)

**Severity Levels:**
- **High** - Critical security issue, blocks merge
- **Medium** - Serious issue, blocks merge
- **Low** - Informational, allows merge

**Artifacts:**
- `bandit-report.json` - Machine-readable SAST report
- Available in GitLab Security Dashboard

**Runtime:** ~20-40 seconds

---

### 3. dependency-scan

**Purpose:** Detect vulnerable packages in dependencies

**Tools:**
- Safety v3.7.0 (CVE database)
- pip-audit v2.9.0 (comprehensive scanning)

**Configuration:**
```yaml
dependency-scan:
  stage: security
  script:
    - poetry run safety check --json --output safety-report.json || true
    - poetry run safety check || true
    - poetry run pip-audit --format json --output pip-audit-report.json || true
    - poetry run pip-audit || true
    - poetry run safety check --severity critical  # Fail on critical
```

**What it checks:**
- Known CVEs in direct dependencies
- Known CVEs in transitive dependencies
- Severity: Critical, High, Medium, Low
- Exploits in the wild

**Failure criteria:**
- **Critical** vulnerabilities → Blocks merge
- **High** vulnerabilities → Blocks merge (by default)
- **Medium/Low** → Informational only

**Artifacts:**
- `safety-report.json` - Safety scan results
- `pip-audit-report.json` - pip-audit scan results

**Runtime:** ~30-60 seconds

---

## Reading Security Reports

### Accessing Reports in GitLab

1. **Go to Merge Request** → Pipelines tab
2. **Click on failed pipeline** → View jobs
3. **Click on failed job** → See console output
4. **Download artifacts** → Browse → Download JSON reports

### Understanding Secrets Scan Output

**Example failure:**
```
[detect-secrets] Potential secret detected!
  File: src/config.py
  Line: 23
  Type: GitLab Personal Access Token

  Secret: glpat-xxxxxxxxxxxx...
```

**Action required:**
1. Remove the secret from the file
2. Use environment variables instead
3. Update the code to load from secure storage

---

### Understanding SAST Scan Output

**Example console output:**
```
Run started:2025-11-12 18:30:24

Test results:
>> Issue: [B608:hardcoded_sql_expressions] Possible SQL injection
   Severity: Medium   Confidence: Low
   Location: src/database.py:45
   More Info: https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html

   44  def get_user(user_id):
   45      query = f"SELECT * FROM users WHERE id = {user_id}"
   46      return db.execute(query)
```

**Key information:**
- **Issue ID:** B608 - Look up in Bandit docs
- **Severity/Confidence:** How serious and how certain
- **Location:** Exact file and line number
- **More Info:** Link to documentation with fix examples

---

### Understanding Dependency Scan Output

**Example Safety output:**
```
+==============================================================================+
| REPORT                                                                        |
+==============================================================================+
| package   | installed | affected     | ID                 | CVE           |
+==============================================================================+
| requests  | 2.25.0    | <2.26.0      | 51668              | CVE-2023-xxxxx|
+==============================================================================+
| vulnerability: Improper Certificate Validation                               |
| Severity: HIGH                                                                |
| Fix: upgrade to requests>=2.26.0                                              |
+==============================================================================+
```

**Action required:**
1. Update the package: `poetry update requests`
2. Test that everything still works
3. Commit the updated `poetry.lock`

---

## Fixing Failing Jobs

### Secrets Scan Failed

**Scenario:** Pipeline fails with "Potential secret detected"

**Steps to fix:**

1. **Identify the secret:**
   ```bash
   # Check the job output for file and line number
   # File: src/config.py, Line: 23
   ```

2. **Remove the secret:**
   ```python
   # Before (BAD)
   api_key = "sk-1234567890abcdef"

   # After (GOOD)
   import os
   api_key = os.getenv("API_KEY")
   ```

3. **Re-run the pipeline:**
   ```bash
   git add src/config.py
   git commit -m "fix: use env var for API key"
   git push
   ```

4. **If it's a false positive (test fixture):**
   ```bash
   # Add to baseline
   poetry run detect-secrets scan --update .secrets.baseline

   # Commit baseline
   git add .secrets.baseline
   git commit -m "chore: update secrets baseline for test fixtures"
   git push
   ```

---

### SAST Scan Failed

**Scenario:** Bandit found a security vulnerability

**Example:** SQL Injection (B608)

**Steps to fix:**

1. **Review the finding:**
   ```
   Issue: [B608] Possible SQL injection
   Location: src/database.py:45
   ```

2. **Fix the vulnerability:**
   ```python
   # Before (VULNERABLE)
   query = f"SELECT * FROM users WHERE id = {user_id}"
   db.execute(query)

   # After (SECURE)
   query = "SELECT * FROM users WHERE id = ?"
   db.execute(query, (user_id,))
   ```

3. **Test locally:**
   ```bash
   poetry run bandit -r src/
   ```

4. **Commit and push:**
   ```bash
   git add src/database.py
   git commit -m "fix(security): use parameterized queries to prevent SQL injection"
   git push
   ```

**If it's a false positive:**
```python
# Add nosec comment with explanation
password = "test_fixture_password"  # nosec B105 - test data only
```

---

### Dependency Scan Failed

**Scenario:** Critical vulnerability in a dependency

**Steps to fix:**

1. **Check the vulnerability:**
   ```bash
   # Run locally
   poetry run safety check
   ```

2. **Update the vulnerable package:**
   ```bash
   # Update specific package
   poetry update <package-name>

   # Or update all packages
   poetry update
   ```

3. **Verify the fix:**
   ```bash
   # Re-run safety check
   poetry run safety check

   # Run tests
   poetry run pytest
   ```

4. **Commit and push:**
   ```bash
   git add poetry.lock
   git commit -m "fix(security): update <package> to address CVE-2023-xxxxx"
   git push
   ```

**If update breaks compatibility:**
- Check if there's a backported security patch
- Consider alternative packages
- Document the risk in a security review issue

---

## Baseline Management

### What is a Baseline?

The `.secrets.baseline` file contains **audited** potential secrets that are actually:
- Test fixtures
- Example data in documentation
- False positives (e.g., variable names containing "password")

### When to Update Baseline

**Legitimate reasons:**
1. Adding new test fixtures with fake credentials
2. Adding example code to documentation
3. False positives from detect-secrets

**Steps to update:**

1. **Generate updated baseline:**
   ```bash
   poetry run detect-secrets scan --update .secrets.baseline
   ```

2. **Audit new findings:**
   ```bash
   poetry run detect-secrets audit .secrets.baseline
   ```

   For each finding:
   - Press `y` if it's a **real secret** (should be removed!)
   - Press `n` if it's a **false positive** (add to baseline)
   - Press `s` to skip for now

3. **Commit the baseline:**
   ```bash
   git add .secrets.baseline
   git commit -m "chore: update secrets baseline for test fixtures"
   ```

**Important:** Baseline changes should be reviewed by another team member!

---

## Exemption Process

### When to Request Exemption

**Valid reasons:**
- False positive that can't be fixed
- Known security trade-off (documented)
- Dependency vulnerability with no fix available (risk accepted)

### How to Request Exemption

1. **Create a security review issue:**
   - Title: `[Security Review] Exemption request for <finding>`
   - Description: Explain why it's safe or necessary
   - Assign to: Security champion or team lead

2. **Document the decision:**
   - Add comment in code explaining why it's safe
   - Add to `.secrets.baseline` if applicable
   - Use `# nosec <code>` for Bandit findings

3. **Get approval:**
   - At least one other developer must approve
   - Security champion must approve for High/Critical findings

### Example: Bandit Exemption

```python
# Legitimate use of eval() for calculator feature
# User input is validated and sanitized before eval
# Reviewed and approved by security team on 2025-11-12
result = eval(sanitized_expression)  # nosec B307 - validated input only
```

---

## Performance

Typical pipeline times:

| Job | Average Time | Timeout |
|-----|-------------|---------|
| secrets-scan | 20s | 5 min |
| sast-scan | 35s | 10 min |
| dependency-scan | 45s | 10 min |
| **Total Security Stage** | **~2 min** | 25 min |

## Artifacts

All security jobs preserve artifacts for **1 week**:

- **bandit-report.json** - SAST findings
- **safety-report.json** - Dependency vulnerabilities (Safety)
- **pip-audit-report.json** - Dependency vulnerabilities (pip-audit)

Download from: MR → Pipelines → Job → Browse artifacts

## Monitoring

### GitLab Security Dashboard

View aggregated security findings:
1. Go to project → Security & Compliance → Security Dashboard
2. Filter by severity, type, or branch
3. Track remediation over time

### Metrics

Track these metrics:
- Number of secrets detected per month
- Mean time to remediation (MTTR)
- False positive rate
- Dependency update lag

---

## Troubleshooting

### Job times out

**Cause:** Network issues downloading dependencies

**Solution:**
```yaml
# Increase timeout in .gitlab-ci.yml
timeout: 10 minutes
```

### Python version mismatch

**Cause:** Using wrong Python version in CI

**Solution:** Ensure all jobs use same image:
```yaml
image: python:3.11-slim
```

### Artifacts not generated

**Cause:** Job fails before artifact creation

**Solution:** Use `when: always` in artifacts:
```yaml
artifacts:
  when: always
  paths:
    - bandit-report.json
```

---

## Additional Resources

- [GitLab Security Scanning Docs](https://docs.gitlab.com/ee/user/application_security/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://github.com/pyupio/safety)
- [detect-secrets Documentation](https://github.com/Yelp/detect-secrets)

## Questions?

For help with security pipeline issues:
1. Check this guide
2. Review job logs in GitLab
3. Ask in team chat
4. Consult [docs/security.md](security.md) for developer guide

---

**Remember:** Security jobs are there to help you catch issues before they reach production!
