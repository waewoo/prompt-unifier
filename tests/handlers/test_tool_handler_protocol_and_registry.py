import pytest

from prompt_manager.handlers.protocol import ToolHandler
from prompt_manager.handlers.registry import ToolHandlerRegistry
from prompt_manager.models.prompt import PromptFrontmatter


# Implement a dummy Prompt for testing
class DummyPrompt(PromptFrontmatter):
    title: str = "Test Prompt"
    description: str = "A dummy prompt for testing"
    version: str = "1.0.0"
    tags: list[str] = ["test"]


# Implement a mock ToolHandler for testing
class MockToolHandler:
    def __init__(self, name: str, status: str = "active"):
        self._name = name
        self._status = status
        self.deployed_prompts = []

    def deploy(self, prompt: PromptFrontmatter) -> None:
        self.deployed_prompts.append(prompt)

    def get_status(self) -> str:
        return self._status

    def get_name(self) -> str:
        return self._name


# Test cases for ToolHandler Protocol
def test_tool_handler_protocol_enforces_methods():
    """Test that the ToolHandler protocol enforces the required methods."""
    mock_handler = MockToolHandler("mock_tool")
    assert isinstance(mock_handler, ToolHandler)

    # Test missing deploy method
    class MissingDeploy:
        def get_status(self) -> str:
            return "active"

        def get_name(self) -> str:
            return "missing_deploy"

    assert not isinstance(MissingDeploy(), ToolHandler)

    # Test missing get_status method
    class MissingGetStatus:
        def deploy(self, prompt: PromptFrontmatter) -> None:
            pass

        def get_name(self) -> str:
            return "missing_get_status"

    assert not isinstance(MissingGetStatus(), ToolHandler)

    # Test missing get_name method
    class MissingGetName:
        def deploy(self, prompt: PromptFrontmatter) -> None:
            pass

        def get_status(self) -> str:
            return "active"

    assert not isinstance(MissingGetName(), ToolHandler)


# Test cases for ToolHandlerRegistry
def test_registry_can_register_and_retrieve_handlers():
    """Test that the registry can register and retrieve handlers."""
    registry = ToolHandlerRegistry()
    mock_handler_1 = MockToolHandler("tool_1")
    mock_handler_2 = MockToolHandler("tool_2")

    registry.register(mock_handler_1)
    registry.register(mock_handler_2)

    retrieved_handler_1 = registry.get_handler("tool_1")
    retrieved_handler_2 = registry.get_handler("tool_2")

    assert retrieved_handler_1 is mock_handler_1
    assert retrieved_handler_2 is mock_handler_2


def test_registry_raises_error_for_non_existent_handler():
    """Test that the registry raises an error for a non-existent handler."""
    registry = ToolHandlerRegistry()
    with pytest.raises(ValueError, match="ToolHandler with name 'non_existent' not found."):
        registry.get_handler("non_existent")


def test_registry_lists_all_registered_handlers():
    """Test that the registry lists all registered handlers."""
    registry = ToolHandlerRegistry()
    mock_handler_1 = MockToolHandler("tool_A")
    mock_handler_2 = MockToolHandler("tool_B")

    registry.register(mock_handler_1)
    registry.register(mock_handler_2)

    assert sorted(registry.list_handlers()) == sorted(["tool_A", "tool_B"])


def test_registry_rejects_non_protocol_conforming_objects():
    """Test that the registry rejects objects not conforming to the protocol."""
    registry = ToolHandlerRegistry()

    class NonConforming:
        # Missing deploy method to not conform to the protocol
        def get_status(self) -> str:
            return "active"

        def get_name(self) -> str:
            return "non_conforming"

    # The registry's register method should raise TypeError for non-conforming objects
    with pytest.raises(
        TypeError, match="Only instances conforming to ToolHandler protocol can be registered."
    ):
        registry.register(NonConforming())


def test_registry_raises_error_for_duplicate_handler_name():
    """Test that the registry raises an error when registering a handler with a duplicate name."""
    registry = ToolHandlerRegistry()
    mock_handler_1 = MockToolHandler("duplicate_name")
    mock_handler_2 = MockToolHandler("duplicate_name")

    registry.register(mock_handler_1)
    with pytest.raises(
        ValueError, match="ToolHandler with name 'duplicate_name' is already registered."
    ):
        registry.register(mock_handler_2)


def test_registry_get_all_handlers():
    """Test that the registry returns all registered handler instances."""
    registry = ToolHandlerRegistry()
    mock_handler_1 = MockToolHandler("handler_1")
    mock_handler_2 = MockToolHandler("handler_2")

    registry.register(mock_handler_1)
    registry.register(mock_handler_2)

    all_handlers = registry.get_all_handlers()
    assert len(all_handlers) == 2
    assert mock_handler_1 in all_handlers
    assert mock_handler_2 in all_handlers
