# Spec Requirements: Extend validate command with functional testing via YAML

## Initial Description

**Feature Name**: Extend validate command with functional testing via YAML

**Description**:
Extend the existing 'validate' command to support functional testing via YAML.

Current behavior:
- 'prompt-unifier validate <file>' checks SCAFF structure (syntax).

New behavior:
- 'prompt-unifier validate <file> --test' (or auto-detect) should look for a corresponding '.test.yaml' file.
- If found, it runs the Functional Validation Engine using the scenarios defined in the YAML.

Requirements:
1. Pure Python implementation (no heavy libs).
2. Support assertion types in YAML: 'contains', 'not-contains', 'regex', 'max-length'.
3. If '--test' is used but no YAML file exists, show a clear warning.
4. Report both Syntax (SCAFF) and Functional (YAML) results in the output.

## Requirements Discussion

### First Round Questions

**Q1:** For the file naming convention, I assume we should look for `<filename>.test.yaml` next to the original file being validated. For example, if validating `prompts/refactor.md`, we'd look for `prompts/refactor.md.test.yaml`. Is that correct, or should it be `prompts/refactor.test.yaml` (replacing the extension)?

**Answer:** `prompts/refactor.md.test.yaml` is correct - the `.test.yaml` suffix is appended to the full filename including its extension.

**Q2:** For the YAML test file structure, I'm thinking of a format like:

```yaml
scenarios:
  - description: "Test case name"
    input: "User prompt or content to test"
    expect:
      - type: contains
        value: "expected string"
      - type: regex
        value: "pattern.*here"
```

Does this structure work for you, or would you prefer a different organization?

**Answer:** The structure is good, but the user provided this more complete example:

```yaml
provider: openai:gpt-4o
iterations: 1
scenarios:
  - description: "Refactoring d'une boucle inefficace"
    input: |
      Refactor this code:
      def process_user_list(users):
          # ... code ...
    expect:
      - type: contains
        value: "Summary of Changes"
        error: "Il manque la section résumé demandée"
      - type: regex
        value: "\[.* for .* in .*\]"
        error: "Le code n'utilise pas de list comprehension"
      - type: not-contains
        value: "== True"
        error: "Comparaison booléenne inutile conservée"
```

Key additions:
- `provider` field (for AI prompt testing): specifies the AI model to use
- `iterations` field: number of times to run each test
- `error` field in assertions: custom error messages for test failures
- Multi-line `input` support using YAML `|` syntax

**Q3:** For the `--test` flag behavior, should it:
- Run ONLY the functional tests (skipping SCAFF validation)?
- Run BOTH SCAFF validation AND functional tests?
- Replace the default behavior entirely?

**Answer:** The `--test` flag runs ONLY the functional tests (skipping SCAFF validation).

**Q4:** I assume we should NOT auto-detect `.test.yaml` files by default (to avoid unexpected behavior), and users must explicitly use `--test` to trigger functional testing. Is that correct?

**Answer:** Correct - auto-detection is DISABLED. The `--test` flag must be used explicitly.

**Q5:** For the assertion types, let me clarify expected behavior:
- `contains`: Case-sensitive substring match, or should we support case-insensitive options?
- `not-contains`: Simple inverse of contains?
- `regex`: Python re.search() or re.match()?
- `max-length`: Character count or word count?

**Answer:**
- `contains`: Case-sensitive by default, but should support case-insensitive option
- `not-contains`: Inverse of contains, also with case-insensitive support
- `regex`: Python regex patterns (using re.search())
- `max-length`: Character count (not word count)

**Q6:** For reporting, I'm thinking we could use Rich tables similar to the current SCAFF validation output, showing:
- Scenario description
- Test status (PASS/FAIL)
- Assertion details for failures

Would you like a similar format to the existing validation output, or something different?

**Answer:** Yes, use the same Rich table format as the current validation output for consistency.

**Q7:** If the `.test.yaml` file exists but has invalid YAML syntax or unknown assertion types, should we:
- Fail the entire validation with an error?
- Show a warning and skip functional tests while still reporting SCAFF results?
- Something else?

**Answer:** Show a warning and ignore the functional tests while still reporting SCAFF results.

**Q8:** Should functional test failures cause the command to exit with a non-zero code (similar to how SCAFF validation failures work)?

**Answer:** Yes, exit code 1 for functional test failures.

**Q9:** Are there existing features in your codebase with similar patterns we should reference? For example:
- Similar interface elements or UI components to re-use
- Comparable page layouts or navigation patterns
- Related backend logic or service objects
- Existing models or controllers with similar functionality

Please provide file/folder paths or names of these features if they exist.

**Answer:** Check existing validation code patterns, YAML parsing utilities, and Rich formatting in the codebase.

**Q10:** Do you have any design mockups, wireframes, or screenshots that could help guide the development?

**Answer:** No visual assets provided.

### Existing Code to Reference

**Similar Features Identified:**

- **YAML Parsing**:
  - `src/prompt_unifier/core/yaml_parser.py` - Core YAML parsing utilities
  - `src/prompt_unifier/core/content_parser.py` - Content parsing with YAML
  - `src/prompt_unifier/config/manager.py` - Configuration YAML handling
  - `src/prompt_unifier/handlers/base_handler.py` - Handler YAML usage

- **Validation Logic**:
  - `src/prompt_unifier/core/validator.py` - Main validation logic
  - `src/prompt_unifier/core/scaff_validator.py` - SCAFF validation implementation
  - `src/prompt_unifier/core/batch_validator.py` - Batch validation patterns
  - `src/prompt_unifier/models/validation.py` - Validation models

- **Rich Formatting**:
  - `src/prompt_unifier/cli/helpers.py` - CLI helpers with Rich Table usage
  - `src/prompt_unifier/cli/commands.py` - Command implementations with Rich Console and Panel
  - `src/prompt_unifier/handlers/base_handler.py` - Handler with Rich Table formatting

- **CLI Commands**:
  - `src/prompt_unifier/cli/main.py` - Main CLI entry point
  - `src/prompt_unifier/cli/commands.py` - Existing command implementations

### Follow-up Questions

No follow-up questions needed - all requirements are clear.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable.

## Requirements Summary

### Functional Requirements

**Core Functionality:**
- Extend the existing `validate` command with a new `--test` flag
- When `--test` is used, look for a `.test.yaml` file with the same base name as the file being validated
- Parse the YAML test file and execute functional test scenarios
- Support AI-based prompt testing with configurable providers and iterations
- Support multiple assertion types: `contains`, `not-contains`, `regex`, `max-length`
- Report test results using Rich table formatting (consistent with existing SCAFF validation output)

**User Actions Enabled:**
- Users can write functional tests for their prompt files in YAML format
- Users can specify AI providers and iteration counts for testing
- Users can run functional tests explicitly using the `--test` flag
- Users can see clear, formatted test results showing pass/fail status
- Users can define custom error messages for failed assertions

**Data to be Managed:**

Test YAML Structure:
```yaml
provider: <ai-provider-specification>  # e.g., "openai:gpt-4o"
iterations: <number>                   # Number of times to run each test
scenarios:
  - description: "<test scenario description>"
    input: |
      <multi-line input content>
    expect:
      - type: <assertion-type>
        value: <expected-value>
        error: "<custom error message>"
        case_sensitive: <true|false>  # Optional, for contains/not-contains
```

Assertion Types:
- `contains`: Substring match (case-sensitive by default, optional `case_sensitive: false`)
- `not-contains`: Inverse substring match (case-sensitive by default, optional `case_sensitive: false`)
- `regex`: Python regex pattern matching (using re.search())
- `max-length`: Maximum character count validation

### Reusability Opportunities

**Components that might exist already:**
- YAML parsing utilities in `src/prompt_unifier/core/yaml_parser.py`
- Rich table formatting patterns in `src/prompt_unifier/cli/helpers.py`
- Validation models in `src/prompt_unifier/models/validation.py`
- Error handling patterns from existing validators

**Backend patterns to investigate:**
- Validation architecture from `src/prompt_unifier/core/scaff_validator.py`
- Batch processing patterns from `src/prompt_unifier/core/batch_validator.py`
- Configuration management from `src/prompt_unifier/config/manager.py`

**Similar code patterns to follow:**
- CLI command structure in `src/prompt_unifier/cli/commands.py`
- Console output formatting in `src/prompt_unifier/cli/helpers.py`
- Handler patterns in `src/prompt_unifier/handlers/base_handler.py`

### Scope Boundaries

**In Scope:**
- Adding `--test` flag to the existing `validate` command
- Creating a functional test YAML parser
- Implementing four assertion types: `contains`, `not-contains`, `regex`, `max-length`
- Case-sensitive and case-insensitive string matching options
- Custom error messages for failed assertions
- Rich table output for test results
- Warning display for invalid YAML or missing test files
- Exit code 1 for functional test failures
- Support for `provider` and `iterations` fields in YAML (parsing and storage)
- Multi-line input support in test scenarios

**Out of Scope:**
- Auto-detection of `.test.yaml` files (must use `--test` explicitly)
- Running SCAFF validation when `--test` flag is used
- Additional assertion types beyond the four specified
- Integration with specific AI providers (just parse and store the provider field)
- Actual execution of AI prompts (this appears to be a future enhancement)
- Word count validation (only character count for `max-length`)
- Interactive test creation or editing
- Test file generation utilities
- Coverage reporting or test statistics

### Technical Considerations

**Integration points mentioned:**
- Must integrate with existing `validate` command in `src/prompt_unifier/cli/commands.py`
- Should follow existing validation patterns from `src/prompt_unifier/core/validator.py`
- Must use existing YAML parsing utilities from `src/prompt_unifier/core/yaml_parser.py`
- Output formatting must use Rich library (already in use)

**Existing system constraints:**
- Pure Python implementation (no heavy external libraries beyond what's already in use)
- Must maintain consistency with existing SCAFF validation output format
- Must use Python's built-in `re` module for regex matching
- Must handle YAML parsing errors gracefully (show warning, continue with SCAFF if applicable)

**Technology preferences stated:**
- PyYAML (already in use in the project)
- Rich library for console output (already in use)
- Python's `re` module for regex operations
- Pydantic models for validation structures (already in use)

**Similar code patterns to follow:**
- Follow TDD practices (write tests first)
- Use dependency injection patterns seen in existing validators
- Follow the project's type hinting conventions (all function signatures)
- Use Google-style docstrings for public APIs
- Mirror source structure in tests: `tests/test_functional_validator.py` for new validator
- Keep functions focused (single responsibility principle)
- Use pytest fixtures for test setup
- Aim for >80% test coverage

**YAML Example for Reference:**

```yaml
provider: openai:gpt-4o
iterations: 1
scenarios:
  - description: "Refactoring d'une boucle inefficace"
    input: |
      Refactor this code:
      def process_user_list(users):
          result = []
          for user in users:
              if user.active == True:
                  result.append(user.name)
          return result
    expect:
      - type: contains
        value: "Summary of Changes"
        error: "Il manque la section résumé demandée"
      - type: regex
        value: "\[.* for .* in .*\]"
        error: "Le code n'utilise pas de list comprehension"
      - type: not-contains
        value: "== True"
        error: "Comparaison booléenne inutile conservée"
```
