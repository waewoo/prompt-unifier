"""Test package version and imports."""

import prompt_manager


def test_version() -> None:
    """Test that package version is defined and correct."""
    assert hasattr(prompt_manager, "__version__")
    assert prompt_manager.__version__ == "0.1.0"


def test_package_imports() -> None:
    """Test that all subpackages can be imported."""
    import prompt_manager.cli
    import prompt_manager.core
    import prompt_manager.handlers
    import prompt_manager.models
    import prompt_manager.utils

    assert prompt_manager.cli is not None
    assert prompt_manager.core is not None
    assert prompt_manager.handlers is not None
    assert prompt_manager.models is not None
    assert prompt_manager.utils is not None
