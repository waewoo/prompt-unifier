"""Tests for SCAFF validation models.

This module contains tests for:
- SCARFFComponent Pydantic model
- SCARFFScore Pydantic model
- ValidationResult extension with scaff_score
"""

from pathlib import Path

import pytest

from prompt_unifier.models.scaff import SCARFFComponent, SCARFFScore
from prompt_unifier.models.validation import ValidationResult


class TestSCARFFComponent:
    """Test SCARFFComponent Pydantic model."""

    def test_create_component_with_valid_score(self) -> None:
        """Test creating SCAFF component with valid score (0-20)."""
        component = SCARFFComponent(
            component_name="Specific", score=15, max_score=20, status="good"
        )
        assert component.component_name == "Specific"
        assert component.score == 15
        assert component.max_score == 20
        assert component.status == "good"

    def test_component_passed_property_above_threshold(self) -> None:
        """Test passed property returns True when score >= 12 (60% threshold)."""
        component = SCARFFComponent(
            component_name="Actionable", score=12, max_score=20, status="passed"
        )
        assert component.passed is True

    def test_component_passed_property_below_threshold(self) -> None:
        """Test passed property returns False when score < 12."""
        component = SCARFFComponent(
            component_name="Formatted", score=10, max_score=20, status="failed"
        )
        assert component.passed is False

    def test_validate_score_range_invalid(self) -> None:
        """Test that invalid scores raise ValueError."""
        import pytest

        with pytest.raises(ValueError, match="Score must be between 0 and 20"):
            SCARFFComponent.validate_score_range(21)

        with pytest.raises(ValueError, match="Score must be between 0 and 20"):
            SCARFFComponent.validate_score_range(-1)


class TestSCARFFScore:
    """Test SCARFFScore Pydantic model."""

    def test_create_score_with_all_components(self) -> None:
        """Test creating SCAFF score with all 5 components."""
        components = [
            SCARFFComponent(component_name="Specific", score=18, max_score=20, status="excellent"),
            SCARFFComponent(component_name="Contextual", score=15, max_score=20, status="good"),
            SCARFFComponent(component_name="Actionable", score=16, max_score=20, status="good"),
            SCARFFComponent(component_name="Formatted", score=20, max_score=20, status="excellent"),
            SCARFFComponent(component_name="Focused", score=14, max_score=20, status="good"),
        ]
        score = SCARFFScore(components=components, total_score=83, max_score=100)
        assert len(score.components) == 5
        assert score.total_score == 83
        assert score.max_score == 100

    def test_score_percentage_property(self) -> None:
        """Test percentage property calculation."""
        components = [
            SCARFFComponent(component_name="Specific", score=16, max_score=20, status="good"),
            SCARFFComponent(component_name="Contextual", score=14, max_score=20, status="good"),
            SCARFFComponent(component_name="Actionable", score=15, max_score=20, status="good"),
            SCARFFComponent(component_name="Formatted", score=18, max_score=20, status="excellent"),
            SCARFFComponent(component_name="Focused", score=12, max_score=20, status="passed"),
        ]
        score = SCARFFScore(components=components, total_score=75, max_score=100)
        assert score.percentage == pytest.approx(75.0)

    def test_score_grade_excellent(self) -> None:
        """Test grade property returns 'excellent' for score >= 80."""
        components = [
            SCARFFComponent(component_name="Specific", score=18, max_score=20, status="excellent"),
            SCARFFComponent(
                component_name="Contextual", score=17, max_score=20, status="excellent"
            ),
            SCARFFComponent(component_name="Actionable", score=16, max_score=20, status="good"),
            SCARFFComponent(component_name="Formatted", score=20, max_score=20, status="excellent"),
            SCARFFComponent(component_name="Focused", score=14, max_score=20, status="good"),
        ]
        score = SCARFFScore(components=components, total_score=85, max_score=100)
        assert score.grade == "excellent"

    def test_score_grade_good(self) -> None:
        """Test grade property returns 'good' for score 60-79."""
        components = [
            SCARFFComponent(component_name="Specific", score=14, max_score=20, status="good"),
            SCARFFComponent(component_name="Contextual", score=13, max_score=20, status="good"),
            SCARFFComponent(component_name="Actionable", score=15, max_score=20, status="good"),
            SCARFFComponent(component_name="Formatted", score=16, max_score=20, status="good"),
            SCARFFComponent(component_name="Focused", score=12, max_score=20, status="passed"),
        ]
        score = SCARFFScore(components=components, total_score=70, max_score=100)
        assert score.grade == "good"

    def test_score_grade_poor(self) -> None:
        """Test grade property returns 'poor' for score < 60."""
        components = [
            SCARFFComponent(component_name="Specific", score=10, max_score=20, status="failed"),
            SCARFFComponent(component_name="Contextual", score=8, max_score=20, status="failed"),
            SCARFFComponent(component_name="Actionable", score=12, max_score=20, status="passed"),
            SCARFFComponent(component_name="Formatted", score=11, max_score=20, status="failed"),
            SCARFFComponent(component_name="Focused", score=9, max_score=20, status="failed"),
        ]
        score = SCARFFScore(components=components, total_score=50, max_score=100)
        assert score.grade == "poor"


class TestValidationResultWithSCAFF:
    """Test ValidationResult extension with scaff_score field."""

    def test_validation_result_with_scaff_score(self) -> None:
        """Test ValidationResult can include optional scaff_score."""
        components = [
            SCARFFComponent(component_name="Specific", score=15, max_score=20, status="good"),
            SCARFFComponent(component_name="Contextual", score=14, max_score=20, status="good"),
            SCARFFComponent(component_name="Actionable", score=16, max_score=20, status="good"),
            SCARFFComponent(component_name="Formatted", score=18, max_score=20, status="excellent"),
            SCARFFComponent(component_name="Focused", score=12, max_score=20, status="passed"),
        ]
        scaff_score = SCARFFScore(components=components, total_score=75, max_score=100)

        result = ValidationResult(
            file=Path("/prompts/test.md"),
            status="passed",
            errors=[],
            warnings=[],
            scaff_score=scaff_score,
        )

        assert result.scaff_score is not None
        assert result.scaff_score.total_score == 75
        assert result.scaff_score.grade == "good"

    def test_validation_result_without_scaff_score(self) -> None:
        """Test ValidationResult maintains backward compatibility (scaff_score defaults to None)."""
        result = ValidationResult(
            file=Path("/prompts/test.md"), status="passed", errors=[], warnings=[]
        )

        assert result.scaff_score is None
        assert result.is_valid is True


def test_rebuild_models() -> None:
    """Test explicit call to rebuild_models."""
    from prompt_unifier.models.scaff import rebuild_models

    # Just ensure it runs without error
    rebuild_models()
