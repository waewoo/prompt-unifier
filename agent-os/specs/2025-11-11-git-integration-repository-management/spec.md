# Specification: Git Integration & Repository Management

## Goal
Enable application projects to sync prompts and rules from a central Git repository by implementing init, sync, and status commands that manage a local .prompt-unifier/ configuration directory with read-only synchronization.

## User Stories
- As a developer, I want to initialize my application project with prompt-unifier so that I can sync prompts and rules from a central repository
- As a developer, I want to sync the latest prompts and rules from the central repository so that my local content stays up-to-date automatically

## Specific Requirements

**CLI Global Options**
- Add --version (-v) flag to display application version and exit
- Version callback should be eager (processed before commands)
- Display format: "prompt-unifier version X.Y.Z"
- Exit with code 0 after displaying version

**Init Command Implementation**
- Create .prompt-unifier/ directory in current working directory (application project root)
- Generate config.yaml file inside .prompt-unifier/ with placeholders for repo_url, last_sync_timestamp, last_sync_commit, and storage_path fields
- Create centralized storage directory (default: ~/.prompt-unifier/storage) with prompts/ and rules/ subdirectories
- Support custom storage path via --storage-path option
- Generate .gitignore template file in centralized storage directory if it doesn't exist
- .prompt-unifier/ directory must be tracked in version control for team collaboration
- **Command is idempotent**: Running init multiple times succeeds without error, creating only missing components
- Display clear status messages showing what was created (green) vs what already existed (dim)
- Use pathlib.Path for all directory operations following existing codebase patterns
- Exit with code 0 on success (including when already initialized), code 1 only on actual errors (permissions, etc.)

**Sync Command Implementation**
- Accept optional --repo flag to specify or override Git repository URL
- Accept optional --storage-path flag to override storage location for this sync
- Validate that init has been run before allowing sync (check for .prompt-unifier/config.yaml existence)
- On first sync or when --repo provided: Store repository URL in .prompt-unifier/config.yaml
- On subsequent syncs: Read repository URL from config.yaml unless --repo override provided
- Use GitPython library to clone repository to temporary directory using tempfile.mkdtemp() (not TemporaryDirectory context manager to avoid premature cleanup)
- Extract prompts/ directory content from cloned repo and copy to centralized storage's prompts/ directory (required)
- Extract rules/ directory content if present in repository and copy to centralized storage's rules/ directory (optional)
- Auto-resolve all conflicts by taking remote changes (overwrite local files completely)
- Update config.yaml with current timestamp and latest commit hash from remote
- Clean up temporary cloned repository automatically after sync completes (manual cleanup with shutil.rmtree in try/finally)
- Provide Rich formatted output showing sync progress: repository URL, storage path, commit hash
- Exit with code 0 on success, code 1 on failure

**Status Command Implementation**
- Display current repository URL being synced from (read from config.yaml)
- Show last sync timestamp in human-readable format (e.g., "2 hours ago" or "2024-11-11 14:30:00")
- Display last synced commit hash (short SHA)
- Check remote repository for new commits since last sync using GitPython
- Indicate clearly if updates are available with message "Updates available" or "Up to date"
- Show number of commits behind if updates available
- Use Rich Console for formatted, colored output with symbols for clear status indication
- Exit with code 0 always (status is informational only)

**Config Management Structure**
- config.yaml format: repo_url (string | null), last_sync_timestamp (ISO 8601 string | null), last_sync_commit (string SHA | null), storage_path (string)
- Use PyYAML for reading and writing config.yaml following existing YAMLParser patterns
- Validate config file structure when reading: check for required fields and valid data types
- Create ConfigManager class in new config/ module to handle all config operations
- Provide methods: load_config(), save_config(), update_sync_info()
- Handle missing or corrupted config.yaml gracefully with clear error messages
- When reading existing config, use storage_path if available, otherwise use default

**Git Operations Wrapper**
- Create GitService class in new git/ module to wrap all GitPython operations
- Implement methods: clone_to_temp(), get_latest_commit(), check_remote_updates(), extract_prompts_dir()
- extract_prompts_dir() extracts both prompts/ (required) and rules/ (optional if present) directories
- Use tempfile.mkdtemp() for temporary directory creation (manual cleanup in try/finally blocks)
- Clean up temporary directories with shutil.rmtree() in finally blocks
- Handle Git authentication errors with clear messages and authentication options (SSH keys, credential helper, PAT in URL)
- Handle network connectivity errors with retry logic (3 attempts with exponential backoff using retry_with_backoff helper)
- Validate that cloned repository contains prompts/ directory before extracting (required)
- Copy rules/ directory if present in repository (optional)
- Handle empty repositories (no commits) with helpful error message explaining how to fix

**Directory Structure & File Operations**
- Follow existing pathlib.Path patterns from FileScanner class
- Use Path.mkdir(parents=True, exist_ok=True) for directory creation
- Use shutil.copytree for recursive directory copying with dirs_exist_ok=True
- Ensure all paths are resolved to absolute paths before operations
- Validate source prompts/ directory exists in cloned repo before copying (required)
- Copy source rules/ directory if it exists in cloned repo (optional)

**Error Handling & Validation**
- Git clone failures: Invalid URL, authentication errors, network issues - exit code 1 with helpful error message
- Empty repository: Error with detailed instructions on how to add prompts/ directory (and optionally rules/) and commit - exit code 1
- Missing .prompt-unifier/: Clear error message "Run 'prompt-unifier init' first" - exit code 1
- Invalid repository structure: Error if prompts/ directory not found in remote repo - exit code 1
- Corrupted config file: Error with suggestion to re-run init or manually fix config.yaml - exit code 1
- Network connectivity issues: Show retry attempts with progress, fail after 3 attempts - exit code 1
- Permission errors: Clear message about directory permissions - exit code 1
- Temporary directory cleanup: Always clean up in finally blocks, even on errors

**Development Environment**
- Ensure Poetry is up to date (poetry self update) to avoid dependency warnings
- If RequestsDependencyWarning appears, run `poetry self update` to update Poetry's dependencies
- Use `make run ARGS="<command>"` shortcut for convenient CLI execution during development

## Visual Design
No visual assets provided - this is a CLI tool with terminal output only.

## Existing Code to Leverage

**CLI Command Pattern from cli/main.py and cli/commands.py**
- Use Typer decorator @app.command() for registering new commands (init, sync, status)
- Follow validate command structure: directory validation, error handling, exit codes
- Use typer.Option for optional flags like --repo
- Use typer.echo for error messages with err=True parameter
- Raise typer.Exit(code=1) for error conditions, implicit code=0 for success

**Rich Console Output from output/rich_formatter.py**
- Use Rich Console for colored terminal output following RichFormatter patterns
- Use color constants: SUCCESS_COLOR ("green"), ERROR_COLOR ("red"), WARNING_COLOR ("yellow")
- Use symbols: PASSED_SYMBOL ("✓"), FAILED_SYMBOL ("✗")
- Use console.print() with Rich markup for formatted messages
- Display progress with clear headers, separators (━ character), and status indicators

**File Operations from utils/file_scanner.py**
- Use pathlib.Path for all file system operations
- Resolve paths to absolute using path.resolve()
- Check path.exists() and path.is_dir() before operations
- Use Path.rglob() for recursive file discovery if needed
- Sort file lists for deterministic ordering

**YAML Parsing from core/yaml_parser.py**
- Use yaml.safe_load() for security (never use yaml.load())
- Validate parsed data is dictionary type
- Handle yaml.YAMLError exceptions with clear error messages
- Check for required fields after parsing
- Use yaml.safe_dump() for writing config with default_flow_style=False

**Validation Models from models/validation.py**
- Create new Pydantic models for GitConfig with validation using Pydantic v2
- Follow BaseModel pattern with Field() descriptors
- Use type hints: str | None for optional fields
- Add model_config with json_schema_extra for examples

## Out of Scope
- Push commands to central repository (read-only sync from remote)
- Branch management or switching between branches
- Manual merge conflict resolution UI or interactive prompts
- Authentication credential management (assume user has Git configured via SSH keys or credentials)
- Multi-repository sync (only single remote repository supported)
- Sync scheduling or automatic background sync
- Diff viewing between local and remote prompts before sync
- Rollback to previous sync states or version history
- Interactive conflict resolution (always auto-resolve to remote)
- Git submodules or LFS support
