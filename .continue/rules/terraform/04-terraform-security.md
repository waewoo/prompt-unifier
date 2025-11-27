---
name: Terraform Security Best Practices
description: Guidelines for writing secure Terraform configurations and managing infrastructure
  security.
globs:
- '**/*.tf'
alwaysApply: false
category: security
version: 1.0.0
tags:
- terraform
- security
- iam
- secrets
- sast
author: prompt-unifier
language: hcl
---
# Terraform Security Best Practices

This document outlines essential security practices for developing and managing infrastructure with
Terraform, ensuring that your cloud resources are provisioned securely.

## 1. Secrets Management

- **Never Hardcode Secrets**: As per global security standards, sensitive information (API keys,
  passwords, tokens) must **NEVER** be hardcoded in `.tf` files or committed to version control.
- **Use Dedicated Secrets Managers**: Retrieve secrets at runtime from secure stores like HashiCorp
  Vault, AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager.
- **`sensitive = true`**: Mark any Terraform variables or outputs that might contain sensitive data
  with `sensitive = true` to prevent them from being displayed in logs or CLI output. This does
  *not* prevent them from being stored in the state file.

```terraform
# Good: Fetching DB password from AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "my-app/db-password"
}

resource "aws_rds_cluster_instance" "my_db" {
  # ...
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
}

# Good: Marking an output as sensitive
output "admin_api_key" {
  description = "API key for admin access."
  value       = aws_api_gateway_api_key.admin.value
  sensitive   = true
}
```

## 2. Least Privilege IAM

- **Principle**: Grant only the minimum necessary permissions to Terraform and the resources it
  provisions.
- **Terraform Execution Role**: The IAM role or user executing Terraform should have permissions
  only to manage the resources defined in the configuration. Avoid granting broad administrative
  access.
- **Resource IAM**: Configure IAM policies for the resources created by Terraform (e.g., EC2
  instances, Lambda functions) to follow the least privilege principle.
- **Avoid `*`**: Never use wildcard (`*`) for actions or resources in IAM policies. Be explicit
  about allowed actions and resources.

```terraform
# Bad: Overly permissive IAM policy
resource "aws_iam_policy" "bad_policy" {
  name = "bad-admin-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "*",
        Effect   = "Allow",
        Resource = "*",
      },
    ],
  })
}

# Good: Least privilege IAM policy
resource "aws_iam_policy" "good_policy" {
  name = "s3-read-only-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = [
          "s3:GetObject",
          "s3:ListBucket",
        ],
        Effect   = "Allow",
        Resource = [
          "arn:aws:s3:::my-data-bucket",
          "arn:aws:s3:::my-data-bucket/*",
        ],
      },
    ],
  })
}
```

## 3. Security Validation and Scanning

- **Static Analysis (SAST)**: Integrate security scanning tools into your CI/CD pipeline to
  automatically detect misconfigurations and vulnerabilities in your Terraform code.
  - **`tfsec`**: Scans Terraform code for potential security issues and misconfigurations.
  - **`Checkov`**: Identifies security and compliance issues in Infrastructure as Code.
  - **`Snyk IaC`**: Finds and fixes vulnerabilities in Terraform, CloudFormation, Kubernetes, etc.
- **Pre-commit Hooks**: Use `pre-commit` hooks to run `terraform fmt` and `terraform validate`
  before committing, and consider adding `tfsec` or `checkov` for early feedback.

## 4. Code Review and Approval

- **Mandatory Code Review**: All Terraform changes must undergo a thorough code review by at least
  one other engineer.
- **Security Focus**: Reviewers should specifically look for:
  - Overly permissive IAM policies.
  - Hardcoded secrets.
  - Publicly exposed resources (e.g., S3 buckets, security groups open to `0.0.0.0/0`).
  - Missing encryption for data at rest or in transit.
- **Approval Gates**: Require successful completion of all automated security scans and manual
  approval before `terraform apply` can be executed, especially for production environments.

## 5. Network Security

- **Restrict Ingress/Egress**: Configure network security groups, firewalls, and network ACLs to
  restrict traffic to the absolute minimum required.
- **No Public Exposure by Default**: Resources should not be publicly accessible unless explicitly
  required and justified (e.g., a public web server).
- **Encryption in Transit**: Ensure all communication between components is encrypted (e.g., using
  TLS for databases, API endpoints).

## 6. Data Protection

- **Encryption at Rest**: Ensure all data storage resources (databases, object storage, disks) are
  configured with encryption at rest.
- **Backup and Recovery**: Implement robust backup and recovery strategies for critical data stores
  provisioned by Terraform.
- **Data Classification**: Understand and classify the sensitivity of the data your infrastructure
  will handle, and apply appropriate controls.