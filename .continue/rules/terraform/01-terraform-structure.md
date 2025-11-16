---
name: Terraform Project Structure
description: Standards for organizing Terraform projects to ensure scalability, maintainability,
  and collaboration.
globs:
- '**/*.tf'
alwaysApply: false
category: infrastructure
version: 1.0.0
tags:
- terraform
- standards
- structure
- modules
- environments
author: prompt-manager
language: hcl
---
# Terraform Project Structure

This document outlines best practices for structuring Terraform projects, promoting reusability, clarity, and efficient management of infrastructure across different environments.

## 1. Organization in Reusable Modules (DRY Principle)

- **Principle**: Avoid repeating yourself (DRY). Abstract common infrastructure patterns into reusable Terraform modules.
- **Benefit**: Modules promote consistency, reduce errors, and accelerate development by allowing teams to consume pre-defined, tested infrastructure components.
- **Example**: Instead of defining an S3 bucket with logging and encryption in every project, create a generic `s3-bucket` module that can be instantiated with different parameters.

```terraform
# Bad: Repeated S3 bucket definition in multiple projects
resource "aws_s3_bucket" "my_app_bucket" {
  bucket = "my-app-prod-bucket"
  acl    = "private"
  # ... many lines for logging, encryption, versioning
}

# Good: Using a reusable module
module "my_app_bucket" {
  source      = "./modules/s3-bucket" # Or a remote source
  bucket_name = "my-app-prod-bucket"
  environment = "prod"
}
```

## 2. Separation of Environments

- **Principle**: Infrastructure for different environments (e.g., `dev`, `staging`, `prod`) must be strictly separated.
- **Method**: Use distinct directories for each environment, each with its own Terraform state.
- **Benefit**: Prevents accidental changes to production from development work and allows for independent deployment pipelines.

```
# Recommended directory structure for environments
.
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── backend.tf
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ec2-instance/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── s3-bucket/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── README.md
```

## 3. Standard Files within a Configuration

Each Terraform configuration (e.g., an environment directory or a module) should adhere to a standard file naming convention for clarity.

- **`main.tf`**: Contains the primary resource definitions and module calls.
- **`variables.tf`**: Defines all input variables for the configuration.
- **`outputs.tf`**: Defines all output values exposed by the configuration.
- **`versions.tf`**: Specifies required Terraform version and provider versions.
- **`backend.tf`**: Configures the remote state backend (often placed in `environments/<env>/` directories).
- **`providers.tf`**: (Optional) Explicitly defines provider configurations if not using default.

## 4. Naming Conventions for Resources

- **Principle**: Use consistent and descriptive naming for all Terraform resources.
- **Format**: `<resource_type>_<name>_<environment>` or `<resource_type>_<name>_<purpose>`
- **Benefit**: Improves readability, makes resources easily identifiable in the cloud provider console, and helps avoid naming conflicts.
- **Example**:
  - `aws_s3_bucket.app_logs_prod`
  - `aws_instance.web_server_dev`
  - `aws_vpc.main_vpc`

## 5. Workspaces vs. Directories for Environments

- **Workspaces**: Terraform workspaces (e.g., `terraform workspace new dev`) allow managing multiple states for a single configuration.
- **Directories**: Using separate directories for each environment is generally preferred for larger, more complex projects.
- **Recommendation**:
  - **Use Directories**: For distinct environments (dev, staging, prod) where configurations might diverge significantly, and independent state management is critical. This provides stronger isolation.
  - **Use Workspaces**: For managing multiple, very similar instances of the *same* configuration within a single environment (e.g., multiple feature branches deploying temporary infrastructure, or different regions for a single application).
- **Anti-pattern**: Do not use workspaces to manage `dev`, `staging`, `prod` environments if those environments have significantly different resource definitions or require different backend configurations.