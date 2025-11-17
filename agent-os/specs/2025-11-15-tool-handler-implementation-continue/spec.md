# Specification: Tool Handler Implementation: Continue

## Goal
The goal of this specification is to implement a `ContinueToolHandler` that allows users to deploy prompts and rules from `prompt-unifier` to the "Continue" AI assistant. This handler will be responsible for converting and copying files to the appropriate directories, as well as handling backups and deployment verification.

## User Stories
- As a developer using "Continue", I want to be able to deploy my `prompt-unifier` prompts and rules to "Continue" so that I can use them in my AI-assisted development workflow.
- As a tech lead, I want to be able to standardize the prompts and rules used by my team in "Continue" by managing them through `prompt-unifier`.

## Specific Requirements

**`ContinueToolHandler` Implementation**
- Create a `ContinueToolHandler` class in `src/prompt_unifier/handlers/continue_handler.py`.
- The class must conform to the `ToolHandler` protocol.
- The handler should be registered in the `ToolHandlerRegistry`.

**Configuration for Deployment**
- The `.prompt-unifier/config.yaml` must be extended to support deployment configuration:
  - `deploy_tags`: List of strings (e.g., ["python", "review"]) to filter prompts and rules by their `tags` field in frontmatter. If empty or absent, deploy all items.
  - `target_handlers`: List of strings (e.g., ["continue", "cursor"]) specifying the handlers to deploy to. If empty or absent, deploy to all registered handlers.
- Example extended config.yaml:
  ```yaml
  repo_url: https://example.com/prompts.git
  last_sync_timestamp: "2025-11-15T10:00:00Z"
  last_sync_commit: "abc123"
  storage_path: "~/.prompt-unifier/storage"
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
- Copy processed .md to `~/.continue/prompts/<original-filename>.md`, preserving the original filename from the source repository.
- **Filename Preservation:** The original filename is preserved during deployment (e.g., `Python Code Refactoring Expert.md` remains as `Python Code Refactoring Expert.md` in the destination, not converted to `Python-Code-Refactoring-Expert.md` or using the title field).

**Rule Deployment**
- Scan storage/rules/ for .md files matching deploy_tags.
- For each matching rule, map title -> name, applies_to -> globs, set alwaysApply: false (default).
- Copy processed .md to `~/.continue/rules/<original-filename>.md`, preserving the original filename from the source repository.
- **Filename Preservation:** Same as prompts - original filenames are preserved (e.g., `backend-python-packages.md` stays as `backend-python-packages.md`).

**Backup Mechanism**
- Before deploying each item, back up existing file in target directory with .bak extension.

**Deployment Verification**
- For each deployed item, verify file exists in target location and frontmatter/content is correct (e.g., name, description, invokable for prompts; name, globs for rules).

**File Formats**
- **Input (prompt-unifier storage):** MD with YAML frontmatter using title, description, tags, etc. Filenames can contain spaces and special characters (e.g., `Python Code Refactoring Expert.md`, `backend-python-packages.md`).
- **Output (Continue):** MD with YAML frontmatter using name (from title), description, invokable: true for prompts; name (from title), globs (from applies_to), description, alwaysApply: false for rules. **Filenames are preserved from source** to maintain consistency and readability.


## Visual Design
No visual assets provided.

## Existing Code to Leverage

**`src/prompt_unifier/git/service.py`**
- The `GitService` class provides a good example of how to structure a service class that interacts with the file system.
- The `ContinueToolHandler` can follow a similar pattern for reading, writing, and copying files.

**Orphaned Files Cleanup (--clean Option)**
- The `deploy` command supports a `--clean` flag to remove orphaned files.
- When `--clean` is used:
  - After deploying all matching prompts/rules, the handler scans destination directories (e.g., `~/.continue/prompts/` and `~/.continue/rules/`)
  - Files in the destination that were NOT just deployed (orphaned files) are permanently removed
  - Any existing `.bak` backup files are also removed during cleanup
  - This ensures the destination only contains files from the current source repository
- Example: `prompt-unifier deploy --clean`
- The number of cleaned files is reported in the deployment summary
- **Note:** Files are deleted permanently without creating backups - use with caution

**YAML Frontmatter Formatting**
- Generated YAML frontmatter must not contain extra blank lines before the closing `---` delimiter
- Implementation uses `.rstrip()` on `yaml.safe_dump()` output to remove trailing newlines
- This ensures clean, consistent YAML formatting in deployed files

## Out of Scope
- Implementation of the "Kilo Code" tool handler.
- Any other tool handler besides "Continue".
- UI for managing tool handlers.
