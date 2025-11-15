# Specification: Tool Handler Implementation: Continue

## Goal
The goal of this specification is to implement a `ContinueToolHandler` that allows users to deploy prompts and rules from `prompt-manager` to the "Continue" AI assistant. This handler will be responsible for converting and copying files to the appropriate directories, as well as handling backups and deployment verification.

## User Stories
- As a developer using "Continue", I want to be able to deploy my `prompt-manager` prompts and rules to "Continue" so that I can use them in my AI-assisted development workflow.
- As a tech lead, I want to be able to standardize the prompts and rules used by my team in "Continue" by managing them through `prompt-manager`.

## Specific Requirements

**`ContinueToolHandler` Implementation**
- Create a `ContinueToolHandler` class in `src/prompt_manager/handlers/continue_handler.py`.
- The class must conform to the `ToolHandler` protocol.
- The handler should be registered in the `ToolHandlerRegistry`.

**Configuration for Deployment**
- The `.prompt-manager/config.yaml` must be extended to support deployment configuration:
  - `deploy_tags`: List of strings (e.g., ["python", "review"]) to filter prompts and rules by their `tags` field in frontmatter. If empty or absent, deploy all items.
  - `target_handlers`: List of strings (e.g., ["continue", "cursor"]) specifying the handlers to deploy to. If empty or absent, deploy to all registered handlers.
- Example extended config.yaml:
  ```yaml
  repo_url: https://example.com/prompts.git
  last_sync_timestamp: "2025-11-15T10:00:00Z"
  last_sync_commit: "abc123"
  storage_path: "~/.prompt-manager/storage"
  deploy_tags: ["python", "api"]
  target_handlers: ["continue", "cursor"]
  ```
- The deploy command reads this config to determine what to deploy and where.

**Deploy Command Behavior**
- The `deploy` command automatically deploys all prompts and rules matching the `deploy_tags` from config (scanning storage/prompts/ and storage/rules/).
- If no tags specified in config, deploys all items.
- Deploys to handlers listed in `target_handlers` from config; if none, to all registered.
- CLI options can override config (e.g., --tags "override-tag" to filter differently, --handlers "override-handler").
- For each matching item, process frontmatter (map title->name, add invokable: true for prompts), backup existing files, copy to handler directories, verify deployment.

**Prompt Deployment**
- Scan storage/prompts/ for .md files matching deploy_tags (via tags field in frontmatter).
- For each matching prompt, map internal fields to Continue format: title -> name, ensure description and invokable: true.
- Copy processed .md to `~/.continue/prompts/<name>.md`.

**Rule Deployment**
- Scan storage/rules/ for .md files matching deploy_tags.
- For each matching rule, map title -> name, applies_to -> globs, set alwaysApply: false (default).
- Copy processed .md to `~/.continue/rules/<name>.md`.

**Backup Mechanism**
- Before deploying each item, back up existing file in target directory with .bak extension.

**Deployment Verification**
- For each deployed item, verify file exists in target location and frontmatter/content is correct (e.g., name, description, invokable for prompts; name, globs for rules).

**File Formats**
- **Input (prompt-manager storage):** MD with YAML frontmatter using title, description, tags, etc.
- **Output (Continue):** MD with YAML frontmatter using name (from title), description, invokable: true for prompts; name (from title), globs (from applies_to), description, alwaysApply: false for rules.


## Visual Design
No visual assets provided.

## Existing Code to Leverage

**`src/prompt_manager/git/service.py`**
- The `GitService` class provides a good example of how to structure a service class that interacts with the file system.
- The `ContinueToolHandler` can follow a similar pattern for reading, writing, and copying files.

## Out of Scope
- Implementation of the "Kilo Code" tool handler.
- Any other tool handler besides "Continue".
- UI for managing tool handlers.
