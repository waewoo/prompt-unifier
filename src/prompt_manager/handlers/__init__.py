"""ToolHandler implementations following Strategy Pattern."""

from prompt_manager.handlers.continue_handler import ContinueToolHandler
from prompt_manager.handlers.protocol import ToolHandler
from prompt_manager.handlers.registry import ToolHandlerRegistry

__all__ = ["ToolHandler", "ToolHandlerRegistry", "ContinueToolHandler"]
