# Manual Testing Guide - Prompt Unifier

This guide details all manual tests to be performed to validate all features of the
**prompt-unifier** application.

______________________________________________________________________

## 📋 Table of Contents

| Section                                             | Description                                 |
| --------------------------------------------------- | ------------------------------------------- |
| [Prerequisites](#prerequisites)                     | Installation and pre-requisite verification |
| [Basic Commands](#basic-commands)                   | Help and global options tests               |
| [Init Command](#init-command)                       | Project initialization tests                |
| [Sync Command](#sync-command)                       | Data synchronization tests                  |
| [Status Command](#status-command)                   | Status display tests                        |
| [Validate Command](#validate-command)               | File validation tests                       |
| [Deploy Command](#deploy-command)                   | Deployment to Continue tests                |
| [Recursive Discovery](#recursive-discovery)         | Tests with subdirectories                   |
| [Kilo Code Handler Tests](#kilo-code-handler-tests) | Tests for Kilo Code handler                 |
| [Error Handling](#error-handling)                   | Error case tests                            |
| [Complete Workflows](#complete-workflows)           | Real scenario tests                         |
| [Cleanup](#cleanup)                                 | Test resources cleanup                      |

______________________________________________________________________

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

______________________________________________________________________

## Basic Commands

### Test 1.1: General help display

```bash
poetry run prompt-unifier --help
```

✓ **Expected result:**

- List of available commands: `init`, `sync`, `status`, `validate`, `deploy`
- Short description of each command
- Global options (`--help`, `--version`, `--verbose`, `--log-file`)

### Test 1.2: Help for each command

```bash
poetry run prompt-unifier init --help
poetry run prompt-unifier sync --help
poetry run prompt-unifier status --help
poetry run prompt-unifier validate --help
poetry run prompt-unifier deploy --help
```

✓ **Expected result:** Each command displays its description, options and usage examples

______________________________________________________________________

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

✓ **Expected result:** Message "Already initialized (all components exist)" (Code: 0)

______________________________________________________________________

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

- Messages: "Syncing prompts..." → "Cloning repository..." → "Extracting prompts..." → "✓ Sync
  complete"
- Config updated with `repos`, `last_sync_timestamp`, `repo_metadata`
- Files in `~/.prompt-unifier/storage/prompts/`

**Created config after sync:**

```yaml
repos:
  - url: git@gitlab.com:waewoo/prompt-unifier-data.git
    branch: main
last_sync_timestamp: "Dynamic ISO 8601 timestamp"
repo_metadata:
  - url: git@gitlab.com:waewoo/prompt-unifier-data.git
    branch: main
    commit: abc1234
    timestamp: "Dynamic ISO 8601 timestamp"
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
last_sync_timestamp: "Dynamic ISO 8601 timestamp"
repo_metadata:
  - url: git@gitlab.com:waewoo/prompt-unifier-data.git
    branch: main
    commit: abc1234
    timestamp: "Dynamic ISO 8601 timestamp"
  - url: git@gitlab.com:company/global-prompts.git
    branch: main
    commit: def5678
    timestamp: "Dynamic ISO 8601 timestamp"
  - url: git@gitlab.com:team/team-prompts.git
    branch: develop
    commit: ghi9012
    timestamp: "Dynamic ISO 8601 timestamp"
storage_path: /root/.prompt-unifier/storage
```

### Test 3.5: Sync with invalid URL (error)

```bash
poetry run prompt-unifier sync --repo https://invalid-url.com/repo.git
```

✗ **Expected result:** Network error (Code: 1)

______________________________________________________________________

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
- Displays deployment status for synced files

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
- Displays deployment status for synced files

______________________________________________________________________

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

### Test 5.6: SCAFF validation (default enabled)

```bash
mkdir -p /tmp/test-scaff
cat > /tmp/test-scaff/high-quality.md << 'EOF'
---
name: high-quality-prompt
description: Well-structured prompt following SCAFF methodology
version: 1.0.0
tags: [example]
---

# High Quality Prompt

## Context
This prompt is designed for code review workflows in a team environment.
The goal is to ensure consistent, thorough reviews that catch bugs early.

## Requirements
- Must review all changed files
- Should check for security vulnerabilities
- Must verify test coverage

## Steps
1. Review the code changes carefully
2. Check for common issues and anti-patterns
3. Verify tests cover the changes
4. Leave constructive feedback

## Expected Output
Provide detailed review comments with:
- Issues found (if any)
- Suggestions for improvement
- Approval status
EOF

poetry run prompt-unifier validate /tmp/test-scaff
```

✓ **Expected result:**

- Validation succeeds (Code: 0)
- SCAFF score displayed (should be 80+/100 - "excellent")
- Component breakdown table shows all 5 SCAFF components
- Green color coding for high score
- No SCAFF warnings (all components pass)

### Test 5.7: SCAFF validation with low quality prompt

```bash
cat > /tmp/test-scaff/low-quality.md << 'EOF'
---
name: low-quality
description: Poorly structured
---

do something
EOF

poetry run prompt-unifier validate /tmp/test-scaff
```

✓ **Expected result:**

- Validation succeeds (format is valid) (Code: 0)
- SCAFF score displayed (should be \<60/100 - "poor")
- Red color coding for low score
- Multiple SCAFF warnings with actionable suggestions:
  - SCAFF_NOT_SPECIFIC: Add specific requirements
  - SCAFF_LACKS_CONTEXT: Include background information
  - SCAFF_NOT_ACTIONABLE: Add concrete action steps
  - SCAFF_POORLY_FORMATTED: Organize with clear headings
  - SCAFF_UNFOCUSED: Content too short

### Test 5.8: Disable SCAFF validation

```bash
poetry run prompt-unifier validate /tmp/test-scaff --no-scaff
```

✓ **Expected result:**

- Validation succeeds (Code: 0)
- No SCAFF score displayed
- No SCAFF warnings shown
- Only YAML frontmatter validation performed

### Test 5.9: SCAFF validation in JSON output

```bash
poetry run prompt-unifier validate /tmp/test-scaff --json
```

✓ **Expected result:**

- JSON output includes `scaff_score` field for each file
- Score object contains:
  - `total_score` (0-100)
  - `percentage` (0.0-1.0)
  - `grade` ("excellent", "good", or "poor")
  - `components` array with 5 objects (Specific, Contextual, Actionable, Formatted, Focused)
  - Each component has: `component_name`, `score`, `max_score`, `status`

______________________________________________________________________

## List Command

### Test 7.1: List all content

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync --repo git@gitlab.com:waewoo/prompt-unifier-data.git
poetry run prompt-unifier list
```

✓ **Expected result:** A table listing all synced prompts and rules, sorted by name.

### Test 7.2: List content with verbose mode

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier -v list
```

✓ **Expected result:** A table listing all synced prompts and rules, with INFO-level logging output
showing storage path and file counts.

### Test 7.3: List content filtered by --tag

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier list --tag python
```

✓ **Expected result:** A table listing only prompts/rules tagged "python".

### Test 7.4: List content filtered by --tool

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier list --tool continue
```

✓ **Expected result:** A table listing content relevant to the "continue" tool. (This will only work
if the content has metadata linking it to a tool, which is not currently implemented in content
models)

### Test 7.5: List content sorted by --sort date

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier list --sort date
```

✓ **Expected result:** A table listing all synced prompts and rules, sorted by their last
modification date.

______________________________________________________________________

## Deploy Command

### Test 11.1: Deploy a specific prompt by name

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync
poetry run prompt-unifier deploy --name "code-review" --handlers continue
```

✓ **Expected result:**

- File `~/.continue/prompts/code-review.md` created with frontmatter (`name`, `description`,
  `invokable: true`)
- Backup created if file existed (`.md.bak`)
- Message "✓ Deployment to continue successful" (Code: 0)
- "Verification Report" displayed, with the deployed file marked as "PASSED"

### Test 11.2: Deploy to a specific handler

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync
poetry run prompt-unifier deploy --name "code-review" --handlers continue
```

✓ **Expected result:** Same as Test 11.1, ensuring deployment to the specified 'continue' handler.

### Test 11.3: Deploy to a custom base path

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync
poetry run prompt-unifier deploy --name "code-review" --handlers continue --base-path /tmp/custom-continue-path
```

✓ **Expected result:**

- File `/tmp/custom-continue-path/prompts/code-review.md` created.
- "Verification Report" displayed, with the deployed file marked as "PASSED".

### Test 11.4: Dry-run deployment

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync
poetry run prompt-unifier deploy --name "code-review" --handlers continue --dry-run
```

✓ **Expected result:**

- Message indicating "Dry-run preview - No files will be modified"
- A preview table showing `code-review` would be deployed, but no actual files are created or
  modified in `~/.continue/` or `/tmp/custom-continue-path`.

### Test 11.5 (was 9.1): Simple deployment of a prompt

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync
poetry run prompt-unifier deploy --name "code-review" --handlers continue
```

✓ **Expected result:**

- File `~/.continue/prompts/code-review.md` created with frontmatter (`name`, `description`,
  `invokable: true`)
- Backup created if file existed (`.md.bak`)
- Message "✓ Deployment to continue successful" (Code: 0)
- "Verification Report" displayed, with the deployed file marked as "PASSED"

### Test 11.6 (was 9.2): Deployment of a rule

```bash
poetry run prompt-unifier deploy --name "python-style" --handlers continue
```

✓ **Expected result:** File `~/.continue/rules/python-style.md` created (Code: 0)

- "Verification Report" displayed, with the deployed file marked as "PASSED"

### Test 11.7 (was 9.3): Deploy with tag filtering

```bash
poetry run prompt-unifier deploy --tags python --handlers continue
```

✓ **Expected result:**

- Only prompts/rules with "python" tag deployed
- Messages for each filtered item
- "Verification Report" displayed, with the deployed files marked as "PASSED"

### Test 11.8 (was 9.4): Deploy all items

```bash
poetry run prompt-unifier deploy --handlers continue
```

✓ **Expected result:** All prompts AND rules from storage deployed (Code: 0)

- "Verification Report" displayed, with all deployed files marked as "PASSED"

### Test 11.9 (was 9.5): Deploy non-existent prompt (error)

```bash
poetry run prompt-unifier deploy --name "non-existent" --handlers continue
```

✗ **Expected result:** Error "Prompt not found in storage" (Code: 1)

### Test 11.10 (was 9.6): Deploy with invalid handler (error)

```bash
poetry run prompt-unifier deploy --name "code-review" --handlers invalid
```

✗ **Expected result:** Error "No matching handlers found for \['invalid'\]" (Code: 1)

### Test 11.11 (was 9.7): Backup verification

```bash
echo "old content" > ~/.continue/prompts/code-review.md
poetry run prompt-unifier deploy --name "code-review" --handlers continue
# Verify: old file in .bak, new one deployed
```

✓ **Expected result:** `.bak` file created with old content (Code: 0)

- "Verification Report" displayed, with the deployed file marked as "PASSED"

### Test 11.12 (was 9.8): Deploy with no matches

```bash
poetry run prompt-unifier deploy --tags nonexistent --handlers continue
```

✓ **Expected result:** Message "No content files match the specified criteria." (Code: 0)

### Test 11.13 (was 9.9): Deploy with config.yaml configuration

```bash
cat > .prompt-unifier/config.yaml << 'EOF'
repos:
  - url: git@gitlab.com:waewoo/prompt-unifier-data.git
    branch: main
storage_path: ~/.prompt-unifier/storage
deploy_tags:
  - python
target_handlers:
  - continue
EOF

poetry run prompt-unifier deploy  # Without options - reads config
```

✓ **Expected result:** Only "python" tagged items deployed to continue (Code: 0)

- "Verification Report" displayed, with the deployed files marked as "PASSED"

### Test 11.14 (was 9.10): Deploy with --clean (cleanup orphans and backups)

```bash
# Deploy some files
poetry run prompt-unifier deploy --tags python --handlers continue

# Create an orphan file and backup files (including in subdirectories)
echo "orphan" > ~/.continue/prompts/orphan.md
echo "backup" > ~/.continue/prompts/old-backup.md.bak
mkdir -p ~/.continue/prompts/subdir
echo "nested backup" > ~/.continue/prompts/subdir/nested-backup.md
echo "backup nested" > ~/.continue/prompts/subdir/nested-backup.md.bak

# Redeploy with --clean
poetry run prompt-unifier deploy --tags python --handlers continue --clean
```

✓ **Expected result:**

- Orphan file permanently deleted
- All .bak files recursively deleted (including in subdirectories)
- Message "Cleaned X orphaned file(s)" (includes both orphans and backups)
- Clean operates recursively through all subdirectories (Code: 0)
- "Verification Report" displayed, with the deployed files marked as "PASSED"

______________________________________________________________________

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
- "Verification Report" displayed, confirming deployed files found at nested paths and marked as
  "PASSED"

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
- File `deprecated/nested.md` PRESERVED (orphaned .md in subdirectories preserved for tag filter
  compatibility)
- Clean removes .bak files recursively but only removes orphaned .md files from root directory
  (Code: 0)
- "Verification Report" displayed, with the deployed files marked as "PASSED"

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

______________________________________________________________________

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

✓ **Expected result:** Immediate network error (Code: 1)

______________________________________________________________________

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

______________________________________________________________________

## Kilo Code Handler Tests

### Test 12.1: Deploy to Kilo Code handler

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier sync --repo git@gitlab.com:waewoo/prompt-unifier-data.git
poetry run prompt-unifier deploy --handlers kilocode
```

✓ **Expected result:**

- Files deployed to `./.kilocode/workflows/` (prompts) and `./.kilocode/rules/` (rules)
- All files are pure Markdown (no YAML frontmatter)
- Files have H1 title (`# Title`) and description
- Directory-prefixed naming (e.g., `misc-code-review.md` for root files)
- Verification report shows all files as "PASSED"

### Test 12.2: Verify pure Markdown conversion

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier deploy --name "code-review" --handlers kilocode
cat ./.kilocode/workflows/misc-code-review.md
```

✓ **Expected result:**

- File starts with `# Code Review` (H1 title)
- Description appears as paragraph after title
- No `---` YAML delimiters in file
- Body content preserved intact
- Optional metadata formatted as: `**Field:** value | **Field:** value`

### Test 12.3: Directory-prefixed file naming

```bash
# Create prompts in subdirectories
mkdir -p ~/.prompt-unifier/storage/prompts/backend/api
cat > ~/.prompt-unifier/storage/prompts/backend/api/api-design.md << 'EOF'
---
title: api-design
description: API design review
tags: [api, backend]
---
# API Design
Content here
EOF

poetry run prompt-unifier deploy --handlers kilocode
```

✓ **Expected result:**

- File deployed as `./.kilocode/workflows/api-api-design.md` (directory prefix: `api-`)
- Root files use `misc-` prefix
- Flat structure maintained (no subdirectories in `.kilocode/workflows/`)

### Test 12.4: Kilo Code rollback

```bash
cd /tmp/test-pm-1
# Deploy initial version
poetry run prompt-unifier deploy --name "code-review" --handlers kilocode

# Modify and redeploy
echo "Modified" >> ./.kilocode/workflows/misc-code-review.md
poetry run prompt-unifier deploy --name "code-review" --handlers kilocode

# Check backup exists
ls -la ./.kilocode/workflows/*.bak

# Rollback (manual - handler provides rollback method)
# Note: CLI rollback command not yet implemented
```

✓ **Expected result:**

- Backup file `./.kilocode/workflows/misc-code-review.md.bak` created
- Original content can be restored from backup

### Test 12.5: Deploy to both Continue and Kilo Code

```bash
cd /tmp/test-pm-1
poetry run prompt-unifier deploy --handlers continue,kilocode
```

✓ **Expected result:**

- Files deployed to both `./.continue/` and `./.kilocode/`
- Continue files preserve YAML frontmatter
- Kilo Code files are pure Markdown
- Verification report shows status for both handlers

### Test 12.6: Kilo Code clean orphaned files

```bash
cd /tmp/test-pm-1
# Deploy some files
poetry run prompt-unifier deploy --tags python --handlers kilocode

# Create orphan files
echo "orphan" > ./.kilocode/workflows/orphan.md
echo "backup" > ./.kilocode/workflows/old.md.bak

# Redeploy with --clean
poetry run prompt-unifier deploy --tags python --handlers kilocode --clean
```

✓ **Expected result:**

- Orphan `.md` files in root removed
- All `.bak` files removed recursively
- Message "Cleaned X orphaned file(s)"
- Deployed files remain intact

### Test 12.7: Kilo Code with all metadata fields

```bash
# Create rule with all optional fields
cat > ~/.prompt-unifier/storage/rules/complete-rule.md << 'EOF'
---
title: complete-rule
description: A rule with all fields
category: testing
version: 2.0.0
tags: [python, testing]
author: Test Author
language: en
applies_to: ["*.py", "*.js"]
---
# Complete Rule
Rule content here
EOF

poetry run prompt-unifier deploy --name "complete-rule" --handlers kilocode
cat ./.kilocode/rules/misc-complete-rule.md
```

✓ **Expected result:**

- File contains:
  `**Category:** testing | **Tags:** python, testing | **Version:** 2.0 | **Author:** Test Author | **Language:** en | **AppliesTo:** *.py, *.js`
- All metadata formatted as Markdown text line
- No YAML frontmatter

______________________________________________________________________

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

______________________________________________________________________

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

## Validate Command
├─ [·] Test 5.1 - Validate prompts
├─ [·] Test 5.2 - Validate JSON
├─ [·] Test 5.3 - Invalid directory (error)
├─ [·] Test 5.4 - Validate rules
├─ [·] Test 5.5 - Validation errors
├─ [·] Test 5.6 - SCAFF validation (enabled by default)
├─ [·] Test 5.7 - SCAFF validation with low quality prompt
├─ [·] Test 5.8 - Disable SCAFF validation (--no-scaff)
└─ [·] Test 5.9 - SCAFF validation in JSON output

List Command
├─ [·] Test 7.1 - List all content
├─ [·] Test 7.2 - List content verbose
├─ [·] Test 7.3 - List content by tag
├─ [·] Test 7.4 - List content by tool
└─ [·] Test 7.5 - List content sorted by date

Deploy
├─ [·] Test 11.1 - Deploy by name
├─ [·] Test 11.2 - Deploy to specific handler
├─ [·] Test 11.3 - Deploy to custom base path
├─ [·] Test 11.4 - Dry-run deployment
├─ [·] Test 11.5 - Simple deploy prompt
├─ [·] Test 11.6 - Deploy rule
├─ [·] Test 11.7 - Deploy + tags
├─ [·] Test 11.8 - Deploy all items
├─ [·] Test 11.9 - Deploy non-existent (error)
├─ [·] Test 11.10 - Invalid handler (error)
├─ [·] Test 11.11 - Backup verification
├─ [·] Test 11.12 - No matches
├─ [·] Test 11.13 - Config.yaml
└─ [·] Test 11.14 - Deploy --clean

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

______________________________________________________________________

## 📝 Test Notes

| Date | Tester | Success | Failures | Observations |
| ---- | ------ | ------- | -------- | ------------ |
|      |        | /       | /        |              |

______________________________________________________________________

## 🔧 Quick Troubleshooting

| Problem                              | Cause                         | Solution                                                |
| ------------------------------------ | ----------------------------- | ------------------------------------------------------- |
| "Reference at 'HEAD' does not exist" | Fixed bug                     | Check current version                                   |
| Storage not created                  | Permissions                   | Check home directory permissions                        |
| Missing prompts                      | No prompts/ folder            | Verify repository structure                             |
| Corrupted config.yaml                | Manual editing                | Delete and re-initialize                                |
| File conflicts in multi-repo         | Multiple repos with same file | Last repo wins (last-wins strategy)                     |
| Wrong file version displayed         | Multi-repo sync order         | Check repo order in config - last repo takes precedence |
