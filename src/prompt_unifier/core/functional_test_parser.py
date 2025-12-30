"""Functional test YAML parser for parsing .test.yaml files.

This module provides parsing functionality for functional test files
that contain test scenarios and assertions for AI prompt validation.
"""

import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from prompt_unifier.models.functional_test import FunctionalTestFile

logger = logging.getLogger(__name__)


class FunctionalTestParser:
    """Parser for functional test YAML files.

    This parser:
    - Loads .test.yaml files using safe_load
    - Validates structure against FunctionalTestFile model
    - Returns None gracefully for missing or invalid files

    Examples:
        >>> from pathlib import Path
        >>> parser = FunctionalTestParser(Path("test.md.test.yaml"))
        >>> result = parser.parse()
        >>> if result:
        ...     print(len(result.scenarios))
        1
    """

    def __init__(self, file_path: Path):
        """Initialize parser with file path.

        Args:
            file_path: Path to the .test.yaml file
        """
        self.file_path = file_path

    @staticmethod
    def get_test_file_path(source_file: Path) -> Path:
        """Get the test file path for a source file.

        Follows the naming convention: <source_file>.test.yaml

        Args:
            source_file: Path to the source file (e.g., refactor.md)

        Returns:
            Path to the corresponding test file (e.g., refactor.md.test.yaml)

        Examples:
            >>> source = Path("prompts/refactor.md")
            >>> FunctionalTestParser.get_test_file_path(source)
            PosixPath('prompts/refactor.md.test.yaml')
        """
        return source_file.with_suffix(source_file.suffix + ".test.yaml")

    def parse(self) -> FunctionalTestFile | None:
        """Parse the functional test YAML file.

        Returns:
            FunctionalTestFile object on success, None on failure

        Examples:
            >>> parser = FunctionalTestParser(Path("test.yaml"))
            >>> result = parser.parse()
        """
        # Check if file exists
        if not self.file_path.exists():
            logger.debug(f"Functional test file not found: {self.file_path}")
            return None

        try:
            # Read and parse YAML
            yaml_content = self.file_path.read_text(encoding="utf-8")
            parsed_data = yaml.safe_load(yaml_content)

            if parsed_data is None:
                logger.warning(
                    f"Functional test file is empty or contains only comments: {self.file_path}"
                )
                return None

            # Validate against FunctionalTestFile model
            test_file = FunctionalTestFile(**parsed_data)
            logger.debug(
                f"Successfully parsed functional test file: {self.file_path} "
                f"({len(test_file.scenarios)} scenarios)"
            )
            return test_file

        except yaml.YAMLError as e:
            logger.warning(
                f"Invalid YAML syntax in functional test file {self.file_path}: {e}. "
                "Skipping functional tests."
            )
            return None

        except ValidationError as e:
            logger.warning(
                f"Validation error in functional test file {self.file_path}: {e}. "
                "Skipping functional tests."
            )
            return None

        except Exception as e:
            logger.warning(
                f"Unexpected error parsing functional test file {self.file_path}: {e}. "
                "Skipping functional tests."
            )
            return None
