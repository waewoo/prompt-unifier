from prompt_unifier.handlers.protocol import ToolHandler


class ToolHandlerRegistry:
    """
    A central registry for discovering and managing ToolHandler implementations.

    This registry allows for registering ToolHandler instances and retrieving them
    by their unique name.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, handler: ToolHandler) -> None:
        """
        Registers a ToolHandler instance with the registry.

        Args:
            handler: An instance of a class conforming to the ToolHandler protocol.

        Raises:
            TypeError: If the provided object does not conform to the ToolHandler protocol.
            ValueError: If a handler with the same name is already registered.
        """
        if not isinstance(handler, ToolHandler):
            raise TypeError("Only instances conforming to ToolHandler protocol can be registered.")
        if handler.get_name() in self._handlers:
            raise ValueError(f"ToolHandler with name '{handler.get_name()}' is already registered.")
        self._handlers[handler.get_name()] = handler

    def get_handler(self, name: str) -> ToolHandler:
        """
        Retrieves a registered ToolHandler by its name.

        Args:
            name: The unique name of the ToolHandler.

        Returns:
            The registered ToolHandler instance.

        Raises:
            ValueError: If no ToolHandler with the given name is found.
        """
        if name not in self._handlers:
            raise ValueError(f"ToolHandler with name '{name}' not found.")
        return self._handlers[name]

    def list_handlers(self) -> list[str]:
        """
        Lists the names of all registered ToolHandlers.

        Returns:
            A list of strings, where each string is the name of a registered handler.
        """
        return list(self._handlers.keys())

    def get_all_handlers(self) -> list[ToolHandler]:
        """
        Returns all registered ToolHandler instances.

        Returns:
            A list of ToolHandler instances.
        """
        return list(self._handlers.values())
