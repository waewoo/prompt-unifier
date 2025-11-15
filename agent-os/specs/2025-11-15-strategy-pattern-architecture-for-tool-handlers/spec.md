# Specification: Strategy Pattern Architecture for Tool Handlers

## 1. Introduction

This specification describes the design and implementation of an architecture based on the "Strategy" design pattern for managing "Tool Handlers" within the Prompt Manager CLI application. The main objective is to create a flexible and extensible system that allows for the addition of new AI tool handlers with minimal changes to the core application, while ensuring robust error handling and the ability to enable/disable these handlers.

## 2. Objectives

*   **Flexibility and Extensibility:** Allow for the easy addition of new tool handlers without modifying the core code.
*   **Standardization:** Define a common interface for all tool handlers.
*   **Robust Error Handling:** Implement a rollback mechanism in case of deployment failure.
*   **User Control:** Provide a mechanism to enable or disable specific tool handlers.
*   **Isolation of Logic:** Each tool handler should be responsible for its own configuration and tool-specific logic.

## 3. Product Context

Prompt Manager is a Python CLI tool designed to centralize and standardize the management of prompt templates and coding rules for various AI assistants (Continue, Cursor, Windsurf, Aider, Kilo Code). The strategy pattern architecture for tool handlers is a key step in achieving the goal of extensibility and multi-tool support, as described in the product roadmap (item 5).

## 4. Functional Requirements

### 4.1. `ToolHandler` Interface

*   Define a `ToolHandler` interface using Python's `Protocol`.
*   The `ToolHandler` interface must include at least the following methods:
    *   `deploy(prompt: Prompt) -> None`: Deploys a specific prompt to the managed tool.
    *   `get_status() -> str`: Returns the current status of the handler (e.g., "active", "inactive", "error").
    *   `get_name() -> str`: Returns the unique name of the tool handler (e.g., "continue", "cursor").

### 4.2. Tool Handler Registry

*   Implement a central registry to discover and load available tool handlers.
*   This registry will be a simple data structure (list or dictionary) that maintains a reference to all available `ToolHandler` implementations.
*   Tool handlers will be registered by their unique name.

### 4.3. Tool Handler Configuration

*   Each tool handler will be responsible for its own tool-specific configuration (e.g., the location of the `.continue/` directory for `ContinueToolHandler`).
*   The configuration logic for each handler should be isolated within its own implementation.

### 4.4. Error Handling and Rollback

*   In case of a prompt deployment failure by a tool handler, the main application must:
    *   Log the error in detail.
    *   Attempt to restore the previous state of the system (rollback) for that specific handler. The details of the rollback mechanism will be defined during the implementation of each handler.
    *   Continue the deployment process with the other tool handlers if possible.

### 4.5. Enabling/Disabling Tool Handlers

*   Implement a mechanism for users to enable or disable specific tool handlers.
*   This configuration will be managed via the existing `ConfigManager` and stored in the application's configuration file (`.prompt-manager/config.yaml`).
*   The application will only attempt to deploy prompts to active tool handlers.

## 5. Architecture and Design

### 5.1. "Strategy" Design Pattern

*   The "Strategy" design pattern will be used to allow the application to dynamically choose the algorithm (the tool handler) to use for deploying a prompt.
*   The `ToolHandler` interface (defined via `Protocol`) will be the common "Strategy".
*   Each concrete implementation of `ToolHandler` (e.g., `ContinueToolHandler`, `CursorToolHandler`) will be a "Concrete Strategy".
*   The main application will act as the "Context", using the registry to select and execute the appropriate strategies.

### 5.2. File Structure

*   `ToolHandler` implementations will be placed in the `src/prompt_manager/handlers/` directory.
*   A `src/prompt_manager/handlers/__init__.py` file will be used for handler registration and export.
*   The `ConfigManager` (in `src/prompt_manager/config/manager.py`) will be updated to manage the enable/disable configuration of the handlers.

### 5.3. Reuse of Existing Code

*   **`src/prompt_manager/git/service.py`**: Will serve as a model for the structure of service classes interacting with external systems.
*   **`src/prompt_manager/config/manager.py`**: Will be extended to manage the configuration of tool handlers (enabled/disabled list).
*   **`src/prompt_manager/handlers/`**: Dedicated directory for new `ToolHandler` implementations.

## 6. Technical Considerations

*   **Strict Typing:** Extensive use of Python type hints and `mypy` in strict mode to ensure code robustness and maintainability.
*   **Testing:** A comprehensive test suite (`pytest`) will be developed for each `ToolHandler` and for the registry/selection mechanism.
*   **Documentation:** Each `ToolHandler` and the overall architecture will be clearly documented.

## 7. Out of Scope

*   The full implementation of all specific tool handlers (Continue, Kilo Code, Windsurf, Cursor, Aider) is not included in this specification. These implementations will be the subject of subsequent specifications and developments.
*   The management of the prompts themselves (creation, modification, validation) remains the responsibility of the existing modules.

## 8. Verification

The verification of this feature will include:

*   Unit tests for each `ToolHandler` implementation.
*   Integration tests for the handler registry and the enable/disable mechanism.
*   End-to-end tests to ensure that deployment with different handlers works as expected, including error and rollback scenarios.
*   Verification that adding a new tool handler does not require changes to the core application code.