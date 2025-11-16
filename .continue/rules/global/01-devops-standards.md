---
name: Global DevOps Standards
description: General engineering and workflow standards applicable to all projects.
globs:
- '**/*'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- devops
- git
- standards
- workflow
- global
author: prompt-manager
language: en
---
# Global DevOps Standards

This document outlines the foundational engineering practices and workflows that apply across all technologies and repositories.

## 1. Version Control with Git

### Branching Strategy
- **Main Branch**: `main` is the single source of truth and should always be in a deployable state. Direct commits to `main` are forbidden.
- **Feature Branches**: All new work (features, bugfixes) must be done on a feature branch, created from `main`.
- **Branch Naming**: Branches should be named descriptively, including the ticket/issue number and a short description.
  - **Format**: `<type>/<ticket-id>-<short-description>`
  - **Examples**: `feature/PROJ-123-add-user-auth`, `fix/PROJ-456-resolve-null-pointer`

### Commit Messages
- **Convention**: All commit messages must follow the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/) specification. This creates a clean, readable history and enables automated versioning and changelog generation.

- **Structure**:
  ```
  <type>[optional scope]: <description>

  [optional body]

  [optional footer(s)]
  ```

- **Types**: The `<type>` must be one of the following:
  - `feat`: A new feature for the user.
  - `fix`: A bug fix for the user.
  - `perf`: A code change that improves performance.
  - `refactor`: A code change that neither fixes a bug nor adds a feature.
  - `docs`: Documentation only changes.
  - `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc).
  - `test`: Adding missing tests or correcting existing tests.
  - `build`: Changes that affect the build system or external dependencies (e.g., npm, poetry).
  - `ci`: Changes to CI configuration files and scripts (e.g., GitHub Actions, GitLab CI).
  - `chore`: Other changes that don't modify `src` or `test` files (e.g., updating `.gitignore`).

- **Scope (Optional)**: The `<scope>` should be a noun describing the section of the codebase affected (e.g., `auth`, `api`, `parser`, `ci`).

- **Subject**: The `<description>` must be a concise summary of the change, in the imperative mood (e.g., "add", "fix", "change").

- **Body (Optional)**: The body provides additional context, explaining the "why" behind the change.

- **Footer (Optional)**: The footer is used for referencing issues (`Refs: #123`) or indicating breaking changes. A `BREAKING CHANGE:` footer is **required** for any commit that introduces a breaking change.

- **Example**:
  ```
  feat(api): add rate limiting to login endpoint

  To enhance security and prevent brute-force attacks, a rate limiter
  has been added to the /api/v1/login endpoint. It is configured
  to allow 10 requests per minute per IP address.

  BREAKING CHANGE: The `authenticate_user` function now returns an object
  with a `status` field instead of a boolean. Callers must be updated
  to handle the new response structure.

  Refs: #456
  ```

### Pull Requests (PRs)
- **Requirement**: All changes must be submitted via a Pull Request.
- **Review**: At least one other engineer must review and approve the PR before merging.
- **CI/CD**: All automated checks (linting, testing, security scans) must pass before a PR can be merged.
- **Description**: The PR description should clearly explain the "what" and the "why" of the change, linking to the relevant issue/ticket.

## 2. "You Build It, You Run It" Philosophy

- **Ownership**: The team that builds a service is responsible for its operation, monitoring, and maintenance in production.
- **Observability**: Services must expose metrics, logs, and traces to be easily monitored.
    - **Logging**: Structured JSON logs sent to a central logging platform.
    - **Metrics**: Key application and business metrics exposed via a `/metrics` endpoint (Prometheus format).
    - **Tracing**: Distributed tracing implemented for all API calls and asynchronous jobs.
- **On-Call**: The development team participates in the on-call rotation for the services they own.

## 3. Code Quality and Consistency

- **Linting**: All code must pass the linter configured for the specific language (e.g., Ruff for Python, `terraform fmt` for Terraform).
- **Formatting**: Code should be automatically formatted using tools like Black, Prettier, or `terraform fmt`.
- **Configuration**: Use pre-commit hooks to automate linting and formatting before code is committed.