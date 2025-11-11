# Task Breakdown: Prompt Format Specification & Validation Engine

## Overview
**Total Task Groups:** 7
**Tech Stack:** Python 3.12+, Pydantic v2, PyYAML, Rich, Typer, pytest
**Methodology:** TDD with 85%+ coverage requirement
**Exit Criteria:** All tests pass, mypy/ruff validation passes, validation engine fully functional

## Task List

### Task Group 1: Core Data Models & Schema Validation
**Dependencies:** None
**Specialist:** Backend/Data Engineer
**Estimated Complexity:** Medium

- [x] 1.0 Complete Pydantic models for frontmatter validation
  - [x] 1.1 Write 5-8 focused tests for PromptFrontmatter model
    - Test required fields validation (name, description)
    - Test optional fields acceptance (version, tags, author)
    - Test prohibited fields rejection (tools field)
    - Test semantic versioning regex validation
    - Test non-empty string constraints
    - Test flat structure enforcement (no nested dicts)
    - Test field type validation (string vs list)
    - Test model serialization to dict
  - [x] 1.2 Create PromptFrontmatter Pydantic model in `src/prompt_manager/models/prompt.py`
    - Required fields: name (str), description (str)
    - Optional fields: version (str | None), tags (list[str] | None), author (str | None)
    - Use `field_validator` for non-empty string validation on name/description
    - Use custom validator for semantic versioning regex: `^\d+\.\d+\.\d+$`
    - Use `model_validator(mode='after')` to reject prohibited fields (tools)
    - Add detailed error messages with field names
    - Use Pydantic v2 API (Field, field_validator, model_validator)
  - [x] 1.3 Create error/warning classification enums in `src/prompt_manager/models/validation.py`
    - ValidationSeverity enum: ERROR, WARNING
    - ErrorCode enum with 12 error types:
      - INVALID_ENCODING, MISSING_REQUIRED_FIELD, INVALID_YAML
      - NESTED_STRUCTURE, NO_SEPARATOR, MULTIPLE_SEPARATORS
      - SEPARATOR_NOT_ALONE, SEPARATOR_WHITESPACE, EMPTY_CONTENT
      - INVALID_SEMVER, PROHIBITED_FIELD, INVALID_FILE_EXTENSION
    - WarningCode enum with 3 warning types:
      - MISSING_OPTIONAL_FIELD, EMPTY_TAGS_LIST, MISSING_AUTHOR
  - [x] 1.4 Create ValidationIssue Pydantic model in `src/prompt_manager/models/validation.py`
    - Fields: line (int | None), severity (ValidationSeverity), code (str)
    - Fields: message (str), excerpt (str | None), suggestion (str)
    - Enable JSON serialization via model_dump()
  - [x] 1.5 Create ValidationResult Pydantic model in `src/prompt_manager/models/validation.py`
    - Fields: file (Path), status (Literal["passed", "failed"])
    - Fields: errors (list[ValidationIssue]), warnings (list[ValidationIssue])
    - Computed property: is_valid (no errors)
  - [x] 1.6 Ensure data model tests pass
    - Run ONLY tests from 1.1 (`pytest tests/models/test_prompt.py`)
    - Verify all validators trigger correctly
    - Verify error messages are descriptive

**Acceptance Criteria:**
- All 5-8 model tests pass
- PromptFrontmatter rejects prohibited fields
- Semantic versioning validation works correctly
- ValidationIssue and ValidationResult serialize to JSON
- mypy passes with strict mode on models
- No Pydantic validation warnings

---

### Task Group 2: File Parsing & Separator Detection
**Dependencies:** Task Group 1 (COMPLETED)
**Specialist:** Backend/Parsing Engineer
**Estimated Complexity:** Medium-High

- [x] 2.0 Complete file parsing and separator validation logic
  - [x] 2.1 Write 6-8 focused tests for separator detection
    - Test single valid separator detection
    - Test no separator error
    - Test multiple separator error (2+ separators)
    - Test separator with trailing content error
    - Test separator with leading whitespace error
    - Test separator with trailing whitespace error
    - Test empty content after separator error
    - Test valid content after separator
  - [x] 2.2 Create SeparatorValidator class in `src/prompt_manager/core/separator.py`
    - Method: validate_separator(file_content: str) -> tuple[str, str, list[ValidationIssue]]
    - Return: (frontmatter_text, content_text, issues)
    - Detect exactly one `>>>` on its own line using line-by-line check
    - Error if 0 separators found (NO_SEPARATOR)
    - Error if 2+ separators found (MULTIPLE_SEPARATORS) with line numbers
    - Error if `>>>` line has other characters (SEPARATOR_NOT_ALONE)
    - Error if `>>>` line has leading/trailing whitespace (SEPARATOR_WHITESPACE)
    - Error if content after separator is empty/whitespace-only (EMPTY_CONTENT)
    - Track line numbers for all issues
  - [x] 2.3 Write 4-6 focused tests for UTF-8 encoding validation
    - Test valid UTF-8 file loads successfully
    - Test invalid UTF-8 bytes trigger INVALID_ENCODING error
    - Test file not found error handling
    - Test permission denied error handling (optional, may be hard to test)
    - Test empty file error handling
  - [x] 2.4 Create EncodingValidator class in `src/prompt_manager/core/encoding.py`
    - Method: validate_encoding(file_path: Path) -> tuple[str | None, list[ValidationIssue]]
    - Return: (file_content or None, issues)
    - Read file with strict UTF-8 encoding (errors='strict')
    - Catch UnicodeDecodeError and generate INVALID_ENCODING error
    - Handle file system errors (FileNotFoundError, PermissionError)
    - Return None content if encoding fails (allows rest of pipeline to skip)
  - [x] 2.5 Write 5-7 focused tests for YAML parsing
    - Test valid flat YAML parses successfully
    - Test invalid YAML syntax triggers INVALID_YAML error
    - Test nested YAML structure triggers NESTED_STRUCTURE error
    - Test empty YAML frontmatter error
    - Test YAML with list values (tags field)
    - Test YAML parsing with line number tracking
    - Test YAML with prohibited fields detection preparation
  - [x] 2.6 Create YAMLParser class in `src/prompt_manager/core/yaml_parser.py`
    - Method: parse_yaml(yaml_text: str) -> tuple[dict | None, list[ValidationIssue]]
    - Return: (parsed_dict or None, issues)
    - Use `yaml.safe_load()` to parse YAML
    - Catch yaml.YAMLError and generate INVALID_YAML error with line number
    - Detect nested structures by checking if any value is dict type
    - Generate NESTED_STRUCTURE error with field name if nesting found
    - Return flattened dict with string/list values only
  - [x] 2.7 Ensure parsing layer tests pass
    - Run ONLY tests from 2.1, 2.3, 2.5 (`pytest tests/core/`)
    - Verify all error codes generated correctly
    - Verify line number tracking works

**Acceptance Criteria:**
- All 15-21 parsing tests pass
- Separator detection handles all edge cases (no separator, multiple separators, whitespace, etc.)
- UTF-8 encoding strictly enforced
- YAML parsing detects nesting
- Line numbers tracked for all errors
- Error messages are actionable

---

### Task Group 3: Schema Validation Pipeline
**Dependencies:** Task Groups 1, 2
**Specialist:** Backend/Validation Engineer
**Estimated Complexity:** Medium

- [x] 3.0 Complete schema validation pipeline integration
  - [x] 3.1 Write 6-8 focused tests for PromptValidator orchestration
    - Test valid minimal prompt (name, description only) passes
    - Test valid full prompt (all optional fields) passes with warnings
    - Test missing required field generates error
    - Test prohibited field generates error
    - Test invalid semver generates error
    - Test missing optional fields generate warnings
    - Test empty tags list generates warning
    - Test multiple errors collected (not stopping at first)
  - [x] 3.2 Create PromptValidator class in `src/prompt_manager/core/validator.py`
    - Method: validate_file(file_path: Path) -> ValidationResult
    - Orchestrate full validation pipeline:
      1. EncodingValidator.validate_encoding()
      2. SeparatorValidator.validate_separator()
      3. YAMLParser.parse_yaml()
      4. PromptFrontmatter Pydantic validation
      5. Content emptiness check
    - Collect all errors/warnings from each step
    - Continue pipeline even after errors (collect all issues)
    - Return ValidationResult with file path, status, errors, warnings
  - [x] 3.3 Implement Pydantic error translation in PromptValidator
    - Catch pydantic.ValidationError from model validation
    - Map Pydantic errors to ValidationIssue objects:
      - missing field -> MISSING_REQUIRED_FIELD
      - invalid version format -> INVALID_SEMVER
      - prohibited field -> PROHIBITED_FIELD
    - Extract field names from Pydantic error location
    - Generate actionable suggestions based on error type
  - [x] 3.4 Implement warning detection logic in PromptValidator
    - Check if optional fields missing (version, author)
    - Generate MISSING_OPTIONAL_FIELD warnings with field name
    - Check if tags field is empty list
    - Generate EMPTY_TAGS_LIST warning if tags == []
    - Warnings do not affect validation status (status can be "passed")
  - [x] 3.5 Write 4-6 tests for ValidationResult aggregation
    - Test file with only errors has status="failed"
    - Test file with only warnings has status="passed"
    - Test file with errors + warnings has status="failed"
    - Test file with no issues has status="passed"
    - Test error/warning count aggregation
    - Test is_valid property
  - [x] 3.6 Ensure schema validation tests pass
    - Run ONLY tests from 3.1, 3.5 (`pytest tests/core/test_validator.py`)
    - Verify end-to-end validation pipeline works
    - Verify error/warning classification correct

**Acceptance Criteria:**
- All 10-14 validation tests pass
- Full pipeline validates files correctly
- Multiple errors collected without early termination
- Warnings classified correctly (do not block)
- Pydantic errors mapped to ValidationIssue objects
- ValidationResult accurately reflects file status

---

### Task Group 4: File Discovery & Multi-File Orchestration
**Dependencies:** Task Group 3
**Specialist:** Backend/System Engineer
**Estimated Complexity:** Low-Medium

- [ ] 4.0 Complete file discovery and multi-file validation
  - [ ] 4.1 Write 4-6 focused tests for file discovery
    - Test directory with multiple .md files found
    - Test recursive directory scanning (subdirectories)
    - Test non-.md files ignored
    - Test directory not found error handling
    - Test empty directory returns empty list
    - Test absolute vs relative path resolution
  - [ ] 4.2 Create FileScanner class in `src/prompt_manager/utils/file_scanner.py`
    - Method: scan_directory(directory: Path) -> list[Path]
    - Use pathlib.Path.rglob("*.md") for recursive scanning
    - Resolve relative paths to absolute paths
    - Filter only .md files (case-insensitive check)
    - Sort file list for deterministic ordering
    - Raise FileNotFoundError if directory doesn't exist
    - Return empty list if no .md files found
  - [ ] 4.3 Write 5-7 focused tests for BatchValidator
    - Test multiple files validated independently
    - Test error aggregation across files
    - Test warning aggregation across files
    - Test summary statistics (total, passed, failed counts)
    - Test validation continues after file errors
    - Test mixed results (some pass, some fail)
    - Test all files pass scenario
  - [ ] 4.4 Create BatchValidator class in `src/prompt_manager/core/batch_validator.py`
    - Method: validate_directory(directory: Path) -> ValidationSummary
    - Use FileScanner to discover .md files
    - Validate each file with PromptValidator.validate_file()
    - Collect all ValidationResult objects
    - Continue validation even if individual files fail
    - Compute summary statistics:
      - total_files, passed_files, failed_files
      - total_errors, total_warnings
      - success (bool: True if no errors across all files)
  - [ ] 4.5 Create ValidationSummary Pydantic model in `src/prompt_manager/models/validation.py`
    - Fields: total_files (int), passed (int), failed (int)
    - Fields: error_count (int), warning_count (int), success (bool)
    - Field: results (list[ValidationResult])
    - Enable JSON serialization via model_dump()
  - [ ] 4.6 Ensure file discovery tests pass
    - Run ONLY tests from 4.1, 4.3 (`pytest tests/utils/test_file_scanner.py tests/core/test_batch_validator.py`)
    - Verify recursive scanning works
    - Verify summary statistics correct

**Acceptance Criteria:**
- All 9-13 file discovery tests pass
- Recursive directory scanning works correctly
- Only .md files processed
- Validation continues after individual file failures
- Summary statistics accurately reflect results
- ValidationSummary serializes to JSON

---

### Task Group 5: Rich Terminal Output Formatting
**Dependencies:** Task Group 4
**Specialist:** UI/Output Engineer
**Estimated Complexity:** Medium

- [ ] 5.0 Complete Rich terminal output formatting
  - [ ] 5.1 Write 5-7 focused tests for RichFormatter
    - Test header displays directory path
    - Test passed file shows checkmark symbol
    - Test failed file shows X symbol
    - Test errors displayed in red
    - Test warnings displayed in yellow
    - Test line numbers formatted correctly
    - Test code excerpts indented properly
  - [ ] 5.2 Create RichFormatter class in `src/prompt_manager/output/rich_formatter.py`
    - Method: format_summary(summary: ValidationSummary, directory: Path) -> None
    - Use Rich Console for output
    - Display header with directory path and separator line
    - For each ValidationResult:
      - Show file name with status symbol (✓ or ✗)
      - Show errors in red with [line X] prefix
      - Show warnings in yellow with [line X] prefix
      - Indent code excerpts with syntax highlighting
      - Display suggestion below each issue
    - Generate summary section with Rich table:
      - Total files, passed, failed, errors, warnings
    - Display final status message: "Validation PASSED ✓" or "Validation FAILED ✗"
  - [ ] 5.3 Write 3-5 tests for excerpt formatting
    - Test 3-line context extraction around error line
    - Test excerpt at file start (lines 1-3)
    - Test excerpt at file end (last 3 lines)
    - Test excerpt highlighting with Rich Syntax
    - Test excerpt with line numbers
  - [ ] 5.4 Create ExcerptFormatter utility in `src/prompt_manager/utils/excerpt.py`
    - Method: extract_excerpt(file_content: str, line_number: int, context_lines: int = 1) -> str
    - Extract line_number ± context_lines from file content
    - Handle edge cases (start/end of file)
    - Format with line numbers in format: "3 | content here"
    - Return formatted multi-line string
  - [ ] 5.5 Implement color/symbol constants in RichFormatter
    - ERROR_COLOR = "red"
    - WARNING_COLOR = "yellow"
    - PASSED_SYMBOL = "✓"
    - FAILED_SYMBOL = "✗"
    - Use Rich markup for colored text: [red]text[/red]
  - [ ] 5.6 Add --verbose flag support to RichFormatter
    - When verbose=True, show validation progress for each file
    - Display "Validating: filename.md..." for each file
    - Show skipped files (if any due to encoding errors)
    - Show timing information if desired
  - [ ] 5.7 Ensure Rich output tests pass
    - Run ONLY tests from 5.1, 5.3 (`pytest tests/output/test_rich_formatter.py tests/utils/test_excerpt.py`)
    - Verify colors applied correctly (test Rich markup strings)
    - Verify symbols display correctly

**Acceptance Criteria:**
- All 8-12 output formatting tests pass
- Errors displayed in red, warnings in yellow
- Line numbers formatted correctly
- Code excerpts show context
- Summary table displays statistics
- Final status message matches validation result
- Verbose mode shows progress

---

### Task Group 6: JSON Output Formatting & CLI Integration
**Dependencies:** Task Groups 4, 5
**Specialist:** Backend/CLI Engineer
**Estimated Complexity:** Medium

- [ ] 6.0 Complete JSON formatter and CLI command
  - [ ] 6.1 Write 4-6 focused tests for JSONFormatter
    - Test summary section structure
    - Test results array structure
    - Test error object structure (line, severity, code, message, excerpt, suggestion)
    - Test warning object structure
    - Test JSON serialization (valid JSON output)
    - Test pretty-printing (indentation)
  - [ ] 6.2 Create JSONFormatter class in `src/prompt_manager/output/json_formatter.py`
    - Method: format_summary(summary: ValidationSummary, directory: Path) -> str
    - Convert ValidationSummary to JSON structure:
      - summary: {total_files, passed, failed, error_count, warning_count, success}
      - results: array of file validation results
    - Each result contains: file, status, errors, warnings
    - Each error/warning: line, severity, code, message, excerpt, suggestion
    - Use json.dumps() with indent=2 for pretty-printing
    - Return JSON string
  - [ ] 6.3 Write 5-7 focused tests for validate CLI command
    - Test command with valid directory executes successfully
    - Test command with invalid directory shows error
    - Test --json flag outputs JSON format
    - Test default output uses Rich format
    - Test --verbose flag shows progress
    - Test exit code 0 when validation passes (warnings OK)
    - Test exit code 1 when validation fails (errors present)
  - [ ] 6.4 Create validate command in `src/prompt_manager/cli/commands.py`
    - Use Typer for CLI framework
    - Command signature: validate(directory: Path, json: bool = False, verbose: bool = False)
    - Required argument: directory (Path to validate)
    - Optional flag: --json (output JSON instead of Rich)
    - Optional flag: --verbose (show detailed progress)
    - Validation flow:
      1. Resolve directory path
      2. Call BatchValidator.validate_directory()
      3. If --json: use JSONFormatter, print to stdout
      4. Else: use RichFormatter, display to console
      5. Exit with code 1 if summary.success == False, else 0
  - [ ] 6.5 Add command to main CLI app in `src/prompt_manager/cli/main.py`
    - Import validate command
    - Register with Typer app
    - Ensure command appears in --help output
    - Add command description: "Validate prompt file format in a directory"
  - [ ] 6.6 Write 3-5 integration tests for end-to-end CLI
    - Test CLI with sample directory of valid prompts (exit 0)
    - Test CLI with sample directory of invalid prompts (exit 1)
    - Test CLI JSON output is parseable
    - Test CLI Rich output contains expected sections
    - Test CLI error message when directory not found
  - [ ] 6.7 Ensure JSON formatter and CLI tests pass
    - Run ONLY tests from 6.1, 6.3, 6.6 (`pytest tests/output/test_json_formatter.py tests/cli/test_commands.py tests/integration/`)
    - Verify JSON structure matches spec
    - Verify exit codes correct

**Acceptance Criteria:**
- All 12-18 JSON/CLI tests pass
- JSON output matches specification structure
- JSON is valid and pretty-printed
- CLI command accepts directory argument
- --json flag switches output format
- --verbose flag shows progress
- Exit codes: 0 (success/warnings), 1 (errors)
- CLI --help displays usage information

---

### Task Group 7: Comprehensive Testing & Test Gap Analysis
**Dependencies:** Task Groups 1-6
**Specialist:** QA/Test Engineer
**Estimated Complexity:** Medium-High

- [ ] 7.0 Review existing tests and fill critical gaps
  - [ ] 7.1 Review tests from Task Groups 1-6
    - Count total tests written: approximately 29-52 tests across all groups
    - Group 1: 5-8 tests (data models)
    - Group 2: 15-21 tests (parsing)
    - Group 3: 10-14 tests (validation)
    - Group 4: 9-13 tests (file discovery)
    - Group 5: 8-12 tests (Rich output)
    - Group 6: 12-18 tests (JSON/CLI)
  - [ ] 7.2 Analyze test coverage gaps for THIS feature only
    - Run coverage report: `pytest --cov=src/prompt_manager --cov-report=term-missing`
    - Identify uncovered critical paths:
      - Edge cases in separator detection
      - Error recovery scenarios
      - File system error handling
      - Pydantic validation edge cases
      - JSON serialization edge cases
    - Focus ONLY on gaps related to validation engine feature
    - Prioritize integration test scenarios over unit test gaps
  - [ ] 7.3 Create test fixture library in `tests/fixtures/`
    - Create `valid_prompts/` directory with sample valid .md files:
      - minimal_valid.md (name, description only)
      - full_valid.md (all fields including optional)
      - with_warnings.md (missing author, empty tags)
    - Create `invalid_prompts/` directory with sample invalid .md files:
      - missing_name.md (MISSING_REQUIRED_FIELD)
      - missing_description.md (MISSING_REQUIRED_FIELD)
      - no_separator.md (NO_SEPARATOR)
      - multiple_separators.md (MULTIPLE_SEPARATORS)
      - separator_not_alone.md (SEPARATOR_NOT_ALONE)
      - empty_content.md (EMPTY_CONTENT)
      - nested_yaml.md (NESTED_STRUCTURE)
      - invalid_semver.md (INVALID_SEMVER)
      - prohibited_tools.md (PROHIBITED_FIELD)
      - invalid_utf8.md (INVALID_ENCODING - if possible)
    - Create conftest.py with pytest fixtures for file paths
  - [ ] 7.4 Write up to 10 additional strategic integration tests
    - Test complete validation pipeline with valid_prompts/ directory
    - Test complete validation pipeline with invalid_prompts/ directory
    - Test mixed directory (some valid, some invalid)
    - Test CLI with real file fixtures (not mocks)
    - Test JSON output with real file fixtures
    - Test error messages contain correct line numbers
    - Test suggestions are actionable
    - Test file system errors (permission denied simulation)
    - Test large directory performance (50+ files)
    - Test concurrent file validation if implemented
    - MAXIMUM 10 TESTS - do not exceed this limit
  - [ ] 7.5 Add property-based tests using Hypothesis (optional, if time permits)
    - Generate random valid YAML frontmatter and verify acceptance
    - Generate random invalid separators and verify rejection
    - Test with random UTF-8 strings for robustness
    - ONLY if coverage still below 85% after 7.4
  - [ ] 7.6 Run comprehensive test suite
    - Execute: `pytest tests/ -v --cov=src/prompt_manager --cov-report=term-missing --cov-report=html`
    - Verify coverage >= 85% (project requirement)
    - Verify all critical paths covered
    - Expected total tests: approximately 39-62 tests maximum
  - [ ] 7.7 Verify type checking and linting
    - Run mypy: `mypy src/prompt_manager/`
    - Verify no type errors with strict mode
    - Run ruff: `ruff check src/ tests/`
    - Verify no linting errors
    - Run ruff format: `ruff format --check src/ tests/`
    - Verify code formatting consistent
  - [ ] 7.8 Create integration test documentation
    - Document test fixture file formats in `tests/fixtures/README.md`
    - List all error codes tested
    - List all warning codes tested
    - Document test coverage report location
    - Document how to run specific test groups

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 39-62 tests total)
- Test coverage >= 85% for validation engine code
- No more than 10 additional tests added in gap-filling phase
- All 12 error codes have test coverage
- All 3 warning codes have test coverage
- mypy passes with strict mode
- ruff linting passes
- Test fixtures cover all validation scenarios
- Integration tests validate end-to-end workflows

---

## Execution Order

**Recommended implementation sequence:**

1. **Task Group 1: Core Data Models & Schema Validation** (Start here - foundation)
   - Pydantic models define data contracts
   - Error/warning enums establish classification system
   - No external dependencies

2. **Task Group 2: File Parsing & Separator Detection** (Build parsing layer)
   - Depends on ValidationIssue models from Group 1
   - Implements core validation logic components
   - UTF-8, separator, YAML parsing are independent units

3. **Task Group 3: Schema Validation Pipeline** (Orchestrate validation)
   - Depends on models (Group 1) and parsers (Group 2)
   - Integrates all validation steps into pipeline
   - Maps Pydantic errors to ValidationIssue format

4. **Task Group 4: File Discovery & Multi-File Orchestration** (Scale to directories)
   - Depends on PromptValidator from Group 3
   - Adds batch processing capability
   - Creates summary aggregation

5. **Task Group 5: Rich Terminal Output Formatting** (Human-readable output)
   - Depends on ValidationSummary from Group 4
   - Independent from Group 6 (parallel development possible)
   - Implements default CLI output format

6. **Task Group 6: JSON Output Formatting & CLI Integration** (Machine-readable + CLI)
   - Depends on ValidationSummary from Group 4
   - Can develop in parallel with Group 5
   - Integrates both formatters into CLI command

7. **Task Group 7: Comprehensive Testing & Test Gap Analysis** (Verify completeness)
   - Depends on ALL previous groups (1-6)
   - Reviews cumulative test coverage
   - Fills critical gaps to reach 85% coverage
   - Final validation of entire feature

---

## Testing Strategy

### Test-Driven Development Approach
Each task group follows this pattern:
1. **Write tests first** (x.1, x.3, x.5 sub-tasks)
2. **Implement code** to make tests pass (x.2, x.4, x.6 sub-tasks)
3. **Verify tests pass** for that group only (x.6/x.7 final sub-task)
4. **Do NOT run entire test suite** until Task Group 7

### Test Count Limits
- **Groups 1-6:** Each writes 2-8 tests per implementation unit (3-4 units per group)
- **Expected total from Groups 1-6:** 29-52 tests
- **Group 7:** Maximum 10 additional tests for gap-filling
- **Final total:** Approximately 39-62 tests (focused, not exhaustive)

### Coverage Philosophy
- Focus on **critical paths** and **error conditions**
- Test **integration points** between components
- Verify **end-to-end workflows** work correctly
- Skip exhaustive edge case testing in early groups
- Defer edge cases to Group 7 if coverage gaps exist

### Test Organization
```
tests/
├── models/
│   ├── test_prompt.py (Group 1)
│   └── test_validation.py (Group 1)
├── core/
│   ├── test_encoding.py (Group 2)
│   ├── test_separator.py (Group 2)
│   ├── test_yaml_parser.py (Group 2)
│   ├── test_validator.py (Group 3)
│   └── test_batch_validator.py (Group 4)
├── utils/
│   ├── test_file_scanner.py (Group 4)
│   └── test_excerpt.py (Group 5)
├── output/
│   ├── test_rich_formatter.py (Group 5)
│   └── test_json_formatter.py (Group 6)
├── cli/
│   └── test_commands.py (Group 6)
├── integration/
│   └── test_end_to_end.py (Group 7)
├── fixtures/
│   ├── valid_prompts/
│   ├── invalid_prompts/
│   └── README.md
└── conftest.py
```

---

## Error Code Reference (Implementation Checklist)

### Errors (Must Implement - 12 Total)
- [ ] INVALID_ENCODING - File not valid UTF-8
- [ ] MISSING_REQUIRED_FIELD - Required field absent (name or description)
- [ ] INVALID_YAML - YAML syntax error
- [ ] NESTED_STRUCTURE - Nested YAML not allowed
- [ ] NO_SEPARATOR - Missing >>> separator
- [ ] MULTIPLE_SEPARATORS - More than one >>> found
- [ ] SEPARATOR_NOT_ALONE - Separator not on own line
- [ ] SEPARATOR_WHITESPACE - Whitespace around separator
- [ ] EMPTY_CONTENT - No content after separator
- [ ] INVALID_SEMVER - Invalid version format
- [ ] PROHIBITED_FIELD - Forbidden field present (tools)
- [ ] INVALID_FILE_EXTENSION - File is not .md (handled by scanner)

### Warnings (Must Implement - 3 Total)
- [ ] MISSING_OPTIONAL_FIELD - Optional field absent (version or author)
- [ ] EMPTY_TAGS_LIST - Tags list is empty
- [ ] MISSING_AUTHOR - Author field not provided (can merge with MISSING_OPTIONAL_FIELD)

---

## Key Technical Decisions

### Pydantic v2 API
- Use `Field()` for field configuration
- Use `field_validator` decorator for field-level validation
- Use `model_validator(mode='after')` for model-level validation
- Use `model_dump()` for JSON serialization

### YAML Parsing
- Use `yaml.safe_load()` (not `yaml.load()` - security)
- Detect nesting by checking `isinstance(value, dict)` on values
- Track line numbers via yaml.Mark if available

### File Discovery
- Use `pathlib.Path.rglob("*.md")` for recursive scanning
- Case-insensitive extension check: `.suffix.lower() == '.md'`
- Sort results for deterministic ordering

### Error Collection
- Continue validation after errors (don't exit early)
- Collect all errors from all validation steps
- Return complete ValidationResult even when errors present

### Exit Codes
- 0 = Success (warnings allowed, no errors)
- 1 = Failure (one or more errors present)
- Align with Unix convention for scripting

---

## Dependencies Between Components

```
Pydantic Models (Group 1)
    ↓
File Parsers (Group 2) ← uses ValidationIssue
    ↓
Validation Pipeline (Group 3) ← uses models + parsers
    ↓
Batch Validator (Group 4) ← uses PromptValidator
    ↓
    ├─→ RichFormatter (Group 5) ← uses ValidationSummary
    └─→ JSONFormatter (Group 6) ← uses ValidationSummary
         ↓
    CLI Command (Group 6) ← uses both formatters
         ↓
    Integration Tests (Group 7) ← tests entire system
```

---

## Success Metrics

### Functional Completeness
- [ ] All 12 error types detected and reported
- [ ] All 3 warning types detected and reported
- [ ] Multi-file validation works correctly
- [ ] CLI command functional with all flags
- [ ] Rich output displays correctly with colors
- [ ] JSON output matches specification exactly

### Quality Metrics
- [ ] Test coverage >= 85%
- [ ] mypy passes with strict mode (100% type hints)
- [ ] ruff linting passes (zero warnings)
- [ ] All tests pass consistently
- [ ] No known bugs in validation logic

### Integration Readiness
- [ ] CLI command available via `prompt-manager validate`
- [ ] Exit codes work correctly for CI/CD
- [ ] JSON output parseable by automated tools
- [ ] Error messages actionable for developers
- [ ] Documentation complete (fixture README, docstrings)

---

## Notes for Developers

### TDD Workflow
1. Read task group requirements
2. Write tests for the component (x.1 sub-task)
3. Run tests - they should FAIL (red)
4. Implement minimum code to pass tests (x.2 sub-task)
5. Run tests - they should PASS (green)
6. Refactor if needed while keeping tests green
7. Move to next component in group

### Common Pitfalls to Avoid
- Don't skip writing tests first (breaks TDD)
- Don't run entire test suite during development (slow feedback)
- Don't add features not in spec (scope creep)
- Don't use `except:` without specific exception type
- Don't forget type hints (mypy will catch this)
- Don't hardcode file paths (use pathlib.Path)
- Don't use `yaml.load()` (security risk, use `yaml.safe_load()`)

### Useful Commands
```bash
# Run specific test file
pytest tests/models/test_prompt.py -v

# Run tests with coverage for specific module
pytest tests/core/ --cov=src/prompt_manager/core --cov-report=term-missing

# Type check specific file
mypy src/prompt_manager/models/prompt.py

# Lint specific directory
ruff check src/prompt_manager/core/

# Format code
ruff format src/prompt_manager/

# Run all quality checks
make test lint typecheck
```

### File Naming Conventions
- Models: `src/prompt_manager/models/*.py`
- Core logic: `src/prompt_manager/core/*.py`
- Utilities: `src/prompt_manager/utils/*.py`
- Output formatters: `src/prompt_manager/output/*.py`
- CLI: `src/prompt_manager/cli/*.py`
- Tests: `tests/*/test_*.py` (mirror source structure)

---

## Appendix: Example Validation Flow

```
1. User runs: prompt-manager validate ./prompts

2. CLI command (Group 6) receives args
   ↓
3. BatchValidator (Group 4) scans directory
   ↓ finds: prompt1.md, prompt2.md
   ↓
4. For each file, PromptValidator (Group 3) runs pipeline:

   4a. EncodingValidator (Group 2)
       → Reads file as UTF-8 strict
       → Returns content or INVALID_ENCODING error

   4b. SeparatorValidator (Group 2)
       → Splits on >>>
       → Returns frontmatter, content, or errors

   4c. YAMLParser (Group 2)
       → Parses frontmatter as YAML
       → Returns dict or INVALID_YAML/NESTED_STRUCTURE errors

   4d. PromptFrontmatter validation (Group 1)
       → Validates against Pydantic model
       → Returns model or MISSING_REQUIRED_FIELD/PROHIBITED_FIELD errors

   4e. Warning detection (Group 3)
       → Checks for missing optional fields
       → Generates warnings (don't affect status)

   ↓ Returns ValidationResult

5. BatchValidator aggregates results into ValidationSummary

6. Formatter (Group 5 or 6) displays output:
   - If --json: JSONFormatter outputs JSON to stdout
   - Else: RichFormatter displays colored terminal output

7. CLI exits with code:
   - 0 if summary.success == True (no errors)
   - 1 if summary.success == False (errors present)
```
