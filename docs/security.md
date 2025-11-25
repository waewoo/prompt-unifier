# Security Guide for Developers

This guide explains how to use the security tools in this project and provides best practices for
secure development.

## Table of Contents

1. [Overview of Security Tools](#overview-of-security-tools)
1. [Getting Started](#getting-started)
1. [Pre-commit Hooks](#pre-commit-hooks)
1. [Handling Detected Secrets](#handling-detected-secrets)
1. [Fixing Bandit Issues](#fixing-bandit-issues)
1. [Best Practices](#best-practices)
1. [Common Errors and Solutions](#common-errors-and-solutions)

## Overview of Security Tools

This project uses a multi-layered security approach:

### Local Security (Pre-commit Hooks)

| Tool               | Purpose                                                   | Documentation                                    |
| ------------------ | --------------------------------------------------------- | ------------------------------------------------ |
| **detect-secrets** | Prevents committing secrets (API keys, tokens, passwords) | [GitHub](https://github.com/Yelp/detect-secrets) |
| **bandit**         | Python SAST - finds security vulnerabilities in code      | [Docs](https://bandit.readthedocs.io/)           |

### CI/CD Security (GitLab Pipeline)

| Tool               | Purpose                           | Stage    |
| ------------------ | --------------------------------- | -------- |
| **detect-secrets** | Scans for secrets in MR           | security |
| **bandit**         | SAST scanning                     | security |
| **safety**         | CVE database for Python packages  | security |
| **pip-audit**      | Comprehensive dependency scanning | security |

## Getting Started

### 1. Install Pre-commit Hooks

After cloning the repository, install the pre-commit hooks:

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

This will automatically run security checks before each commit.

### 2. Verify Installation

Test that hooks are working:

```bash
poetry run pre-commit run --all-files
```

You should see all checks pass:

```
ruff.....................................................................Passed
ruff-format..............................................................Passed
mypy.....................................................................Passed
Detect secrets...........................................................Passed
Bandit security linter...................................................Passed
```

## Pre-commit Hooks

### What Runs on Every Commit?

1. **Ruff** - Linting and formatting
1. **mypy** - Type checking
1. **detect-secrets** - Secret detection
1. **bandit** - Security vulnerability scanning

### Bypassing Hooks (NOT RECOMMENDED)

You can bypass hooks with `git commit --no-verify`, but **this is strongly discouraged**. Security
checks exist for a reason!

### Running Hooks Manually

```bash
# Run all hooks
poetry run pre-commit run --all-files

# Run specific hook
poetry run pre-commit run detect-secrets --all-files
poetry run pre-commit run bandit --all-files
```

## Handling Detected Secrets

### When a Secret is Detected

If you try to commit a file containing a secret, you'll see:

```
Detect secrets...........................................................Failed
- hook id: detect-secrets
- exit code: 1

ERROR: Potential secret detected in file.py:42
```

### Step 1: Identify the Secret

Check the file and line number mentioned in the error.

### Step 2: Remove the Secret

**Option A: Remove it completely** (preferred)

```python
# Bad - hardcoded secret
api_key = "sk-1234567890abcdef"

# Good - use environment variable
import os
api_key = os.getenv("API_KEY")
```

**Option B: Use configuration file** (excluded from git)

```python
# Good - load from config (in .gitignore)
from config import load_config
api_key = load_config()["api_key"]
```

### Step 3: Add to Baseline (if legitimate test data)

If the "secret" is actually test data or a fake example:

```bash
# Update baseline
poetry run detect-secrets scan --update .secrets.baseline

# Audit the new finding
poetry run detect-secrets audit .secrets.baseline
# Press 'n' to mark as false positive
```

### Example: Test Fixtures

```python
# tests/test_auth.py
# This is OK - it's a fake key for testing
FAKE_API_KEY = "test_key_12345_not_real"
```

Add this to `.secrets.baseline` to prevent false positives.

## Fixing Bandit Issues

### Common Bandit Findings

#### 1. SQL Injection (B608)

```python
# Bad - vulnerable to SQL injection
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# Good - use parameterized queries
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

#### 2. Use of eval() / exec() (B307)

```python
# Bad - dangerous code execution
result = eval(user_input)

# Good - use ast.literal_eval for safe evaluation
import ast
result = ast.literal_eval(user_input)
```

#### 3. Weak Cryptography (B303, B304)

```python
# Bad - MD5 is cryptographically weak
import hashlib
hash = hashlib.md5(data)

# Good - use SHA-256 or stronger
hash = hashlib.sha256(data)
```

#### 4. Insecure Deserialization (B301)

```python
# Bad - pickle is unsafe with untrusted data
import pickle
data = pickle.loads(user_data)

# Good - use JSON for untrusted data
import json
data = json.loads(user_data)
```

#### 5. Hardcoded Passwords (B105, B106)

```python
# Bad - hardcoded password
password = "supersecret123"

# Good - use environment variables
import os
password = os.getenv("DB_PASSWORD")
```

### Suppressing False Positives

If you're certain a finding is a false positive:

```python
# Use # nosec comment with justification
password = "test_password_for_fixtures"  # nosec B105 - test fixture only
```

**Important:** Always add a comment explaining why it's safe!

## Best Practices

### 1. Credential Management

**DO:**

- Store secrets in environment variables
- Use SSH keys for Git authentication
- Use secure credential managers (e.g., Vault, AWS Secrets Manager)
- Rotate credentials regularly

**DON'T:**

- Hardcode secrets in code
- Commit `.env` files with real credentials
- Share credentials via email or chat
- Use personal access tokens in URLs

### 2. SSH Keys vs Tokens

**Recommended: SSH Keys**

```bash
# Generate SSH key (ed25519 - modern and secure)
ssh-keygen -t ed25519 -C "prompt-unifier-gitlab" -f ~/.ssh/id_ed25519

# Add public key to GitLab/GitHub
cat ~/.ssh/id_ed25519.pub

# Use SSH URL
poetry run prompt-unifier sync --repo git@gitlab.com:username/repo.git
```

**Avoid: Tokens in URLs**

```bash
# NEVER do this - token will be in logs and history
poetry run prompt-unifier sync --repo https://user:glpat-xyz@gitlab.com/user/repo.git
```

### 3. Safe Git Usage

```bash
# Good practices
git add .
git commit -m "feat: add new feature"  # Pre-commit hooks will run

# Check what you're committing
git diff --cached

# Verify no secrets in staging area
poetry run detect-secrets scan
```

### 4. Dependency Security

```bash
# Check for vulnerable dependencies
poetry run safety check

# Check with pip-audit
poetry run pip-audit

# Update vulnerable packages
poetry update <package-name>
```

## Common Errors and Solutions

### Error: "No such `GitLabTokenDetector` plugin"

**Cause:** Version mismatch between baseline and detect-secrets version

**Solution:**

```bash
# Regenerate baseline with current version
poetry run detect-secrets scan . > .secrets.baseline

# Or update pre-commit version
poetry run pre-commit autoupdate
```

### Error: "Potential secret detected" for test data

**Cause:** Test fixtures flagged as secrets

**Solution:**

```bash
# Add to baseline
poetry run detect-secrets scan --update .secrets.baseline

# Audit and mark as false positive
poetry run detect-secrets audit .secrets.baseline
```

### Error: Bandit fails with "Module not found"

**Cause:** Using pre-commit repo instead of local Poetry environment

**Solution:** Already configured to use local hook in `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: bandit
      entry: poetry run bandit
      language: system
```

### Error: Pre-commit hooks not running

**Cause:** Hooks not installed

**Solution:**

```bash
# Install hooks
poetry run pre-commit install

# Verify
poetry run pre-commit run --all-files
```

### Error: Safety reports vulnerabilities in dev dependencies

**Cause:** Dev dependencies with known CVEs

**Solution:**

```bash
# Check severity
poetry run safety check

# Update if critical
poetry update

# Ignore if acceptable risk (dev only)
# Add to safety policy file
```

## Testing Security Features

### Test Secrets Detection

Create a test file with a fake secret:

```bash
# Create test file
echo "api_key = 'sk-1234567890abcdef'" > test_secret.py

# Try to add it
git add test_secret.py

# Try to commit (should be blocked)
git commit -m "test"

# Clean up
git reset HEAD test_secret.py
rm test_secret.py
```

### Test SAST Detection

Create a file with a security issue:

```bash
# Create test file
echo "eval(user_input)" > test_vuln.py

# Try to commit (should be blocked)
git add test_vuln.py
git commit -m "test"

# Clean up
rm test_vuln.py
```

## CI/CD Security Pipeline

All security checks also run in GitLab CI on every merge request:

1. **Secrets scan** - Blocks merge if secrets detected
1. **SAST scan** - Blocks merge if vulnerabilities found
1. **Dependency scan** - Blocks merge if critical CVEs found

See `docs/ci-security.md` for details on interpreting CI security reports.

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Common web vulnerabilities
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [detect-secrets Documentation](https://github.com/Yelp/detect-secrets)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [GitLab Security Scanning](https://docs.gitlab.com/ee/user/application_security/)

## Questions?

If you have questions about security practices or tools:

1. Check this guide first
1. Review the main [SECURITY.md](../SECURITY.md)
1. Ask in team chat or create an issue

______________________________________________________________________

**Remember:** Security is everyone's responsibility. When in doubt, ask!
