# Spec Requirements: Prompt Format Specification & Validation Engine

## Initial Description
Prompt Format Specification & Validation Engine — Define and document the standardized prompt format (YAML frontmatter + >>> separator), implement Pydantic models for prompt structure, create validation logic to parse and verify prompt files, and provide detailed error messages for format violations.

## Requirements Discussion

### First Round Questions

**Q1: YAML Schema Structure**
**Answer:**
- Required fields: `name` (string), `description` (string), `tags` (list of strings)
- Optional fields: `version` (semver string), `author` (string)
- NO tools field
- STRUCTURE: FLAT ONLY (no nested YAML structures)

**Q2: Separator Rules**
**Answer:**
- ONE SINGLE `>>>` allowed in the entire file
- Must be on its own line without any other characters
- Additional `>>>` separators = ERROR
- No whitespace before/after the separator on its line

**Q3: Error Messages Format**
**Answer:**
- Colors: Red for ERRORS, Yellow for WARNINGS
- Warnings DO NOT BLOCK deployment
- Errors BLOCK deployment
- Include line numbers, code excerpts, and suggestions

**Q4: File Encoding**
**Answer:**
- UTF-8 mandatory
- REJECT files with invalid UTF-8 sequences
- No auto-detection or conversion

**Q5: Strict Mode**
**Answer:** NO (not for now)

**Q6: Prompt Content Validation**
**Answer:**
- Validate ONLY frontmatter + separator
- Treat content after `>>>` as opaque text (no validation)
- Empty content after `>>>` = ERROR

**Q7: Multi-File Validation**
**Answer:**
- File extension: .md
- Collect ALL errors (don't stop at first error)
- Generate summary report
- Continue validation even after errors

**Q8: Example Format**
**Answer:**
```yaml
name: python-expert
description: Expert Python developer with focus on clean code
version: 1.0.0
tags:
  - python
  - backend
author: John Doe
>>>
You are an expert Python developer...
```

### Follow-up Questions

**Follow-up 1: File Discovery Method**
**Answer:** Option B - Scanner scans a specific directory

**Follow-up 2: Report Output Format**
**Answer:**
- Default: Human-readable text for CLI
- Flag `--json` available for machine-readable output (CI/CD)
- Exit codes: 0 = success, 1 = errors found

**Follow-up 3: Warning Triggers**
**Answer:**
- Missing optional fields (version, author)
- Empty tags list `tags: []`

**Follow-up 4: Separator Line Format**
**Answer:**
- On its own line without other characters
- No whitespace before/after
- Empty content after `>>>` = ERROR

### Existing Code to Reference

No similar existing features identified for reference.

### Visual Assets

No visual assets provided.

## Requirements Summary

### Functional Requirements

#### FR1: Prompt File Format Specification
- **Format Structure**: YAML frontmatter + `>>>` separator + prompt content
- **File Extension**: `.md` (Markdown)
- **Encoding**: UTF-8 only (strict enforcement)
- **Structure**: Flat YAML only (no nested objects/structures)

#### FR2: YAML Frontmatter Schema

**Required Fields:**
- `name` (string): Prompt identifier
- `description` (string): Brief description of prompt purpose

**Optional Fields:**
- `version` (string): Semantic version (e.g., "1.0.0")
- `tags` (list of strings): Categorization tags
- `author` (string): Author name

**Prohibited Fields:**
- `tools`: Not allowed in this format

**Field Validation Rules:**
- All field names must be lowercase
- No nested YAML structures permitted
- `name` must be non-empty string
- `description` must be non-empty string
- `version` must follow semantic versioning if provided
- `tags` must be a list (can be empty, but triggers warning)

#### FR3: Separator Rules
- **Exactly ONE** `>>>` separator allowed per file
- Separator must be on its own line
- No whitespace before or after `>>>` on the line
- No other characters allowed on separator line
- Multiple `>>>` separators = validation error

#### FR4: Prompt Content Rules
- Content after `>>>` is treated as opaque text
- No validation performed on prompt content structure
- Empty content after `>>>` = validation error
- Content can span multiple lines
- UTF-8 encoding enforced for content

#### FR5: Validation Error Classification

**ERRORS (Block Deployment):**
- Invalid UTF-8 encoding
- Missing required fields (`name`, `description`)
- Multiple `>>>` separators
- No `>>>` separator found
- `>>>` separator not on its own line
- Whitespace before/after `>>>` on separator line
- Empty content after `>>>` separator
- Invalid YAML syntax
- Nested YAML structures
- Invalid semver format in `version` field
- Prohibited field present (e.g., `tools`)

**WARNINGS (Do Not Block):**
- Missing optional field: `version`
- Missing optional field: `author`
- Empty `tags` list (`tags: []`)

#### FR6: Multi-File Validation
- Scan specific directory for `.md` files
- Validate ALL files in directory
- Collect all errors from all files (don't stop at first)
- Generate summary report across all files
- Continue validation even when errors found
- Report per-file validation status

#### FR7: Validation Report Format

**Default: Human-Readable CLI Output**
- Red text for errors
- Yellow text for warnings
- Include line numbers
- Include code excerpts showing problematic lines
- Provide actionable suggestions for fixes
- Summary section with counts

**JSON Output Format (--json flag):**
- Machine-readable structured output
- Array of validation results per file
- Error/warning objects with:
  - `file`: file path
  - `line`: line number
  - `severity`: "error" or "warning"
  - `code`: error code identifier
  - `message`: description
  - `excerpt`: code snippet
  - `suggestion`: fix recommendation

**Exit Codes:**
- `0`: Validation successful (warnings allowed)
- `1`: Validation failed (errors found)

### Technical Requirements

#### TR1: UTF-8 Encoding Validation
- Read files as UTF-8 with strict error handling
- Reject files with invalid UTF-8 byte sequences
- Report encoding errors with file name
- No automatic encoding detection or conversion

#### TR2: YAML Parsing
- Use PyYAML for frontmatter parsing
- Validate YAML syntax before schema validation
- Detect and reject nested structures
- Extract frontmatter section (before `>>>`)

#### TR3: Pydantic Data Models
- Create Pydantic model for prompt frontmatter
- Field validators for:
  - Required field presence
  - Semantic versioning format
  - Non-empty strings
  - List type for tags
- Custom validators for format-specific rules

#### TR4: File System Operations
- Use pathlib for cross-platform path handling
- Scan directory for `.md` files recursively
- Handle file read errors gracefully
- Support absolute and relative paths

#### TR5: Terminal Output
- Use Rich library for colored output
- Format tables for summary reports
- Syntax highlighting for code excerpts
- Progress indicators for multi-file validation

#### TR6: Command Line Interface
- Validate command with directory argument
- Optional `--json` flag for JSON output
- Support `--verbose` for detailed logging
- Clear help text with examples

### Validation Algorithm

#### Step 1: File Discovery
1. Accept directory path as input
2. Scan directory for `.md` files
3. Collect list of files to validate

#### Step 2: Per-File Validation
For each file:
1. **Encoding Check**: Attempt to read file as UTF-8
   - If fails: Record error, skip file
2. **Separator Detection**: Split content on `>>>`
   - If 0 separators: Record error
   - If >1 separator: Record error
   - If separator not on own line: Record error
   - If whitespace around separator: Record error
3. **Frontmatter Parsing**: Parse YAML before separator
   - If invalid YAML: Record error
   - If nested structures detected: Record error
4. **Schema Validation**: Validate against Pydantic model
   - Check required fields present
   - Check prohibited fields absent
   - Validate field types and formats
   - Record errors and warnings
5. **Content Check**: Verify content after separator
   - If empty: Record error

#### Step 3: Report Generation
1. Aggregate all errors and warnings
2. Format output based on mode (CLI vs JSON)
3. Return exit code based on error presence

### Example Valid Prompt Files

#### Example 1: Minimal Valid Prompt
```markdown
name: code-reviewer
description: Reviews code for best practices
>>>
You are a code reviewer focused on identifying bugs and improvements.
```

#### Example 2: Full Valid Prompt
```markdown
name: python-expert
description: Expert Python developer with focus on clean code
version: 1.0.0
tags:
  - python
  - backend
author: John Doe
>>>
You are an expert Python developer with deep knowledge of:
- Clean code principles
- Design patterns
- Performance optimization
- Testing best practices

Always provide well-documented, type-hinted code.
```

#### Example 3: Valid with Empty Tags (Warning)
```markdown
name: general-assistant
description: General purpose coding assistant
tags: []
>>>
You are a helpful coding assistant.
```

### Example Invalid Prompt Files

#### Invalid 1: Missing Required Field
```markdown
name: broken-prompt
>>>
This will fail validation - missing description.
```
**Error**: Missing required field 'description'

#### Invalid 2: Multiple Separators
```markdown
name: multi-separator
description: Has too many separators
>>>
First section
>>>
Second section
```
**Error**: Multiple '>>>' separators found (2), only 1 allowed

#### Invalid 3: Separator Not Alone
```markdown
name: bad-separator
description: Separator has extra content
>>> some text
Content here
```
**Error**: Separator '>>>' must be on its own line

#### Invalid 4: Empty Content
```markdown
name: no-content
description: Has no content after separator
>>>
```
**Error**: Empty content after '>>>' separator

#### Invalid 5: Nested YAML Structure
```markdown
name: nested-structure
description: Contains nested YAML
metadata:
  team: engineering
  priority: high
>>>
Content here
```
**Error**: Nested YAML structures not allowed (found 'metadata' with nested fields)

#### Invalid 6: Invalid UTF-8
```
File contains byte sequence: 0xFF 0xFE (invalid UTF-8)
```
**Error**: Invalid UTF-8 encoding detected

#### Invalid 7: Prohibited Field
```markdown
name: has-tools
description: Contains prohibited tools field
tools:
  - continue
  - cursor
>>>
Content here
```
**Error**: Prohibited field 'tools' found in frontmatter

### CLI Command Interface

#### Command Structure
```bash
prompt-unifier validate <directory> [OPTIONS]
```

#### Arguments
- `<directory>`: Path to directory containing .md prompt files (required)

#### Options
- `--json`: Output validation results in JSON format
- `--verbose`: Show detailed validation progress
- `--help`: Display help information

#### Example Usage
```bash
# Validate prompts directory with human-readable output
prompt-unifier validate ./prompts

# Validate with JSON output for CI/CD
prompt-unifier validate ./prompts --json

# Verbose validation
prompt-unifier validate ./prompts --verbose
```

### Expected Validation Report Format

#### CLI Format (Human-Readable)

```
Validating prompts in: ./prompts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ python-expert.md (PASSED)
  ⚠ Warning: Missing optional field 'author'

✗ broken-prompt.md (FAILED)
  ✗ Error [line 1]: Missing required field 'description'
     Suggestion: Add 'description' field to frontmatter

✗ multi-separator.md (FAILED)
  ✗ Error [line 5]: Multiple '>>>' separators found (2), only 1 allowed
     Excerpt:
       3 | >>>
       4 | First section
       5 | >>>
     Suggestion: Remove extra '>>>' separators, keep only one

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
  Total files: 3
  Passed: 1
  Failed: 2
  Errors: 3
  Warnings: 1

Validation FAILED ✗
```

#### JSON Format (Machine-Readable)

```json
{
  "summary": {
    "total_files": 3,
    "passed": 1,
    "failed": 2,
    "error_count": 3,
    "warning_count": 1,
    "success": false
  },
  "results": [
    {
      "file": "python-expert.md",
      "status": "passed",
      "errors": [],
      "warnings": [
        {
          "line": null,
          "severity": "warning",
          "code": "MISSING_OPTIONAL_FIELD",
          "message": "Missing optional field 'author'",
          "suggestion": "Consider adding 'author' field"
        }
      ]
    },
    {
      "file": "broken-prompt.md",
      "status": "failed",
      "errors": [
        {
          "line": 1,
          "severity": "error",
          "code": "MISSING_REQUIRED_FIELD",
          "message": "Missing required field 'description'",
          "excerpt": "name: broken-prompt\n>>>",
          "suggestion": "Add 'description' field to frontmatter"
        }
      ],
      "warnings": []
    },
    {
      "file": "multi-separator.md",
      "status": "failed",
      "errors": [
        {
          "line": 5,
          "severity": "error",
          "code": "MULTIPLE_SEPARATORS",
          "message": "Multiple '>>>' separators found (2), only 1 allowed",
          "excerpt": ">>>\nFirst section\n>>>",
          "suggestion": "Remove extra '>>>' separators, keep only one"
        }
      ],
      "warnings": []
    }
  ]
}
```

### Error Code Reference

| Code | Severity | Description |
|------|----------|-------------|
| `INVALID_ENCODING` | Error | File not valid UTF-8 |
| `MISSING_REQUIRED_FIELD` | Error | Required field absent |
| `INVALID_YAML` | Error | YAML syntax error |
| `NESTED_STRUCTURE` | Error | Nested YAML not allowed |
| `NO_SEPARATOR` | Error | Missing `>>>` separator |
| `MULTIPLE_SEPARATORS` | Error | More than one `>>>` found |
| `SEPARATOR_NOT_ALONE` | Error | Separator not on own line |
| `SEPARATOR_WHITESPACE` | Error | Whitespace around separator |
| `EMPTY_CONTENT` | Error | No content after separator |
| `INVALID_SEMVER` | Error | Invalid version format |
| `PROHIBITED_FIELD` | Error | Forbidden field present |
| `MISSING_OPTIONAL_FIELD` | Warning | Optional field absent |
| `EMPTY_TAGS_LIST` | Warning | Tags list is empty |

### Acceptance Criteria

#### AC1: File Format Validation
- [x] System rejects files without `.md` extension
- [x] System enforces UTF-8 encoding strictly
- [x] System validates YAML frontmatter syntax
- [x] System enforces flat YAML structure (no nesting)

#### AC2: Required Fields Validation
- [x] System errors when `name` field missing
- [x] System errors when `description` field missing
- [x] System accepts valid prompts with only required fields

#### AC3: Optional Fields Validation
- [x] System warns when `version` field missing
- [x] System warns when `author` field missing
- [x] System warns when `tags` list is empty
- [x] System validates semver format in `version` when present

#### AC4: Separator Validation
- [x] System errors when no `>>>` separator found
- [x] System errors when multiple `>>>` separators found
- [x] System errors when `>>>` not on its own line
- [x] System errors when whitespace around `>>>` on its line

#### AC5: Content Validation
- [x] System errors when content after `>>>` is empty
- [x] System treats prompt content as opaque text
- [x] System does not validate prompt content structure

#### AC6: Prohibited Fields
- [x] System errors when `tools` field present
- [x] System can be extended to prohibit additional fields

#### AC7: Error Reporting
- [x] Errors displayed in red, warnings in yellow
- [x] Line numbers included for all issues
- [x] Code excerpts shown for context
- [x] Actionable suggestions provided
- [x] Error codes assigned to each issue type

#### AC8: Multi-File Validation
- [x] System validates all `.md` files in directory
- [x] System collects all errors from all files
- [x] System continues after encountering errors
- [x] System generates summary report

#### AC9: Output Formats
- [x] Default CLI output is human-readable
- [x] `--json` flag produces machine-readable JSON
- [x] Exit code 0 on success (warnings allowed)
- [x] Exit code 1 on errors

#### AC10: Integration with Product
- [x] Aligns with CLI-first architecture
- [x] Uses Rich for terminal output
- [x] Uses Pydantic for validation models
- [x] Follows TDD methodology
- [x] Supports CI/CD integration via JSON output

### Alignment with Product Context

#### Mission Alignment
- **CLI-First Design**: Validation runs entirely via command-line, no GUI
- **Git-Centric**: Validates prompts stored in Git repositories
- **Standardization**: Enforces formal prompt format specification
- **Developer-Focused**: Clear error messages, exit codes for scripting

#### Roadmap Integration
- **Roadmap Item #2**: Directly implements prompt format specification and validation engine
- **Foundation for Item #7**: Deploy command will depend on validated prompts
- **Enables Item #10**: Testable validation logic for TDD approach
- **Supports Item #12**: Format specification becomes core documentation

#### Tech Stack Usage
- **Python 3.12+**: Modern type hints, Protocol classes
- **Pydantic**: Frontmatter schema validation
- **PyYAML**: YAML parsing
- **Rich**: Colored terminal output, tables, progress
- **pytest**: Test-driven validation logic
- **Ruff**: Linted codebase
- **mypy**: Type-safe validation code

#### TDD Methodology
Each requirement maps to testable behavior:
- Test valid prompt files pass validation
- Test each error condition triggers correct error
- Test each warning condition triggers correct warning
- Test multi-file aggregation
- Test JSON output structure
- Test exit codes
- Test encoding rejection
- Test separator detection
- Test content emptiness check

### Implementation Notes

#### Phase 1: Core Validation Logic
1. Implement Pydantic models for frontmatter schema
2. Create validator for separator detection
3. Build UTF-8 encoding checker
4. Implement error/warning collection

#### Phase 2: File Processing
1. Directory scanner for `.md` files
2. Per-file validation orchestrator
3. Error aggregation across files
4. Summary generation

#### Phase 3: Output Formatting
1. CLI formatter with Rich (colors, tables)
2. JSON formatter with structured output
3. Exit code handling
4. Error code system

#### Phase 4: CLI Integration
1. Add `validate` command to CLI
2. Argument/option parsing
3. Progress indicators for multi-file
4. Help text and examples

#### Phase 5: Testing & Documentation
1. Comprehensive pytest suite
2. Valid/invalid example files
3. Format specification documentation
4. CLI usage guide

### Future Enhancements (Out of Scope)
- Strict mode (mentioned but deferred)
- Custom validation rules via config
- Auto-fix suggestions for common errors
- Watch mode for continuous validation
- Integration with pre-commit hooks
- Validation of prompt content semantics
