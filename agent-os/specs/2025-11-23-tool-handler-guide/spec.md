# Specification: Tool Handler Guide

## Goal
Create a comprehensive, beginner-friendly guide in DEVELOPMENT.md that teaches developers how to add new tool handlers to prompt-unifier, using a tutorial-style approach with a complete fictitious handler example.

## User Stories
- As a contributor, I want a step-by-step guide so that I can add support for a new AI tool without needing to reverse-engineer the existing code
- As a beginner Python developer, I want clear explanations and complete code examples so that I can understand the handler architecture and implement my own handler

## Specific Requirements

**Protocol Documentation Section**
- Document all 7 methods in `ToolHandler` Protocol from `src/prompt_unifier/handlers/protocol.py`
- Explain each method's purpose, parameters, and return values
- Document required attributes: `prompts_dir`, `rules_dir`
- Include type hints explanations for beginners (Path, Any, Protocol)
- Explain what `@runtime_checkable` decorator does

**Tutorial Handler Example**
- Create a complete fictitious handler example (e.g., "ExampleToolHandler" for a hypothetical "ExampleAI" tool)
- Show the full implementation from start to finish
- Include all required methods with working code
- Demonstrate advanced features: backup/rollback, verification reports, subdirectory support
- Follow exact patterns from ContinueToolHandler

**Registry Integration Section**
- Explain the ToolHandlerRegistry class from `src/prompt_unifier/handlers/registry.py`
- Show how to register a handler in `commands.py` (lines 1097-1120)
- Document the `register()`, `get_handler()`, `list_handlers()`, `get_all_handlers()` methods
- Explain handler name uniqueness requirements

**TDD Testing Section**
- Explain test-driven development workflow for handlers
- Show test file structure mirroring `tests/handlers/`
- Provide example test cases for each Protocol method
- Include pytest fixtures examples for handler setup
- Reference existing test patterns from `test_continue_handler.py`

**CLI Integration Section**
- Explain how handlers are used in the `deploy` command (lines 1014-1322 in commands.py)
- Document the `resolve_handler_base_path()` helper function
- Show how `--handlers` flag filters which handlers to use
- Explain handler validation via `validate_tool_installation()`
- Document the verification report flow

**File Structure Section**
- Document naming conventions: `<tool>_handler.py`, `test_<tool>_handler.py`
- Show required file locations in `src/prompt_unifier/handlers/` and `tests/handlers/`
- Explain how to update `__init__.py` exports
- Include checklist of files to create/modify

**Content Processing Section**
- Explain `_process_prompt_content()` and `_process_rule_content()` methods
- Document YAML frontmatter transformation for tool-specific formats
- Show how to handle optional fields
- Explain content hash comparison in `get_deployment_status()`

**CONTRIBUTING.md Update**
- Add reference to DEVELOPMENT.md in the "Development and Testing" section
- Ensure CONTRIBUTING.md properly directs contributors to the new guide

## Existing Code to Leverage

**src/prompt_unifier/handlers/protocol.py**
- Contains the ToolHandler Protocol definition
- Documents all required methods with docstrings
- Use as the authoritative reference for interface requirements

**src/prompt_unifier/handlers/continue_handler.py**
- Complete reference implementation (681 lines)
- Demonstrates all Protocol methods
- Shows advanced patterns: VerificationResult dataclass, Rich console output, backup/rollback
- Use as the model for the tutorial example

**src/prompt_unifier/handlers/registry.py**
- Simple registry pattern implementation
- Shows registration, retrieval, and listing methods
- Document type checking with `isinstance(handler, ToolHandler)`

**src/prompt_unifier/cli/commands.py**
- Shows handler instantiation with `resolve_handler_base_path()` (lines 1062-1094)
- Shows registry usage in deploy command (lines 1097-1127)
- Demonstrates verification report display (lines 1260-1267, 1304-1307)

**tests/handlers/test_continue_handler.py**
- Reference for test patterns and fixtures
- Shows how to test each Protocol method
- Demonstrates mocking and temporary directory usage

## Out of Scope
- Actually implementing new handlers (Kilo Code, Windsurf, Cursor, Aider)
- Modifying the ToolHandler Protocol
- Changing the ToolHandlerRegistry implementation
- Adding new Protocol methods
- Creating a plugin system for dynamic handler loading
- Internationalization of the guide
- Video tutorials or interactive examples
- Detailed explanation of Rich library usage beyond handler context
- Explaining the entire prompt-unifier architecture beyond handlers
