"""Test package version and imports."""

import re

import prompt_unifier


def test_version() -> None:
    """Test that package version is defined and follows semver format."""
    assert hasattr(prompt_unifier, "__version__")
    # Vérifie que la version suit le format semver (X.Y.Z)
    assert re.match(r"^\d+\.\d+\.\d+$", prompt_unifier.__version__), (
        f"Version '{prompt_unifier.__version__}' doesn't follow semver format"
    )


def test_package_imports() -> None:
    """Test that all subpackages can be imported."""
    import prompt_unifier.cli
    import prompt_unifier.core
    import prompt_unifier.handlers
    import prompt_unifier.models
    import prompt_unifier.utils

    assert prompt_unifier.cli is not None
    assert prompt_unifier.core is not None
    assert prompt_unifier.handlers is not None
    assert prompt_unifier.models is not None
    assert prompt_unifier.utils is not None
