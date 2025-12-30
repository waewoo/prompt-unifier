# Specification: Extend validate command with functional testing via YAML

## Goal
Extend the existing `validate` command to support functional testing of AI prompts through YAML-defined test scenarios with multiple assertion types, enabling developers to verify prompt behavior and output quality programmatically.

## User Stories
- As a prompt developer, I want to define functional tests in YAML format so that I can verify my prompts produce expected outputs
- As a quality engineer, I want to run explicit functional tests using the `--test` flag so that I can validate prompt behavior without running syntax checks

## Specific Requirements

**CLI Interface Extension**
- Add `--test` flag to existing `validate` command
- When `--test` is present, execute ONLY functional tests (skip SCAFF validation entirely)
- No auto-detection - flag must be explicitly provided to run functional tests
- Exit with code 1 if any functional test assertions fail
- Look for test file named `<original-file>.test.yaml` (e.g., `refactor.md.test.yaml` for `refactor.md`)

**YAML Test File Structure**
- Top-level optional fields: `provider` (string), `iterations` (integer)
- Required field: `scenarios` (array of scenario objects)
- Each scenario contains: `description` (string), `input` (string, supports multi-line with `|`), `expect` (array of assertion objects)
- Each assertion contains: `type` (string), `value` (string or integer), optional `error` (string), optional `case_sensitive` (boolean)
- Use PyYAML safe_load for parsing (follow existing `YAMLParser` pattern)

**Assertion Types Implementation**
- `contains`: substring match, case-sensitive by default, supports optional `case_sensitive: false`
- `not-contains`: inverse substring match, case-sensitive by default, supports optional `case_sensitive: false`
- `regex`: Python regex pattern matching using `re.search()` from standard library
- `max-length`: character count validation (not word count), value must be integer

**Error Handling Strategy**
- Invalid YAML syntax → display warning, skip functional tests, continue with SCAFF validation if no `--test` flag
- Unknown assertion type → display warning, skip that specific assertion, continue with other assertions
- Missing `.test.yaml` file when `--test` provided → display clear warning message, exit with code 1
- Assertion failures → collect all failures, display in report, exit with code 1

**Output Format Requirements**
- Use Rich table formatting identical to existing SCAFF validation output
- Display separate sections if both SCAFF and functional tests run together
- Each failed assertion shows: scenario description, assertion type, expected value, actual output excerpt (first 100 chars)
- Summary statistics: total scenarios, passed/failed, assertion counts
- Follow color scheme: green for passed, red for failed, yellow for warnings

**Integration with Existing Code**
- Create new `FunctionalValidator` class following pattern from `SCARFFValidator`
- Extend `ValidationResult` model to include optional `functional_test_results` field
- Reuse `ValidationIssue` model for reporting assertion failures
- Follow existing error code pattern: new codes starting with `FUNC_` prefix
- Use existing `RichTableFormatter` for consistent output formatting

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**`src/prompt_unifier/core/yaml_parser.py`**
- YAMLParser class with `parse_yaml()` method for safe YAML loading
- ValidationIssue generation pattern for YAML syntax errors
- Nested structure detection logic (adapt for test file validation)
- Error handling with line number tracking
- Use as foundation for parsing `.test.yaml` files

**`src/prompt_unifier/core/scaff_validator.py`**
- SCARFFValidator class structure as template for FunctionalValidator
- Pattern for component-based scoring and validation
- `generate_issues()` method pattern for creating ValidationIssue objects
- Suggestion template system for user-friendly error messages
- Status determination logic (excellent/good/needs improvement)

**`src/prompt_unifier/models/validation.py`**
- ValidationResult, ValidationIssue, ValidationSummary models
- ValidationSeverity enum (ERROR/WARNING)
- ErrorCode and WarningCode enum patterns
- Property methods for computed fields (e.g., `is_valid`)
- Pydantic BaseModel patterns for type safety

**`src/prompt_unifier/cli/commands.py`**
- `validate()` command structure and Typer option definitions
- `_validate_with_rich_output()` and `_validate_with_json_output()` helper patterns
- Directory resolution and validation target determination logic
- Exit code handling for validation failures
- Rich Console and Panel usage for formatted output

**`src/prompt_unifier/cli/helpers.py`**
- Rich Table creation patterns
- Console output formatting conventions
- Color scheme standards (green/red/yellow)
- Parser integration patterns for file handling
- Warning display patterns for non-critical issues

## Out of Scope
- Auto-detection of `.test.yaml` files (must use `--test` flag explicitly)
- Running SCAFF validation when `--test` flag is used
- Additional assertion types beyond the four specified (contains, not-contains, regex, max-length)
- Integration with actual AI providers for executing prompts
- Executing AI prompts based on `provider` field (field is parsed but not used)
- Using `iterations` field for multiple test runs (field is parsed but not used)
- Word count validation (only character count for max-length)
- Interactive test file creation or editing features
- Test file generation utilities or scaffolding commands
- Coverage reporting or detailed test statistics
- Parametrized tests or test fixtures
- Mocking or stubbing of AI responses
- Performance benchmarking of prompts
- Test result caching or incremental test runs
