"""Git operations service for repository cloning and prompt extraction.

This module provides the GitService class for managing Git operations including
cloning repositories, extracting prompts, retrieving commit information, and
checking for remote updates using GitPython library.
"""

import shutil
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

import git

T = TypeVar("T")


def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> T:
    """Retry a function with exponential backoff.

    This helper function implements retry logic with exponential backoff
    for network operations. It retries the function up to max_attempts times,
    with increasing delays between attempts.

    Args:
        func: The function to retry
        max_attempts: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for delay between retries (default: 2.0)

    Returns:
        The return value from the successful function call

    Raises:
        The last exception raised if all retry attempts fail

    Examples:
        >>> def fetch_data():
        ...     return "data"
        >>> result = retry_with_backoff(fetch_data, max_attempts=3)
        >>> result
        'data'
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_attempts:
                print(f"Network error. Retrying... (attempt {attempt}/{max_attempts})")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                # Last attempt failed, re-raise exception
                raise last_exception from None

    # This should never be reached, but satisfies type checker
    raise last_exception  # type: ignore[misc]


class GitService:
    """Service for Git repository operations.

    This class provides methods for cloning repositories, extracting prompts,
    retrieving commit information, and checking for remote updates. It uses
    GitPython library for Git operations and implements retry logic with
    exponential backoff for network operations.

    Examples:
        >>> service = GitService()
        >>> repo_path, repo = service.clone_to_temp("https://github.com/example/prompts.git")
        >>> commit = service.get_latest_commit(repo)
        >>> len(commit)
        7
    """

    def clone_to_temp(self, repo_url: str) -> tuple[Path, git.Repo]:
        """Clone repository to temporary directory with retry logic.

        This method clones a Git repository to a temporary directory using
        tempfile.TemporaryDirectory() context manager. It implements retry
        logic with exponential backoff for network resilience.

        Args:
            repo_url: URL of the Git repository to clone

        Returns:
            Tuple containing:
            - Path to the temporary directory containing cloned repo
            - git.Repo object for the cloned repository

        Raises:
            ValueError: If clone fails after retry attempts with clear error message

        Examples:
            >>> service = GitService()
            >>> repo_path, repo = service.clone_to_temp("https://github.com/example/prompts.git")
            >>> repo_path.exists()
            True
        """
        # Create temporary directory for clone
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir = Path(temp_dir_obj.__enter__())

        try:

            def clone_operation() -> git.Repo:
                """Inner function for retry logic."""
                try:
                    return git.Repo.clone_from(repo_url, temp_dir)
                except git.exc.GitCommandError as e:
                    # Re-raise as network error for retry logic
                    raise ConnectionError(f"Git clone failed: {e}") from e

            # Clone with retry logic
            repo = retry_with_backoff(clone_operation, max_attempts=3)

            return temp_dir, repo

        except (git.exc.GitCommandError, ConnectionError) as e:
            # Clean up temp directory on failure
            temp_dir_obj.__exit__(None, None, None)

            # Provide clear error message
            error_msg = str(e).lower()
            if "authentication" in error_msg or "authentication failed" in error_msg:
                raise ValueError(
                    "Failed to clone repository: Authentication failed. "
                    "Ensure Git credentials are configured."
                ) from e
            raise ValueError(
                f"Failed to clone repository: {repo_url}. " "Check URL and network connection."
            ) from e

    def get_latest_commit(self, repo: git.Repo) -> str:
        """Get latest commit hash from repository in short SHA format.

        Args:
            repo: git.Repo object to get commit from

        Returns:
            Short commit hash (7 characters)

        Examples:
            >>> service = GitService()
            >>> # Assuming repo is a valid git.Repo object
            >>> commit = service.get_latest_commit(repo)
            >>> len(commit)
            7
        """
        # Get full commit hash and return first 7 characters (short SHA)
        full_sha: str = repo.head.commit.hexsha
        return full_sha[:7]

    def extract_prompts_dir(self, repo_path: Path, target_path: Path) -> None:
        """Extract prompts/ directory from cloned repo to target location.

        This method validates that the prompts/ directory exists in the
        cloned repository, then copies it to the target location using
        shutil.copytree with dirs_exist_ok=True to overwrite existing files.

        Args:
            repo_path: Path to the cloned repository
            target_path: Path where prompts/ should be copied to

        Raises:
            ValueError: If prompts/ directory not found in repository

        Examples:
            >>> service = GitService()
            >>> service.extract_prompts_dir(Path("/tmp/repo"), Path("/app"))
        """
        # Validate that prompts/ directory exists in repository
        source_prompts = repo_path / "prompts"

        if not source_prompts.exists() or not source_prompts.is_dir():
            raise ValueError(
                f"Repository does not contain a prompts/ directory. "
                f"Expected at: {source_prompts}"
            )

        # Copy prompts/ directory to target location
        target_prompts = target_path / "prompts"

        # Use shutil.copytree with dirs_exist_ok=True to overwrite existing files
        shutil.copytree(source_prompts, target_prompts, dirs_exist_ok=True)

    def check_remote_updates(self, repo_url: str, last_commit: str) -> tuple[bool, int]:
        """Check if remote repository has updates since last commit.

        This method clones the repository to a temporary location, fetches
        remote updates, and compares the remote HEAD with the last synced
        commit to determine if updates are available.

        Args:
            repo_url: URL of the Git repository
            last_commit: Last synced commit hash (short or full SHA)

        Returns:
            Tuple containing:
            - has_updates: True if new commits are available, False otherwise
            - commits_behind: Number of commits behind remote

        Examples:
            >>> service = GitService()
            >>> has_updates, count = service.check_remote_updates(
            ...     "https://github.com/example/prompts.git",
            ...     "abc1234"
            ... )
            >>> has_updates
            True
            >>> count
            3
        """
        # Clone repository to temporary directory
        repo_path, repo = self.clone_to_temp(repo_url)

        try:
            # Fetch remote updates
            origin = repo.remote(name="origin")

            def fetch_operation() -> None:
                """Inner function for retry logic."""
                try:
                    origin.fetch()
                except git.exc.GitCommandError as e:
                    raise ConnectionError(f"Git fetch failed: {e}") from e

            # Fetch with retry logic
            retry_with_backoff(fetch_operation, max_attempts=3)

            # Get default branch name (usually 'main' or 'master')
            # Use origin/HEAD to get the default branch
            try:
                default_branch = repo.active_branch.name
            except Exception:
                # Fallback to 'main' if unable to determine
                default_branch = "main"

            # Check commits between last_commit and remote HEAD
            try:
                # Build commit range: last_commit..origin/default_branch
                commit_range = f"{last_commit}..origin/{default_branch}"
                commits = list(repo.iter_commits(commit_range))
                commits_behind = len(commits)
                has_updates = commits_behind > 0
            except git.exc.GitCommandError:
                # If commit range fails, assume updates available
                # (e.g., last_commit might not exist in remote)
                has_updates = True
                commits_behind = 1

            return has_updates, commits_behind

        finally:
            # Note: In actual usage, the TemporaryDirectory context manager
            # from clone_to_temp will handle cleanup automatically
            pass
