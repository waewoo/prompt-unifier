# Spec Requirements: Kilo Code Handler

## Initial Description

Tool Handler Implementation: Kilo Code — Complete tool handler for Kilo Code following the established pattern, with full deployment logic, configuration file handling, and validation that prompts are correctly placed in the tool's expected location.

## Requirements Discussion

### First Round Questions

**Q1: Directory Structure**
Kilo Code uses `.kilocode/` as the base directory with TWO subdirectories:
- `.kilocode/workflows/` - for all invokable prompts (via slash-command /)
- `.kilocode/rules/` - for all passive rules applied globally (always active)

**Flat structure required** - No subdirectories within /workflows or /rules for maximum compatibility.

**Q2: Frontmatter Format**
**CRITICAL DIFFERENCE**: Kilo Code requires **pure Markdown without YAML frontmatter**.
- NO `---` delimiters
- NO YAML/JSON blocks at start of file
- Title from YAML becomes first line as `# Title`
- Description from YAML becomes paragraphs after title
- Body content preserved intact

**Q3: Handler Name & Constant**
Handler name: "kilocode" (no hyphen)
Constant: `KILO_CODE_DIR = ".kilocode"`

**Q4: Base Path Default**
Use `Path.cwd()` for project-local installations (not `Path.home()`)

**Q5: Feature Parity**
YES - Implement all same features as Continue handler:
- Backup/rollback functionality
- Subdirectory structure preservation (for source tracking)
- Content hash verification for deployment status
- Rich verification reports with VerificationResult dataclass
- Orphaned file cleanup

**Q6: Testing Coverage**
YES - Maintain >95% test coverage following TDD pattern

**Q7: Field Mapping for Metadata**
**ANSWER**: Include metadata as formatted Markdown text in the intro section after the description.

Format example:
```markdown
# Title

Description text here.

**Category:** Security | **Tags:** validation, security | **Version:** 1.0.0

[rest of content...]
```

Fields to include:
- `category` - if present
- `tags` - if present (comma-separated)
- `version` - if present
- `author` - if present
- `language` - if present
- `applies_to` - if present (for rules)

Format: `**FieldName:** value | **NextField:** value`

If no metadata fields are present, skip this section entirely.

### File Naming Convention

Files in output follow the pattern: `[directory]-[filename].md`

**Extraction Rules:**
- Extract parent directory name from source file path
- Normalize to kebab-case
- Examples:
  - `prompts/commands/explain.md` → `commands` → `commands-explain.md`
  - `prompts/standards/code-style.md` → `standards` → `standards-code-style.md`
  - `rules/security/restricted-files.md` → `security` → `security-restricted-files.md`
  - `prompts/explain.md` (no subdir) → none → `misc-explain.md`
- For multi-level paths (e.g., `prompts/dev/commands/explain.md`), use closest directory to file (`commands`)
- Default prefix for root files: `misc-` (configurable)

### Content Transformation Rules

1. **Extract YAML frontmatter fields:**
   - `name` → becomes Markdown H1 title (`# Title`)
   - `description` → becomes intro paragraphs after title
   - Optional metadata fields → formatted Markdown text line after description:
     - `category`, `tags`, `version`, `author`, `language`, `applies_to`
     - Format: `**Category:** value | **Tags:** tag1, tag2 | **Version:** 1.0.0`
     - Only include if fields are present in source

2. **Remove all YAML delimiters:**
   - No `---` blocks in output
   - Pure Markdown only

3. **Preserve body content:**
   - Keep all content after YAML frontmatter separator (`>>>` or after `---`)
   - Maintain code blocks, formatting, examples

4. **Variables/placeholders:**
   - Document any Continue-specific variables that may need adaptation
   - Note differences in placeholder syntax between Continue and Kilo Code

**Example Transformation:**

Source (with YAML):
```markdown
---
name: Code Review
description: Perform thorough code review
category: quality
tags: [review, testing]
version: 1.0.0
---
>>>
Review the code for...
```

Output (pure Markdown):
```markdown
# Code Review

Perform thorough code review

**Category:** quality | **Tags:** review, testing | **Version:** 1.0.0

Review the code for...
```

### Validation Requirements

Handler must validate:
- All generated files start with `# Title` (Markdown H1)
- No YAML frontmatter blocks remain
- All files are UTF-8 encoded (no BOM)
- File name uniqueness after applying `[directory]-[filename]` pattern
- Flat structure is maintained (no subdirs in /workflows or /rules)
- Directory names are normalized to kebab-case

### Configuration Options

Handler should support:
- Activation/deactivation of numeric prefixes (optional ordering)
- Choice of default prefix for root files (default: `misc-`)
- Format of directory-based prefixes (short vs. full name preservation)
- Inclusion/exclusion of description from YAML in output
- Custom output directory for testing before deployment
- Multi-level directory name handling (closest vs. concatenated)

## Existing Code to Reference

### Similar Features Identified:

**ContinueToolHandler** - Path: `src/prompt_unifier/handlers/continue_handler.py`
- Complete reference implementation with all Protocol methods
- Demonstrates backup/rollback, verification reports, Rich console output
- Use as model for structure and patterns
- **Key difference**: Kilo Code outputs pure Markdown, Continue preserves YAML frontmatter

**ToolHandler Protocol** - Path: `src/prompt_unifier/handlers/protocol.py`
- Defines interface with 7 required methods
- Documents required attributes: `prompts_dir`, `rules_dir`
- Must implement all methods from this Protocol

**ToolHandlerRegistry** - Path: `src/prompt_unifier/handlers/registry.py`
- Handler registration pattern
- Shows how to register new handlers in system

**Test Patterns** - Path: `tests/handlers/test_continue_handler.py`
- Reference for TDD test structure
- Shows pytest fixtures and test patterns for each Protocol method
- Demonstrates mocking and temporary directory usage

**CLI Integration** - Path: `src/prompt_unifier/cli/commands.py`
- Shows handler instantiation and usage in deploy command
- Handler validation via `validate_tool_installation()`
- Verification report display flow

## Visual Assets

### Files Provided:
Visual check performed via bash command - no files found in `planning/visuals/` directory.

### Visual Insights:
No visual assets provided. Implementation will rely on:
- Reference patterns from ContinueToolHandler

## Requirements Summary

### Functional Requirements

**Directory Structure:**
- Create `.kilocode/` base directory
- Create two flat subdirectories: `workflows/` and `rules/`
- No nested subdirectories in output

**File Naming:**
- Apply `[directory]-[filename].md` pattern
- Extract directory from source path
- Normalize to kebab-case
- Handle root files with default prefix

**Content Transformation:**
- Convert YAML frontmatter to pure Markdown
- Title as H1 (`# Title`)
- Description as intro paragraphs after title
- Metadata fields as formatted Markdown text: `**Field:** value | **Field:** value`
- Remove all YAML blocks (`---` delimiters)
- Preserve body content intact after YAML separator

**Validation:**
- Verify pure Markdown format (no YAML)
- Check file name uniqueness
- Ensure UTF-8 encoding
- Validate flat structure

### Reusability Opportunities

- Reuse ContinueToolHandler structure and patterns
- Follow ToolHandler Protocol interface
- Copy backup/rollback mechanisms
- Adapt verification report system
- Reuse orphaned file cleanup logic
- Follow test patterns from test_continue_handler.py

### Scope Boundaries

**In Scope:**
- Complete Kilo Code handler implementation
- YAML to pure Markdown transformation
- Directory-prefixed file naming
- Flat structure deployment
- Backup/rollback functionality
- Verification reports
- Comprehensive test coverage (>95%)
- Integration with handler registry
- CLI integration

**Out of Scope:**
- Modifying ToolHandler Protocol
- Changing handler registry implementation
- Implementing other handlers (Windsurf, Cursor, Aider)
- Creating plugin system for dynamic handler loading
- Internationalization
- GUI or web interface

### Technical Considerations

**Integration Points:**
- Must implement ToolHandler Protocol completely
- Register handler in `src/prompt_unifier/handlers/registry.py`
- Add constant to `src/prompt_unifier/constants.py`
- Update CLI commands.py for handler instantiation
- Follow existing patterns for base path configuration

**Existing System Constraints:**
- Python 3.12+ with type hints
- Pydantic models for validation
- Rich library for console output
- pytest with >95% coverage requirement
- Ruff linting and mypy type checking
- Cross-platform compatibility (Linux, macOS, Windows)

**Technology Stack:**
- Follow existing Python patterns from ContinueToolHandler
- Use pathlib for path handling
- Use PyYAML for frontmatter extraction
- Use Rich Console for output
- Use dataclasses for VerificationResult

**Key Differences from Continue Handler:**
1. **Pure Markdown output** (no YAML frontmatter blocks)
2. **Flat directory structure** with prefixed filenames
3. **Directory names**: `workflows/` and `rules/` (not `prompts/` and `rules/`)
4. **Content transformation**: YAML → Markdown text conversion
5. **File naming**: `[directory]-[filename].md` pattern

### Documentation Requirements

**README.md Updates:**
- Add Kilo Code handler section
- Explain usage and file generation process
- Document `[directory]-[filename].md` naming convention
- Include correspondence table (source → output mapping)
- Installation instructions for Kilo Code projects
- List available workflows and how to invoke them
- Describe active rules and behavior
- Note placeholder syntax differences vs. Continue

**TEST.md Updates:**
- Add Kilo Code handler test cases
- Test YAML frontmatter transformation
- Test multi-level directory handling
- Test edge cases (root files, name conflicts, special chars)
- Validate output specification compliance
- Verify no YAML frontmatter in output
- Confirm flat structure and file name uniqueness

### Correspondence Table Format

Example table to include in README.md:

| Source File | Source Directory | Generated File | Type | Invocation |
|-------------|------------------|----------------|------|------------|
| prompts/commands/explain.md | commands | commands-explain.md | workflow | /commands-explain |
| prompts/standards/code-style.md | standards | standards-code-style.md | rule | (always active) |
| rules/security/restricted-files.md | security | security-restricted-files.md | rule | (always active) |
