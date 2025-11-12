# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of Prompt Manager seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

**DO NOT** open a public GitHub/GitLab issue for security vulnerabilities.

Instead, please report security vulnerabilities by emailing:

**Security Contact:** [your-security-email@example.com]

Please include the following information in your report:

- Type of vulnerability (e.g., secret exposure, code injection, etc.)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

When you report a security vulnerability, you can expect:

1. **Acknowledgment:** We will acknowledge receipt of your vulnerability report within **24 hours**

2. **Investigation:** We will investigate and validate the vulnerability

3. **Timeline:**
   - **Critical vulnerabilities:** Fix within **7 days**
   - **High severity:** Fix within **14 days**
   - **Medium severity:** Fix within **30 days**
   - **Low severity:** Fix within **90 days**

4. **Updates:** We will keep you informed of our progress throughout the process

5. **Credit:** If you wish, we will publicly credit you for responsibly disclosing the vulnerability

### Disclosure Policy

- We ask that you give us reasonable time to fix the vulnerability before public disclosure
- We will notify you when the fix is released
- Once the fix is deployed, we will publish a security advisory
- We follow coordinated disclosure practices

## Security Best Practices for Contributors

### Secret Management

- **NEVER** commit secrets, API keys, tokens, or passwords to the repository
- Use environment variables or secure credential managers
- Add sensitive files to `.gitignore`
- Use SSH keys instead of personal access tokens when possible

### Pre-commit Hooks

This project uses automated security scanning via pre-commit hooks:

- **detect-secrets:** Prevents committing secrets
- **bandit:** Detects security vulnerabilities in Python code

Install hooks with:
```bash
poetry run pre-commit install
```

### CI/CD Security Checks

Every merge request is automatically scanned for:

- **Secrets detection:** Prevents accidental credential leaks
- **SAST (Static Application Security Testing):** Identifies code vulnerabilities
- **Dependency scanning:** Detects vulnerable packages

All security checks must pass before code can be merged.

## Security Features

This project implements multiple layers of security:

### 1. Pre-commit Hooks (Local)
- Secrets detection with baseline for legitimate test fixtures
- Static security analysis with Bandit
- Blocks commits containing security issues

### 2. CI/CD Pipeline (GitLab)
- Comprehensive security scanning on every MR
- Automated vulnerability detection
- Security reports as pipeline artifacts

### 3. Dependency Management
- Regular dependency vulnerability scans
- Automated alerts for vulnerable packages
- Strict version constraints in `pyproject.toml`

## Known Security Considerations

### SSH Key Authentication

When syncing with Git repositories, we recommend using SSH keys instead of HTTPS with personal access tokens:

```bash
# Good: SSH authentication
prompt-manager sync --repo git@gitlab.com:username/repo.git

# Avoid: Token in URL (risk of exposure)
prompt-manager sync --repo https://username:TOKEN@gitlab.com/username/repo.git
```

### Local Configuration

The `.prompt-manager/config.yaml` file may contain repository URLs. Ensure this file:
- Is excluded from version control (in `.gitignore`)
- Uses SSH URLs or secure credential storage
- Has appropriate file permissions (readable only by user)

## Security Updates

We regularly update our dependencies to address security vulnerabilities. Security updates are prioritized and released as soon as possible.

To stay informed about security updates:
- Watch this repository for security advisories
- Check the changelog for security-related updates
- Subscribe to our security mailing list (if available)

## Responsible Disclosure Hall of Fame

We appreciate security researchers who responsibly disclose vulnerabilities. Contributors who have helped improve our security:

- (No vulnerabilities reported yet)

## Questions?

If you have questions about this security policy, please contact:
[your-security-email@example.com]

---

**Last Updated:** 2025-11-12
