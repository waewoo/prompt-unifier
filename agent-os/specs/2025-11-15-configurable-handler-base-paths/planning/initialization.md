# Feature Initialization: Configurable Handler Base Paths

## Feature Name
Configurable Handler Base Paths

## Feature Description
Add support for customizing tool handler base paths via config.yaml and CLI options. Allow users to specify custom deployment locations for each handler (e.g., deploy Continue to custom path instead of default ~/.continue/).

## Key Requirements

1. Support configuration via config.yaml with per-handler base paths (e.g., handlers.continue.base_path)
2. Support CLI override option (e.g., --continue-base-path flag) for one-time deployments
3. Maintain backward compatibility with default paths (Path.home())
4. Apply pattern consistently across all handlers (Continue, and future: Cursor, Windsurf, Aider)

## Current Limitation

The ContinueToolHandler currently has a base_path parameter in its __init__ method, but it's never utilized. The handler is always instantiated with default Path.home() in commands.py line 628: `registry.register(ContinueToolHandler())`

## Context

This is for the prompt-manager project which manages AI prompts/rules deployment to various AI coding assistants. The Continue handler is already implemented and working, but lacks the ability to customize deployment location.

## Product Context

This feature aligns with the product's mission to provide flexible, developer-centric prompt management across multiple AI coding assistants. It addresses the need for developers who may have non-standard installation paths for their AI tools (e.g., containerized environments, custom configurations, or multi-user systems).

This feature is currently item #7 on the product roadmap, positioned after the core tool handler implementation (Continue) and before completing multi-tool support. It establishes a configuration pattern that will be reused for all future tool handlers (Windsurf, Cursor, Aider).

## Technical Context

- Python 3.12+ with type hints and Protocol-based architecture
- Pydantic models for configuration validation
- Typer CLI framework for command-line interface
- PathLib for cross-platform path handling
- Strategy Pattern implementation for tool handlers
- Config management via YAML files

## Initialization Date
2025-11-15
