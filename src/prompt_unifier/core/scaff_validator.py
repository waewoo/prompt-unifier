"""SCAFF methodology validator for prompt content quality assessment.



This module implements validation logic for the SCAFF methodology:

- Specific: Concrete requirements and measurable goals

- Contextual: Background information and user context

- Actionable: Clear verbs, tasks, and instructions

- Formatted: Proper structure, sections, and markdown formatting

- Focused: Appropriate length and single topic focus

"""

import re

from prompt_unifier.models.scaff import SCARFFComponent, SCARFFScore
from prompt_unifier.models.validation import ValidationIssue, ValidationSeverity, WarningCode

# SCAFF Criteria Constants

SPECIFIC_KEYWORDS = ["must", "should", "require", "exactly", "at least", "maximum", "minimum"]


# Extended context keywords to include common prompt structures

CONTEXT_KEYWORDS = [
    "background",
    "context",
    "why",
    "purpose",
    "problem",
    "audience",
    "users",
    "situation",
    "challenge",
    "mission",
    "goal",
    "description",
    "role",
    "about",
    "introduction",
]


# Extended action verbs to cover more imperative patterns

ACTION_VERBS = [
    "create",
    "implement",
    "test",
    "build",
    "configure",
    "deploy",
    "analyze",
    "review",
    "validate",
    "generate",
    "develop",
    "design",
    "define",
    "set",
    "add",
    "enable",
    "disable",
    "include",
    "ensure",
    "use",
    "apply",
    "follow",
    "check",
    "verify",
    "specify",
    "establish",
    "refactor",
    "optimize",
    "audit",
    "migrate",
    "update",
    "upgrade",
    "install",
    "setup",
    "execute",
    "run",
    "document",
    "plan",
]


# Scoring thresholds

COMPONENT_MAX_SCORE = 20

TOTAL_MAX_SCORE = 100


# Optimal content length (in words)

OPTIMAL_MIN_WORDS = 100

OPTIMAL_MAX_WORDS = 800

# Regex Patterns and Literals
REGEX_FOUNDATIONS = r"###?\s*foundations"
REGEX_CHALLENGE = r"###?\s*challenge"
REGEX_SITUATION = r"###?\s*situation"
REGEX_AUDIENCE = r"###?\s*audience"
REGEX_FORMAT = r"###?\s*format"

STATUS_EXCELLENT = "excellent"
STATUS_GOOD = "good"
STATUS_NEEDS_IMPROVEMENT = "needs improvement"


# Suggestion templates

SUGGESTIONS = {
    "specific": (
        "Add concrete requirements with measurable goals. "
        "Use specific metrics, thresholds, or clear acceptance criteria."
    ),
    "contextual": (
        "Provide background information about the target audience and use case. "
        "Explain why this prompt is needed."
    ),
    "actionable": (
        "Include clear action verbs and step-by-step instructions. "
        "Make it clear what tasks should be performed."
    ),
    "formatted": (
        "Improve structure with markdown headings, bullet points, or numbered lists. "
        "Break content into clear sections."
    ),
    "focused": (
        "Ensure content is focused on a single topic with appropriate length. "
        "Aim for 100-800 words to maintain clarity."
    ),
}


class SCARFFValidator:
    """Validator for SCAFF methodology compliance.



    This validator analyzes prompt content against five SCAFF components

    using simple text-based heuristics. Each component is scored 0-20 points

    for a total score of 0-100.



    Examples:

        >>> validator = SCARFFValidator()

        >>> score = validator.validate_content("## Context\\nThis is for...")

        >>> score.total_score

        65

        >>> score.grade

        'good'

    """

    def validate_content(self, content: str) -> SCARFFScore:
        """Validate content against SCAFF methodology.



        Analyzes the content against all five SCAFF components and aggregates

        the scores into a total 0-100 scale.



        Args:

            content: The prompt content to validate



        Returns:

            SCARFFScore containing component scores and total score



        Examples:

            >>> validator = SCARFFValidator()

            >>> score = validator.validate_content("# Title\\nContent")

            >>> len(score.components)

            5

        """

        components = []

        # Analyze each SCAFF component

        specific_score, specific_status = self._analyze_specific(content)

        components.append(
            SCARFFComponent(component_name="Specific", score=specific_score, status=specific_status)
        )

        contextual_score, contextual_status = self._analyze_contextual(content)

        components.append(
            SCARFFComponent(
                component_name="Contextual", score=contextual_score, status=contextual_status
            )
        )

        actionable_score, actionable_status = self._analyze_actionable(content)

        components.append(
            SCARFFComponent(
                component_name="Actionable", score=actionable_score, status=actionable_status
            )
        )

        formatted_score, formatted_status = self._analyze_formatted(content)

        components.append(
            SCARFFComponent(
                component_name="Formatted", score=formatted_score, status=formatted_status
            )
        )

        focused_score, focused_status = self._analyze_focused(content)

        components.append(
            SCARFFComponent(component_name="Focused", score=focused_score, status=focused_status)
        )

        # Calculate total score

        total_score = sum(c.score for c in components)

        return SCARFFScore(components=components, total_score=total_score)

    def _analyze_specific(self, content: str) -> tuple[int, str]:
        """Analyze content for specific requirements and measurable goals.

        Checks for:
        - Concrete requirement keywords (must, should, require, etc.)
        - Imperative technical instructions (Set X, Disable Y, Enable Z)
        - Measurable metrics and thresholds
        - Clear scope definition and structured requirements

        Args:
            content: Content to analyze

        Returns:
            Tuple of (score, status) where score is 0-20
        """
        content_lower = content.lower()
        score = 0

        score += self._check_specific_keywords(content_lower)
        score += self._check_imperative_instructions(content)
        score += self._check_numeric_metrics(content, content_lower)
        score += self._check_specific_structure(content, content_lower)

        # PENALTY: Missing mandatory specific sections
        missing_sections = []
        if not re.search(REGEX_FOUNDATIONS, content_lower):
            missing_sections.append("Foundations")
        if not re.search(REGEX_CHALLENGE, content_lower):
            missing_sections.append("Challenge")

        if missing_sections:
            # Cap score at 10 (Needs Improvement) if mandatory sections are missing
            score = min(score, 10)

        # Cap at max score
        score = min(score, COMPONENT_MAX_SCORE)

        # Determine status
        if score >= 16:
            status = STATUS_EXCELLENT
        elif score >= 12:
            status = STATUS_GOOD
        else:
            status = STATUS_NEEDS_IMPROVEMENT

        return score, status

    def _check_specific_keywords(self, content_lower: str) -> int:
        """Check for specific requirement keywords."""
        keyword_count = sum(content_lower.count(keyword) for keyword in SPECIFIC_KEYWORDS)
        if keyword_count >= 5:
            return 8
        elif keyword_count >= 3:
            return 6
        elif keyword_count >= 1:
            return 3
        return 0

    def _check_imperative_instructions(self, content: str) -> int:
        """Check for imperative technical instructions."""
        # Simplify regex by matching structure first, then checking verbs
        # Matches: "- [**Prefix**: ] Verb Word"
        bullet_pattern = r"^\s*[-*+]\s*(?:\*\*[^*]+\*\*:\s*)?(\w+)\s+\w+"
        candidates = re.findall(bullet_pattern, content, re.MULTILINE)
        imperative_instructions = sum(1 for word in candidates if word.lower() in ACTION_VERBS)

        requirement_bullets = len(
            re.findall(
                r"^\s*[-*+]\s+\w+\s+(must|should|require[sd]?|need[sd]?)\s+",
                content,
                re.MULTILINE | re.I,
            )
        )

        total = imperative_instructions + requirement_bullets
        if total >= 5:
            return 8
        elif total >= 3:
            return 6
        elif total >= 1:
            return 3
        return 0

    def _check_numeric_metrics(self, content: str, content_lower: str) -> int:
        """Check for numeric metrics and thresholds."""
        numbers_pattern = (
            r"\d+\s{0,10}(?:characters|words|minutes|seconds|items|percent|%|attempts)"
        )
        numeric_metrics = len(re.findall(numbers_pattern, content_lower))

        if numeric_metrics == 0:
            general_numbers = len(re.findall(r"\d+", content))
            if general_numbers >= 3:
                numeric_metrics = general_numbers

        if numeric_metrics >= 3:
            return 7
        elif numeric_metrics >= 2:
            return 5
        elif numeric_metrics >= 1:
            return 3
        return 0

    def _check_specific_structure(self, content: str, content_lower: str) -> int:
        """Check for structural elements that indicate specificity."""
        score = 0
        if re.search(REGEX_FOUNDATIONS, content_lower):
            score += 6
        if re.search(REGEX_CHALLENGE, content_lower):
            score += 6

        negative_constraints = len(
            re.findall(r"\b(do not|never|avoid|must not|should not|don't)\b", content_lower)
        )
        if negative_constraints >= 2:
            score += 3
        elif negative_constraints >= 1:
            score += 2

        internal_refs = len(re.findall(r"\b(rules|prompts)/[\w/-]+\.md\b", content))
        if internal_refs >= 1:
            score += 5

        other_structure = ["requirements", "acceptance criteria", "configuration", "specifications"]
        if any(keyword in content_lower for keyword in other_structure):
            score += 2

        return score

    def _analyze_contextual(self, content: str) -> tuple[int, str]:
        """Analyze content for contextual information and background.

        Checks for:
        - Standard SCAFF sections (Situation, Challenge, Audience)
        - Background information sections
        - User context and target audience
        - Problem statement or purpose
        - Expert persona definitions (implicit context)

        Args:
            content: Content to analyze

        Returns:
            Tuple of (score, status) where score is 0-20
        """
        content_lower = content.lower()
        score = 0

        # 1. SCAFF Sections (Situation, Audience)
        section_score, _ = self._check_contextual_sections(content_lower)
        score += section_score

        # 2. Generic Context Sections
        score += self._check_generic_context_sections(content_lower)

        # 3. Preamble
        if self._has_substantial_preamble(content):
            score += 5

        # 4. Keywords
        score += self._check_context_keywords(content_lower)

        # 5. Audience Description (fallback if section missing)
        if self._has_audience_description(content_lower):
            score += 3

        # 6. Expert Persona
        if self._has_expert_persona(content_lower):
            score += 3

        # 7. User Request Example
        if re.search(r"\*\*user request example\*\*", content_lower):
            score += 2

        # PENALTY: Missing mandatory contextual sections
        missing_sections = []
        if not re.search(REGEX_SITUATION, content_lower):
            missing_sections.append("Situation")
        if not re.search(REGEX_AUDIENCE, content_lower):
            missing_sections.append("Audience")

        if missing_sections:
            # Cap score at 10 (Needs Improvement) if mandatory sections are missing
            score = min(score, 10)

        score = min(score, COMPONENT_MAX_SCORE)

        if score >= 16:
            status = STATUS_EXCELLENT
        elif score >= 12:
            status = STATUS_GOOD
        else:
            status = STATUS_NEEDS_IMPROVEMENT

        return score, status

    def _check_contextual_sections(self, content_lower: str) -> tuple[int, int]:
        """Check for contextual SCAFF sections (Situation, Audience) with density verification.
        Returns (score, count_of_found_sections)."""
        score = 0
        sections_found_count = 0

        sections = {
            rf"{REGEX_SITUATION}\s*\n(.+?)(?=\n#{{1,3}}\s|\Z)": 5,
            rf"{REGEX_AUDIENCE}\s*\n(.+?)(?=\n#{{1,3}}\s|\Z)": 5,
        }

        for pattern, points in sections.items():
            match = re.search(pattern, content_lower, re.DOTALL)
            if match:
                section_body = match.group(1).strip()
                word_count = len(section_body.split())
                if word_count >= 5:
                    score += points
                    sections_found_count += 1
                elif word_count >= 1:
                    score += points // 2
                    sections_found_count += 1  # Count even if minimal content
        return score, sections_found_count

    def _check_scaff_sections(self, content_lower: str) -> int:
        """Check for standard SCAFF sections with density verification."""
        score = 0

        # Mandatory sections with high weight
        mandatory_sections = {
            rf"{REGEX_SITUATION}\s*\n(.+?)(?=\n#{{1,3}}\s|\Z)": 4,
            rf"{REGEX_CHALLENGE}\s*\n(.+?)(?=\n#{{1,3}}\s|\Z)": 4,
            rf"{REGEX_AUDIENCE}\s*\n(.+?)(?=\n#{{1,3}}\s|\Z)": 4,
            rf"{REGEX_FORMAT}\s*\n(.+?)(?=\n#{{1,3}}\s|\Z)": 4,
            rf"{REGEX_FOUNDATIONS}\s*\n(.+?)(?=\n#{{1,3}}\s|\Z)": 4,
        }

        # Check for mandatory sections
        sections_found = 0
        for pattern, points in mandatory_sections.items():
            match = re.search(pattern, content_lower, re.DOTALL)
            if match:
                section_body = match.group(1).strip()
                word_count = len(section_body.split())
                if word_count >= 5:  # Minimum content requirement
                    score += points
                    sections_found += 1

        # Penalty if mandatory sections are missing (cap score if not all present)
        if sections_found < 5:
            score = min(score, 10)  # Cannot exceed 10/20 if missing mandatory sections

        return score

    def _check_generic_context_sections(self, content_lower: str) -> int:
        """Check for generic context-providing section headings."""
        generic_context_sections = [
            r"###?\s*context",
            r"###?\s*background",
            r"###?\s*why\s+this\s+matters",
            r"###?\s*purpose",
            r"###?\s*overview",
            r"###?\s*description",
            r"###?\s*about",
            r"###?\s*role",
            r"###?\s*introduction",
        ]

        generic_sections_found = sum(
            1 for pattern in generic_context_sections if re.search(pattern, content_lower)
        )

        if generic_sections_found >= 2:
            return 8
        elif generic_sections_found >= 1:
            return 5
        return 0

    def _has_substantial_preamble(self, content: str) -> bool:
        """Check if content has substantial text before the first header."""
        clean_content = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                clean_content = parts[2].strip()

        first_header_match = re.search(r"^#{1,6}\s", clean_content, re.MULTILINE)
        if first_header_match:
            preamble = clean_content[: first_header_match.start()].strip()
            return len(preamble.split()) >= 15
        return False

    def _check_context_keywords(self, content_lower: str) -> int:
        """Check for context keywords."""
        keyword_count = sum(1 for keyword in CONTEXT_KEYWORDS if keyword in content_lower)
        if keyword_count >= 4:
            return 5
        elif keyword_count >= 2:
            return 3
        return 0

    def _has_audience_description(self, content_lower: str) -> bool:
        """Check for explicit audience/user descriptions."""
        return bool(
            re.search(
                r"(target\s+(audience|users)|audience\s+is|users\s+are|for\s+\w+\s+who)",
                content_lower,
            )
        )

    def _has_expert_persona(self, content_lower: str) -> bool:
        """Check for expert persona definitions."""
        # Split regex to reduce complexity
        roles = (
            r"(?:expert|specialist|senior|experienced|"
            r"professional|developer|engineer|assistant|guide)"
        )

        # Pattern 1: "You are (an) X" or "Act as (an) X"
        if re.search(rf"(?:you\s+are|act\s+as)\s+(?:an?\s+)?{roles}", content_lower):
            return True

        # Pattern 2: "Role: X"
        # Using bool() to convert Match object/None to boolean (Ruff SIM103 compliant)
        return bool(re.search(rf"role:\s*{roles}", content_lower))

    def _analyze_actionable(self, content: str) -> tuple[int, str]:
        """Analyze content for actionable verbs and instructions.



        Checks for:

        - Templating placeholders ({{ }}, < >) - shows parametrized actions

        - Code blocks (``` ```) - concrete output examples

        - Action verbs in imperative form (create, implement, test, set, define, etc.)

        - Imperative bullet points (- Create X, - Set Y, - Configure Z)

        - Step-by-step numbered instructions



        Args:

            content: Content to analyze



        Returns:

            Tuple of (score, status) where score is 0-20

        """

        content_lower = content.lower()

        score = 0

        # Detect templating placeholders (parametrized actions)

        placeholders = len(re.findall(r"(\{\{.+?\}\}|<[^>]+>)", content))

        if placeholders >= 2:
            score += 4

        elif placeholders >= 1:
            score += 2

        # Detect code blocks (concrete examples of expected output)

        code_blocks = len(re.findall(r"```", content))

        if code_blocks >= 2:  # At least one complete block (open + close)
            score += 4

        elif code_blocks >= 1:
            score += 2

        # Check for action verbs (broader search)

        verb_count = sum(1 for verb in ACTION_VERBS if verb in content_lower)

        if verb_count >= 7:
            score += 8

        elif verb_count >= 5:
            score += 6

        elif verb_count >= 3:
            score += 4

        elif verb_count >= 1:
            score += 2

        # Detect imperative bullet points and numbered lists with action verbs
        # Matches both: "- Create X" and "1. Create X"
        # Use simplified regex and set membership for complexity reduction
        # Allow for optional markdown formatting chars like ** or * at the start of the word
        list_pattern = r"^\s*(?:[-*+]|\d+\.)\s*(?:[*_]{1,3})?(\w+)(?:[*_]{1,3})?\s+"
        list_candidates = re.findall(list_pattern, content, re.MULTILINE)
        imperative_bullets = sum(1 for word in list_candidates if word.lower() in ACTION_VERBS)

        if imperative_bullets >= 5:
            score += 7

        elif imperative_bullets >= 3:
            score += 5

        elif imperative_bullets >= 1:
            score += 3

        # Check for Instructions section (Actionable core)
        if re.search(r"###?\s*instructions\s*\n", content_lower):
            score += 5

        # Cap at max score

        score = min(score, COMPONENT_MAX_SCORE)

        # Determine status

        if score >= 16:
            status = STATUS_EXCELLENT

        elif score >= 12:
            status = STATUS_GOOD

        else:
            status = STATUS_NEEDS_IMPROVEMENT

        return score, status

    def _analyze_formatted(self, content: str) -> tuple[int, str]:
        """Analyze content for proper markdown formatting and structure.

        Checks for:
        - YAML frontmatter (required for prompt-unifier)
        - Format section (specifies output format)
        - Markdown headings (# ## ###)
        - Bullet points and numbered lists
        - Proper sectioning

        Args:
            content: Content to analyze

        Returns:
            Tuple of (score, status) where score is 0-20
        """
        score = 0
        has_frontmatter = content.startswith("---")

        score += self._check_frontmatter_yaml(content)

        # Format section check
        if re.search(REGEX_FORMAT, content.lower()):
            score += 6
        else:
            # PENALTY: Missing Format section
            score = min(score, 10)

        score += self._check_markdown_structure(content, has_frontmatter)
        score += self._check_lists(content)
        score += self._check_language_consistency(content)

        # Cap at max score
        score = min(score, COMPONENT_MAX_SCORE)

        # Determine status
        if score >= 16:
            status = STATUS_EXCELLENT
        elif score >= 12:
            status = STATUS_GOOD
        else:
            status = STATUS_NEEDS_IMPROVEMENT

        return score, status

    def _check_frontmatter_yaml(self, content: str) -> int:
        """Check for YAML frontmatter and key fields."""
        score = 0
        if content.startswith("---"):
            score += 6
            if re.search(r"^title:", content, re.MULTILINE):
                score += 2
            if re.search(r"^tags:", content, re.MULTILINE):
                score += 1
        return score

    def _check_markdown_structure(self, content: str, has_frontmatter: bool) -> int:
        """Check for markdown headings and structure."""
        score = 0
        heading_count = len(re.findall(r"^#{1,6}\s+.+", content, re.MULTILINE))

        if has_frontmatter:
            if heading_count >= 3:
                score += 4
            elif heading_count >= 1:
                score += 2
        elif heading_count >= 3:
            score += 8
        elif heading_count >= 1:
            score += 5
        return score

    def _check_lists(self, content: str) -> int:
        """Check for bullet points and numbered lists."""
        score = 0
        bullet_count = len(re.findall(r"^\s*[-*+]\s+", content, re.MULTILINE))
        if bullet_count >= 3:
            score += 5
        elif bullet_count >= 1:
            score += 3

        numbered_count = len(re.findall(r"^\d+\.\s+", content, re.MULTILINE))
        if numbered_count >= 3:
            score += 4
        elif numbered_count >= 1:
            score += 2

        # Bonus for having diverse formatting (both bullets AND numbered lists)
        if bullet_count >= 1 and numbered_count >= 1:
            score += 2
        return score

    def _check_language_consistency(self, content: str) -> int:
        """Check if declared language matches code blocks."""
        score = 0
        # Extract declared language from frontmatter
        lang_match = re.search(r"^language:\s*[\"']?(\w+)[\"']?", content, re.MULTILINE | re.I)

        if lang_match:
            declared_lang = lang_match.group(1).lower()
            # Ignore natural languages (en, fr, etc.) - we're looking for programming languages
            if declared_lang not in ["en", "fr", "es", "de", "it", "pt", "ru", "zh", "ja"]:
                # Check if code blocks use the declared language
                code_block_pattern = rf"```\s*{re.escape(declared_lang)}"
                if re.search(code_block_pattern, content, re.I):
                    score += 3  # Bonus for language consistency
                elif re.search(r"```\s*\w+", content):
                    score -= 1  # Minor penalty for inconsistency
        return score

    def _analyze_focused(self, content: str) -> tuple[int, str]:
        """Analyze content for focus and appropriate length.

        Checks for:

        - Content length (optimal range: 100-800 words)

        - Topic coherence (single main topic)

        - No scope creep indicators



        Args:

            content: Content to analyze



        Returns:

            Tuple of (score, status) where score is 0-20

        """

        score = 0

        # Count words

        words = content.split()

        word_count = len(words)

        # Score based on length

        if OPTIMAL_MIN_WORDS <= word_count <= OPTIMAL_MAX_WORDS:
            score += 15  # Optimal range

        elif 50 <= word_count < OPTIMAL_MIN_WORDS:
            score += 10  # Acceptable but short

        elif OPTIMAL_MAX_WORDS < word_count <= 1500:
            score += 10  # Acceptable but long

        elif word_count < 50:
            score += 3  # Too short

        else:
            score += 5  # Too long

        # Check for focus indicators (not jumping between unrelated topics)

        # Penalty for too many top-level headings (suggests scattered topics)

        top_level_headings = len(re.findall(r"^#\s+.+", content, re.MULTILINE))

        if top_level_headings <= 2:
            score += 5  # Bonus for focused structure

        elif top_level_headings > 5:
            score -= 3  # Penalty for scattered topics

        # Ensure score is within bounds

        score = max(0, min(score, COMPONENT_MAX_SCORE))

        # Determine status

        if score >= 16:
            status = STATUS_EXCELLENT

        elif score >= 12:
            status = STATUS_GOOD

        else:
            status = STATUS_NEEDS_IMPROVEMENT

        return score, status

    def generate_issues(self, content: str) -> list[ValidationIssue]:
        """Generate ValidationIssue objects for failed SCAFF components.

        Creates warning-level issues with actionable suggestions for each
        component that fails to meet the minimum threshold (score < 12).
        Also checks for mandatory SCAFF sections.

        Args:
            content: Content to validate

        Returns:
            List of ValidationIssue objects with suggestions

        Examples:
            >>> validator = SCARFFValidator()
            >>> issues = validator.generate_issues("vague content", Path("test.md"))
        """
        issues: list[ValidationIssue] = []

        score = self.validate_content(content)

        # Check total score threshold (95%)
        if score.total_score < 95:
            issues.append(
                ValidationIssue(
                    line=None,
                    severity=ValidationSeverity.WARNING,
                    code="SCAFF000",  # General SCAFF warning
                    message=(
                        f"SCAFF Total Score: {score.total_score}/100 "
                        "(Threshold: 95/100). Please improve prompt quality."
                    ),
                    suggestion="Improve specific components to raise the total score.",
                )
            )

        # Check mandatory sections
        content_lower = content.lower()
        mandatory_sections = {
            "Situation": REGEX_SITUATION,
            "Challenge": REGEX_CHALLENGE,
            "Audience": REGEX_AUDIENCE,
            "Format": REGEX_FORMAT,
            "Foundations": REGEX_FOUNDATIONS,
        }

        for section_name, pattern in mandatory_sections.items():
            if not re.search(pattern, content_lower):
                issues.append(
                    ValidationIssue(
                        line=None,
                        severity=ValidationSeverity.WARNING,
                        code="SCAFF001",
                        message=f"Missing mandatory section: {section_name}",
                        suggestion=f"Add a '### {section_name}' section to the prompt.",
                    )
                )

        # Check each component and generate issues for failures

        for component in score.components:
            if not component.passed:  # Score < 12 (60%)
                # Map component name to warning code and suggestion
                component_mapping = {
                    "Specific": (
                        WarningCode.SCAFF_NOT_SPECIFIC,
                        SUGGESTIONS["specific"],
                    ),
                    "Contextual": (
                        WarningCode.SCAFF_LACKS_CONTEXT,
                        SUGGESTIONS["contextual"],
                    ),
                    "Actionable": (
                        WarningCode.SCAFF_NOT_ACTIONABLE,
                        SUGGESTIONS["actionable"],
                    ),
                    "Formatted": (
                        WarningCode.SCAFF_POORLY_FORMATTED,
                        SUGGESTIONS["formatted"],
                    ),
                    "Focused": (
                        WarningCode.SCAFF_UNFOCUSED,
                        SUGGESTIONS["focused"],
                    ),
                }

                if component.component_name in component_mapping:
                    warning_code, suggestion = component_mapping[component.component_name]

                    issues.append(
                        ValidationIssue(
                            line=None,
                            severity=ValidationSeverity.WARNING,
                            code=warning_code.value,
                            message=(
                                f"SCAFF {component.component_name}: Score {component.score}/20 "
                                f"({component.status})"
                            ),
                            excerpt=None,
                            suggestion=suggestion,
                        )
                    )

        return issues
