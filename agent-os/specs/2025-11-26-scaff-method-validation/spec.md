# Specification: SCAFF Method Validation

## Goal
Add SCAFF methodology validation to the existing validation system to assess prompt quality based on five components (Specific, Contextual, Actionable, Formatted, Focused) with equal weighting, actionable suggestions, and Rich terminal output. SCAFF validation runs by default with an opt-out flag.

## User Stories
- As a prompt author, I want to validate my prompts against SCAFF methodology so that I can ensure they follow best practices for clarity and effectiveness
- As a developer, I want SCAFF validation enabled by default but with an option to disable it so that I can choose when to apply quality checks

## Specific Requirements

**SCAFF Component Analysis**
- Analyze each prompt against five distinct SCAFF components: Specific, Contextual, Actionable, Formatted, Focused
- Use simple text-based heuristics for analysis (no AI/ML dependencies)
- Each component receives a binary or weighted score (0-20 points per component)
- Total compliance score aggregates to 100% (20% weight per component)
- Generate component-specific ValidationIssue objects for failed checks
- Use ValidationSeverity.WARNING for SCAFF compliance issues (not deployment-blocking)

**Scoring and Weighting**
- Equal weighting: 20 points per SCAFF component (Specific=20, Contextual=20, Actionable=20, Formatted=20, Focused=20)
- Aggregate score calculation: sum of all component scores (0-100)
- Pass/fail thresholds can be hard-coded (e.g., <60 = poor, 60-79 = good, 80+ = excellent)
- Include score breakdown per component in ValidationResult
- Store overall SCAFF score as metadata in ValidationResult

**Actionable Suggestions**
- Each failed or weak SCAFF component must generate a specific, actionable suggestion
- Examples: "Add more context about the target audience" (Contextual), "Include specific acceptance criteria" (Actionable), "Break content into clear sections" (Formatted)
- Suggestions should be stored in ValidationIssue.suggestion field
- Hard-code suggestion templates based on which component failed
- Make suggestions concise (1-2 sentences maximum)

**CLI Integration**
- SCAFF validation enabled by default when running `prompt-unifier validate`
- Add `--no-scaff` flag to disable SCAFF validation
- Follow existing flag patterns from `src/prompt_unifier/cli/commands.py` (use typer.Option)
- SCAFF validation runs alongside existing format validation (not replacement)
- Support `--type` flag filtering (prompts, rules, all) with SCAFF validation
- Maintain backward compatibility with existing validation output

**Rich Terminal Output**
- Use RichFormatter patterns for colored terminal output
- Display SCAFF score prominently (e.g., "SCAFF Score: 75/100" with color based on threshold)
- Use WARNING_COLOR (yellow) for SCAFF compliance issues
- Include ⚠ symbol for SCAFF warnings
- Display component breakdown in formatted table (Component | Score | Status)
- Follow existing format_summary structure from RichFormatter
- Add SCAFF section after standard validation results

**SCAFF Criteria (Hard-Coded)**
- Specific: Check for concrete requirements, measurable goals, clear scope (keywords: "must", "should", specific metrics)
- Contextual: Check for background information, user context, problem statement (sections explaining "why" or "background")
- Actionable: Check for verbs, tasks, steps, or instructions (action verbs like "create", "implement", "test")
- Formatted: Check for structure, sections, headings, lists (markdown headings, bullet points, numbered lists)
- Focused: Check for length constraints, single topic focus, no scope creep (content length, topic coherence)
- Store criteria as constants or configuration in SCAFF validator module

**Validation Engine Integration**
- Create new SCARFFValidator class following PromptValidator pattern from `src/prompt_unifier/core/validator.py`
- SCARFFValidator should integrate with BatchValidator workflow
- Use existing ValidationResult model but extend with SCAFF-specific metadata
- Add new WarningCode enum values for SCAFF components (e.g., SCAFF_NOT_SPECIFIC, SCAFF_LACKS_CONTEXT)
- Return ValidationIssue objects compatible with existing RichFormatter display logic

**Extensibility for Future Methods**
- Design SCARFFValidator as one implementation of a validation method interface
- Use strategy pattern or registry to allow selection of validation methods
- Architecture should support adding other methods (e.g., CRISP, STAR) in future
- Current implementation only includes SCAFF (no other methods built yet)
- CLI flag structure should support future `--method <name>` option

**Semantic Validation (Future)**
- Requirements mention semantic validation integration (enabled by default, can be disabled)
- For this spec, acknowledge semantic validation as out of scope but design with integration point
- Add placeholder for `--no-semantic` flag in CLI
- Future semantic validation would complement SCAFF validation (both can run together)

**Testing Requirements**
- Write 2-8 focused tests for SCARFFValidator core logic
- Test each SCAFF component's scoring independently
- Test score aggregation and threshold classification
- Test CLI flag parsing (`--no-scaff`, `--type`)
- Test Rich output formatting for SCAFF results
- Run only SCAFFF-specific tests during development (not full suite)

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**ValidationResult and ValidationSummary Models (`src/prompt_unifier/models/validation.py`)**
- Extend ValidationResult to include SCAFFF score metadata (add optional scaff_score field)
- Use ValidationIssue model for SCAFFF component failures
- Use ValidationSeverity.WARNING for SCAFFF compliance issues
- Add new WarningCode enum values: SCAFF_NOT_SPECIFIC, SCAFF_LACKS_CONTEXT, SCAFF_NOT_ACTIONABLE, SCAFF_POORLY_FORMATTED, SCAFF_UNFOCUSED
- Follow Pydantic model patterns for validation and serialization

**BatchValidator (`src/prompt_unifier/core/batch_validator.py`)**
- Follow validation orchestration pattern: scan files → validate each → aggregate results
- Integrate SCARFFValidator into batch validation workflow
- Maintain separation of concerns (format validation vs. SCAFF validation)
- Use same ValidationSummary aggregation for SCAFFF results
- Ensure SCAFFF validation runs after format validation

**RichFormatter (`src/prompt_unifier/output/rich_formatter.py`)**
- Reuse ERROR_COLOR, WARNING_COLOR, SUCCESS_COLOR constants
- Follow _display_issue method pattern for SCAFFF warnings
- Add new _display_scafff_score method for score breakdown
- Use Console.print with Rich markup for colored output
- Integrate SCAFFF section into format_summary method
- Use symbols: ⚠ for warnings, ✓ for passed components

**CLI Commands (`src/prompt_unifier/cli/commands.py`)**
- Follow typer.Option pattern for `--no-scaff` flag
- Add flag to validate function signature: scaff: bool = typer.Option(True, "--scaff/--no-scaff")
- Follow existing boolean flag patterns (e.g., `--json`, `--clean`)
- Pass SCAFFF flag to BatchValidator or SCARFFValidator
- Maintain consistency with other CLI options

**Typer CLI Patterns (`src/prompt_unifier/cli/main.py`)**
- Follow command registration pattern for any new CLI commands
- Use Rich Console for formatted output
- Follow logging patterns with logger.info, logger.debug
- Maintain error handling with typer.Exit(code=1)

## Out of Scope
- AI/ML-powered content analysis or scoring (use simple text heuristics only)
- Automatic prompt rewriting or improvement suggestions beyond basic text feedback
- Multi-language validation support (English only)
- External configuration files for SCAFF criteria (hard-coded only)
- Real-time validation during prompt editing
- Integration with external quality assessment APIs or services
- Historical compliance tracking or analytics dashboard
- Semantic validation implementation (acknowledged as future work)
- Other validation methods beyond SCAFF (architecture supports, but not built)
- Advanced NLP analysis requiring external libraries
