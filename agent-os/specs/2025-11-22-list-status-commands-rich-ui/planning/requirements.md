# Spec Requirements: List & Status Commands with Rich UI

## Initial Description
Create list command showing all available prompts with metadata (name, description, tools, last modified), implement status command displaying deployment state per tool, add filtering/sorting options, and format output using Rich tables and syntax highlighting.

## Requirements Discussion

### First Round Questions

**Q1:** I assume the `list` command should display Name, Description, Target Tools, and Last Modified. Should we also include **Validation Status** (valid/invalid) or **Tags** in the main table view?
**Answer:** yes

**Q2:** For the `status` command, how should we determine "deployment status"?
- *Option A*: Simple existence check (is the file present in the tool's folder?).
- *Option B*: Content verification (compare hash/content of source prompt vs. deployed prompt to detect drift/outdated files).
- I recommend **Option B** for a more useful status, but it's more complex. What do you prefer?
**Answer:** Option B

**Q3:** I'm thinking of adding flags like `--tool [name]`, `--tag [tag]`, and `--sort [name|date]`. Are there other specific filters you need?
**Answer:** ok for--tool [name], --tag [tag], and --sort [name|date].

**Q4:** Should the `list` command support a `--verbose` or `--preview` flag to show the actual prompt content (syntax highlighted) directly in the terminal?
**Answer:** yes

### Existing Code to Reference

**Similar Features Identified:**
- **Rich Integration**: `src/prompt_unifier/output/rich_formatter.py` contains `RichFormatter` class with methods for headers and summary tables. `src/prompt_unifier/cli/commands.py` uses `rich.table.Table`.
- **Models**: `src/prompt_unifier/models/prompt.py` (PromptFrontmatter) contains the metadata fields (name, description, tags, etc.).
- **Deployment Logic**: `src/prompt_unifier/cli/commands.py` has `deploy` command logic. `ContinueToolHandler` in `src/prompt_unifier/handlers/continue_handler.py` has `validate_deployment` which can be adapted for the status check (Option B).

### Follow-up Questions
None needed.

## Visual Assets

### Files Provided:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- **List Command**:
    - Display a table of all available prompts/rules.
    - Columns: Name, Description, Tags, Target Tools, Last Modified, Validation Status.
    - Support filtering by `--tool` and `--tag`.
    - Support sorting by `--sort` (name, date).
    - Support `--verbose` or `--preview` to show full content with syntax highlighting.
- **Status Command**:
    - Display deployment status for each prompt across configured tools.
    - Status states: Not Deployed, Synced, Outdated (drift detected), Missing (if expected but gone).
    - Use **Content Verification** (Option B) to detect drift (compare source vs. deployed content/hash).
    - Group output by Tool or by Prompt (likely by Tool is clearer).

### Reusability Opportunities
- Reuse `RichFormatter` for consistent styling.
- Reuse `BatchValidator` for the "Validation Status" column in `list`.
- Reuse `ToolHandler` protocol and implementations (like `ContinueToolHandler`) to query deployment state.

### Scope Boundaries
**In Scope:**
- `list` command implementation.
- `status` command implementation.
- Updates to `RichFormatter` or new `RichTableFormatter`.
- Integration with existing `ToolHandler`s for status checks.

**Out of Scope:**
- Creating new Tool Handlers (only supporting existing ones).
- Editing prompts via CLI.

### Technical Considerations
- **Performance**: `status` command with Option B might be slow if there are many prompts/tools. Consider parallel checks or a progress bar.
- **Rich UI**: Use `rich.table.Table` for the main views. Use `rich.syntax.Syntax` for the preview.
