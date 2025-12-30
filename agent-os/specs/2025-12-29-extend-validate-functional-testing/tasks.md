# Task Breakdown: Extend validate command with functional testing via YAML

## Overview
Total Tasks: 4 task groups with ~25 sub-tasks
Estimated Complexity: Medium
Feature Type: CLI Extension + New Validation Engine

## Task List

### Data Models Layer

#### Task Group 1: Pydantic Models and Error Codes
**Dependencies:** None
**Skills Required:** Python, Pydantic
**Files to Create/Modify:**
- `src/prompt_unifier/models/functional_test.py` (new)
- `src/prompt_unifier/models/validation.py` (extend existing)

- [x] 1.0 Complete data models layer
  - [x] 1.1 Write 2-8 focused tests for functional test models
    - Test file: `tests/test_models/test_functional_test.py`
    - Test `FunctionalTestAssertion` validation (type, value, error, case_sensitive)
    - Test `FunctionalTestScenario` validation (description, input, expect list)
    - Test `FunctionalTestFile` validation (provider, iterations, scenarios)
    - Test `FunctionalTestResult` structure (scenario, status, failures)
    - Test invalid assertion types raise validation errors
    - Test case_sensitive defaults to True when omitted
    - Test multi-line input handling
    - Maximum 8 tests focusing on critical model behaviors
  - [x] 1.2 Create `FunctionalTestAssertion` model in `src/prompt_unifier/models/functional_test.py`
    - Fields: `type` (Literal["contains", "not-contains", "regex", "max-length"])
    - Fields: `value` (Union[str, int] - str for text assertions, int for max-length)
    - Fields: `error` (Optional[str] - custom error message)
    - Fields: `case_sensitive` (Optional[bool] - defaults to True, only for contains/not-contains)
    - Add validator to ensure max-length uses int value
    - Add validator to ensure case_sensitive only used with contains/not-contains
  - [x] 1.3 Create `FunctionalTestScenario` model
    - Fields: `description` (str)
    - Fields: `input` (str - multi-line content to test)
    - Fields: `expect` (List[FunctionalTestAssertion] - list of assertions)
    - Add validator to ensure at least one assertion in expect list
  - [x] 1.4 Create `FunctionalTestFile` model
    - Fields: `provider` (Optional[str] - e.g., "openai:gpt-4o")
    - Fields: `iterations` (Optional[int] - defaults to 1)
    - Fields: `scenarios` (List[FunctionalTestScenario])
    - Add validator to ensure at least one scenario
    - Add validator to ensure iterations >= 1 if provided
  - [x] 1.5 Create `FunctionalTestResult` model
    - Fields: `scenario_description` (str)
    - Fields: `status` (Literal["PASS", "FAIL"])
    - Fields: `passed_count` (int)
    - Fields: `failed_count` (int)
    - Fields: `failures` (List[Dict[str, str]] - assertion details)
    - Add property method `is_passing` returning bool
  - [x] 1.6 Extend error codes in `src/prompt_unifier/models/validation.py`
    - Add new error codes to existing enum: `FUNC_YAML_INVALID`, `FUNC_FILE_MISSING`, `FUNC_ASSERTION_FAILED`
    - Add new warning codes: `FUNC_UNKNOWN_ASSERTION_TYPE`
    - Follow existing pattern from `ErrorCode` and `WarningCode` enums
  - [x] 1.7 Ensure data models tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify all model validations work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- All models validate correctly with Pydantic
- Error codes follow existing naming patterns
- Models handle optional fields with appropriate defaults
- Invalid data raises clear validation errors

### Parser Layer

#### Task Group 2: Functional Test YAML Parser
**Dependencies:** Task Group 1
**Skills Required:** Python, PyYAML, Error Handling
**Files to Create/Modify:**
- `src/prompt_unifier/core/functional_test_parser.py` (new)

- [x] 2.0 Complete parser layer
  - [x] 2.1 Write 2-8 focused tests for YAML parser
    - Test file: `tests/test_core/test_functional_test_parser.py`
    - Create fixtures: valid `.test.yaml`, invalid YAML, missing file
    - Test successful parsing of valid test file
    - Test error handling for invalid YAML syntax
    - Test error handling for missing file
    - Test parsing of optional fields (provider, iterations)
    - Test multi-line input parsing with `|` syntax
    - Test unknown assertion type handling (warning, not error)
    - Maximum 8 tests focusing on critical parsing behaviors
  - [x] 2.2 Create `FunctionalTestParser` class in `src/prompt_unifier/core/functional_test_parser.py`
    - Constructor: accepts file_path (Path)
    - Method: `parse() -> Optional[FunctionalTestFile]`
    - Use `yaml.safe_load()` following pattern from `YAMLParser`
    - Return None if file doesn't exist (graceful handling)
    - Catch YAMLError and return None with warning logged
  - [x] 2.3 Implement YAML validation logic
    - Parse YAML and validate against `FunctionalTestFile` model
    - Catch Pydantic ValidationError and log warnings
    - Handle missing required fields gracefully
    - Return validated `FunctionalTestFile` object on success
  - [x] 2.4 Implement error message generation
    - Generate clear error messages for YAML syntax errors
    - Generate warnings for unknown assertion types
    - Include line numbers in error messages (if available from PyYAML)
    - Follow error message patterns from existing `YAMLParser`
  - [x] 2.5 Add file path resolution
    - Method: `get_test_file_path(source_file: Path) -> Path`
    - Returns `source_file.with_suffix(source_file.suffix + '.test.yaml')`
    - Example: `refactor.md` → `refactor.md.test.yaml`
    - Static method for utility usage
  - [x] 2.6 Ensure parser tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify all parsing scenarios work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- Parser handles valid YAML files correctly
- Invalid YAML returns None with clear warnings
- File path resolution follows `.test.yaml` convention
- Multi-line inputs parsed correctly

### Validation Engine Layer

#### Task Group 3: Functional Validator Implementation
**Dependencies:** Task Groups 1-2
**Skills Required:** Python, Regex, String Operations
**Files to Create/Modify:**
- `src/prompt_unifier/core/functional_validator.py` (new)

- [x] 3.0 Complete validation engine
  - [x] 3.1 Write 2-8 focused tests for functional validator
    - Test file: `tests/test_core/test_functional_validator.py`
    - Test `contains` assertion (case-sensitive and insensitive)
    - Test `not-contains` assertion (case-sensitive and insensitive)
    - Test `regex` assertion with valid/invalid patterns
    - Test `max-length` assertion (pass and fail cases)
    - Test scenario execution with multiple assertions
    - Test failure collection (all failures reported, not just first)
    - Test result generation (FunctionalTestResult objects)
    - Maximum 8 tests focusing on critical validation behaviors
  - [x] 3.2 Create `FunctionalValidator` class in `src/prompt_unifier/core/functional_validator.py`
    - Follow pattern from `SCARFFValidator` class
    - Constructor: accepts `FunctionalTestFile` object
    - Method: `validate(output: str) -> List[FunctionalTestResult]`
    - Execute all scenarios against provided output
    - Collect results for each scenario
  - [x] 3.3 Implement `contains` assertion validator
    - Method: `_validate_contains(output: str, assertion: FunctionalTestAssertion) -> bool`
    - Case-sensitive by default: `assertion.value in output`
    - Case-insensitive if specified: `assertion.value.lower() in output.lower()`
    - Return True if assertion passes, False otherwise
  - [x] 3.4 Implement `not-contains` assertion validator
    - Method: `_validate_not_contains(output: str, assertion: FunctionalTestAssertion) -> bool`
    - Inverse logic of `contains`
    - Support case_sensitive option
    - Return True if substring NOT found
  - [x] 3.5 Implement `regex` assertion validator
    - Method: `_validate_regex(output: str, assertion: FunctionalTestAssertion) -> bool`
    - Use `re.search(assertion.value, output)`
    - Import: `import re` from standard library
    - Handle invalid regex patterns gracefully (catch re.error, log warning, return False)
    - Return True if pattern matches
  - [x] 3.6 Implement `max-length` assertion validator
    - Method: `_validate_max_length(output: str, assertion: FunctionalTestAssertion) -> bool`
    - Check: `len(output) <= assertion.value`
    - assertion.value must be int (enforced by model)
    - Return True if length is within limit
  - [x] 3.7 Implement scenario execution logic
    - Method: `_execute_scenario(scenario: FunctionalTestScenario, output: str) -> FunctionalTestResult`
    - Execute all assertions in scenario.expect list
    - Collect all failures (don't stop at first failure)
    - Generate failure details: {type, expected, actual_excerpt, error_message}
    - actual_excerpt: first 100 chars of output for context
    - Return FunctionalTestResult with pass/fail status
  - [x] 3.8 Implement assertion dispatcher
    - Method: `_execute_assertion(assertion: FunctionalTestAssertion, output: str) -> bool`
    - Use match/case (Python 3.10+) or if/elif to dispatch by assertion.type
    - Call appropriate validator method based on type
    - Log warning for unknown assertion types (skip execution)
    - Return False for unknown types
  - [x] 3.9 Ensure functional validator tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify all assertion types work correctly
    - Verify failure collection works
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- All four assertion types work correctly
- Case-sensitive/insensitive options work for string assertions
- All failures collected before returning results
- Invalid regex patterns handled gracefully

### CLI Integration Layer

#### Task Group 4: CLI Extension and Output Formatting
**Dependencies:** Task Groups 1-3
**Skills Required:** Typer, Rich, CLI Design
**Files to Create/Modify:**
- `src/prompt_unifier/cli/commands.py` (extend existing)
- `src/prompt_unifier/cli/helpers.py` (extend existing)

- [x] 4.0 Complete CLI integration
  - [x] 4.1 Write 2-8 focused tests for CLI integration
    - Test file: `tests/test_cli/test_functional_validation.py`
    - Test `--test` flag triggers functional validation only
    - Test missing `.test.yaml` file shows warning and exits with code 1
    - Test successful test execution shows results
    - Test failed assertions cause exit code 1
    - Test invalid YAML shows warning
    - Test output formatting matches existing SCAFF validation style
    - Maximum 8 tests focusing on critical CLI behaviors
  - [x] 4.2 Add `--test` flag to `validate` command in `src/prompt_unifier/cli/commands.py`
    - Add Typer option: `test: bool = typer.Option(False, "--test", help="Run functional tests from .test.yaml file")`
    - Position after existing options (show_recommendations, json_output, etc.)
    - Update function signature
  - [x] 4.3 Implement functional test execution logic
    - Add helper method: `_validate_functional_tests(file_path: Path) -> Tuple[bool, List[FunctionalTestResult]]`
    - Use `FunctionalTestParser.get_test_file_path()` to locate test file
    - Check if test file exists, return warning if missing
    - Parse test file using `FunctionalTestParser`
    - Handle parsing errors gracefully (invalid YAML)
    - Return (success: bool, results: List[FunctionalTestResult])
  - [x] 4.4 Integrate into validate command flow
    - Early in `validate()` function: check if `test` flag is True
    - If True: skip SCAFF validation entirely, run functional tests only
    - Call `_validate_functional_tests()` and collect results
    - Determine exit code: 0 if all pass, 1 if any failures
    - Call output formatter with results
  - [x] 4.5 Handle missing test file case
    - If `--test` provided but `.test.yaml` doesn't exist:
    - Display clear warning: "Functional test file not found: {path}"
    - Suggest: "Create a test file at: {path}"
    - Exit with code 1
  - [x] 4.6 Create Rich table formatter in `src/prompt_unifier/cli/helpers.py`
    - Function: `format_functional_test_results(results: List[FunctionalTestResult]) -> Table`
    - Follow existing Rich table patterns from SCAFF validation
    - Columns: "Scenario", "Status", "Passed", "Failed", "Details"
    - Status: green "✓ PASS" or red "✗ FAIL"
    - Details: show first failure for each failed scenario
    - Return Rich Table object
  - [x] 4.7 Create summary panel formatter
    - Function: `create_functional_test_summary(results: List[FunctionalTestResult]) -> Panel`
    - Calculate: total scenarios, passed count, failed count, pass rate
    - Display statistics in Rich Panel
    - Color: green if all pass, red if any failures
    - Follow existing panel patterns from SCAFF validation
  - [x] 4.8 Create detailed failure formatter
    - Function: `format_assertion_failures(result: FunctionalTestResult) -> str`
    - For each failure: show type, expected value, actual excerpt, custom error
    - Format: bullet list with indentation
    - Include actual output excerpt (first 100 chars)
    - Return formatted string for table display
  - [x] 4.9 Wire up output in validate command
    - After functional validation: call `format_functional_test_results()`
    - Display table using Rich Console
    - Display summary panel using `create_functional_test_summary()`
    - For failures: display detailed failure messages
    - Match existing output style for consistency
  - [x] 4.10 Ensure CLI integration tests pass
    - Run ONLY the 2-8 tests written in 4.1
    - Verify `--test` flag works correctly
    - Verify exit codes are correct
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 4.1 pass
- `--test` flag triggers functional validation only (skips SCAFF)
- Missing test files show clear warnings
- Test results display in Rich tables matching existing style
- Exit codes: 0 for success, 1 for failures or missing files
- Output is clear, formatted, and consistent with existing validation

### Testing Coverage

#### Task Group 5: Test Review & Integration Testing
**Dependencies:** Task Groups 1-4
**Skills Required:** pytest, Integration Testing
**Files to Create/Modify:**
- Various test files created in previous groups
- `tests/integration/test_functional_validation_e2e.py` (new)

- [x] 5.0 Review existing tests and fill critical gaps
  - [x] 5.1 Review tests from Task Groups 1-4
    - Review tests from data models (Task 1.1)
    - Review tests from parser (Task 2.1)
    - Review tests from validator (Task 3.1)
    - Review tests from CLI integration (Task 4.1)
    - Total existing tests: approximately 8-32 tests
  - [x] 5.2 Analyze test coverage gaps for functional testing feature only
    - Identify missing end-to-end workflows
    - Check for untested error paths
    - Verify all assertion types tested in combination
    - Focus ONLY on this feature's requirements
    - Prioritize integration over unit test gaps
  - [x] 5.3 Write up to 10 additional strategic tests maximum
    - Create `tests/integration/test_functional_validation_e2e.py`
    - Test end-to-end: file with `.test.yaml` → validation → output
    - Test combined scenarios: multiple assertions, mixed pass/fail
    - Test edge cases: empty scenarios list, zero iterations
    - Test CLI with real file fixtures
    - Test all four assertion types in realistic scenarios
    - Test case-sensitive variations
    - Test invalid YAML recovery
    - Test missing file handling
    - Maximum 10 tests to fill critical gaps
  - [x] 5.4 Run feature-specific tests only
    - Run tests from groups 1.1, 2.1, 3.1, 4.1, and 5.3
    - Expected total: approximately 18-42 tests maximum
    - Verify all critical workflows pass
    - Do NOT run entire application test suite
    - Check coverage with: `pytest --cov=src/prompt_unifier --cov-report=term-missing`
    - Aim for >80% coverage on new code only

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 18-42 tests total)
- End-to-end workflows validated
- No more than 10 additional tests added
- Coverage >80% on new code (models, parser, validator, CLI changes)
- All assertion types tested in realistic scenarios

## Execution Order

Recommended implementation sequence:
1. **Data Models Layer** (Task Group 1) - Foundation for all other components
2. **Parser Layer** (Task Group 2) - Depends on models
3. **Validation Engine Layer** (Task Group 3) - Depends on models and parser
4. **CLI Integration Layer** (Task Group 4) - Depends on all previous layers
5. **Testing Coverage** (Task Group 5) - Validate entire feature integration

## Important Notes

### Test-Driven Development Flow
Each task group follows TDD:
1. Write 2-8 focused tests first (x.1 sub-task)
2. Implement functionality to pass tests
3. Run ONLY those tests at end of group (final sub-task)
4. Do NOT run entire test suite until Task Group 5

### Reuse Existing Patterns
- **YAML Parsing**: Follow `src/prompt_unifier/core/yaml_parser.py` patterns
- **Validation**: Follow `src/prompt_unifier/core/scaff_validator.py` structure
- **Rich Output**: Match `src/prompt_unifier/cli/helpers.py` formatting
- **Error Codes**: Extend enums in `src/prompt_unifier/models/validation.py`

### Key Design Decisions
- `--test` flag runs ONLY functional tests (no SCAFF validation)
- Test file naming: `<original>.test.yaml` (e.g., `refactor.md.test.yaml`)
- No auto-detection (explicit `--test` required)
- Collect ALL failures before reporting (don't fail fast)
- Exit code 1 for any test failures or missing test files

### File Naming Convention
All test files follow the pattern: `{source_file}.test.yaml`
- Example: `prompts/refactor.md` → `prompts/refactor.md.test.yaml`
- Example: `api-guide.txt` → `api-guide.txt.test.yaml`

### Pre-Commit Checklist
Before committing any task group:
- [ ] All tests for that group pass
- [ ] Code follows PEP 8 and project conventions
- [ ] Type hints on all function signatures
- [ ] Docstrings on public APIs
- [ ] No unused imports or variables
- Run `make app-lint` to verify
