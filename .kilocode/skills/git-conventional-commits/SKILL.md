---
name: git-conventional-commits
description: Guides writing conventional commits following the Conventional Commits
  specification with proper type, scope, and message formatting.
license: MIT
---
# Conventional Commits Skill

## When to Use

Apply this skill when:
- The user asks to write, generate, or suggest a commit message
- The user asks to review or fix an existing commit message
- The user runs `git commit` and needs help phrasing the message
- A staged diff is shown and a commit is expected

## Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## Types

| Type | Usage |
|---|---|
| `feat` | A new feature (correlates with MINOR in semver) |
| `fix` | A bug fix (correlates with PATCH in semver) |
| `docs` | Documentation only changes |
| `style` | Formatting, missing semicolons, etc. (no code change) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `build` | Changes to build system or external dependencies |
| `ci` | Changes to CI/CD configuration files and scripts |
| `chore` | Other changes that don't modify src or test files |
| `revert` | Reverts a previous commit |

## Rules

1. **type** is mandatory and must be lowercase
2. **scope** is optional; use the affected module/component (e.g., `api`, `auth`, `k8s`, `dag`)
3. **description** is mandatory: imperative, present tense, no period at end, max 72 chars
4. **Breaking changes**: add `!` after type/scope (`feat!:`) and `BREAKING CHANGE:` footer
5. Never add AI attribution ("Co-authored-by: Claude", etc.)

## Examples

```
feat(k8s): add horizontal pod autoscaler to deployment manifests

fix(dag): handle empty upstream task list in dependency resolver

ci: add sonarqube quality gate to merge request pipeline

refactor(terraform)!: rename module variables to snake_case convention

BREAKING CHANGE: all callers must update variable references
```

## Process

1. Analyze the staged diff to understand what changed
2. Choose the most specific applicable type
3. Infer the scope from the affected directory or module
4. Write the description in imperative mood ("add", "fix", "update" — not "added", "fixed")
5. Add a body if the change is non-trivial or the "why" isn't obvious