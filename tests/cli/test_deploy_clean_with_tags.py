"""Tests for deploy --clean with --tags filter."""

from pathlib import Path

import pytest

from prompt_unifier.handlers.continue_handler import ContinueToolHandler


@pytest.fixture
def setup_multi_tag_storage(tmp_path: Path) -> dict[str, Path]:
    """Setup storage with prompts having different tags."""
    storage_dir = tmp_path / "storage"
    prompts_dir = storage_dir / "prompts"
    prompts_dir.mkdir(parents=True)

    # Create Python prompt
    python_prompt = prompts_dir / "python-guide.md"
    python_prompt.write_text(
        """---
title: Python Guide
description: Python coding guide
tags:
  - python
  - backend
---
Python coding content here"""
    )

    # Create JavaScript prompt
    js_prompt = prompts_dir / "javascript-guide.md"
    js_prompt.write_text(
        """---
title: JavaScript Guide
description: JavaScript coding guide
tags:
  - javascript
  - frontend
---
JavaScript coding content here"""
    )

    # Create React prompt
    react_prompt = prompts_dir / "react-guide.md"
    react_prompt.write_text(
        """---
title: React Guide
description: React coding guide
tags:
  - react
  - frontend
---
React coding content here"""
    )

    return {
        "storage_dir": storage_dir,
        "prompts_dir": prompts_dir,
        "python_prompt": python_prompt,
        "js_prompt": js_prompt,
        "react_prompt": react_prompt,
    }


def test_clean_removes_files_not_matching_tag_filter(
    setup_multi_tag_storage: dict[str, Path], tmp_path: Path
) -> None:
    """
    Test that --clean with --tags removes files that don't match the filter.

    Scenario:
    1. Deploy all prompts (no filter)
    2. Deploy with --tags python --clean
    3. Only Python files should remain, others should be removed
    """
    paths = setup_multi_tag_storage
    storage_dir = paths["storage_dir"]
    base_path = tmp_path / "continue_base"

    # Setup handler
    handler = ContinueToolHandler(base_path=base_path)
    handler.validate_tool_installation()

    # First deployment: deploy all prompts (no filter)
    from prompt_unifier.cli.helpers import deploy_content_to_handler
    from prompt_unifier.core.content_parser import ContentFileParser

    parser = ContentFileParser()
    all_content_files = []
    for md_file in paths["prompts_dir"].glob("*.md"):
        parsed_content = parser.parse_file(md_file)
        all_content_files.append((parsed_content, "prompt", md_file))

    # Deploy all files first
    deploy_content_to_handler(
        handler,
        all_content_files,
        paths["prompts_dir"],
        storage_dir / "rules",
    )

    # Verify all files were deployed
    deployed_prompts_dir = base_path / ".continue" / "prompts"
    assert (deployed_prompts_dir / "python-guide.md").exists()
    assert (deployed_prompts_dir / "javascript-guide.md").exists()
    assert (deployed_prompts_dir / "react-guide.md").exists()

    # Second deployment: deploy only python tagged files with --clean
    python_files = [
        (content, ctype, fpath)
        for content, ctype, fpath in all_content_files
        if hasattr(content, "tags") and content.tags and "python" in content.tags
    ]

    _, deployed_filenames, _ = deploy_content_to_handler(
        handler,
        python_files,
        paths["prompts_dir"],
        storage_dir / "rules",
    )

    # Now clean orphaned files (files not in deployed set)
    removed_results = handler.clean_orphaned_files(deployed_filenames)

    # Check what was removed
    removed_files = [
        r.actual_file_path for r in removed_results if r.deployment_status == "deleted"
    ]

    # Assert: javascript and react guides SHOULD be removed
    assert any("javascript-guide.md" in f for f in removed_files), (
        "javascript-guide.md should be removed as it doesn't match --tags python"
    )
    assert any("react-guide.md" in f for f in removed_files), (
        "react-guide.md should be removed as it doesn't match --tags python"
    )

    # These files should be removed
    assert not (deployed_prompts_dir / "javascript-guide.md").exists(), (
        "javascript-guide.md should be removed after deploy with --tags python --clean"
    )
    assert not (deployed_prompts_dir / "react-guide.md").exists(), (
        "react-guide.md should be removed after deploy with --tags python --clean"
    )

    # Python file should still exist
    assert (deployed_prompts_dir / "python-guide.md").exists(), (
        "python-guide.md should still exist after deploy with --tags python --clean"
    )


def test_clean_should_only_remove_truly_orphaned_files(
    setup_multi_tag_storage: dict[str, Path], tmp_path: Path
) -> None:
    """
    Test that --clean correctly identifies and removes only orphaned files.

    Scenario:
    1. Deploy python prompts
    2. Manually create an orphaned file (not from storage)
    3. Run deploy with --clean
    4. Only the manually created file should be removed
    """
    paths = setup_multi_tag_storage
    storage_dir = paths["storage_dir"]
    base_path = tmp_path / "continue_base"

    handler = ContinueToolHandler(base_path=base_path)
    handler.validate_tool_installation()

    from prompt_unifier.cli.helpers import deploy_content_to_handler
    from prompt_unifier.core.content_parser import ContentFileParser

    parser = ContentFileParser()

    # Deploy only python files
    python_files = []
    for md_file in paths["prompts_dir"].glob("*.md"):
        parsed_content = parser.parse_file(md_file)
        if (
            hasattr(parsed_content, "tags")
            and parsed_content.tags
            and "python" in parsed_content.tags
        ):
            python_files.append((parsed_content, "prompt", md_file))

    _, deployed_filenames, _ = deploy_content_to_handler(
        handler,
        python_files,
        paths["prompts_dir"],
        storage_dir / "rules",
    )

    # Manually create an orphaned file (simulates a file that was deployed before
    # but no longer exists in storage)
    deployed_prompts_dir = base_path / ".continue" / "prompts"
    orphaned_file = deployed_prompts_dir / "old-deleted-prompt.md"
    orphaned_file.write_text(
        """---
title: Old Deleted Prompt
description: This prompt was deleted from storage
---
Old content"""
    )

    # Run clean
    removed_results = handler.clean_orphaned_files(deployed_filenames)

    # Check what was removed
    removed_md_files = [
        r.actual_file_path
        for r in removed_results
        if r.deployment_status == "deleted" and r.actual_file_path.endswith(".md")
    ]

    # Assert: Only the orphaned file should be removed
    assert len(removed_md_files) == 1, f"Expected 1 orphaned file, got {len(removed_md_files)}"
    assert "old-deleted-prompt.md" in removed_md_files[0], (
        "The orphaned file should be old-deleted-prompt.md"
    )

    # Python guide should still exist
    assert (deployed_prompts_dir / "python-guide.md").exists()

    # Orphaned file should be removed
    assert not orphaned_file.exists()
