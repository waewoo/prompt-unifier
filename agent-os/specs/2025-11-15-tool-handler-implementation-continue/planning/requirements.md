# Spec Requirements: Configurable Handler Base Paths

## Initial Description
Tool Handler Implementation: Continue & Kilo Code

This specification evolved to focus specifically on adding configurable base paths for tool handlers, enabling users to customize deployment locations for each handler (Continue, Windsurf, Cursor, Aider, Kilo Code) via config.yaml and CLI options.

## Requirements Discussion

### First Round Questions

**Q1:** For the configuration structure, I'm assuming we'll use a nested YAML structure like `handlers.{handler_name}.base_path` in config.yaml. This keeps it organized and allows per-handler configuration. Is that the structure you want, or would you prefer something like `continue_base_path` at the top level?

**Answer:** YES - nested YAML structure `handlers.{handler_name}.base_path` is preferred.

**Q2:** I'm thinking the default base_path should be Path.cwd() (current working directory where command is launched) rather than Path.home(), which would allow plugins to be installed in the project/repo directory. Should we use Path.cwd() as default, or stick with Path.home()?

**Answer:** YES - use Path.cwd() as the default instead of Path.home(). This allows plugins to be installed in project directories.

**Q3:** For the CLI flag naming, since we're already using `--handlers` to specify which handler to use, should the base path flag be `--base-path` (generic) or `--continue-base-path` (handler-specific)? The generic approach would be simpler since the handler is already specified.

**Answer:** Use `--base-path` (generic) since the handler is already specified via `--handlers`.

**Q4:** Regarding configuration precedence: CLI flag > config.yaml > default Path.cwd() - does this precedence order work for you? This allows one-time overrides via CLI while maintaining persistent config.

**Answer:** YES - precedence order is correct: CLI flag > config.yaml > default Path.cwd()

**Q5:** For path handling, I'm assuming we should: (a) auto-create the path if it doesn't exist, (b) support environment variable expansion (like $HOME/.continue), (c) validate that the base_path points to a valid tool installation. Are these assumptions correct?

**Answer:** YES on all three:
- Auto-create paths if they don't exist
- Support environment variable expansion ($HOME, $USER, $PWD)
- Support both syntaxes: `$VAR` and `${VAR}`
- Validate that base_path points to valid tool installation

**Q6:** Since the config.yaml is per-project (in `.prompt-manager/config.yaml`), does this mean each project can have Continue in its own directory? Or should there be both global and per-project config support?

**Answer:** YES - per-project configuration is supported and expected. Each project's `.prompt-manager/config.yaml` can specify different base paths. The same handler can deploy to different locations depending on the project.

**Q7:** For the multi-handler schema in config.yaml, should we add stub/placeholder support for all future handlers (continue, cursor, windsurf, aider, kilo) even if not implemented yet? This would make the schema clear and prevent breaking changes.

**Answer:** YES - add stub/placeholder support for all future handlers in the config schema, even if not yet implemented.

**Q8:** What should be explicitly OUT of scope? For example: custom environment variables beyond standard ones ($HOME, $USER, $PWD), advanced path templating, or automatic handler installation?

**Answer:** OUT OF SCOPE:
- Custom/user-defined environment variables beyond standard ones
- Advanced shell expansion features

**Q9:** Is there any backward compatibility concern, or can we freely change the default from Path.home() to Path.cwd() since the tool hasn't been deployed to users yet?

**Answer:** N/A - No backward compatibility concerns. Tool not yet deployed to users.

**Q10:** Are there existing features in the codebase with similar path configuration patterns we should follow for consistency?

**Answer:** YES - Follow existing patterns from `src/prompt_manager/models/git_config.py` for storage_path field.

### Follow-up Questions

**Follow-up 1:** For per-project base paths: Does this mean each project can have the handler Continue in its own directory? This would allow project-specific tool installations.

**Answer:** YES - each project can have the handler Continue in its own directory. Per-project configuration is supported and expected.

**Follow-up 2:** For environment variable support: Should we support (A) only standard variables like $HOME, $USER, $PWD, or (B) any environment variable the user has set? Also, should we support both `$VAR` and `${VAR}` syntax?

**Answer:**
- Option A - Standard variables only ($HOME, $USER, $PWD)
- Support BOTH syntaxes: `$VAR` and `${VAR}`

### Existing Code to Reference

**Similar Features Identified:**

1. **GitConfig Model with storage_path field:**
   - Path: `src/prompt_manager/models/git_config.py`
   - Purpose: Shows existing pattern for configurable path handling
   - Pattern: Field validation, default value handling, path expansion

2. **ContinueToolHandler with base_path parameter:**
   - Path: `src/prompt_manager/handlers/continue_handler.py` (Lines 20-26)
   - Purpose: Shows that base_path parameter already exists but is unused
   - Pattern: Constructor accepts base_path, currently defaults to Path.home()

3. **Handler registration without base_path:**
   - Path: `src/prompt_manager/cli/commands.py` (Line 628)
   - Purpose: Shows where handler is instantiated without passing base_path
   - Pattern: Needs modification to read config and pass base_path

**Components to Potentially Reuse:**
- Path validation logic from GitConfig
- Environment variable expansion patterns (if they exist)
- Configuration loading mechanisms

**Backend Logic to Reference:**
- GitConfig's approach to default values and field validation
- Existing Pydantic models for configuration structure

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A - No visual files found in planning/visuals/ directory.

## Requirements Summary

### Functional Requirements

1. **Configuration Structure:**
   - Use nested YAML structure: `handlers.{handler_name}.base_path` in `.prompt-manager/config.yaml`
   - Example:
     ```yaml
     handlers:
       continue:
         base_path: "$HOME/.continue"
       cursor:
         base_path: "./project-tools/cursor"
       windsurf:
         base_path: "$HOME/.windsurf"
       aider:
         base_path: "$HOME/.aider"
       kilo:
         base_path: "$HOME/.kilo-code"
     ```
   - Include stubs for all handlers (continue, cursor, windsurf, aider, kilo) even if not yet implemented

2. **Default Behavior:**
   - Change default base_path from `Path.home()` to `Path.cwd()` (current working directory)
   - Rationale: Allows plugins/tools to be installed in project/repo directory
   - Affects: `src/prompt_manager/handlers/continue_handler.py` constructor default

3. **CLI Flag Support:**
   - Add `--base-path` flag to deploy command
   - Generic flag (not handler-specific like `--continue-base-path`)
   - Works with existing `--handlers` flag to specify which handler
   - Example: `prompt-manager deploy --handlers continue --base-path ./tools/continue`

4. **Configuration Precedence (highest to lowest):**
   - CLI flag (`--base-path`)
   - Config file (`.prompt-manager/config.yaml` handlers section)
   - Default value (`Path.cwd()`)

5. **Path Handling:**
   - Auto-create paths if they don't exist
   - Support environment variable expansion:
     - Standard variables: `$HOME`, `$USER`, `$PWD`
     - Both syntaxes: `$VAR` and `${VAR}`
   - Example: `$HOME/.continue` expands to `/home/username/.continue`
   - Example: `${HOME}/.continue` expands to `/home/username/.continue`

6. **Tool Installation Validation:**
   - Validate that base_path points to valid tool installation
   - Check for expected tool-specific files/directories
   - Provide clear error messages if validation fails
   - Example: For Continue, verify `.continue/` directory structure exists or can be created

7. **Per-Project Configuration:**
   - Each project's `.prompt-manager/config.yaml` can specify different base paths
   - Same handler can deploy to different locations depending on project
   - Example: Project A deploys Continue to `./dev-tools/continue`, Project B deploys to `$HOME/.continue`

8. **Multi-Handler Schema:**
   - Config schema includes all handlers even if not implemented
   - Prevents breaking changes when new handlers are added
   - Makes available options clear to users
   - Handlers: continue, cursor, windsurf, aider, kilo

### Reusability Opportunities

1. **GitConfig Pattern:**
   - File: `src/prompt_manager/models/git_config.py`
   - Reuse: Field validation, default value handling, path expansion
   - Apply: Create similar Pydantic model for handlers configuration

2. **Existing base_path Parameter:**
   - File: `src/prompt_manager/handlers/continue_handler.py` (Lines 20-26)
   - Status: Parameter exists but unused
   - Action: Wire up to config and CLI flag

3. **Handler Registration:**
   - File: `src/prompt_manager/cli/commands.py` (Line 628)
   - Modify: Read base_path from config, pass to handler constructor
   - Pattern: Apply to all future handlers

### Scope Boundaries

**In Scope:**
- Nested YAML configuration structure for handlers
- CLI flag `--base-path` for deploy command
- Environment variable substitution ($HOME, $USER, $PWD)
- Both `$VAR` and `${VAR}` syntax support
- Tool installation validation
- Per-project base path configuration
- Auto-creation of paths if missing
- Default change from Path.home() to Path.cwd()
- Multi-handler schema with stubs for all handlers

**Out of Scope:**
- Custom/user-defined environment variables beyond standard ones ($HOME, $USER, $PWD)
- Advanced shell expansion features (tilde expansion, glob patterns, command substitution)
- Automatic handler/tool installation
- Global configuration file (only per-project config supported)
- Handler-specific CLI flags (e.g., `--continue-base-path`, `--cursor-base-path`)
- Bidirectional path syncing or monitoring
- Path validation beyond basic existence and tool-specific checks

### Technical Considerations

1. **Integration Points:**
   - Config loading in CLI commands
   - Handler instantiation in deploy command
   - Pydantic models for configuration validation
   - Environment variable expansion utility

2. **Existing System Constraints:**
   - Python 3.12+ required
   - Pydantic for data validation
   - Path handling via pathlib
   - TDD methodology with pytest

3. **Technology Preferences:**
   - Follow existing GitConfig pattern for consistency
   - Use Pydantic field validators
   - Maintain type safety with mypy
   - Cross-platform path handling with pathlib

4. **Similar Code Patterns:**
   - GitConfig's storage_path field approach
   - Existing handler protocol implementation
   - CLI flag handling in commands.py

### Implementation Notes

1. **Key Files to Modify:**
   - `src/prompt_manager/handlers/continue_handler.py`: Change default from Path.home() to Path.cwd()
   - `src/prompt_manager/cli/commands.py`: Add --base-path flag, read config, pass to handler
   - `src/prompt_manager/models/` (new or existing): Create handlers config Pydantic model
   - Config validation logic: Add handlers section validation

2. **Environment Variable Expansion:**
   - Create utility function for variable expansion
   - Support both `$VAR` and `${VAR}` syntax
   - Limit to standard variables: $HOME, $USER, $PWD
   - Handle missing variables gracefully with clear errors

3. **Tool Validation Logic:**
   - Each handler should validate its base_path
   - Check for expected directory structure
   - Provide handler-specific validation messages
   - Allow creation of missing directories with user confirmation or auto-create

4. **Edge Cases:**
   - Base path doesn't exist: Auto-create or error?
   - Invalid environment variable: Clear error message
   - Relative vs absolute paths: Resolve relative to Path.cwd()
   - Permissions issues: Handle gracefully with clear error
   - Multiple handlers with same base_path: Allow but warn?

5. **Testing Requirements:**
   - Unit tests for environment variable expansion
   - Unit tests for configuration precedence
   - Unit tests for path validation
   - Integration tests for deploy with custom base_path
   - Test cross-platform path handling
   - Mock file system operations

6. **Backward Compatibility:**
   - N/A - tool not yet deployed to users
   - Free to change defaults without migration

### Validation Requirements

1. **Configuration Validation:**
   - Validate handlers section structure
   - Ensure base_path is valid path string
   - Check environment variables exist before expansion
   - Validate against Pydantic schema

2. **Path Validation:**
   - Verify path is well-formed (not empty, no null bytes)
   - Check parent directory is writable if creating
   - Validate expanded path is absolute or relative
   - Tool-specific validation (e.g., Continue expects certain structure)

3. **Environment Variable Validation:**
   - Check variable is in allowed list ($HOME, $USER, $PWD)
   - Verify variable exists in environment
   - Handle both `$VAR` and `${VAR}` formats correctly
   - Clear error if variable undefined

4. **CLI Validation:**
   - Validate --base-path is provided with --handlers
   - Check --base-path is valid path string
   - Ensure --handlers specifies valid handler name
   - Error if handler not implemented yet

5. **Error Messages:**
   - Clear message if environment variable undefined
   - Helpful suggestion if path doesn't exist
   - Explicit error if tool validation fails
   - Guide user to fix configuration issues

### Success Criteria

1. User can specify custom base_path in config.yaml per handler
2. User can override base_path via --base-path CLI flag
3. Environment variables ($HOME, $USER, $PWD) expand correctly in both syntaxes
4. Paths auto-create if missing (or clear error if cannot create)
5. Tool validation confirms valid installation at base_path
6. Default behavior uses Path.cwd() instead of Path.home()
7. Per-project configs work independently with different base paths
8. All handlers have schema stubs even if not implemented
9. Comprehensive test coverage (>95%)
10. Type-safe implementation passing mypy strict mode
