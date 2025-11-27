# Spec Requirements: SCAFF Method Validation

## Initial Description
SCAFF Method Validation — Implement validation to ensure prompts follow the SCAFF methodology (Specific, Contextual, Actionable, Formatted, Focused). Add SCAFF compliance checker that analyzes prompt structure and content, detects missing SCAFF components, provides suggestions for improvement, and reports SCAFF compliance score. Support --scaff flag in validate command to enable SCAFF-specific validation. Integrate with semantic validation to provide comprehensive prompt quality assessment.

## Requirements Discussion

### First Round Questions

**Q1:** I assume the SCAFF validation should analyze content as distinct sections (Specific, Contextual, Actionable, Formatted, Focused) with weighted scoring for each component. Is that correct, or should it evaluate them holistically?
**Answer:** Décomposition des sections distinctes. Pour l'aspect sémantique pourquoi pas, mais je ne peux pas utiliser d'IA... cela doit rester simple.

**Q2:** For the compliance score, I'm thinking equal weighting (20% per SCAFF component) for a total score out of 100. Should we use this balanced approach or prioritize certain components?
**Answer:** Poids égal (20% par composant)

**Q3:** Should the validator provide specific, actionable suggestions for improving each SCAFF component (e.g., "Add more context about the target audience" for Contextual)?
**Answer:** Oui, actionables et spécifiques

**Q4:** I assume the --scaff flag should enable SCAFF validation by default when running `validate` command. Should there also be an option to disable it, or a way to specify other validation methods in the future?
**Answer:** La validation doit intégrer SCAFF par défaut, mais il faut une option pour le désactiver. Éventuellement aussi choisir une autre méthode que SCAFF (pas prévu pour l'instant mais un jour peut-être)

**Q5:** For the output format, should we use Rich formatting similar to the existing validation output (with colors, symbols like ✓/✗, and formatted tables)?
**Answer:** Oui, Rich formatting avec feedback coloré

**Q6:** Regarding semantic validation integration, should this be a separate flag (--semantic) that works alongside --scaff, or should they always be integrated together?
**Answer:** Activé par défaut mais désactivable

**Q7:** Should the SCAFF criteria be configurable through a config file, or should they be hard-coded based on best practices?
**Answer:** Codés en dur basés sur les best practices

**Q8:** What specific features should be excluded from this implementation? For example: AI-powered content analysis, automatic prompt rewriting, multi-language validation?
**Answer:** Exclure les 3 proposés (analyse AI/ML, réécriture automatique de prompts, validation multi-langue)

### Existing Code to Reference
User requested investigation of existing code patterns in the codebase.

**Similar Features Identified:**
- Validation Models: `src/prompt_unifier/models/validation.py` - Contains ValidationResult, ValidationSummary, ValidationIssue, ValidationSeverity, ErrorCode, and WarningCode enums
- Batch Validator: `src/prompt_unifier/core/batch_validator.py` - Contains BatchValidator class with validate_directory method
- Rich Formatter: `src/prompt_unifier/output/rich_formatter.py` - Contains RichFormatter class with color constants (ERROR_COLOR, WARNING_COLOR, SUCCESS_COLOR), symbols (PASSED_SYMBOL, FAILED_SYMBOL), and formatting methods
- CLI Commands: `src/prompt_unifier/cli/commands.py` - Contains validate command with typer.Option patterns for flags
- CLI Main: `src/prompt_unifier/cli/main.py` - Shows Typer app structure and command registration pattern

### Follow-up Questions
No follow-up questions needed.

## Visual Assets

### Files Provided:
No visual files found.

### Visual Insights:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- Analyze prompts against SCAFF methodology (Specific, Contextual, Actionable, Formatted, Focused)
- Decompose validation into distinct sections for each SCAFF component
- Calculate compliance score with equal weighting (20% per component, 100% total)
- Detect missing or weak SCAFF components
- Provide specific, actionable suggestions for improvement (e.g., "Add more context about the target audience")
- SCAFF validation enabled by default in validate command
- Add --no-scaff flag to disable SCAFF validation
- Support for future validation method selection (architecture should allow other methods)
- Semantic validation integration (enabled by default, can be disabled)
- Rich terminal output with colors, symbols (✓/✗), and formatted display
- Hard-coded SCAFF criteria based on best practices (no external configuration)
- Simple implementation without AI/ML dependencies

### Reusability Opportunities
- Extend ValidationResult and ValidationSummary models from `src/prompt_unifier/models/validation.py`
- Follow validation pattern from BatchValidator in `src/prompt_unifier/core/batch_validator.py`
- Reuse RichFormatter patterns from `src/prompt_unifier/output/rich_formatter.py` for colored output
- Follow CLI flag patterns from `src/prompt_unifier/cli/commands.py` and `src/prompt_unifier/cli/main.py`
- Use existing ValidationIssue model for SCAFF-specific issues
- Leverage Console, color constants, and formatting methods from Rich library

### Scope Boundaries
**In Scope:**
- SCAFF methodology validation with 5 components
- Compliance scoring (20% per component)
- Actionable improvement suggestions
- CLI flag integration (--scaff enabled by default, --no-scaff to disable)
- Rich formatted terminal output
- Semantic validation as a complementary feature (enabled by default, can be disabled)
- Hard-coded validation criteria based on best practices
- Simple text-based analysis without AI

**Out of Scope:**
- AI/ML-powered content analysis
- Automatic prompt rewriting or suggestions generation using AI
- Multi-language validation support
- External configuration files for SCAFF criteria
- Complex NLP or semantic analysis requiring external services
- Real-time validation during prompt editing
- Integration with external prompt quality assessment tools
- Historical compliance tracking or analytics

### Technical Considerations
- Must integrate with existing validation command in `src/prompt_unifier/cli/commands.py`
- Should follow existing Pydantic model patterns from `src/prompt_unifier/models/validation.py`
- Use Typer for CLI flag handling (consistent with existing commands)
- Leverage Rich library for formatted output (already used throughout codebase)
- Must not introduce AI/ML dependencies (keep it simple and deterministic)
- Should be extensible for future validation methods beyond SCAFF
- Need to maintain backward compatibility with existing validation output format
- Consider adding new error/warning codes specific to SCAFF validation
