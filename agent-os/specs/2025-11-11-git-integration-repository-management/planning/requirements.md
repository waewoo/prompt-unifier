# Spec Requirements: Git Integration & Repository Management

## Initial Description
Implement init command to create centralized prompt repository with .gitignore and structure, add sync command to pull prompts from Git remote, handle Git operations (clone, pull, status), and implement error handling for Git conflicts or network issues.

## Application Context & Architecture

The prompt-manager application follows this workflow:
1. A central Git repository stores prompts/rules in a standardized format
2. Application projects (any project in development) use prompt-manager to sync prompts from the central repository
3. Synced prompts are then transformed/deployed to tool-specific formats (Continue, Cursor, etc.)

This means:
- Each application project has its own `.prompt-manager/` directory (tracked in git)
- The `.prompt-manager/config.yaml` file stores the central repository URL to sync from
- Synced prompts are placed in the `prompts/` directory structure within the application project

## Requirements Discussion

### First Round Questions

**Q1:** I assume the `init` command should create a `.prompt-manager/` directory in the current working directory with a `config.yaml` file to store the remote repository URL and sync settings. Is that correct, or should it be a different directory structure?

**Answer:** Yes, `.prompt-manager/` directory with `config.yaml` is correct.

**Q2:** For the sync command, I'm thinking it should work like: `prompt-manager sync --repo <git-url>` for the first sync, then subsequent syncs can just be `prompt-manager sync` (reading the URL from config). Should we support both approaches?

**Answer:** Yes, this approach is correct.

**Q3:** When syncing prompts, should the command:
- (a) Clone the entire repository to a temporary location and copy only the prompts/ directory content
- (b) Use sparse checkout to fetch only the prompts/ directory
- (c) Clone the entire repository into `.prompt-manager/repo/`

**Answer:** Option (a) - Clone to temp location and copy only prompts/ directory content.

**Q4:** For error handling, should Git conflicts during sync:
- (a) Auto-resolve by always taking remote changes (overwrite local)
- (b) Prompt user to choose (keep local, take remote, or abort)
- (c) Abort sync and show error message with manual resolution instructions

**Answer:** Option (a) - Auto-resolve by always taking remote changes (overwrite local). This is acceptable because prompts should be version-controlled in the central repo.

**Q5:** Should the `.gitignore` file created by init specifically exclude any prompt-manager temporary files or sync artifacts?

**Answer:** The init command should create a basic `.gitignore` template, but NOT ignore `.prompt-manager/` directory. The `.prompt-manager/` directory must be tracked in the application's git repository.

**Q6:** For the repository structure created by init, should it also create the prompts/ directory structure, or just the configuration directory?

**Answer:** Yes, create both `.prompt-manager/` for configuration and a basic `prompts/` directory structure as a template.

**Q7:** Should there be a status command to show the current sync state (last synced commit, any pending updates from remote)?

**Answer:** Yes, implement a status command showing last synced commit and whether updates are available.

**Q8:** What features or capabilities should explicitly NOT be included in this spec (e.g., push commands to central repo, branch management, merge conflict UI)?

**Answer:** Explicitly exclude push commands. This is read-only sync from central repo to application projects.

### Existing Code to Reference

**Similar Features Identified:**
- `lib/prompt_manager.rb` - Main entry point with command structure pattern
- `lib/prompt_manager/cli.rb` - CLI command handling using Thor
- `lib/prompt_manager/template_transformer.rb` - File operations and directory structure handling
- These provide patterns for CLI structure, file operations, and configuration management

### Follow-up Questions

**Follow-up 1:** Where exactly should the config directory be created? In the current working directory of any application project, or in a specific global location?

**Answer:** In the current working directory, which corresponds to any application project under development. The `.prompt-manager/` directory is specific to each application project.

**Follow-up 2:** Is the config directory the same as `.prompt-manager/`, or are these two separate concepts?

**Answer:** They are the same - `.prompt-manager/` is the config directory.

**Follow-up 3:** Should the `.gitignore` file ignore the `.prompt-manager/` directory?

**Answer:** NO. The `.prompt-manager/` directory must be tracked in the application project's git repository. This directory contains the configuration that other developers need.

**Follow-up 4:** If someone runs `sync` without running `init` first, should the command:
- (a) Auto-run init automatically
- (b) Return an error and tell them to run init first

**Answer:** Option (b) - Return an error and instruct the user to run `init` first.

**Follow-up 5:** For subsequent syncs, should the `--repo` argument be:
- (a) Optional (read from saved config if not provided)
- (b) Required every time

**Answer:** Option (a) - Optional. Read the URL from the saved config if not provided, but allow override with `--repo` flag.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A - This is a CLI tool feature with no visual interface.

## Requirements Summary

### Functional Requirements

**Init Command:**
- Create `.prompt-manager/` directory in current working directory (application project root)
- Generate `config.yaml` file inside `.prompt-manager/` to store:
  - Remote repository URL
  - Last sync timestamp
  - Last synced commit hash
- Create basic `prompts/` directory structure as a template
- Create a basic `.gitignore` template file (but do NOT ignore `.prompt-manager/` itself)
- `.prompt-manager/` directory should be tracked in version control

**Sync Command:**
- Accept optional `--repo <git-url>` argument
- On first sync (or when --repo provided): Store repository URL in `.prompt-manager/config.yaml`
- On subsequent syncs: Read repository URL from config (unless --repo override provided)
- Clone repository to temporary location
- Extract only `prompts/` directory content from the cloned repo
- Copy prompts to application project's `prompts/` directory
- Auto-resolve conflicts by taking remote changes (overwrite local)
- Update `config.yaml` with sync timestamp and commit hash
- Clean up temporary cloned repository
- Validate that init has been run before allowing sync (error if `.prompt-manager/` doesn't exist)

**Status Command:**
- Show current repository URL being synced from
- Display last sync timestamp
- Display last synced commit hash
- Check remote repository for new commits
- Indicate if updates are available from remote

**Error Handling:**
- Git clone failures (invalid URL, network issues, authentication errors)
- Git pull failures during sync
- Missing or corrupted config file
- Invalid repository structure (missing prompts/ directory in remote)
- Attempting to sync before running init
- Network connectivity issues

### Reusability Opportunities

**Components to Reference:**
- `lib/prompt_manager/cli.rb` - Use Thor command structure pattern for new commands
- `lib/prompt_manager/template_transformer.rb` - File operations, directory copying, template handling patterns
- General Ruby file I/O patterns from existing codebase
- YAML configuration handling (if exists elsewhere in codebase)

**New Components to Create:**
- Git operations wrapper/service object
- Config manager for `.prompt-manager/config.yaml`
- Sync orchestrator to coordinate clone, extract, copy operations
- Status checker to compare local vs remote state

### Scope Boundaries

**In Scope:**
- `init` command implementation
- `sync` command implementation (pull-only from remote)
- `status` command implementation
- Configuration management (`.prompt-manager/config.yaml`)
- Git operations: clone, pull, status check
- Error handling for Git and network failures
- Automatic conflict resolution (always take remote)
- Temporary directory management for cloning
- `.gitignore` template creation

**Out of Scope:**
- Push commands to central repository (read-only sync)
- Branch management or switching
- Manual merge conflict resolution UI
- Interactive prompts for conflict resolution
- Authentication credential management (assume user has Git configured)
- Multi-repository sync (single remote repository only)
- Sync scheduling or automatic background sync
- Diff viewing between local and remote prompts
- Rollback to previous sync states

### Technical Considerations

**Integration Points:**
- Must integrate with existing Thor CLI structure in `lib/prompt_manager/cli.rb`
- Should follow file operation patterns from `lib/prompt_manager/template_transformer.rb`
- Config file should be YAML format for consistency with Ruby ecosystem
- Git operations should use Ruby's `git` gem or shell commands via backticks/system calls

**Existing System Constraints:**
- Application is Ruby-based using Thor for CLI
- Current directory structure uses `lib/prompt_manager/` for modules
- Must maintain compatibility with existing prompt transformation features

**Technology Preferences:**
- Use Ruby's built-in YAML library for config parsing
- Consider using `git` gem for Git operations (or shell commands if simpler)
- Use `FileUtils` for directory operations
- Use `tmpdir` for temporary directory management during clone operations

**Similar Code Patterns to Follow:**
- Follow command structure from existing CLI implementation
- Mirror file/directory handling patterns from template transformer
- Maintain consistent error handling style with existing commands

**Critical Design Decisions:**
1. `.prompt-manager/` directory must be tracked in version control (not gitignored)
2. Each application project has its own `.prompt-manager/` config directory
3. Sync is always unidirectional: central repo → application project (never reverse)
4. Conflicts are always resolved in favor of remote (central repo is source of truth)
5. Init must be run before sync (no automatic init)
6. Repository URL can be overridden with --repo flag even after initial sync
