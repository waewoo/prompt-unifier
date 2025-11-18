# Manual Testing Guide - Prompt Unifier

This guide details all manual tests to be performed to validate all features of the **prompt-unifier** application.

---

## 📋 Table of Contents

| Section | Description |
|---------|-------------|
| [Prerequisites](#prerequisites) | Installation and pre-requisite verification |
| [Basic Commands](#basic-commands) | Help and global options tests |
| [Init Command](#init-command) | Project initialization tests |
| [Sync Command](#sync-command) | Data synchronization tests |
| [Status Command](#status-command) | Status display tests |
| [Validate Command](#validate-command) | File validation tests |
| [Deploy Command](#deploy-command) | Deployment to Continue tests |
| [Recursive Discovery](#recursive-discovery) | Tests with subdirectories |
| [Error Handling](#error-handling) | Error case tests |
| [Complete Workflows](#complete-workflows) | Real scenario tests |
| [Cleanup](#cleanup) | Test resources cleanup |

---

## Prerequisites

### Installation

```bash
cd /root/travail/prompt-unifier
poetry install
```

✓ **Expected result:** Successful installation of all dependencies

### Verification

```bash
poetry run prompt-unifier --version
```

✓ **Expected result:** Version display (ex: `0.1.0`)

---

## Basic Commands

### Test 1.1: General help display

```bash
poetry run prompt-unifier --help
```

✓ **Expected result:**
- List of available commands: `init`, `sync`, `status`, `validate`, `deploy`
- Short description of each command
- Global options (`--help`, `--version`)

### Test 1.2: Help for each command

```bash
poetry run prompt-unifier init --help
poetry run prompt-unifier sync --help
poetry run prompt-unifier status --help
poetry run prompt-unifier validate --help
poetry run prompt-unifier deploy --help
```

✓ **Expected result:** Each command displays its description, options and usage examples

---

## Init Command

### Test 2.1: Simple initialization

```bash
mkdir -p /tmp/test-pm-1 && cd /tmp/test-pm-1
poetry run prompt-unifier init
```

✓ **Expected result:**
- ✓ Message "Initialization complete"
- Creation of `.prompt-unifier/config.yaml`
- Creation of `~/.prompt-unifier/storage/{prompts,rules}` with `.gitignore`

**Created config.yaml file:**

```yaml
repos: null
last_sync_timestamp: null
repo_metadata: null
storage_path: /root/.prompt-unifier/storage
```

### Test 2.2: Initialization with custom storage

```bash
mkdir -p /tmp/test-pm-2 && cd /tmp/test-pm-2
poetry run prompt-unifier init --storage-path /tmp/custom-storage
```

✓ **Expected result:** Config with `storage_path: /tmp/custom-storage`

### Test 2.3: Re-initialization (expected error)

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier init  # Fails - already initialized
```

✗ **Expected result:** Error "Project is already initialized" (Code: 1)

---

## Sync Command

### Test 3.1: Sync without initialization (error)

```bash
mkdir -p /tmp/test-pm-3 && cd /tmp/test-pm-3
poetry run prompt-unifier sync --repo git@gitlab.com:waewoo/prompt-unifier-data.git
```

✗ **Expected result:** Error "Configuration not found" (Code: 1)

### Test 3.2: First synchronization (single repository)

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync --repo git@gitlab.com:waewoo/prompt-unifier-data.git
```

✓ **Expected result:**
- Messages: "Syncing prompts..." → "Cloning repository..." → "Extracting prompts..." → "✓ Sync complete"
- Config updated with `repos`, `last_sync_timestamp`, `repo_metadata`
- Files in `~/.prompt-unifier/storage/prompts/`

**Created config after sync:**

```yaml
repos:
  - url: git@gitlab.com:waewoo/prompt-unifier-data.git
    branch: main
last_sync_timestamp: "2024-11-18T14:30:00Z"
repo_metadata:
  - url: git@gitlab.com:waewoo/prompt-unifier-data.git
    branch: main
    commit: abc1234
    timestamp: "2024-11-18T14:30:00Z"
storage_path: /root/.prompt-unifier/storage
```

### Test 3.3: Subsequent synchronization (without URL)

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync  # Read URLs from config
```

✓ **Expected result:** Successful sync using configured repository URLs

### Test 3.4: Multi-repository synchronization

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync \
  --repo git@gitlab.com:waewoo/prompt-unifier-data.git \
  --repo git@gitlab.com:company/global-prompts.git \
  --repo git@gitlab.com:team/team-prompts.git
```

✓ **Expected result:**
- All three repositories synced successfully
- Last-wins merge strategy: if multiple repos have the same file, last repo wins
- Config updated with all three repositories in `repos` list
- Each repository tracked separately in `repo_metadata` with individual commit hashes
- Files from all repos merged in `~/.prompt-unifier/storage/prompts/`

**Multi-repo config structure:**

```yaml
repos:
  - url: git@gitlab.com:waewoo/prompt-unifier-data.git
    branch: main
  - url: git@gitlab.com:company/global-prompts.git
    branch: main
  - url: git@gitlab.com:team/team-prompts.git
    branch: develop
last_sync_timestamp: "2024-11-18T14:35:00Z"
repo_metadata:
  - url: git@gitlab.com:waewoo/prompt-unifier-data.git
    branch: main
    commit: abc1234
    timestamp: "2024-11-18T14:35:00Z"
  - url: git@gitlab.com:company/global-prompts.git
    branch: main
    commit: def5678
    timestamp: "2024-11-18T14:35:00Z"
  - url: git@gitlab.com:team/team-prompts.git
    branch: develop
    commit: ghi9012
    timestamp: "2024-11-18T14:35:00Z"
storage_path: /root/.prompt-unifier/storage
```

### Test 3.5: Sync with invalid URL (error)

```bash
poetry run prompt-unifier sync --repo https://invalid-url.com/repo.git
```

✗ **Expected result:** Network error (Code: 1)

---

## Status Command

### Test 4.1: Status without initialization (error)

```bash
mkdir -p /tmp/test-pm-5 && cd /tmp/test-pm-5
poetry run prompt-unifier status
```

✗ **Expected result:** Error "Configuration not found" (Code: 1)

### Test 4.2: Status after init (before sync)

```bash
cd /tmp/test-pm-1 && rm -rf .prompt-unifier
poetry run prompt-unifier init
poetry run prompt-unifier status
```

✓ **Expected result:**
- Displays storage path
- "Repository: Not configured"
- Message suggesting to run `sync`

### Test 4.3: Status after successful sync (single repository)

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync --repo git@gitlab.com:waewoo/prompt-unifier-data.git
poetry run prompt-unifier status
```

✓ **Expected result:**
- Repository URL
- "Last sync: X minutes ago"
- "✓ Up to date" or "⚠ Updates available (X commits behind)"

### Test 4.4: Status with multiple repositories

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync \
  --repo git@gitlab.com:waewoo/prompt-unifier-data.git \
  --repo git@gitlab.com:company/global-prompts.git
poetry run prompt-unifier status
```

✓ **Expected result:**
- Multiple repository URLs listed with individual commit info
- Each repository shows its branch and last commit
- "Last sync: X minutes ago" (overall sync timestamp)
- Individual status for each repository if updates available

---

## Validate Command

### Test 5.1: Validation of valid prompts

```bash
mkdir -p /tmp/test-prompts
cat > /tmp/test-prompts/example.md << 'EOF'
---
name: example-prompt
description: Prompt example
version: 1.0.0
author: Test User
tags:
  - example
  - test
---

# Example Prompt

Variables:
- {{var1}}: Description 1
- {{var2}}: Description 2
EOF

poetry run prompt-unifier validate /tmp/test-prompts
```

✓ **Expected result:** Success message, counted valid files (Code: 0)

### Test 5.2: Validation in JSON

```bash
poetry run prompt-unifier validate /tmp/test-prompts --json
```

✓ **Expected result:** JSON format output with results (Code: 0)

### Test 5.3: Validation of non-existent directory (error)

```bash
poetry run prompt-unifier validate /tmp/does-not-exist
```

✗ **Expected result:** Error "Directory does not exist" (Code: 1)

### Test 5.4: Validation of valid rules

```bash
mkdir -p /tmp/test-rules
cat > /tmp/test-rules/python-style.md << 'EOF'
name: python-style-guide
description: Python coding standards
type: rule
category: coding-standards
tags: [python, pep8]
version: 1.0.0
>>>
# Python Style Guide

- Use snake_case for functions
- Use PascalCase for classes
EOF

poetry run prompt-unifier validate /tmp/test-rules
```

✓ **Expected result:** Successful validation including rules (Code: 0)

### Test 5.5: Validation with errors (malformed YAML file)

```bash
mkdir -p /tmp/test-invalid
cat > /tmp/test-invalid/bad.md << 'EOF'
---
name: bad-prompt
unclosed frontmatter here

Content without proper closing
EOF

poetry run prompt-unifier validate /tmp/test-invalid
```

✗ **Expected result:** Validation error with details (Code: 1)

---

## Deploy Command

### Test 9.1: Simple deployment of a prompt

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync
poetry run prompt-unifier deploy "code-review" --handlers continue
```

✓ **Expected result:**
- File `~/.continue/prompts/code-review.md` created with frontmatter (`name`, `description`, `invokable: true`)
- Backup created if file existed (`.md.bak`)
- Message "✓ Deployment to continue successful" (Code: 0)

### Test 9.2: Deployment of a rule

```bash
poetry run prompt-unifier deploy "python-style" --handlers continue
```

✓ **Expected result:** File `~/.continue/rules/python-style.md` created (Code: 0)

### Test 9.3: Deploy with tag filtering

```bash
poetry run prompt-unifier deploy --tags python --handlers continue
```

✓ **Expected result:**
- Only prompts/rules with "python" tag deployed
- Messages for each filtered item

### Test 9.4: Deploy all items

```bash
poetry run prompt-unifier deploy --handlers continue
```

✓ **Expected result:** All prompts AND rules from storage deployed (Code: 0)

### Test 9.5: Deploy non-existent prompt (error)

```bash
poetry run prompt-unifier deploy "non-existent" --handlers continue
```

✗ **Expected result:** Error "Prompt not found in storage" (Code: 1)

### Test 9.6: Deploy with invalid handler (error)

```bash
poetry run prompt-unifier deploy "code-review" --handlers invalid
```

✗ **Expected result:** Error "ToolHandler not found" (Code: 1)

### Test 9.7: Backup verification

```bash
echo "old content" > ~/.continue/prompts/code-review.md
poetry run prompt-unifier deploy "code-review" --handlers continue
# Verify: old file in .bak, new one deployed
```

✓ **Expected result:** `.bak` file created with old content (Code: 0)

### Test 9.8: Deploy with no matches

```bash
poetry run prompt-unifier deploy --tags nonexistent --handlers continue
```

✓ **Expected result:** Message "No content files match the specified criteria" (Code: 0)

### Test 9.9: Deploy with config.yaml configuration

```bash
cat > .prompt-unifier/config.yaml << 'EOF'
repo_url: git@gitlab.com:waewoo/prompt-unifier-data.git
storage_path: ~/.prompt-unifier/storage
deploy_tags:
  - python
target_handlers:
  - continue
EOF

poetry run prompt-unifier deploy  # Without options - reads config
```

✓ **Expected result:** Only "python" tagged items deployed to continue (Code: 0)

### Test 9.10: Deploy with --clean (cleanup orphans and backups)

```bash
# Deploy some files
poetry run prompt-unifier deploy --tags python --handlers continue

# Create an orphan file and backup files (including in subdirectories)
echo "orphan" > ~/.continue/prompts/orphan.md
echo "backup" > ~/.continue/prompts/old-backup.md.bak
mkdir -p ~/.continue/prompts/subdir
echo "nested backup" > ~/.continue/prompts/subdir/nested-backup.md.bak

# Redeploy with --clean
poetry run prompt-unifier deploy --tags python --handlers continue --clean
```

✓ **Expected result:**
- Orphan file permanently deleted
- All .bak files recursively deleted (including in subdirectories)
- Message "Cleaned X orphaned file(s)" (includes both orphans and backups)
- Clean operates recursively through all subdirectories (Code: 0)

---

## Recursive Discovery

### Test 10.1: Discovery with subdirectories

```bash
mkdir -p ~/.prompt-unifier/storage/prompts/backend/api
mkdir -p ~/.prompt-unifier/storage/prompts/frontend
mkdir -p ~/.prompt-unifier/storage/rules/security/auth

# Create files at different levels
cat > ~/.prompt-unifier/storage/prompts/backend/api/api-prompt.md << 'EOF'
---
title: api-prompt
description: API development
tags: [api, backend]
version: 1.0.0
---
EOF

cat > ~/.prompt-unifier/storage/prompts/root-prompt.md << 'EOF'
---
title: root-prompt
description: Root level
tags: [general]
---
EOF

poetry run prompt-unifier deploy --handlers continue
```

✓ **Expected result:**
- All files discovered (root AND subdirectories)
- Structure preserved: `~/.continue/prompts/backend/api/api-prompt.md`, etc.

### Test 10.2: Duplicate title detection (error)

```bash
cat > ~/.prompt-unifier/storage/prompts/backend/dup.md << 'EOF'
---
title: duplicate-prompt
version: 1.0.0
---
EOF

cat > ~/.prompt-unifier/storage/prompts/frontend/dup.md << 'EOF'
---
title: duplicate-prompt
version: 1.0.0
---
EOF

poetry run prompt-unifier deploy --handlers continue
```

✗ **Expected result:**
- Error "Duplicate titles detected"
- List of paths with duplicate titles (Code: 1)

### Test 10.3: Recursive cleanup with --clean

```bash
# Deploy
poetry run prompt-unifier deploy --tags backend --handlers continue

# Create backup files in subdirectory (will be removed)
mkdir -p ~/.continue/prompts/deprecated
echo "backup" > ~/.continue/prompts/deprecated/backup.md.bak

# Create orphaned .md file in ROOT directory (will be removed)
echo "old" > ~/.continue/prompts/old-prompt.md

# Create .md file in subdirectory (will be PRESERVED - not cleaned)
echo "nested" > ~/.continue/prompts/deprecated/nested.md

# Redeploy with --clean
poetry run prompt-unifier deploy --tags backend --handlers continue --clean
```

✓ **Expected result:**
- Backup file `deprecated/backup.md.bak` deleted (recursive cleanup of .bak files)
- Orphaned .md file `old-prompt.md` in root deleted
- File `deprecated/nested.md` PRESERVED (orphaned .md in subdirectories preserved for tag filter compatibility)
- Clean removes .bak files recursively but only removes orphaned .md files from root directory (Code: 0)

### Test 10.4: Deep nesting (4+ levels)

```bash
mkdir -p ~/.prompt-unifier/storage/prompts/a/b/c/d/e
cat > ~/.prompt-unifier/storage/prompts/a/b/c/d/e/deep.md << 'EOF'
---
title: deep-prompt
version: 1.0.0
---
EOF

poetry run prompt-unifier deploy --handlers continue
test -f ~/.continue/prompts/a/b/c/d/e/deep.md && echo "✓ Deep nesting works"
```

✓ **Expected result:** Complete structure preserved, file at correct location (Code: 0)

### Test 10.5: Empty directories

```bash
mkdir -p ~/.prompt-unifier/storage/prompts/empty-dir
mkdir -p ~/.prompt-unifier/storage/rules/empty-rules

poetry run prompt-unifier deploy --handlers continue
```

✓ **Expected result:** No error, empty directories ignored (Code: 0)

### Test 10.6: Backward compatibility (root)

```bash
cat > ~/.prompt-unifier/storage/prompts/legacy.md << 'EOF'
---
title: legacy-prompt
version: 1.0.0
---
EOF

poetry run prompt-unifier deploy legacy --handlers continue
test -f ~/.continue/prompts/legacy.md && echo "✓ Root files work"
```

✓ **Expected result:** Root files continue to work (Code: 0)

---

## Error Handling

### Test 6.1: Insufficient permissions (error)

```bash
mkdir -p /tmp/no-write && chmod 555 /tmp/no-write
cd /tmp/no-write
poetry run prompt-unifier init
chmod 755 /tmp/no-write
```

✗ **Expected result:** Error "Permission denied" (Code: 1)

### Test 6.2: Retry on network error

```bash
# Test with URL that times out (multiple retries)
# Messages: "Network error. Retrying... (attempt 1/3)"
# Delays: 1s → 2s → 4s between attempts
```

✓ **Expected result:** 3 attempts, then final error (Code: 1)

---

## Complete Workflows

### Test 8.1: Team workflow (new member with single repository)

```bash
mkdir -p /tmp/team-project && cd /tmp/team-project

# Pre-existing configuration
mkdir -p .prompt-unifier
cat > .prompt-unifier/config.yaml << 'EOF'
repos:
  - url: git@gitlab.com:waewoo/prompt-unifier-data.git
    branch: main
storage_path: /root/.prompt-unifier/storage
EOF

# New member simply syncs
poetry run prompt-unifier sync
poetry run prompt-unifier status
```

✓ **Expected result:** Successful sync, config used (Code: 0)

### Test 8.2: Team workflow with multiple repositories

```bash
mkdir -p /tmp/team-multi && cd /tmp/team-multi

# Pre-existing configuration with multiple repos
mkdir -p .prompt-unifier
cat > .prompt-unifier/config.yaml << 'EOF'
repos:
  - url: git@gitlab.com:company/global-prompts.git
    branch: main
  - url: git@gitlab.com:team/team-prompts.git
    branch: develop
storage_path: /root/.prompt-unifier/storage
EOF

# New member syncs all repositories
poetry run prompt-unifier sync
poetry run prompt-unifier status
```

✓ **Expected result:**
- Both repositories synced successfully
- Files from both repos merged in storage (last-wins strategy)
- Status shows both repositories with individual commit info (Code: 0)

### Test 8.3: Daily update

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier status  # Check state
poetry run prompt-unifier sync     # Update
poetry run prompt-unifier status   # Confirm
```

✓ **Expected result:** Each command completes (Code: 0)

---

## Cleanup

### Test directories

```bash
rm -rf /tmp/test-pm-* /tmp/test-prompts* /tmp/test-rules* \
        /tmp/custom-storage /tmp/team-project /tmp/no-write
echo "✓ Test directories cleaned"
```

### Centralized storage (optional)

```bash
rm -rf ~/.prompt-unifier/
rm -rf ~/.continue/
echo "✓ Centralized storage cleaned"
```

---

## 📊 Testing Checklist

Use this checklist to track your progress:

```
Basic Commands
├─ [·] Test 1.1 - General help
├─ [·] Test 1.2 - Init help
├─ [·] Test 1.3 - Sync help
├─ [·] Test 1.4 - Status help
└─ [·] Test 1.5 - Validate, deploy help

Init
├─ [·] Test 2.1 - Simple init
├─ [·] Test 2.2 - Init custom storage
└─ [·] Test 2.3 - Re-init (error)

Sync
├─ [·] Test 3.1 - Sync without init (error)
├─ [·] Test 3.2 - First sync (single repo)
├─ [·] Test 3.3 - Subsequent sync
├─ [·] Test 3.4 - Multi-repository sync
└─ [·] Test 3.5 - Invalid URL (error)

Status
├─ [·] Test 4.1 - Status without init (error)
├─ [·] Test 4.2 - Status post-init
├─ [·] Test 4.3 - Status post-sync (single repo)
└─ [·] Test 4.4 - Status with multiple repos

Validate
├─ [·] Test 5.1 - Validate prompts
├─ [·] Test 5.2 - Validate JSON
├─ [·] Test 5.3 - Invalid directory (error)
├─ [·] Test 5.4 - Validate rules
└─ [·] Test 5.5 - Validation errors

Deploy
├─ [·] Test 9.1 - Deploy prompt
├─ [·] Test 9.2 - Deploy rule
├─ [·] Test 9.3 - Deploy + tags
├─ [·] Test 9.4 - Deploy all items
├─ [·] Test 9.5 - Deploy non-existent (error)
├─ [·] Test 9.6 - Invalid handler (error)
├─ [·] Test 9.7 - Backup verification
├─ [·] Test 9.8 - No matches
├─ [·] Test 9.9 - Config.yaml
└─ [·] Test 9.10 - Deploy --clean

Recursive Discovery
├─ [·] Test 10.1 - Subdirectories
├─ [·] Test 10.2 - Duplicate titles (error)
├─ [·] Test 10.3 - Recursive clean
├─ [·] Test 10.4 - Deep nesting
├─ [·] Test 10.5 - Empty directories
└─ [·] Test 10.6 - Backward compatibility

Error Handling
├─ [·] Test 6.1 - Permissions (error)
└─ [·] Test 6.2 - Network retry

Workflows
├─ [·] Test 8.1 - Team workflow (single repo)
├─ [·] Test 8.2 - Team workflow (multi-repo)
└─ [·] Test 8.3 - Daily update

Cleanup
├─ [·] Test directories
└─ [·] Centralized storage
```

---

## 📝 Test Notes

| Date | Tester | Success | Failures | Observations |
|------|--------|---------|----------|--------------|
| | | / | / | |

---

## 🔧 Quick Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "Reference at 'HEAD' does not exist" | Fixed bug | Check current version |
| Storage not created | Permissions | Check home directory permissions |
| Missing prompts | No prompts/ folder | Verify repository structure |
| Corrupted config.yaml | Manual editing | Delete and re-initialize |
| File conflicts in multi-repo | Multiple repos with same file | Last repo wins (last-wins strategy) |
| Wrong file version displayed | Multi-repo sync order | Check repo order in config - last repo takes precedence |
