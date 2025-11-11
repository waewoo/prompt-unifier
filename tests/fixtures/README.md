# Test Fixtures for Validation Engine

This directory contains test fixtures used by the integration tests to validate the prompt validation engine behavior.

## Directory Structure

```
fixtures/
├── valid_prompts/      # Valid prompt files that should pass validation
└── invalid_prompts/    # Invalid prompt files that should fail validation
```

## Valid Prompts

### minimal_valid.md
Minimal valid prompt with only required fields (name, description).
- **Purpose**: Test that prompts with only required fields pass validation
- **Expected result**: PASS with warnings about missing optional fields

### full_valid.md
Complete prompt with all optional fields included (version, tags, author).
- **Purpose**: Test that fully specified prompts pass validation without warnings
- **Expected result**: PASS with no warnings

### with_warnings.md
Valid prompt that triggers warnings (missing optional fields, empty tags).
- **Purpose**: Test that prompts with warnings still pass validation
- **Expected result**: PASS with warnings for missing version, author, and empty tags

## Invalid Prompts

### missing_name.md
Prompt missing the required 'name' field.
- **Error code**: MISSING_REQUIRED_FIELD
- **Expected result**: FAIL

### missing_description.md
Prompt missing the required 'description' field.
- **Error code**: MISSING_REQUIRED_FIELD
- **Expected result**: FAIL

### no_separator.md
Prompt with no separator (>>>) between frontmatter and content.
- **Error code**: NO_SEPARATOR
- **Expected result**: FAIL

### multiple_separators.md
Prompt with multiple separator lines (>>>).
- **Error code**: MULTIPLE_SEPARATORS
- **Expected result**: FAIL

### separator_not_alone.md
Prompt with separator that has content on the same line.
- **Error code**: SEPARATOR_NOT_ALONE
- **Expected result**: FAIL

### empty_content.md
Prompt with empty or whitespace-only content after separator.
- **Error code**: EMPTY_CONTENT
- **Expected result**: FAIL

### nested_yaml.md
Prompt with nested YAML structure (not flat key-value pairs).
- **Error code**: NESTED_STRUCTURE
- **Expected result**: FAIL

### invalid_semver.md
Prompt with invalid semantic version format.
- **Error code**: INVALID_SEMVER
- **Expected result**: FAIL

### prohibited_tools.md
Prompt with prohibited 'tools' field in frontmatter.
- **Error code**: PROHIBITED_FIELD
- **Expected result**: FAIL

## Usage

These fixtures are exposed as pytest fixtures via `tests/conftest.py` and can be accessed in tests:

```python
def test_example(minimal_valid_prompt: Path):
    validator = PromptValidator()
    result = validator.validate_file(minimal_valid_prompt)
    assert result.is_valid is True
```

Available fixtures:
- `valid_prompts_dir` - Directory containing all valid prompts
- `invalid_prompts_dir` - Directory containing all invalid prompts
- `minimal_valid_prompt` - Path to minimal_valid.md
- `full_valid_prompt` - Path to full_valid.md
- `prompt_with_warnings` - Path to with_warnings.md
- `missing_name_prompt` - Path to missing_name.md
- `missing_description_prompt` - Path to missing_description.md
- `no_separator_prompt` - Path to no_separator.md
- `multiple_separators_prompt` - Path to multiple_separators.md
- `nested_yaml_prompt` - Path to nested_yaml.md
- `invalid_semver_prompt` - Path to invalid_semver.md
- `prohibited_field_prompt` - Path to prohibited_tools.md
