# Spec Requirements: Multiple Source Repository Support

## Initial Description
Add support for syncing prompts from multiple Git repositories simultaneously, with configurable merge strategies and conflict handling.

## Requirements Discussion

### First Round Questions

**Q1:** I'm assuming we'll need a merge strategy for when multiple repositories contain files with the same path. Should we use a "last-wins" approach (repositories listed later override earlier ones), or would you prefer an explicit conflict resolution mechanism?

**Answer:** Use "last-wins" approach where repositories listed later override earlier ones.

**Q2:** For configuration, I'm thinking we'll extend the config.yaml to support a `repos:` list instead of the current single `repo:` field. Should we also allow CLI --repo flag to accept multiple values for one-time sync overrides?

**Answer:** Primary configuration in config.yaml with repos: list, CLI --repo flag for one-time sync overrides.

**Q3:** When tracking which files came from which repository, should we store repository metadata (like source repo URL, branch, commit) alongside each synced file, or maintain a separate manifest file that maps files to their sources?

**Answer:** Use ~/.prompt-unifier/storage/.repo-metadata.json to track repository metadata.

**Q4:** If conflicts are detected during multi-repo sync, should we provide feedback to the user (e.g., "prompt-x.md was overridden from repo-B, originally from repo-A"), or handle silently based on the merge strategy?

**Answer:** Display conflict feedback only when conflicts are detected.

**Q5:** For validation, should we fail fast if any repository in the list is invalid/inaccessible, or continue syncing available repositories and report errors at the end?

**Answer:** Fail fast if any repository is invalid.

**Q6:** Regarding the existing storage behavior - currently a single repo completely replaces the storage on sync. With multiple repos, should we preserve this behavior (completely replace storage with merged results from all repos), or support incremental updates where only changed repos are re-synced?

**Answer:** Completely replace storage during multi-repo sync, merging all sources.

**Q7:** Should we maintain backward compatibility with the existing single-repo configuration format, or is it acceptable to require users to migrate to the new multi-repo format?

**Answer:** Backward compatibility is not required.

**Q8:** Are there any features that should explicitly be OUT of scope for this implementation?

**Answer:** See scope boundaries below.

### Existing Code to Reference

**Similar Features Identified:**

- **GitService** - Path: `src/prompt_unifier/git/service.py`
  - Components to potentially reuse: clone_to_temp(), extract_prompts_dir(), get_latest_commit() methods can be called iteratively for each repository
  - Current single-repo logic provides pattern for implementing multi-repo iteration

- **ConfigManager** - Path: `src/prompt_unifier/config/manager.py`
  - Components to potentially reuse: load_config(), save_config(), update_sync_info() methods need extension to handle multiple repositories
  - Configuration loading/saving patterns can be adapted for repos list structure

- **GitConfig Model** - Path: `src/prompt_unifier/models/git_config.py`
  - Backend logic to reference: Currently handles single repo, needs modification to support list of repositories
  - Validation logic can be extended to validate list of repo configurations

- **CLI sync command** - Path: `src/prompt_unifier/cli/commands.py:385`
  - Components to potentially reuse: Current --repo flag implementation provides pattern for multi-value support
  - Command structure can be extended to iterate through multiple repositories

### Follow-up Questions

**Follow-up 1:** You mentioned branch-per-repository support, per-repository authentication configuration, selective file syncing from specific repos, and repository priority/weighting systems. Can you clarify which of these should be IN SCOPE vs OUT OF SCOPE for this implementation?

**Answer:**
- Branch-per-repository support: IN SCOPE
- Per-repository authentication configuration: IN SCOPE
- Selective file syncing from specific repos: IN SCOPE
- Repository priority/weighting systems: OUT OF SCOPE

## Visual Assets

### Files Provided:
No visual files found.

### Visual Insights:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- Sync prompts from multiple Git repositories simultaneously
- Support repos list configuration in config.yaml format
- Extend CLI --repo flag to accept multiple repositories for one-time overrides
- Implement "last-wins" merge strategy where later repositories override earlier ones
- Store repository metadata in ~/.prompt-unifier/storage/.repo-metadata.json
- Track source repo URL, branch, and commit hash for each synced file
- Display conflict feedback when files are overridden from multiple sources
- Fail fast validation: halt sync process if any repository is invalid or inaccessible
- Completely replace storage with merged results from all configured repositories
- Support branch-per-repository configuration
- Support per-repository authentication configuration (tokens, SSH keys)
- Support selective file syncing patterns per repository (include/exclude paths)

### Reusability Opportunities
- GitService.clone_to_temp() can be called iteratively for each repository
- GitService.extract_prompts_dir() can process each cloned repository
- GitService.get_latest_commit() can retrieve commit metadata for tracking
- ConfigManager patterns for load/save can be extended for list structures
- GitConfig validation logic can be adapted to validate repository lists
- CLI --repo flag implementation provides pattern for multi-value support

### Scope Boundaries

**In Scope:**
- Multiple repository configuration in config.yaml
- CLI support for multi-repository overrides
- Last-wins merge strategy implementation
- Repository metadata tracking (source, branch, commit)
- Conflict detection and user feedback
- Fail-fast validation for invalid repositories
- Complete storage replacement with merged multi-repo results
- Branch-per-repository support
- Per-repository authentication configuration
- Selective file syncing from specific repositories

**Out of Scope:**
- Repository priority/weighting systems
- Backward compatibility with single-repo configuration format
- Incremental sync (only changed repos)
- Interactive conflict resolution
- Custom merge strategies beyond last-wins
- Repository health monitoring
- Automatic retry mechanisms for failed repositories

### Technical Considerations
- GitConfig model needs modification from single repo to list of repos structure
- Metadata storage format (.repo-metadata.json) needs design for mapping files to source repos
- CLI argument parsing must handle multiple --repo flags
- Validation logic must check all repositories before starting sync
- Merge logic must track file path collisions across repositories
- Each repository may have different branch configurations
- Each repository may require different authentication methods (HTTPS token vs SSH key)
- File path filtering must be applied per-repository during sync
