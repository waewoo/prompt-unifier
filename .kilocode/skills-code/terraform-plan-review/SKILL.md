---
name: terraform-plan-review
description: Guides systematic review of terraform plan output to identify risks,
  cost impacts, and breaking changes before applying infrastructure changes.
mode: code
license: MIT
---
# Terraform Plan Review Skill

## When to Use

Apply this skill when:
- The user shares a `terraform plan` output and asks for a review
- The user asks "is it safe to apply this plan?"
- A plan output is pasted and approval or feedback is expected

Do NOT apply when the user is writing Terraform code (use `terraform-module` instead) or when no plan output is present.

## Step 1 — Summary Check

Read the plan summary line:

```
Plan: X to add, Y to change, Z to destroy.
```

- **Destroys > 0**: treat as high-risk — examine every destroy carefully
- **Large add counts**: may indicate a state drift or wrong workspace

## Step 2 — Classify Each Change

For each resource in the plan, classify it:

| Symbol | Meaning | Risk |
|---|---|---|
| `+` | Create | Low (usually) |
| `~` | Update in-place | Medium |
| `-/+` | Destroy & recreate | High |
| `-` | Destroy | High |
| `<=` | Data source read | Low |

## Step 3 — High-Risk Patterns

Flag immediately if you see:

- **Stateful resources destroyed**: databases, S3 buckets, persistent volumes, secrets
- **`-/+` on RDS/CloudSQL**: causes downtime and potential data loss
- **IAM policy replacement**: may break running services immediately
- **VPC/subnet/security group changes**: network disruption risk
- **`force_new_resource` on nodes**: node pool recreation drains workloads

## Step 4 — Sensitive Values

Check for `(sensitive value)` in the plan. Verify:
- Secrets are sourced from Vault or secret manager, not hardcoded
- No plaintext passwords in `locals` or `variables`

## Step 5 — Cost Estimation

Note resource types that affect cost:
- Instance type changes (downsizing vs upsizing)
- Storage class changes
- New persistent disks or load balancers

## Step 6 — Output Your Review

Structure your review as:

```
## Terraform Plan Review

**Risk level**: Low / Medium / High

**Summary**: <what this plan does in plain language>

**Concerns**:
- [ ] <specific concern 1>
- [ ] <specific concern 2>

**Recommendation**: Approve / Approve with conditions / Block
```

Always recommend a dry-run in a staging environment before applying to production.