---
name: terraform-module
description: Guides creation of reusable, well-structured Terraform modules following
  HashiCorp best practices.
mode: code
license: MIT
---
# Terraform Module Skill

## When to Use

Apply this skill when:
- The user asks to create, write, or scaffold a new Terraform module
- The user asks to refactor Terraform code into a reusable module
- The user asks "how should I structure this Terraform code?"
- Infrastructure code needs to be made reusable across environments or teams

Do NOT apply when the user is reviewing a `terraform plan` output (use `terraform-plan-review` instead).

## Module Structure

```
modules/my-module/
├── main.tf          # Core resources
├── variables.tf     # Input variables
├── outputs.tf       # Output values
├── versions.tf      # Required providers and Terraform version
└── README.md        # Usage documentation
```

## versions.tf (always include)

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

## variables.tf — Patterns

```hcl
variable "name" {
  description = "Name prefix applied to all resources."
  type        = string

  validation {
    condition     = length(var.name) > 0 && length(var.name) <= 32
    error_message = "name must be between 1 and 32 characters."
  }
}

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}

variable "enable_feature" {
  description = "Set to true to enable the optional feature."
  type        = bool
  default     = false
}
```

## outputs.tf — Patterns

```hcl
output "id" {
  description = "The ID of the created resource."
  value       = aws_resource.this.id
}

output "arn" {
  description = "The ARN of the created resource."
  value       = aws_resource.this.arn
  sensitive   = false
}
```

## main.tf — Best Practices

### Use `locals` for Computed Values
```hcl
locals {
  name_prefix = "${var.environment}-${var.name}"
  common_tags = merge(var.tags, {
    Environment = var.environment
    ManagedBy   = "terraform"
  })
}

resource "aws_s3_bucket" "this" {
  bucket = local.name_prefix
  tags   = local.common_tags
}
```

### Use `count` or `for_each` for Conditional/Multiple Resources
```hcl
# Conditional resource
resource "aws_cloudwatch_log_group" "this" {
  count = var.enable_logging ? 1 : 0
  name  = "/aws/${local.name_prefix}"
}

# Multiple resources from a map
resource "aws_iam_role" "this" {
  for_each = var.roles
  name     = "${local.name_prefix}-${each.key}"
}
```

## Module Usage (calling side)

```hcl
module "my_service" {
  source  = "./modules/my-module"

  name        = "my-service"
  environment = "prod"
  tags        = { Team = "platform" }
}

output "service_id" {
  value = module.my_service.id
}
```

## Checklist Before Committing

- [ ] `versions.tf` pins Terraform and provider versions
- [ ] All variables have `description` and `type`
- [ ] All outputs have `description`
- [ ] No hardcoded account IDs, regions, or secrets
- [ ] `terraform fmt` applied
- [ ] `terraform validate` passes
- [ ] `tflint` or `checkov` run for security checks
- [ ] README documents inputs, outputs, and usage example