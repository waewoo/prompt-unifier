# Specification: Centralized Logging & Verbose Flag

## Goal
Implement a centralized logging system using Python's built-in logging module with a global --verbose flag that enables multiple verbosity levels across all CLI commands, supporting both terminal and file output with Rich formatting.

## User Stories
- As a developer debugging issues, I want to enable verbose output with -v or -vv flags so that I can see detailed logs without modifying code
- As a user troubleshooting, I want to save logs to a file with --log-file so that I can share debug information or review it later
- As a CLI user, I want consistent logging behavior across all commands so that the debugging experience is predictable

## Specific Requirements

**Logging Module Architecture**
- Create new logging module at `src/prompt_unifier/logging/` or add to `src/prompt_unifier/utils/`
- Use Python's built-in logging module (no third-party libraries like loguru)
- Implement a `configure_logging()` function that sets up handlers based on verbosity level
- Export logging configuration through the module's `__init__.py`
- Design for easy import and use throughout the codebase

**Global Verbose Flag Implementation**
- Add --verbose option to the `@app.callback()` in `main.py`
- Resolve -v conflict: change --version to use only --version (no short flag) or use -V for version
- Support multiple verbosity levels: no flag = WARNING, -v = INFO, -vv = DEBUG
- Use `typer.Option` with `count=True` to accumulate -v flags
- Set `is_eager=True` to configure logging before command execution
- Pass verbosity level to `configure_logging()` in the callback

**Log Level Configuration**
- Default level: WARNING (shows warnings and errors only)
- Single -v flag: INFO level (shows informational messages)
- Double -vv flag: DEBUG level (shows all debug output)
- Map integer count to logging levels: 0=WARNING, 1=INFO, 2+=DEBUG
- Apply level to root logger to affect all modules

**File Logging Support**
- Add --log-file option to the global callback alongside --verbose
- Accept file path string; create/append to the specified file
- Use plain text format for file output (no Rich colors/ANSI codes)
- Include timestamp, level, module name, and message in file format
- Handle file permission errors gracefully with user-friendly messages

**Rich Terminal Formatting**
- Use `rich.logging.RichHandler` for console output
- Include timestamps in log messages
- Apply color coding: red for ERROR, yellow for WARNING, green for INFO, default for DEBUG
- Follow color constants pattern from `RichFormatter` (ERROR_COLOR, WARNING_COLOR, SUCCESS_COLOR)
- Ensure Rich markup is properly escaped in log messages

**Existing Verbose Flag Migration**
- Update `validate` command (line 69 in main.py) to use global logging level
- Update `list_content` command (line 147 in main.py) to use global logging level
- Remove local --verbose/-v options from these commands
- Commands should call `logging.info()`, `logging.debug()` instead of checking verbose boolean
- Maintain backward compatibility in command behavior

**Logging Integration Pattern**
- Import logger with `logging.getLogger(__name__)` in each module
- Use appropriate log levels: DEBUG for detailed tracing, INFO for progress, WARNING for issues
- Log at module entry points for key operations (sync, validate, deploy, etc.)
- Include contextual information (file paths, counts, durations) in log messages

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**Global CLI Callback Pattern (`src/prompt_unifier/cli/main.py`)**
- Use existing `@app.callback()` decorator pattern at lines 48-60
- Follow `version_callback` pattern for option handling
- Modify `main_callback` to accept new --verbose and --log-file options
- Note: -v is currently used for --version; needs resolution (change to -V or remove short flag)

**Rich Console Usage (`src/prompt_unifier/output/rich_formatter.py`)**
- Reuse color constants: ERROR_COLOR = "red", WARNING_COLOR = "yellow", SUCCESS_COLOR = "green"
- Follow Console instantiation pattern
- Apply Rich markup escaping pattern using `rich.markup.escape()`
- Consider using `rich.logging.RichHandler` for formatted log output

**Utils Module Structure (`src/prompt_unifier/utils/`)**
- Follow existing module pattern for new logging utilities
- Review `__init__.py` exports for adding logging configuration
- Consider placing logging.py alongside path_helpers.py and other utilities

**Existing Verbose Flags in Commands**
- `validate` command has `verbose: bool = typer.Option(False, "--verbose", "-v")` at line 69
- `list_content` command has similar pattern at line 147
- These demonstrate current verbose usage that will be consolidated into global logging

## Out of Scope
- Remote logging services or external log aggregation
- Metrics collection or performance monitoring
- Structured JSON log format output
- Log rotation or size-based file management
- Third-party logging libraries (loguru, structlog, etc.)
- Automatic exception logging integration with existing error handlers
- Log filtering by module or component
- Environment variable configuration for log levels
- Async logging handlers
- Log message templating or string interpolation optimization
