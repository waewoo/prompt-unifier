# Spec Requirements: Centralized Logging & Verbose Flag

## Initial Description
**Centralized Logging & Verbose Flag** - Add a centralized logging system and a global --verbose flag for debugging. This completes the Error Handling, Logging & User Feedback feature (item 13 in roadmap). The comprehensive error handling with user-friendly messages is already implemented.

## Requirements Discussion

### First Round Questions

**Q1:** I assume we'll use Python's built-in logging module for the centralized logging system rather than a third-party library like loguru. Is that correct?
**Answer:** Oui - use Python's built-in logging module

**Q2:** For the --verbose flag, I'm thinking a single level (-v for debug output). Should we instead support multiple verbosity levels (-v for INFO, -vv for DEBUG)?
**Answer:** Oui plusieurs niveaux - support multiple verbosity levels (-v for INFO, -vv for DEBUG)

**Q3:** I assume the default log level (without --verbose) should be WARNING, showing only warnings and errors. Is that correct, or should it default to INFO?
**Answer:** Oui - default to WARNING level

**Q4:** Should we include a --log-file option to write logs to a file for persistent debugging, or keep it terminal-only for the initial implementation?
**Answer:** Inclure --log-file - include the --log-file option for persistent debugging

**Q5:** For log formatting, should we have plain text formatting for file output but Rich formatting (colors, timestamps) for terminal output? Or keep both consistent?
**Answer:** Avoir le formatage Rich (couleurs, timestamps) - use Rich formatting for logs

**Q6:** Do you have specific requirements for how the logging should integrate with existing error handling (e.g., should caught exceptions automatically log at ERROR level)?
**Answer:** Non rien de specifique - no specific requirements for error handling integration

**Q7:** Is anything explicitly OUT OF SCOPE for this initial implementation (e.g., remote logging, log rotation, structured JSON logs)?
**Answer:** OUT OF SCOPE: remote logging, metriques, JSON structure

### Existing Code to Reference
User indicated to search the codebase for similar patterns.

**Similar Features Identified:**
- Feature: Global CLI Callback Pattern - Path: `src/prompt_unifier/cli/main.py`
  - Uses `@app.callback()` for global options like `--version`
  - Currently uses `-v` for version flag - need to handle conflict with verbose
  - Typer global option pattern with `is_eager=True` for priority processing

- Feature: Rich Console Usage - Path: `src/prompt_unifier/output/rich_formatter.py`
  - Uses `rich.console.Console()` for colored output
  - Established color constants (ERROR_COLOR = "red", WARNING_COLOR = "yellow", SUCCESS_COLOR = "green")
  - Symbol constants for status indicators
  - Pattern for Rich markup escaping

- Feature: Rich Table Formatter - Path: `src/prompt_unifier/output/rich_table_formatter.py`
  - Additional Rich output patterns

- Feature: Existing --verbose Flag - Path: `src/prompt_unifier/cli/main.py`
  - Commands `validate` (line 69) and `list_content` (line 147) already have local --verbose flags
  - Need to consolidate these into the global verbose system

### Follow-up Questions
None needed - user provided comprehensive answers.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable.

## Requirements Summary

### Functional Requirements
- Centralized logging system using Python's built-in logging module
- Global --verbose flag available on all commands
- Multiple verbosity levels: default WARNING, -v for INFO, -vv for DEBUG
- --log-file option for persistent log output to file
- Rich formatting for terminal log output (colors, timestamps)
- Integration with existing commands that have local verbose flags

### Reusability Opportunities
- **CLI Pattern**: Extend `@app.callback()` pattern in `main.py` for global verbose flag
- **Rich Console**: Use existing `RichFormatter` console patterns and color constants
- **Output Module**: Potential location for logging configuration in `src/prompt_unifier/output/`
- **Utils Module**: Alternative location for logging utilities in `src/prompt_unifier/utils/`

### Scope Boundaries
**In Scope:**
- Centralized logging module with Python logging
- Global --verbose/-v flag (with -vv for DEBUG)
- Default WARNING level
- --log-file option for file output
- Rich-formatted terminal logs with colors and timestamps
- Consolidation of existing local verbose flags into global system

**Out of Scope:**
- Remote logging
- Metrics collection
- Structured JSON logs
- Log rotation
- Performance monitoring
- Third-party logging libraries

### Technical Considerations
- **Flag Conflict**: Current -v is used for --version in main callback; need to change version to use only --version (no short flag) or use -V for version
- **Global State**: Need to establish logging configuration early in CLI lifecycle via callback
- **Rich Integration**: Use Rich's logging handler for colored terminal output
- **Typer Integration**: Use Typer's callback mechanism for global options
- **Existing Verbose Flags**: Commands `validate` and `list_content` have local --verbose flags that should delegate to global logging level
- **Tech Stack**: Python 3.11+, Typer CLI, Rich library, standard logging module
