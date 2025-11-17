# Specification: Rules/Context Files Support

## Goal
Extend the Prompt Manager CLI to fully support rules/context files alongside prompts, using the same YAML frontmatter + >>> separator format, with complete validation, listing, and filtering capabilities to provide a unified experience for managing both prompts and coding rules.

## User Stories

- As a developer, I want to validate rules files just like prompts so that I can ensure they follow the correct format
- As a team lead, I want to list all available rules so that I can see what coding standards are defined
- As a developer, I want to filter rules by category so that I can quickly find relevant guidelines
- As a contributor, I want clear error messages when rules are invalid so that I can fix formatting issues
- As a team, we want to maintain both prompts and rules in the same repository with consistent tooling

## Context & Motivation

**Current State:**
- Item 3.6 (Rules Directory Synchronization) successfully syncs rules/ from Git
- Rules are stored in `~/.prompt-unifier/storage/rules/`
- No validation or CLI support for rules beyond sync

**Why This Feature:**
- Teams need to share coding standards, architectural guidelines, and best practices
- Rules should have the same quality guarantees as prompts (validated format)
- Unified CLI experience for managing both content types
- Enable discovery of available rules through `list` command

## Specific Requirements

### 1. Rules File Format

Rules use **standard Markdown with YAML frontmatter** format (Jekyll/Hugo style), delimited by `---` markers.

**Type Detection:** Rules are identified by their location in the `rules/` directory (no `type` field needed).

#### Required Fields

```yaml
---
title: Python Coding Standards
description: Comprehensive coding standards for Python development
category: coding-standards
---

# Content goes here...
```

**Field Specifications:**

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `title` | string | Yes | Human-readable title | Any string |
| `description` | string | Yes | Brief description | 1-200 chars |
| `category` | string | Yes (rules only) | Rule category | One of predefined categories |
| `tags` | array | No | Searchable tags | YAML array: `[tag1, tag2]`, max 10 |
| `version` | string | No | Semantic version | Default: "1.0.0" |
| `applies_to` | array | No | Glob patterns for files | **Must quote patterns**: `["*.py", "*.js"]` |
| `author` | string | No | Author name | Optional |
| `language` | string | No | Primary language | e.g., "python", "javascript" |

**Important:** The `applies_to` field must use quoted strings for glob patterns to avoid YAML anchor conflicts with `*` character.

#### Full Example

```yaml
---
title: API Design Patterns
description: REST API design best practices for microservices
category: architecture
tags: [rest, api, http, microservices]
version: 1.2.0
applies_to: ["*.py", "api/*.js"]
author: team-platform
language: python
---

# API Design Guide

## Resource Naming
- Use plural nouns for collections: `/users`, `/posts`
- Use singular for singletons: `/profile`

## HTTP Methods
- GET: Retrieve resources (idempotent)
- POST: Create new resources
...
```

#### Rule Categories

Predefined categories for better organization:

- `coding-standards` - Language-specific style guides, naming conventions
- `architecture` - System design, patterns, architectural decisions
- `security` - Security best practices, authentication, authorization
- `testing` - Testing strategies, coverage requirements, test patterns
- `documentation` - Documentation standards, comment styles
- `performance` - Performance guidelines, optimization patterns
- `deployment` - Deployment processes, CI/CD standards
- `git` - Git workflow, branching strategies, commit messages

**Custom categories allowed but warned:**
```
⚠ Warning: Using custom category 'my-category'
  Standard categories: coding-standards, architecture, security, testing,
  documentation, performance, deployment, git
```

### 2. Validation Engine Extension

#### 2.1 Pydantic Models

**New Model: `RuleFile`**

```python
# src/prompt_unifier/models/rule_file.py
from typing import Literal
from pydantic import BaseModel, Field, field_validator

VALID_CATEGORIES = [
    "coding-standards",
    "architecture",
    "security",
    "testing",
    "documentation",
    "performance",
    "deployment",
    "git",
]

class RuleFile(BaseModel):
    """Represents a validated rule file"""

    name: str = Field(
        ...,
        pattern=r"^[a-z][a-z0-9-]*$",
        description="Unique identifier in kebab-case"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Human-readable description"
    )
    type: Literal["rule"] = Field(
        default="rule",
        description="File type, must be 'rule'"
    )
    category: str = Field(
        ...,
        description="Rule category"
    )
    tags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Searchable tags"
    )
    version: str = Field(
        default="1.0.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Semantic version"
    )
    applies_to: list[str] = Field(
        default_factory=list,
        description="Languages/frameworks this rule applies to"
    )
    author: str | None = Field(
        default=None,
        description="Rule author"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Rule content (after >>> separator)"
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is in standard list (warning if not)"""
        if v not in VALID_CATEGORIES:
            # Log warning but don't fail
            import warnings
            warnings.warn(
                f"Non-standard category '{v}'. "
                f"Standard categories: {', '.join(VALID_CATEGORIES)}"
            )
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate tags are lowercase and kebab-case"""
        for tag in v:
            if not tag.islower() or " " in tag:
                raise ValueError(f"Tag '{tag}' must be lowercase without spaces")
        return v
```

**Unified Type: `ContentFile`**

```python
# src/prompt_unifier/models/__init__.py
from typing import Union
from .prompt_file import PromptFile
from .rule_file import RuleFile

ContentFile = Union[PromptFile, RuleFile]
```

#### 2.2 Parser Extension

**Extend existing parser to detect type:**

```python
# src/prompt_unifier/validation/parser.py

def parse_content_file(file_path: Path) -> ContentFile:
    """
    Parse a content file (prompt or rule) and return appropriate model.

    Automatically detects type from frontmatter.
    """
    # Existing parsing logic...
    frontmatter = parse_yaml_frontmatter(content)

    # Detect type
    file_type = frontmatter.get("type", "prompt")  # Default to prompt

    if file_type == "rule":
        return RuleFile(**frontmatter, content=body)
    elif file_type == "prompt":
        return PromptFile(**frontmatter, content=body)
    else:
        raise ValueError(
            f"Unknown file type '{file_type}'. "
            f"Must be 'prompt' or 'rule'"
        )
```

#### 2.3 Validation Errors

**Rule-specific validation errors:**

```python
# Example validation errors

# Missing required field
"""
❌ Validation Error in rules/python-style.md
  Field 'category' is required for rules

  File: rules/python-style.md
  Type: rule

  Fix: Add category field to frontmatter:
  ---
  name: python-style
  type: rule
  category: coding-standards
  ---
"""

# Invalid category (warning)
"""
⚠ Warning in rules/my-rule.md
  Non-standard category 'custom-cat'

  Standard categories: coding-standards, architecture, security, testing,
  documentation, performance, deployment, git

  You can still use custom categories, but standard ones are recommended.
"""

# Invalid tag format
"""
❌ Validation Error in rules/api-guide.md
  Tag 'REST API' must be lowercase without spaces

  Suggested fix: rest-api or rest_api
"""
```

### 3. CLI Commands Extension

#### 3.1 `validate` Command

**Current behavior:** Only validates prompts/

**New behavior:** Validates both prompts and rules

**Usage:**

```bash
# Validate everything (prompts + rules)
prompt-unifier validate

# Validate only prompts
prompt-unifier validate --type prompts

# Validate only rules
prompt-unifier validate --type rules

# Validate specific file
prompt-unifier validate path/to/rule.md
```

**Output:**

```
Validating content files...

📋 Prompts: 5 files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ code-review.md
✅ bug-fixer.md
✅ refactor-helper.md
✅ test-generator.md
✅ doc-writer.md

📜 Rules: 3 files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ python-style-guide.md (coding-standards)
⚠  api-design-guide.md (custom-category) - Non-standard category
✅ security-checklist.md (security)

Summary:
  ✅ 8 files valid
  ⚠  1 warning
  ❌ 0 errors
```

**Error example:**

```
Validating content files...

📜 Rules: 2 files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ python-style-guide.md (coding-standards)
❌ broken-rule.md - Validation failed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Validation Error in rules/broken-rule.md
  Field 'category' is required for rules

  File: rules/broken-rule.md
  Type: rule

  Fix: Add category field to frontmatter:
  ---
  name: broken-rule
  type: rule
  category: coding-standards  # or another valid category
  ---
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  ✅ 1 file valid
  ⚠  0 warnings
  ❌ 1 error
```

**Command signature:**

```python
@app.command()
def validate(
    path: Optional[Path] = typer.Argument(
        None,
        help="Specific file or directory to validate. Defaults to storage path."
    ),
    type: Optional[str] = typer.Option(
        None,
        "--type",
        help="Filter by type: 'prompts' or 'rules'"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation output"
    ),
) -> None:
    """Validate prompts and rules format."""
    ...
```

#### 3.2 `list` Command (NEW)

**Purpose:** List all prompts and rules with filtering

**Usage:**

```bash
# List everything
prompt-unifier list

# List only prompts
prompt-unifier list --type prompts

# List only rules
prompt-unifier list --type rules

# Filter rules by category
prompt-unifier list --type rules --category coding-standards

# Filter by tags
prompt-unifier list --tags python,fastapi

# Search by name/description
prompt-unifier list --search "api"

# Output formats
prompt-unifier list --format table  # Rich table (default)
prompt-unifier list --format json   # JSON output
prompt-unifier list --format simple # Simple text list
```

**Output (table format - default):**

```
📋 Prompts (5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name                Description                              Tools              Tags
────────────────────────────────────────────────────────────────────────────────────────────────────────────
code-review         Review code for bugs and improvements    continue, cursor   python, review
bug-fixer           Automatically fix common Python bugs     aider              python, bugs
refactor-helper     Refactor legacy code for maintainability continue           refactor, legacy
test-generator      Generate pytest test cases               cursor, aider      testing, pytest
doc-writer          Write comprehensive documentation        continue           docs, python

📜 Rules (4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name                Description                              Category           Tags
────────────────────────────────────────────────────────────────────────────────────────────────────────────
python-style        Python coding standards (PEP 8)          coding-standards   python, pep8, style
api-design          REST API design best practices           architecture       api, rest, design
security-auth       Authentication and authorization guide   security           auth, security, jwt
pytest-guide        Testing guidelines with pytest           testing            python, pytest

Total: 9 files (5 prompts, 4 rules)
```

**Output (JSON format):**

```bash
$ prompt-unifier list --format json
```

```json
{
  "prompts": [
    {
      "name": "code-review",
      "description": "Review code for bugs and improvements",
      "type": "prompt",
      "tools": ["continue", "cursor"],
      "tags": ["python", "review"],
      "version": "1.0.0",
      "file_path": "~/.prompt-unifier/storage/prompts/code-review.md"
    }
  ],
  "rules": [
    {
      "name": "python-style",
      "description": "Python coding standards (PEP 8)",
      "type": "rule",
      "category": "coding-standards",
      "tags": ["python", "pep8", "style"],
      "version": "1.0.0",
      "file_path": "~/.prompt-unifier/storage/rules/python-style.md"
    }
  ],
  "summary": {
    "total": 9,
    "prompts": 5,
    "rules": 4
  }
}
```

**Command signature:**

```python
@app.command()
def list(
    type: Optional[str] = typer.Option(
        None,
        "--type",
        help="Filter by type: 'prompts' or 'rules'"
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category",
        help="Filter rules by category"
    ),
    tags: Optional[str] = typer.Option(
        None,
        "--tags",
        help="Filter by tags (comma-separated)"
    ),
    search: Optional[str] = typer.Option(
        None,
        "--search",
        help="Search in name and description"
    ),
    format: str = typer.Option(
        "table",
        "--format",
        help="Output format: table, json, simple"
    ),
) -> None:
    """List all prompts and rules."""
    ...
```

### 4. File Discovery & Loading

**Service Layer:**

```python
# src/prompt_unifier/services/content_loader.py

from pathlib import Path
from typing import Literal
from ..models import ContentFile, PromptFile, RuleFile

class ContentLoader:
    """Load and manage prompts and rules"""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.prompts_path = storage_path / "prompts"
        self.rules_path = storage_path / "rules"

    def load_all(self) -> list[ContentFile]:
        """Load all prompts and rules"""
        prompts = self.load_prompts()
        rules = self.load_rules()
        return prompts + rules

    def load_prompts(self) -> list[PromptFile]:
        """Load all prompts from prompts/ directory"""
        return self._load_files(self.prompts_path, "prompt")

    def load_rules(self) -> list[RuleFile]:
        """Load all rules from rules/ directory"""
        return self._load_files(self.rules_path, "rule")

    def _load_files(
        self,
        path: Path,
        expected_type: Literal["prompt", "rule"]
    ) -> list[ContentFile]:
        """Load all .md files from directory"""
        if not path.exists():
            return []

        files = []
        for md_file in path.rglob("*.md"):
            try:
                content_file = parse_content_file(md_file)

                # Validate type matches expected
                if content_file.type != expected_type:
                    logger.warning(
                        f"File {md_file} has type '{content_file.type}' "
                        f"but is in {expected_type}s/ directory"
                    )

                files.append(content_file)
            except Exception as e:
                logger.error(f"Failed to load {md_file}: {e}")

        return files

    def filter_by_category(
        self,
        rules: list[RuleFile],
        category: str
    ) -> list[RuleFile]:
        """Filter rules by category"""
        return [r for r in rules if r.category == category]

    def filter_by_tags(
        self,
        files: list[ContentFile],
        tags: list[str]
    ) -> list[ContentFile]:
        """Filter by tags (any match)"""
        return [
            f for f in files
            if any(tag in f.tags for tag in tags)
        ]

    def search(
        self,
        files: list[ContentFile],
        query: str
    ) -> list[ContentFile]:
        """Search in name and description"""
        query_lower = query.lower()
        return [
            f for f in files
            if query_lower in f.name.lower()
            or query_lower in f.description.lower()
        ]
```

### 5. Rich UI Components

**Display functions:**

```python
# src/prompt_unifier/ui/display.py

from rich.console import Console
from rich.table import Table
from ..models import PromptFile, RuleFile

console = Console()

def display_prompts_table(prompts: list[PromptFile]) -> None:
    """Display prompts in a Rich table"""

    table = Table(title=f"📋 Prompts ({len(prompts)})")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Tools", style="green")
    table.add_column("Tags", style="yellow")

    for prompt in prompts:
        table.add_row(
            prompt.name,
            prompt.description,
            ", ".join(prompt.tools),
            ", ".join(prompt.tags),
        )

    console.print(table)

def display_rules_table(rules: list[RuleFile]) -> None:
    """Display rules in a Rich table"""

    table = Table(title=f"📜 Rules ({len(rules)})")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Category", style="magenta")
    table.add_column("Tags", style="yellow")

    for rule in rules:
        table.add_row(
            rule.name,
            rule.description,
            rule.category,
            ", ".join(rule.tags),
        )

    console.print(table)

def display_validation_results(
    prompts_valid: list[PromptFile],
    prompts_errors: list[tuple[Path, Exception]],
    rules_valid: list[RuleFile],
    rules_errors: list[tuple[Path, Exception]],
) -> None:
    """Display validation results with Rich formatting"""

    # Display prompts validation
    if prompts_valid or prompts_errors:
        console.print(f"\n📋 Prompts: {len(prompts_valid) + len(prompts_errors)} files")
        console.print("━" * 80)

        for prompt in prompts_valid:
            console.print(f"✅ {prompt.name}.md")

        for path, error in prompts_errors:
            console.print(f"❌ {path.name} - {error}", style="red")

    # Display rules validation
    if rules_valid or rules_errors:
        console.print(f"\n📜 Rules: {len(rules_valid) + len(rules_errors)} files")
        console.print("━" * 80)

        for rule in rules_valid:
            console.print(f"✅ {rule.name}.md ({rule.category})")

        for path, error in rules_errors:
            console.print(f"❌ {path.name} - {error}", style="red")

    # Summary
    total_valid = len(prompts_valid) + len(rules_valid)
    total_errors = len(prompts_errors) + len(rules_errors)

    console.print("\nSummary:")
    console.print(f"  ✅ {total_valid} files valid")
    console.print(f"  ❌ {total_errors} errors")
```

## Error Handling

### Validation Errors

**1. Missing required field:**
```
❌ Validation Error in rules/api-guide.md
  Field 'category' is required for rules

  Fix: Add category field:
  ---
  category: architecture
  ---
```

**2. Invalid type value:**
```
❌ Validation Error in rules/bad-type.md
  Invalid type 'rulz'. Must be 'rule' or 'prompt'

  Current: type: rulz
  Fix: type: rule
```

**3. Invalid name format:**
```
❌ Validation Error in rules/Bad_Name.md
  Invalid name 'Bad_Name'. Must be kebab-case (lowercase with hyphens)

  Current: Bad_Name
  Valid examples: bad-name, api-guide, python-style
```

**4. Too many tags:**
```
❌ Validation Error in rules/over-tagged.md
  Too many tags (15). Maximum is 10.

  Consider using more general tags or removing redundant ones.
```

### Command Errors

**1. Invalid filter type:**
```bash
$ prompt-unifier list --type invalid
```
```
❌ Error: Invalid type 'invalid'
  Valid types: prompts, rules

  Usage: prompt-unifier list --type [prompts|rules]
```

**2. Category filter on prompts:**
```bash
$ prompt-unifier list --type prompts --category coding-standards
```
```
⚠ Warning: --category filter only applies to rules
  Ignoring --category flag for prompts
```

**3. No storage directory:**
```bash
$ prompt-unifier list
```
```
❌ Error: Storage directory not found

  Run 'prompt-unifier init' first to initialize storage
  Or run 'prompt-unifier sync --repo <url>' to sync from repository
```

## Success Metrics

**Goals:**
- ✅ Rules validation accuracy: 100%
- ✅ List command performance: < 1s for 100 files
- ✅ Validation performance: < 2s for 50 files
- ✅ Test coverage: > 95% for new code
- ✅ Zero breaking changes to existing prompts functionality

**Monitoring:**
- Track number of rules vs prompts in repositories
- Monitor validation error rates
- Collect user feedback on categorization
- Measure command execution times

## Out of Scope

❌ **Not Included:**
- Deployment of rules to tools (rules are reference only)
- Interactive rule editing
- Rule templates or scaffolding
- Advanced versioning or branching of rules
- Merging or diffing of rules
- Auto-generation of rules from code
- Rule enforcement in CI/CD (future feature)

## Implementation Phases

### Phase 1: Data Models & Validation
- Create `RuleFile` Pydantic model
- Extend parser to detect and parse rules
- Add validation for rule-specific fields
- Unit tests for models and validation

### Phase 2: File Loading & Discovery
- Implement `ContentLoader` service
- Add filtering and search capabilities
- Integration tests for file loading

### Phase 3: CLI Commands
- Extend `validate` command with `--type` flag
- Implement new `list` command
- Add Rich UI components for display
- CLI tests

### Phase 4: Documentation & Examples
- Document rule file format
- Create example rules for common scenarios
- Update README with list command usage
- Add rules to test data repository

### Phase 5: Testing & Refinement
- End-to-end testing
- Performance testing (100+ files)
- Error message refinement
- User acceptance testing

## References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Typer Documentation](https://typer.tiangolo.com/)
- Item 3.6: Rules Directory Synchronization (completed)
- Existing PromptFile model: `src/prompt_unifier/models/prompt_file.py`
- Existing validation: `src/prompt_unifier/validation/`
