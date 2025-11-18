# Specification: Multiple Source Repository Support

## Goal
Enable users to sync prompts and rules from multiple Git repositories simultaneously, merging content from all sources into centralized storage using a last-wins merge strategy, with per-repository configuration for branches, authentication, and selective file syncing.

## User Stories
- As a developer using multiple prompt libraries, I want to sync from several Git repositories at once so that I can combine prompts from different sources in one centralized location
- As a team lead managing shared coding standards, I want to specify different branches per repository so that I can pull production-ready prompts from one repo and experimental prompts from another
- As a DevOps engineer managing private repositories, I want per-repository authentication configuration so that I can sync from both public and private sources with different credentials

## Specific Requirements

**Multi-Repository Configuration**
- Extend GitConfig model to support `repos: list[RepositoryConfig]` instead of single `repo_url: str`
- Each RepositoryConfig contains: url (required), branch (optional, defaults to main), auth_method (optional), include_patterns (optional), exclude_patterns (optional)
- Config YAML format: `repos: [{url: "...", branch: "main"}, {url: "...", branch: "dev"}]`
- Maintain single `storage_path`, `last_sync_timestamp` at root level for all repos
- Add `repo_metadata` list to track per-repository sync info (url, branch, commit, timestamp)
- Backward compatibility NOT required - users must migrate to new format

**CLI Multi-Repository Support**
- Extend `sync` command to accept multiple `--repo` flags: `sync --repo URL1 --repo URL2`
- When CLI provides --repo flags, use those instead of config.yaml repos list
- Support `--repo URL --branch BRANCH` pairing for CLI overrides (process flags in pairs)
- Display each repository being synced in progress output with Rich console formatting
- Show repository URL, branch, and commit hash for each source in completion message

**Last-Wins Merge Strategy**
- Process repositories in order listed (config.yaml list order, or CLI flag order)
- When same file path exists in multiple repos, later repository overwrites earlier
- Track all file-to-repository mappings in `.repo-metadata.json` in storage root
- Metadata JSON structure: `{"files": {"path/to/file.md": {"source_url": "...", "branch": "...", "commit": "...", "timestamp": "..."}}, "repositories": [...]}`
- Display conflict feedback when overwrite occurs: "Prompt 'X' from repo A overridden by repo B"

**Fail-Fast Validation**
- Before starting any clone operations, validate ALL repository URLs
- Validation checks: URL format valid, repository accessible, prompts/ directory exists
- If any repository fails validation, display error and exit without syncing
- Run validation sequentially to provide clear error messages per repository
- No partial sync - either all repositories sync successfully or none do

**Complete Storage Replacement**
- Clear entire storage directory before multi-repo sync begins
- Merge prompts/ and rules/ from all repositories into storage location
- Preserve subdirectory structure from each repository during merge
- Generate fresh .repo-metadata.json with complete mapping after sync

**Branch-Per-Repository Configuration**
- RepositoryConfig model includes optional `branch: str | None` field
- If branch specified, clone that specific branch instead of default
- Update GitService.clone_to_temp() to accept optional branch parameter
- Display branch being synced in progress messages for each repository

**Per-Repository Authentication**
- RepositoryConfig model includes optional `auth_config: dict[str, str] | None` field
- Support auth_method types: "ssh_key", "token", "credential_helper"
- For token auth: store token in auth_config or use git credential helper
- For SSH: rely on system SSH key configuration, validate SSH URL format
- GitService.clone_to_temp() handles different auth approaches per repository

**Selective File Syncing**
- RepositoryConfig includes optional `include_patterns: list[str] | None` and `exclude_patterns: list[str] | None`
- Patterns are glob-style: "*.md", "python/**", "rules/security/*"
- Apply filters after extracting prompts/ and rules/ but before copying to storage
- Include patterns: only sync files matching patterns (if specified)
- Exclude patterns: skip files matching patterns (applied after includes)

## Visual Design

No visual mockups provided.

## Existing Code to Leverage

**GitService (src/prompt_unifier/git/service.py)**
- clone_to_temp() method can be called iteratively for each repository in repos list
- Extend method signature to accept optional branch parameter for checkout
- extract_prompts_dir() processes prompts/ and rules/ - reuse for each cloned repo
- get_latest_commit() retrieves commit metadata - call for each repo to populate metadata
- retry_with_backoff() pattern should be used for all network operations across repos

**ConfigManager (src/prompt_unifier/config/manager.py)**
- load_config() and save_config() YAML handling patterns adapt to repos list structure
- update_sync_info() needs complete redesign to handle repo_metadata list instead of single repo
- Add new method update_multi_repo_sync_info(config_path, repo_metadata_list) for batch updates
- Validation error handling patterns reusable for multi-repo validation feedback

**GitConfig Model (src/prompt_unifier/models/git_config.py)**
- Create new RepositoryConfig Pydantic model with url, branch, auth_config, include_patterns, exclude_patterns fields
- Replace repo_url: str | None with repos: list[RepositoryConfig] | None
- Add repo_metadata: list[dict] | None to store per-repo sync results
- Reuse HandlerConfig pattern for nested configuration structure
- Maintain existing deploy_tags, target_handlers, handlers fields unchanged

**CLI sync command (src/prompt_unifier/cli/commands.py:385)**
- Current --repo flag handling provides pattern for multi-value support using typer.Option with multiple=True
- Repo URL determination logic (flag > config > error) extends to list handling
- Rich console progress display patterns reusable for multi-repo sync status
- Error handling structure (ValueError for Git errors, PermissionError, generic Exception) applies to multi-repo failures

**Path filtering utilities**
- Implement new PathFilter utility class with glob pattern matching using pathlib.Path.match()
- Apply include/exclude filters to file lists before copying to storage
- Patterns match against relative paths within prompts/ or rules/ directories

## Out of Scope
- Repository priority or weighting systems beyond last-wins order
- Backward compatibility with single-repo config.yaml format
- Incremental sync (sync only changed repositories while preserving others)
- Interactive conflict resolution UI or prompts for user decisions
- Custom merge strategies beyond last-wins (e.g., first-wins, manual merge, keep-both)
- Repository health monitoring or status dashboard
- Automatic retry mechanisms for individual failed repositories
- Parallel/concurrent repository cloning (process sequentially)
- Repository-specific deployment configurations or handler overrides
- Git submodule or nested repository support
