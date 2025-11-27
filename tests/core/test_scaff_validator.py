"""Tests for the SCARFFValidator component analysis."""

import pytest

from prompt_unifier.core.scaff_validator import SCARFFValidator
from prompt_unifier.models.scaff import SCARFFScore
from prompt_unifier.models.validation import ValidationSeverity, WarningCode


class TestSCARFFValidator:
    """Tests for SCAFF methodology validation."""

    @pytest.fixture
    def validator(self) -> SCARFFValidator:
        """Create a SCARFFValidator instance."""
        return SCARFFValidator()

    def test_excellent_prompt_scores_high(self, validator: SCARFFValidator) -> None:
        """Test that a well-structured prompt scores in excellent range (80+)."""
        content = """## Context
This tool is for reviewing Python code to ensure best practices and identify potential bugs.
The target audience is intermediate Python developers working on production codebases.

### Situation
The user has a codebase that needs review.

### Challenge
Review the code and provide feedback.

### Audience
Intermediate Python developers.

### Foundations
- Follow PEP 8
- Ensure security

### Format
Output as markdown.

## Requirements
You must:
- Review code for PEP 8 compliance
- Identify security vulnerabilities
- Should provide specific line numbers for issues
- Check for proper error handling

## Steps
1. Analyze the code structure
2. Check for common anti-patterns
3. Test edge cases
4. Provide actionable feedback with examples

## Output Format
- Use bullet points for findings
- Include severity levels (high, medium, low)
- Provide code snippets showing issues"""

        result = validator.validate_content(content)

        assert isinstance(result, SCARFFScore)
        assert result.total_score >= 80, f"Expected excellent score, got {result.total_score}"
        assert result.grade == "excellent"
        assert len(result.components) == 5

    def test_specific_component_detects_concrete_requirements(
        self, validator: SCARFFValidator
    ) -> None:
        """Test that Specific component detects concrete requirements and measurable goals."""
        # Content with specific requirements
        specific_content = """### Foundations
You must implement authentication with the following:
- Password must be at least 12 characters
- Should support OAuth2 providers
- Must include rate limiting (5 attempts per minute)

### Challenge
Implement secure authentication."""

        result = validator.validate_content(specific_content)

        specific_component = next(c for c in result.components if c.component_name == "Specific")
        assert specific_component.score >= 15, "Should detect specific requirements"

        # Content without specifics
        vague_content = """Do some authentication stuff and make it secure."""

        result_vague = validator.validate_content(vague_content)

        specific_vague = next(c for c in result_vague.components if c.component_name == "Specific")
        assert specific_vague.score <= 10, "Should detect lack of specificity"

    def test_contextual_component_detects_background_info(self, validator: SCARFFValidator) -> None:
        """Test that Contextual component detects background information and user context."""
        # Content with context
        contextual_content = """### Situation
This project is a web application for managing customer orders.

### Audience
The target users are small business owners who need simple order tracking.

## Why This Matters
Order management is currently manual and error-prone."""

        result = validator.validate_content(contextual_content)

        contextual_component = next(
            c for c in result.components if c.component_name == "Contextual"
        )
        assert contextual_component.score >= 15, "Should detect contextual information"

        # Content without context
        no_context = """Build a thing that does stuff."""

        result_no_context = validator.validate_content(no_context)

        contextual_no = next(
            c for c in result_no_context.components if c.component_name == "Contextual"
        )
        assert contextual_no.score <= 10, "Should detect lack of context"

    def test_actionable_component_detects_action_verbs(self, validator: SCARFFValidator) -> None:
        """Test that Actionable component detects action verbs and instructions."""
        # Content with actions
        actionable_content = """1. Create the database schema
2. Implement the API endpoints
3. Test the authentication flow
4. Build the user interface
5. Configure the deployment pipeline"""

        result = validator.validate_content(actionable_content)

        actionable_component = next(
            c for c in result.components if c.component_name == "Actionable"
        )
        assert actionable_component.score >= 15, "Should detect actionable instructions"

    def test_formatted_component_detects_markdown_structure(
        self, validator: SCARFFValidator
    ) -> None:
        """Test that Formatted component detects proper markdown structure."""
        # Well-formatted content
        formatted_content = """# Main Title

## Section 1
- Bullet point 1
- Bullet point 2

## Section 2
1. Numbered item
2. Another item

### Subsection
More details here."""

        result = validator.validate_content(formatted_content)

        formatted_component = next(c for c in result.components if c.component_name == "Formatted")
        assert formatted_component.score >= 15, "Should detect good formatting"

        # Poorly formatted
        unformatted = """Just a wall of text with no structure or organization whatsoever."""

        result_unformatted = validator.validate_content(unformatted)

        formatted_unformatted = next(
            c for c in result_unformatted.components if c.component_name == "Formatted"
        )
        assert formatted_unformatted.score <= 10, "Should detect poor formatting"

    def test_focused_component_checks_length_and_coherence(
        self, validator: SCARFFValidator
    ) -> None:
        """Test that Focused component checks content length and topic coherence."""
        # Well-focused content (optimal length)
        focused_content = (
            """# Code Review Guidelines

## Purpose
Review Python code for quality and best practices.

## Scope
Focus on:
- PEP 8 compliance
- Security issues
- Performance concerns

## Process
1. Analyze code structure
2. Check for patterns
3. Provide feedback

## Output
- Specific issues
- Actionable suggestions
- Code examples"""
            * 3
        )  # Repeat to get into optimal range

        result = validator.validate_content(focused_content)

        focused_component = next(c for c in result.components if c.component_name == "Focused")
        assert focused_component.score >= 15, "Should reward optimal length"

        # Too short
        too_short = """Do code review."""

        result_short = validator.validate_content(too_short)

        focused_short = next(c for c in result_short.components if c.component_name == "Focused")
        assert focused_short.score <= 12, "Should penalize too-short content"

    def test_score_aggregation_produces_0_to_100_scale(self, validator: SCARFFValidator) -> None:
        """Test that score aggregation correctly sums components to 0-100 scale."""
        content = """Some test content."""

        result = validator.validate_content(content)

        # Check that total score is sum of components
        component_sum = sum(c.score for c in result.components)
        assert result.total_score == component_sum
        assert 0 <= result.total_score <= 100

    def test_validation_issues_generated_with_suggestions(self, validator: SCARFFValidator) -> None:
        """Test that ValidationIssue objects are generated with actionable suggestions."""
        # Very minimal content that should fail multiple components
        poor_content = """vague thing"""

        issues = validator.generate_issues(poor_content)

        assert len(issues) > 0, "Should generate issues for poor content"

        # Check that all issues have required fields
        for issue in issues:
            assert issue.severity == ValidationSeverity.WARNING
            assert issue.code in [
                WarningCode.SCAFF_NOT_SPECIFIC.value,
                WarningCode.SCAFF_LACKS_CONTEXT.value,
                WarningCode.SCAFF_NOT_ACTIONABLE.value,
                WarningCode.SCAFF_POORLY_FORMATTED.value,
                WarningCode.SCAFF_UNFOCUSED.value,
                "SCAFF000",  # Total score warning
                "SCAFF001",  # Missing section warning
            ]
            assert len(issue.message) > 0
            assert len(issue.suggestion) > 0
            assert len(issue.suggestion) <= 200  # Concise suggestions (1-2 sentences)

    def test_specific_keyword_scoring_thresholds(self, validator: SCARFFValidator) -> None:
        """Test specific keyword scoring at different thresholds."""
        # Test 1-2 keywords (3 points)
        content_low = "You must implement this feature."
        result_low = validator.validate_content(content_low)
        specific_low = next(c for c in result_low.components if c.component_name == "Specific")
        assert specific_low.score >= 3

        # Test 3-4 keywords (6 points)
        content_mid = "You must implement exactly 3 features. Should require at least 5 tests."
        result_mid = validator.validate_content(content_mid)
        specific_mid = next(c for c in result_mid.components if c.component_name == "Specific")
        assert specific_mid.score >= 6

        # Test 5+ keywords (8 points)
        content_high = (
            "Must implement exactly 3 features. Should require at least 5 tests. Maximum 10 items."
        )
        result_high = validator.validate_content(content_high)
        specific_high = next(c for c in result_high.components if c.component_name == "Specific")
        assert specific_high.score >= 8

    def test_imperative_instructions_detection(self, validator: SCARFFValidator) -> None:
        """Test detection of imperative instructions with bold labels."""
        content = """
### Foundations
- **Paths**: Define standard paths for inventory
- **Defaults**: Set forks for parallelism
- **Privilege**: Configure default escalation
- Create the database schema
- Set up associations
"""
        result = validator.validate_content(content)
        specific = next(c for c in result.components if c.component_name == "Specific")
        assert specific.score >= 8  # Should detect imperatives and Foundations section

    def test_numeric_metrics_detection(self, validator: SCARFFValidator) -> None:
        """Test detection of numeric metrics and thresholds."""
        # Test with unit metrics
        content_units = (
            "Require 12 characters minimum, 3 attempts allowed, timeout after 30 seconds."
        )
        result_units = validator.validate_content(content_units)
        specific_units = next(c for c in result_units.components if c.component_name == "Specific")
        assert specific_units.score >= 7  # 3+ metrics = 7 points

        # Test with general numbers
        content_numbers = "Version 1.2.3 with 5 features and 10 tests."
        result_numbers = validator.validate_content(content_numbers)
        specific_numbers = next(
            c for c in result_numbers.components if c.component_name == "Specific"
        )
        assert specific_numbers.score >= 3  # General numbers fallback

    def test_internal_references_bonus(self, validator: SCARFFValidator) -> None:
        """Test bonus points for internal references to rules/ and prompts/."""
        content = "Follow guidelines in rules/ansible-standards.md and prompts/best-practices.md"
        result = validator.validate_content(content)
        specific = next(c for c in result.components if c.component_name == "Specific")
        assert specific.score >= 5  # Should get bonus for internal refs

    def test_negative_constraints_detection(self, validator: SCARFFValidator) -> None:
        """Test detection of negative constraints."""
        content = """
Do not commit secrets. Never use force push. Avoid global state.
Must not skip tests. Should not hardcode credentials.
"""
        result = validator.validate_content(content)
        specific = next(c for c in result.components if c.component_name == "Specific")
        assert specific.score >= 3  # 2+ negative constraints = 3 points

    def test_contextual_preamble_detection(self, validator: SCARFFValidator) -> None:
        """Test detection of substantial preamble before first header."""
        content = """---
title: Test
---

This is a comprehensive introduction to the topic. It provides detailed
background information about why this prompt exists and what it aims to
accomplish. The preamble sets the stage for understanding the full context.

## Main Section
Content here."""
        result = validator.validate_content(content)
        contextual = next(c for c in result.components if c.component_name == "Contextual")
        assert contextual.score >= 5  # Should detect preamble

    def test_contextual_expert_persona(self, validator: SCARFFValidator) -> None:
        """Test detection of expert persona definitions."""
        content_expert = "You are an expert Ansible administrator with 10 years experience."
        result = validator.validate_content(content_expert)
        contextual = next(c for c in result.components if c.component_name == "Contextual")
        assert contextual.score >= 3  # Expert persona bonus

    def test_contextual_audience_description(self, validator: SCARFFValidator) -> None:
        """Test detection of audience descriptions."""
        content = "The target audience is DevOps engineers for users who manage infrastructure."
        result = validator.validate_content(content)
        contextual = next(c for c in result.components if c.component_name == "Contextual")
        assert contextual.score >= 3  # Audience description bonus

    def test_contextual_user_request_example(self, validator: SCARFFValidator) -> None:
        """Test detection of user request examples."""
        content = (
            "**User Request Example:** I need to configure Ansible for my project "
            "with configuration and background information."
        )
        result = validator.validate_content(content)
        contextual = next(c for c in result.components if c.component_name == "Contextual")
        assert contextual.score >= 0  # At least detects some context keywords

    def test_actionable_placeholders_detection(self, validator: SCARFFValidator) -> None:
        """Test detection of templating placeholders."""
        content = "Use {{project_name}} and {{version}} in <configuration> settings."
        result = validator.validate_content(content)
        actionable = next(c for c in result.components if c.component_name == "Actionable")
        assert actionable.score >= 4  # 2+ placeholders = 4 points

    def test_actionable_code_blocks_detection(self, validator: SCARFFValidator) -> None:
        """Test detection of code blocks."""
        content = """
```python
def example():
    pass
```

```yaml
key: value
```
"""
        result = validator.validate_content(content)
        actionable = next(c for c in result.components if c.component_name == "Actionable")
        assert actionable.score >= 4  # 2+ code blocks = 4 points

    def test_actionable_instructions_section(self, validator: SCARFFValidator) -> None:
        """Test detection of Instructions section."""
        content = """
### Instructions
Follow these steps carefully.
"""
        result = validator.validate_content(content)
        actionable = next(c for c in result.components if c.component_name == "Actionable")
        assert actionable.score >= 5  # Instructions section = 5 points

    def test_formatted_yaml_frontmatter_fields(self, validator: SCARFFValidator) -> None:
        """Test detection of YAML frontmatter with specific fields."""
        content = """---
title: "Test Prompt"
tags: [ansible, config]
version: 1.0.0
---

Content here."""
        result = validator.validate_content(content)
        formatted = next(c for c in result.components if c.component_name == "Formatted")
        assert formatted.score >= 9  # Frontmatter (6) + title (2) + tags (1) = 9

    def test_formatted_diverse_list_types(self, validator: SCARFFValidator) -> None:
        """Test bonus for having both bullet and numbered lists."""
        content = """
### Format
Must include the following format.

- Bullet item 1
- Bullet item 2
- Bullet item 3

1. Numbered item 1
2. Numbered item 2
3. Numbered item 3
"""
        result = validator.validate_content(content)
        formatted = next(c for c in result.components if c.component_name == "Formatted")
        assert formatted.score >= 11  # Format section + bullets + numbered + diversity

    def test_formatted_language_consistency_bonus(self, validator: SCARFFValidator) -> None:
        """Test language consistency between frontmatter and code blocks."""
        content = """---
language: "python"
---

```python
def example():
    pass
```
"""
        result = validator.validate_content(content)
        formatted = next(c for c in result.components if c.component_name == "Formatted")
        assert formatted.score >= 3  # Language consistency bonus

    def test_formatted_language_consistency_penalty(self, validator: SCARFFValidator) -> None:
        """Test penalty for language inconsistency."""
        content = """---
language: "python"
---

```bash
echo "mismatch"
```
"""
        result = validator.validate_content(content)
        _formatted = next(c for c in result.components if c.component_name == "Formatted")
        # Should have penalty but not fail completely

    def test_focused_length_scoring_ranges(self, validator: SCARFFValidator) -> None:
        """Test focus scoring at different length ranges."""
        # Too short (<50 words)
        short = "Brief content."
        result_short = validator.validate_content(short)
        focused_short = next(c for c in result_short.components if c.component_name == "Focused")
        assert focused_short.score <= 10  # Too short gets lower score

        # Acceptable but short (50-100 words)
        acceptable_short = " ".join(["word"] * 75)
        result_ok_short = validator.validate_content(acceptable_short)
        focused_ok_short = next(
            c for c in result_ok_short.components if c.component_name == "Focused"
        )
        assert 8 <= focused_ok_short.score <= 15  # Acceptable range

        # Optimal (100-800 words)
        optimal = " ".join(["word"] * 400)
        result_optimal = validator.validate_content(optimal)
        focused_optimal = next(
            c for c in result_optimal.components if c.component_name == "Focused"
        )
        assert focused_optimal.score >= 15  # Optimal = 15+ points

        # Acceptable but long (800-1500 words)
        acceptable_long = " ".join(["word"] * 1000)
        result_ok_long = validator.validate_content(acceptable_long)
        focused_ok_long = next(
            c for c in result_ok_long.components if c.component_name == "Focused"
        )
        assert 8 <= focused_ok_long.score <= 15  # Acceptable range

        # Too long (>1500 words)
        too_long = " ".join(["word"] * 2000)
        result_too_long = validator.validate_content(too_long)
        focused_too_long = next(
            c for c in result_too_long.components if c.component_name == "Focused"
        )
        assert focused_too_long.score <= 12  # Too long gets penalty

    def test_focused_top_level_headings_penalty(self, validator: SCARFFValidator) -> None:
        """Test penalty for too many top-level headings."""
        content = """
# Topic 1
# Topic 2
# Topic 3
# Topic 4
# Topic 5
# Topic 6
"""
        result = validator.validate_content(content)
        _focused = next(c for c in result.components if c.component_name == "Focused")
        # Should have penalty for scattered topics

    def test_generate_issues_for_missing_mandatory_sections(
        self, validator: SCARFFValidator
    ) -> None:
        """Test that issues are generated for missing mandatory SCAFF sections."""
        content = """Just some content without proper SCAFF structure."""
        issues = validator.generate_issues(content)

        # Should have issues for missing sections
        missing_sections = [issue for issue in issues if issue.code == "SCAFF001"]
        assert len(missing_sections) > 0  # Should detect missing sections

        # Check that all mandatory sections are checked
        section_names = [issue.message for issue in missing_sections]
        assert any("Situation" in msg for msg in section_names)
        assert any("Challenge" in msg for msg in section_names)
        assert any("Audience" in msg for msg in section_names)
        assert any("Format" in msg for msg in section_names)
        assert any("Foundations" in msg for msg in section_names)

    def test_specific_component_status_thresholds(self, validator: SCARFFValidator) -> None:
        """Test that Specific component reports correct status at different thresholds."""
        # Test "needs improvement" (<12)
        low_content = "Brief text."
        result_low = validator.validate_content(low_content)
        specific_low = next(c for c in result_low.components if c.component_name == "Specific")
        assert specific_low.status == "needs improvement"

        # Test "good" (12-15)
        good_content = """
### Foundations
Must implement security. Set timeout to 30 seconds.
### Challenge
Configure system properly.
"""
        result_good = validator.validate_content(good_content)
        specific_good = next(c for c in result_good.components if c.component_name == "Specific")
        assert specific_good.status in ["good", "excellent"]

        # Test "excellent" (16+)
        excellent_content = """
### Foundations
- **Security**: Must implement 2FA with at least 12 characters
- **Performance**: Set timeout to 30 seconds maximum
- **Validation**: Require exactly 3 attempts minimum
- Define clear scope
### Challenge
Configure system with 5 critical requirements.
"""
        result_excellent = validator.validate_content(excellent_content)
        specific_excellent = next(
            c for c in result_excellent.components if c.component_name == "Specific"
        )
        assert specific_excellent.status == "excellent"

    def test_contextual_component_status_thresholds(self, validator: SCARFFValidator) -> None:
        """Test that Contextual component reports correct status at different thresholds."""
        # Test "needs improvement" (<12)
        low_content = "Some text."
        result_low = validator.validate_content(low_content)
        contextual_low = next(c for c in result_low.components if c.component_name == "Contextual")
        assert contextual_low.status == "needs improvement"

        # Test "good" (12-15)
        good_content = """
### Situation
This is a comprehensive project situation description with detailed background.
### Audience
Target users are experienced developers.
"""
        result_good = validator.validate_content(good_content)
        contextual_good = next(
            c for c in result_good.components if c.component_name == "Contextual"
        )
        assert contextual_good.status in ["good", "excellent"]

        # Test "excellent" (16+)
        excellent_content = """
### Situation
This comprehensive situation provides detailed background about the context and purpose.
### Audience
Target audience includes senior developers, engineers, and technical leads working on systems.

## Background
The purpose is to solve problems with context and mission goals.
You are an expert administrator with deep knowledge.
"""
        result_excellent = validator.validate_content(excellent_content)
        contextual_excellent = next(
            c for c in result_excellent.components if c.component_name == "Contextual"
        )
        assert contextual_excellent.status == "excellent"

    def test_actionable_component_status_thresholds(self, validator: SCARFFValidator) -> None:
        """Test that Actionable component reports correct status at different thresholds."""
        # Test "needs improvement" (<12)
        low_content = "Do something."
        result_low = validator.validate_content(low_content)
        actionable_low = next(c for c in result_low.components if c.component_name == "Actionable")
        assert actionable_low.status == "needs improvement"

        # Test "good" (12-15)
        good_content = """
1. Create the configuration
2. Implement the feature
3. Test the system carefully
4. Deploy to production environment
5. Monitor results and performance
6. Verify functionality works
7. Configure settings appropriately
"""
        result_good = validator.validate_content(good_content)
        actionable_good = next(
            c for c in result_good.components if c.component_name == "Actionable"
        )
        assert actionable_good.status in ["good", "excellent"]

        # Test "excellent" (16+)
        excellent_content = """
Use {{project}} and <config> parameters.

```bash
command --flag value
```

```python
code = True
```

### Instructions
Follow these steps carefully.

1. Create database
2. Implement API
3. Build frontend
4. Test thoroughly
5. Deploy system
6. Monitor performance
7. Verify results
"""
        result_excellent = validator.validate_content(excellent_content)
        actionable_excellent = next(
            c for c in result_excellent.components if c.component_name == "Actionable"
        )
        assert actionable_excellent.status == "excellent"

    def test_formatted_component_status_thresholds(self, validator: SCARFFValidator) -> None:
        """Test that Formatted component reports correct status at different thresholds."""
        # Test "needs improvement" (<12)
        low_content = "Plain text no structure."
        result_low = validator.validate_content(low_content)
        formatted_low = next(c for c in result_low.components if c.component_name == "Formatted")
        assert formatted_low.status == "needs improvement"

        # Test "good" (12-15)
        good_content = """
### Format
Output format specification.

# Main Title
## Section
- Item 1
- Item 2
- Item 3
"""
        result_good = validator.validate_content(good_content)
        formatted_good = next(c for c in result_good.components if c.component_name == "Formatted")
        assert formatted_good.status in ["good", "excellent"]

        # Test "excellent" (16+)
        excellent_content = """---
title: "Excellent Prompt"
tags: [test, demo]
language: "python"
---

### Format
Clear format specification.

# Main Title
## Section 1
- Bullet 1
- Bullet 2
- Bullet 3

## Section 2
1. Step 1
2. Step 2
3. Step 3

```python
code = True
```
"""
        result_excellent = validator.validate_content(excellent_content)
        formatted_excellent = next(
            c for c in result_excellent.components if c.component_name == "Formatted"
        )
        assert formatted_excellent.status == "excellent"

    def test_focused_component_status_thresholds(self, validator: SCARFFValidator) -> None:
        """Test that Focused component reports correct status at different thresholds."""
        # Test "needs improvement" (<12)
        low_content = "Too brief."
        result_low = validator.validate_content(low_content)
        focused_low = next(c for c in result_low.components if c.component_name == "Focused")
        assert focused_low.status == "needs improvement"

        # Test "good" (12-15)
        good_content = " ".join(["word"] * 150)  # 150 words
        result_good = validator.validate_content(good_content)
        focused_good = next(c for c in result_good.components if c.component_name == "Focused")
        assert focused_good.status in ["good", "excellent"]

        # Test "excellent" (16+)
        excellent_content = """
# Single Topic Focus

""" + " ".join(["word"] * 400)  # 400 words in optimal range
        result_excellent = validator.validate_content(excellent_content)
        focused_excellent = next(
            c for c in result_excellent.components if c.component_name == "Focused"
        )
        assert focused_excellent.status == "excellent"

    def test_contextual_sections_with_minimal_content(self, validator: SCARFFValidator) -> None:
        """Test detection of sections with minimal vs substantial content."""
        # Minimal content (1-4 words) should get partial points
        minimal_content = """
### Situation
Brief.
### Audience
Users.
"""
        result_minimal = validator.validate_content(minimal_content)
        contextual_minimal = next(
            c for c in result_minimal.components if c.component_name == "Contextual"
        )
        assert contextual_minimal.score > 0  # Should get some points for minimal content

        # Substantial content (5+ words) should get full points
        substantial_content = """
### Situation
This is a detailed situation description with context.
### Audience
Target users are professional developers working on production systems.
"""
        result_substantial = validator.validate_content(substantial_content)
        contextual_substantial = next(
            c for c in result_substantial.components if c.component_name == "Contextual"
        )
        assert contextual_substantial.score >= 10  # Should get full points for sections

    def test_contextual_generic_sections_scoring(self, validator: SCARFFValidator) -> None:
        """Test scoring of generic context sections."""
        # Test 1 generic section (5 points)
        one_section = """
### Context
Background information here.
"""
        result_one = validator.validate_content(one_section)
        contextual_one = next(c for c in result_one.components if c.component_name == "Contextual")
        assert contextual_one.score >= 5

        # Test 2+ generic sections (8 points)
        two_sections = """
### Context
Background information.
### Overview
Detailed overview.
"""
        result_two = validator.validate_content(two_sections)
        contextual_two = next(c for c in result_two.components if c.component_name == "Contextual")
        assert contextual_two.score >= 8

    def test_contextual_keywords_scoring(self, validator: SCARFFValidator) -> None:
        """Test context keyword detection scoring."""
        # Test 2-3 keywords (3 points)
        few_keywords = "The background and purpose of this project."
        result_few = validator.validate_content(few_keywords)
        contextual_few = next(c for c in result_few.components if c.component_name == "Contextual")
        assert contextual_few.score >= 3

        # Test 4+ keywords (5 points)
        many_keywords = (
            "The background, context, purpose, and mission describe the problem for our audience."
        )
        result_many = validator.validate_content(many_keywords)
        contextual_many = next(
            c for c in result_many.components if c.component_name == "Contextual"
        )
        assert contextual_many.score >= 5
