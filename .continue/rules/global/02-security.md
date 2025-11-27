---
name: Global Security Standards
description: Baseline security principles and practices for all infrastructure and
  application code.
globs:
- '**/*'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- security
- standards
- iam
- secrets
- sast
- global
author: prompt-unifier
language: en
---
# Global Security Standards

This document defines the minimum security requirements that must be implemented in all projects,
code, and infrastructure.

## 1. Principle of Least Privilege

- **IAM**: All Identity and Access Management (IAM) policies, whether for users or services (e.g.,
  Kubernetes Service Accounts, AWS IAM Roles), must grant only the minimum permissions required to
  perform their intended function.
- **Avoid Wildcards**: Never use wildcard (`*`) permissions for actions or resources in IAM
  policies. Be explicit.
- **Regular Review**: Permissions should be reviewed periodically (e.g., quarterly) to remove any
  that are no longer needed.

## 2. Secrets Management

- **No Hardcoded Secrets**: Secrets (API keys, passwords, database credentials, certificates) must
  **NEVER** be hardcoded in source code, configuration files, or committed to Git.
- **Centralized Vault**: Use a dedicated secrets management tool like HashiCorp Vault, AWS Secrets
  Manager, or Azure Key Vault.
- **Injection at Runtime**: Secrets should be injected into applications or infrastructure at
  runtime (e.g., via environment variables in Kubernetes, Ansible Vault for playbooks).
- **Terraform State**: The Terraform state file is a sensitive asset and must be treated as a
  secret. It must be stored in a secure, encrypted remote backend with strict access controls.
- **Rotation**: Implement a strategy for rotating secrets regularly.

## 3. Secure Software Development Lifecycle (SSDLC)

### Static and Dynamic Analysis

- **SAST (Static Application Security Testing)**: Automated static analysis tools (e.g., `tfsec`,
  `checkov` for Terraform; `semgrep`, `snyk` for Python) must be integrated into the CI/CD pipeline
  to scan for vulnerabilities on every commit.
- **DAST (Dynamic Application Security Testing)**: For web applications, dynamic analysis should be
  performed periodically in staging environments to find runtime vulnerabilities.

### Dependency Scanning

- **Vulnerability Scanning**: All third-party dependencies (e.g., Python packages, Terraform
  providers, Docker base images) must be scanned for known vulnerabilities.
- **Automated Updates**: Use tools like Dependabot or Renovate to automatically create pull requests
  for updating vulnerable dependencies.
- **Base Images**: Use minimal, trusted, and regularly updated base images for containers (e.g.,
  `distroless`, `alpine`).

### Code Review

- **Security Focus**: All code reviews must include a security check. Reviewers should look for
  common vulnerabilities like those in the OWASP Top 10.
- **Checklist**: Consider using a security checklist during PR reviews to ensure consistency.

## 4. Network Security

- **Defense in Depth**: Employ multiple layers of security controls.
- **Firewalls/Security Groups**: Network access must be restricted by default. Only open ports and
  protocols that are explicitly required.
- **Encryption in Transit**: All network communication between services, and between clients and
  services, must be encrypted using TLS 1.2 or higher.
- **Encryption at Rest**: All data stored at rest (e.g., in databases, object storage) must be
  encrypted.