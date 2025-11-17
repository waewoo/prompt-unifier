# Specification: Recursive File Discovery for Deploy Command

## Goal
Implement recursive file discovery for prompts and rules in the `deploy` command, preserving subdirectory structure in target handlers, and ensuring no duplicate prompt/rule titles.

## User Stories
- As a developer, I want the `deploy` command to find all my prompts and rules, even if they are organized in subdirectories, so that I can structure my prompt repository logically.
- As a developer, I want the deployed prompts and rules to maintain their subdirectory structure in the target tool, so that my organization is preserved across different AI assistants.
- As a developer, I want to be notified if I accidentally create two prompts/rules with the same title, so that I can avoid conflicts and maintain a clean prompt repository.

## Specific Requirements

**1. Recursive File Discovery in `deploy` command**
- Modify `src/prompt_unifier/cli/commands.py` to use `glob("**/*.md")` for `prompts_dir` and `rules_dir`.
- This change will enable the `deploy` command to find `.md` files in all subdirectories within `prompts/` and `rules/`.

**2. Preserve Subdirectory Structure during Deployment**
- The `deploy` method of `ToolHandler` implementations (e.g., `ContinueToolHandler`) must receive the relative path of the source file (relative to `prompts/` or `rules/`).
- The `ToolHandler.deploy` method signature in `handlers/protocol.py` needs to be updated to include a parameter for this relative path.
- `ToolHandler` implementations must use this relative path to reproduce the subdirectory structure in the target deployment location.

**3. Duplicate Title Conflict Detection**
- Before deploying to handlers, the `deploy` command must check all parsed `content_files` for duplicate `title` values in their YAML frontmatter.
- If duplicates are found, the command must exit with `typer.Exit(code=1)` and an informative error message listing the conflicting files and their titles.

**4. Consistency with other commands**
- The `validate` command already uses `FileScanner` which performs recursive discovery, so no changes are needed for its file discovery.
- `list` and `status` commands (when implemented) should also leverage recursive file discovery.

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**File Scanning Pattern**
- The `FileScanner` class (`src/prompt_unifier/utils/file_scanner.py`) already demonstrates recursive scanning using `rglob`.

**Content Parsing**
- The `ContentFileParser` (`src/prompt_unifier/core/content_parser.py`) should continue to be used for parsing individual `.md` files.

**Deployment Loop**
- The existing loop iterating through `filtered_files` and then `all_handlers` in the `deploy` command will be adapted.

## Out of Scope
- Modifying the `sync` command's logic for retrieving files from Git.
- Changing the `FileScanner`'s existing recursive behavior.
- Implementing `list` or `status` commands.
- Any GUI or web interface.
- Bidirectional sync or cross-tool prompt conversion.
