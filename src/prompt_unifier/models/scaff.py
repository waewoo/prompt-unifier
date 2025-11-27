"""SCAFF methodology validation models.

This module provides data structures for representing SCAFF (Specific, Contextual,
Actionable, Formatted, Focused) validation scores and components.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class SCARFFComponent(BaseModel):
    """Represents a single SCAFF component score.

    Each SCAFF component (Specific, Contextual, Actionable, Formatted, Focused)
    is scored individually on a 0-20 scale.

    Attributes:
        component_name: Name of the SCAFF component
        score: Component score (0-20 points)
        max_score: Maximum possible score (default 20)
        status: Descriptive status (e.g., "excellent", "good", "failed")

    Properties:
        passed: True if score meets minimum threshold (>=12, which is 60%)
    """

    component_name: str = Field(description="Name of the SCAFF component")
    score: int = Field(description="Component score (0-20)", ge=0, le=20)
    max_score: int = Field(default=20, description="Maximum possible score")
    status: str = Field(description="Descriptive status of the component")

    @field_validator("score")
    @classmethod
    def validate_score_range(cls, v: int) -> int:
        """Validate that score is between 0 and 20.

        Args:
            v: Score value to validate

        Returns:
            Validated score value

        Raises:
            ValueError: If score is not between 0 and 20
        """
        if not 0 <= v <= 20:
            raise ValueError("Score must be between 0 and 20")
        return v

    @property
    def passed(self) -> bool:
        """Check if component passed minimum threshold.

        A component passes if it scores at least 60% (12/20 points).

        Returns:
            True if score >= 12, False otherwise
        """
        return self.score >= 12


class SCARFFScore(BaseModel):
    """Represents the complete SCAFF validation score.

    Aggregates scores from all five SCAFF components into a total score
    with grade classification.

    Attributes:
        components: List of individual component scores
        total_score: Aggregated total score (0-100)
        max_score: Maximum possible total score (default 100)

    Properties:
        percentage: Score as a percentage (0-100)
        grade: Quality grade ("excellent", "good", or "poor")
        all_passed: True if all components meet minimum threshold
    """

    components: list[SCARFFComponent] = Field(
        description="List of individual SCAFF component scores"
    )
    total_score: int = Field(description="Aggregated total score (0-100)", ge=0, le=100)
    max_score: int = Field(default=100, description="Maximum possible score")

    @property
    def percentage(self) -> float:
        """Calculate score as percentage.

        Returns:
            Percentage value (0.0-100.0)
        """
        return (self.total_score / self.max_score) * 100

    @property
    def grade(self) -> str:
        """Classify score into quality grade.

        Grading scale:
        - excellent: >= 80%
        - good: 60-79%
        - poor: < 60%

        Returns:
            Grade classification string
        """
        percentage = self.percentage
        if percentage >= 80:
            return "excellent"
        elif percentage >= 60:
            return "good"
        else:
            return "poor"

    @property
    def all_passed(self) -> bool:
        """Check if all components passed minimum threshold.

        Returns:
            True if all components scored >= 12, False otherwise
        """
        return all(component.passed for component in self.components)


def rebuild_models() -> None:
    """Rebuild ValidationResult model to resolve forward references.

    This function should be called after both modules are imported to ensure
    proper resolution of the forward reference from ValidationResult to SCARFFScore.
    """
    from prompt_unifier.models.validation import ValidationResult

    # Pass SCARFFScore to the rebuild to resolve the forward reference
    ValidationResult.model_rebuild(_types_namespace={"SCARFFScore": SCARFFScore})


# Rebuild models to resolve forward references when this module is imported
rebuild_models()
