# Specification: Configurable Handler Base Paths

## Goal
Enable flexible deployment locations for AI coding assistant handlers through per-handler base path configuration via config.yaml and CLI options, replacing the current hardcoded Path.home() default with Path.cwd() to support project-local tool installations.

## User Stories
- As a developer with project-local Continue installations, I want to specify custom base paths in config.yaml so that prompts deploy to my project directory instead of my home directory
- As a developer deploying to non-standard locations, I want to use a --base-path CLI flag to override the configured path for one-time deployments without modifying my config file

## Specific Requirements

**Change Default Base Path from Path.home() to Path.cwd()**
- Modify ContinueToolHandler default base_path logic from Path.home() to Path.cwd()
- Rationale: Modern AI coding assistants like Continue are typically installed per-project in the repository directory
- Apply consistently to all future handlers (Cursor, Windsurf, Aider)
- No migration needed as tool not yet deployed to users

**Add Handler Configuration Model**
- Create HandlerConfig Pydantic model with base_path field (str | None)
- Add handlers field to GitConfig model: dict[str, HandlerConfig] | None
- Support nested structure: handlers.{handler_name}.base_path in config.yaml
- Include placeholder entries for all planned handlers: continue, cursor, windsurf, aider
- Validate handler names against known handlers list
- Use Field with descriptive help text and examples

**Implement Environment Variable Expansion**
- Create utility function expand_env_vars(path: str) -> str in new module utils/path_helpers.py
- Support standard environment variables: $HOME, $USER, $PWD
- Support both syntaxes: $VAR and ${VAR} using regex substitution
- Apply expansion before passing base_path to handler constructors
- Return original path unchanged if no environment variables detected
- Handle missing environment variables gracefully with clear error messages

**Add CLI --base-path Option to Deploy Command**
- Add --base-path option to deploy() command in cli/commands.py
- Accept single Path value (works with existing --handlers flag for selecting handler)
- Apply to whichever handler is being deployed (deploy handles one handler at a time)
- Resolve precedence: CLI flag > config.yaml > default Path.cwd()
- Validate that path is accessible and writable before deployment

**Update Handler Instantiation Logic**
- Modify deploy() command handler registration to pass resolved base_path
- Read handlers config from config.yaml via ConfigManager
- Apply environment variable expansion to configured base_path
- Create handler instances with appropriate base_path: ContinueToolHandler(base_path=resolved_path)
- Support per-project configuration through project's .prompt-manager/config.yaml

**Auto-Create Deployment Paths**
- Maintain existing auto-creation behavior in ContinueToolHandler.__init__
- Create base_path directories automatically if they don't exist (mkdir with parents=True, exist_ok=True)
- Create handler-specific subdirectories (.continue/prompts/, .continue/rules/)
- Provide informative console output when creating new directories

**Validate Tool Installation Before Deployment**
- Add validate_tool_installation() method to ContinueToolHandler
- Check that base_path exists and contains expected tool structure
- For Continue: Verify .continue/ directory exists or can be created
- Provide clear error messages if validation fails (e.g., "Continue installation not found at {path}")
- Call validation before deploying first prompt/rule

**Configuration Persistence and Examples**
- ConfigManager should load/save handlers section using existing patterns
- Provide default empty dict for handlers if not present in config
- Example config.yaml structure with all handlers:
```yaml
repo_url: https://github.com/example/prompts.git
last_sync_timestamp: '2024-11-15T10:30:00Z'
last_sync_commit: abc1234
storage_path: ~/.prompt-manager/storage
deploy_tags:
  - python
  - review
target_handlers:
  - continue
handlers:
  continue:
    base_path: $PWD/.continue
  cursor:
    base_path: $PWD/.cursor
  windsurf:
    base_path: $PWD/.windsurf
  aider:
    base_path: $PWD/.aider
```

**Error Handling and User Feedback**
- Invalid handler names in config: Print warning, skip invalid entries
- Missing environment variables: Print error with variable name, exit with code 1
- Path permission errors: Print error with path and permission details, exit with code 1
- Path does not exist but cannot be created: Print error, suggest manual creation, exit with code 1
- Validation failures: Print descriptive error with handler name and path attempted
- Use Rich console for formatted, color-coded error messages

**Support Per-Project Configuration**
- Each project's .prompt-manager/config.yaml can specify different base paths
- Same handler can deploy to different locations based on project context
- Example workflow: Project A has continue.base_path=$PWD/.continue, Project B has continue.base_path=$HOME/.continue
- Configuration is loaded from current working directory's .prompt-manager/config.yaml

## Out of Scope
- Custom/user-defined environment variables beyond $HOME, $USER, $PWD
- Advanced shell expansion (globbing, command substitution, tilde expansion beyond ~)
- Automatic handler installation or setup at non-existent paths
- Global configuration file (only per-project .prompt-manager/config.yaml supported)
- Modifying handler protocol to require base_path parameter
- Backward compatibility or migration (tool not yet in production)
- Handler-specific CLI flags like --continue-base-path (single --base-path is sufficient)
- Validation of handler-specific tool versions or configurations
- Symlink resolution or handling of complex path scenarios
- Windows-specific path handling beyond PathLib's built-in support

## Existing Code to Leverage

**GitConfig Model Pattern (src/prompt_manager/models/git_config.py)**
- Follow existing Pydantic model structure with Field descriptors
- Use model_dump() for serialization to YAML
- Include json_schema_extra with examples for documentation
- Apply similar optional field pattern (field: Type | None = Field(default=None))
- Reuse validation patterns already established

**ConfigManager Load/Save Pattern (src/prompt_manager/config/manager.py)**
- Use existing load_config() and save_config() methods as template
- Follow yaml.safe_load() and yaml.safe_dump() patterns
- Apply same error handling approach (ValidationError, YAMLError)
- Use console.print() for error messages with Rich formatting
- Maintain existing config_path.parent.mkdir(parents=True, exist_ok=True) pattern

**ContinueToolHandler Base Path Infrastructure (src/prompt_manager/handlers/continue_handler.py)**
- Leverage existing base_path parameter in __init__ (line 20)
- Modify default logic at line 22: Change Path.home() to Path.cwd()
- Reuse existing directory creation pattern: self.prompts_dir.mkdir(parents=True, exist_ok=True)
- Maintain current backup and deployment logic unchanged

**Deploy Command Handler Registration (src/prompt_manager/cli/commands.py)**
- Modify registry.register(ContinueToolHandler()) at line 628
- Pass base_path parameter: registry.register(ContinueToolHandler(base_path=resolved_path))
- Reuse existing config loading pattern from lines 609-613
- Apply similar precedence logic as used for deploy_tags and target_handlers (lines 621-624)

**Path Expansion Patterns (throughout codebase)**
- Use Path.expanduser() for ~ expansion (seen in commands.py lines 113, 204, 417)
- Use Path.resolve() for absolute path resolution
- Combine: Path(path_str).expanduser().resolve() as standard pattern
- Apply consistent path handling across all path-related operations
