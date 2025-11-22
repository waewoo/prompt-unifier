# Specification: List & Status Commands with Rich UI

## Goal
Implement `list` and `status` commands to provide visibility into prompt management, showing available prompts with metadata and their deployment status across configured tools using a rich terminal interface.

## User Stories
- As a developer, I want to list all available prompts with their tags and modification times so that I can quickly find the prompt I need.
- As a developer, I want to check the deployment status of my prompts across all tools so that I can identify which tools have outdated or missing prompts.
- As a team lead, I want to filter prompts by tag or tool so that I can verify specific subsets of our prompt library.

## Specific Requirements

**List Command**
- Implement `list` command using `rich.table.Table` to display prompts and rules.
- Columns: Name, Type (Prompt/Rule), Tags, Target Tools, Last Modified, Validation Status.
- Support filtering: `--tool [name]` (filter by target handler), `--tag [tag]` (filter by tag).
- Support sorting: `--sort [name|date]` (default to name).
- Support `--verbose` flag to show full content preview with syntax highlighting using `rich.syntax.Syntax`.

**Status Command**
- Implement `status` command to show deployment state per tool.
- Group output by Tool (e.g., "Continue", "Cursor").
- Status states:
    - **Synced**: Deployed file matches source content.
    - **Outdated**: Deployed file exists but content differs (hash mismatch).
    - **Missing**: Source exists but not deployed.
    - **Orphaned**: Deployed file exists but no corresponding source file (optional, maybe for future cleanup).
- Use content hashing (SHA-256) for robust comparison between source and deployed files.

**ToolHandler Protocol Update**
- Extend `ToolHandler` protocol with `get_deployment_status(self, content_name, content_type, source_content) -> str` (or similar).
- Implement this method in `ContinueToolHandler` (and others if they existed).
- Ensure backward compatibility or default implementation for handlers.

**Rich UI Integration**
- Create a reusable `RichTableFormatter` (or extend `RichFormatter`) to handle table generation for both commands.
- Use consistent color coding: Green (Synced/Valid), Yellow (Outdated/Warning), Red (Missing/Invalid).

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**Rich Integration**
- `src/prompt_unifier/output/rich_formatter.py`: Reuse `RichFormatter` patterns for colors and symbols.
- `src/prompt_unifier/cli/commands.py`: Reuse `console` instance and `Table` setup from existing commands.

**Deployment Verification**
- `src/prompt_unifier/handlers/continue_handler.py`: Reuse `verify_deployment_with_details` logic, extending it for content comparison.
- `src/prompt_unifier/handlers/protocol.py`: Extend the `ToolHandler` protocol.

**Models**
- `src/prompt_unifier/models/prompt.py`: Use `PromptFrontmatter` fields (tags, tools, etc.) for list columns.

## Out of Scope
- Interactive mode (selecting prompts from list to deploy).
- Editing prompts directly from the CLI.
- Automatic synchronization/fixing from the status command (only reporting).
- Support for tools other than "Continue" (unless other handlers are added separately).
