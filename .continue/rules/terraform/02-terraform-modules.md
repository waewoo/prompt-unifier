---
name: Terraform Module Standards
description: Best practices for designing, developing, and consuming reusable Terraform
  modules.
globs:
- modules/**/*.tf
alwaysApply: false
category: infrastructure
version: 1.0.0
tags:
- terraform
- modules
- standards
- reusability
- versioning
author: prompt-manager
language: hcl
---
# Terraform Module Standards

This document outlines the best practices for creating and consuming Terraform modules, which are key to building scalable and maintainable infrastructure as code.

## 1. Module Structure

A well-structured module is easy to understand, use, and maintain.

- **`main.tf`**: Contains the primary resources defined by the module.
- **`variables.tf`**: Defines all input variables for the module. Each variable must have a `description`, `type`, and `default` value (if applicable).
- **`outputs.tf`**: Defines all output values exposed by the module. Each output must have a `description`.
- **`versions.tf`**: Specifies the required Terraform version and provider versions for the module.
- **`README.md`**: A comprehensive README is crucial for module usability. (See Global Documentation Standards for details).
- **`LICENSE`**: Include a license file.
- **`examples/`**: (Optional but recommended) A directory containing example usage of the module.

```
# Example module structure
.
├── my-vpc-module/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── versions.tf
│   ├── README.md
│   ├── LICENSE
│   └── examples/
│       └── simple-vpc/
│           ├── main.tf
│           └── variables.tf
```

## 2. Input Variables (`variables.tf`)

- **Descriptive Names**: Variable names should clearly indicate their purpose.
- **Type Constraints**: Always specify a `type` for variables (e.g., `string`, `number`, `bool`, `list(string)`, `map(string)`, `object`).
- **Descriptions**: Every variable must have a `description` explaining its purpose, accepted values, and any constraints.
- **Default Values**: Provide sensible `default` values where possible to make the module easier to use. If a variable is mandatory, omit the `default`.
- **Sensitive Variables**: Mark sensitive variables (e.g., passwords) with `sensitive = true` to prevent them from being displayed in `terraform plan` or `terraform apply` output.

```terraform
variable "region" {
  description = "AWS region where resources will be deployed."
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type for the web server."
  type        = string
  default     = "t3.micro"
  validation {
    condition     = contains(["t3.micro", "t3.small", "t3.medium"], var.instance_type)
    error_message = "Instance type must be one of t3.micro, t3.small, or t3.medium."
  }
}

variable "db_password" {
  description = "Password for the database user."
  type        = string
  sensitive   = true
}
```

## 3. Output Values (`outputs.tf`)

- **Descriptive Names**: Output names should clearly indicate what value they represent.
- **Descriptions**: Every output must have a `description` explaining its purpose.
- **Sensitive Outputs**: Mark sensitive outputs with `sensitive = true` to prevent them from being displayed in `terraform plan` or `terraform apply` output.
- **Minimize Outputs**: Only expose outputs that are necessary for consuming modules or for external systems. Avoid exposing internal details.

```terraform
output "vpc_id" {
  description = "The ID of the created VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "A list of IDs of the public subnets."
  value       = aws_subnet.public.*.id
}

output "db_connection_string" {
  description = "Connection string for the database."
  value       = "postgresql://${aws_db_instance.main.address}:${aws_db_instance.main.port}/${aws_db_instance.main.name}"
  sensitive   = true
}
```

## 4. Module Versioning

- **Semantic Versioning**: Use [Semantic Versioning](https://semver.org/) (e.g., `v1.0.0`, `v2.1.3`) for your modules.
- **Source Reference**: Always specify a version constraint when referencing a module to ensure predictable behavior.
- **Benefit**: Allows consumers to upgrade modules safely and prevents unexpected breaking changes.

```terraform
# Good: Pin to a specific major version
module "vpc" {
  source = "git::https://github.com/my-org/terraform-modules.git//aws/vpc?ref=v1.x"
  # ...
}

# Better: Pin to a specific version
module "s3_bucket" {
  source = "git::https://github.com/my-org/terraform-modules.git//aws/s3-bucket?ref=v1.2.0"
  # ...
}

# Bad: No version specified, will always use latest (potentially breaking)
module "ec2" {
  source = "git::https://github.com/my-org/terraform-modules.git//aws/ec2"
  # ...
}
```

## 5. Module Sources

- **Terraform Registry**: For public or widely shared modules, use the Terraform Registry.
- **Git Repositories**: For private modules, use Git repositories (GitHub, GitLab, Bitbucket). Specify the path to the module within the repository and the desired version.
- **Local Paths**: For modules under active development or very specific to a single project, local paths can be used. Avoid for shared modules.

## 6. Module Composition

- **Principle**: Build complex infrastructure by composing smaller, single-purpose modules.
- **Benefit**: Reduces complexity, improves testability, and increases reusability.
- **Example**: A `web-app` module might compose a `vpc` module, an `ec2-instance` module, and a `rds-database` module.

```terraform
# In modules/web-app/main.tf
module "vpc" {
  source = "../../modules/vpc" # Relative path to a local module
  # ...
}

module "web_server" {
  source = "../../modules/ec2-instance"
  vpc_id = module.vpc.vpc_id
  # ...
}

module "database" {
  source = "../../modules/rds-database"
  subnet_ids = module.vpc.private_subnet_ids
  # ...
}
```