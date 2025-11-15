from typing import Protocol, runtime_checkable

from prompt_manager.models.prompt import PromptFrontmatter


@runtime_checkable
class ToolHandler(Protocol):
    """
    Protocol for defining a ToolHandler.

    Any class implementing this protocol must provide the specified methods.
    """

    def deploy(self, prompt: PromptFrontmatter) -> None:
        """
        Deploys a given prompt to the specific AI tool.

        Args:
            prompt: The PromptFrontmatter object to deploy.
        """
        ...

    def get_status(self) -> str:
        """
        Returns the current status of the tool handler.

        Returns:
            A string representing the status (e.g., "active", "inactive", "error").
        """
        ...

    def get_name(self) -> str:
        """
        Returns the unique name of the tool handler.

        Returns:
            A string representing the name (e.g., "continue", "cursor").
        """
        ...
