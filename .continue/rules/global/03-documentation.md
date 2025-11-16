---
name: Global Documentation Standards
description: Guidelines for creating clear, consistent, and maintainable documentation.
globs:
- '**/*.md'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- documentation
- standards
- readme
- architecture
- global
author: prompt-manager
language: en
---
# Global Documentation Standards

This document provides the standards for documenting projects, code, and infrastructure. Good documentation is essential for maintainability, onboarding, and incident response.

## 1. README Files

Every repository, module, and component must have a `README.md` file at its root.

### Repository README
The main `README.md` at the root of a repository should include:
- **Project Title**: What the project is.
- **Description**: A brief explanation of what the project does and the problem it solves.
- **Getting Started**: How to set up a local development environment.
- **Usage**: How to run the application or use the library.
- **Testing**: How to run the test suite.
- **Deployment**: How the project is deployed (and by what tools, e.g., ArgoCD, Terraform).
- **Architecture**: A link to more detailed architecture documentation.

### Module/Role/Component README
README files for sub-components (e.g., a Terraform module, an Ansible role) should be more focused:
- **Purpose**: What the component does.
- **Inputs**: Variables, parameters, and their types/defaults.
- **Outputs**: Values returned by the component.
- **Dependencies**: Any other components or tools required.
- **Example Usage**: A clear, copy-pasteable code snippet showing how to use the component.

```terraform
# Example for a Terraform module README

## AWS S3 Bucket Module

This module creates a private S3 bucket with versioning and encryption.

### Usage

```hcl
module "private_bucket" {
  source      = "git::https://github.com/my-org/terraform-modules.git//aws/s3-private-bucket?ref=v1.2.0"
  bucket_name = "my-secure-data-bucket"
  tags = {
    Environment = "production"
    Team        = "data-eng"
  }
}
```

### Inputs

| Name          | Description                 | Type   | Default | Required |
|---------------|-----------------------------|--------|---------|----------|
| `bucket_name` | The name of the S3 bucket.  | `string` | `null`  | yes      |
| `tags`          | A map of tags to assign.    | `map(string)` | `{}`    | no       |

### Outputs

| Name        | Description                   |
|-------------|-------------------------------|
| `bucket_id` | The ID (name) of the bucket.  |
| `bucket_arn`| The ARN of the bucket.        |
```

## 2. Architecture Documentation

- **High-Level Diagrams**: Use tools like Mermaid, PlantUML, or diagrams.net to create diagrams illustrating the system architecture. These diagrams should be version-controlled alongside the code.
- **Architecture Decision Records (ADRs)**: Document significant architectural decisions in a dedicated `docs/adr/` directory. An ADR should capture:
    - **Title**: A short summary of the decision.
    - **Context**: The problem or forces at play.
    - **Decision**: The chosen solution.
    - **Consequences**: The results and tradeoffs of the decision.
- **Data Flow**: Document how data flows through the system, especially for data pipelines (e.g., Airflow DAGs).

## 3. Code Comments

- **Comment the "Why", Not the "What"**: Code should be self-documenting. Use comments to explain *why* a particular implementation was chosen, especially if it's non-obvious or involves a workaround.
- **TODOs**: Use a standard format for temporary code, workarounds, or future improvements. Include a ticket number if possible.
  - **Format**: `TODO(TICKET-123): Refactor this to use the new service class.`
- **Docstrings/Annotations**: All functions, classes, and modules must have docstrings explaining their purpose, arguments, and return values, as defined by the language-specific standards.

## 4. Runbooks and Playbooks

- **Purpose**: Create runbooks for common operational tasks and responding to alerts.
- **Location**: Store them in a central, easily accessible location (e.g., a `runbooks/` directory or a team wiki).
- **Content**: A good runbook includes:
    - **Alert Name**: The alert that triggered the runbook.
    - **Summary**: A brief description of what the alert means.
    - **Impact**: What systems or users are affected.
    - **Triage Steps**: Commands to run to diagnose the issue (e.g., `kubectl get pods`, checking logs).
    - **Resolution Steps**: How to fix the issue.
    - **Escalation**: Who to contact if the issue cannot be resolved.

```