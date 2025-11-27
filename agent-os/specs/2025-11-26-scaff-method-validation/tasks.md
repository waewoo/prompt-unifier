# Task Breakdown: SCAFF Method Validation

## Overview
Total Tasks: 4 task groups with approximately 25-35 sub-tasks

## Task List

### Models Layer

#### Task Group 1: SCAFF Data Models and Validation Enums
**Dependencies:** None

- [x] 1.0 Complete SCAFF models layer
  - [x] 1.1 Write 2-8 focused tests for SCAFF models
    - Limit to 2-8 highly focused tests maximum
    - Test SCARFFScore model creation and validation
    - Test SCARFFComponent model with score ranges (0-20)
    - Test ValidationResult extension with scaff_score metadata
    - Skip exhaustive validation testing of all edge cases
  - [x] 1.2 Extend WarningCode enum in `src/prompt_unifier/models/validation.py`
    - Add SCAFF_NOT_SPECIFIC warning code
    - Add SCAFF_LACKS_CONTEXT warning code
    - Add SCAFF_NOT_ACTIONABLE warning code
    - Add SCAFF_POORLY_FORMATTED warning code
    - Add SCAFF_UNFOCUSED warning code
    - Follow existing WarningCode enum pattern
  - [x] 1.3 Create SCARFFComponent model in `src/prompt_unifier/models/scaff.py`
    - Fields: component_name (str), score (int 0-20), max_score (int = 20), status (str)
    - Validation: score must be 0-20
    - Computed property: passed (bool) based on score threshold
  - [x] 1.4 Create SCARFFScore model in `src/prompt_unifier/models/scaff.py`
    - Fields: components (list[SCARFFComponent]), total_score (int), max_score (int = 100)
    - Computed properties: percentage, grade (excellent/good/poor), all_passed (bool)
    - Aggregation method: calculate total from components
  - [x] 1.5 Extend ValidationResult model in `src/prompt_unifier/models/validation.py`
    - Add optional scaff_score field (SCARFFScore | None = None)
    - Maintain backward compatibility (field defaults to None)
    - Update model_config examples to show SCAFF usage
  - [x] 1.6 Ensure models layer tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify models validate correctly
    - Verify SCARFFScore aggregation works
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- New WarningCode enum values added successfully
- SCARFFComponent and SCARFFScore models validate correctly
- ValidationResult extended with optional scaff_score field
- Backward compatibility maintained for existing code

### Core Validation Logic

#### Task Group 2: SCAFF Validator Implementation
**Dependencies:** Task Group 1 (COMPLETED)

- [x] 2.0 Complete SCAFF validator implementation
  - [x] 2.1 Write 2-8 focused tests for SCARFFValidator
    - Limit to 2-8 highly focused tests maximum
    - Test each SCAFF component analyzer (specific, contextual, actionable, formatted, focused)
    - Test score aggregation and threshold classification
    - Test ValidationIssue generation with suggestions
    - Skip exhaustive testing of all heuristic patterns
  - [x] 2.2 Create SCARFFValidator class in `src/prompt_unifier/core/scaff_validator.py`
    - Follow PromptValidator pattern from `src/prompt_unifier/core/validator.py`
    - Initialize with hard-coded SCAFF criteria constants
    - Main method: validate_content(content: str, file_path: Path) -> SCARFFScore
  - [x] 2.3 Implement _analyze_specific method
    - Check for concrete requirements using keywords: "must", "should", specific metrics
    - Check for measurable goals and clear scope
    - Score: 0-20 points based on specificity level
    - Return component score and issues list
  - [x] 2.4 Implement _analyze_contextual method
    - Check for background information and user context
    - Look for problem statement sections (keywords: "why", "background", "context")
    - Score: 0-20 points based on contextual information
    - Return component score and issues list
  - [x] 2.5 Implement _analyze_actionable method
    - Check for action verbs: "create", "implement", "test", "build", "configure"
    - Check for tasks, steps, or instructions
    - Score: 0-20 points based on actionability
    - Return component score and issues list
  - [x] 2.6 Implement _analyze_formatted method
    - Check for markdown structure: headings (# ## ###), bullet points, numbered lists
    - Check for proper sectioning and organization
    - Score: 0-20 points based on formatting quality
    - Return component score and issues list
  - [x] 2.7 Implement _analyze_focused method
    - Check content length (optimal range: 500-2000 words)
    - Check for topic coherence (single main topic vs. scattered topics)
    - Check for scope creep indicators
    - Score: 0-20 points based on focus level
    - Return component score and issues list
  - [x] 2.8 Implement _generate_issues method
    - For each failed component, create ValidationIssue with:
      - severity: ValidationSeverity.WARNING
      - code: appropriate SCAFF_* WarningCode
      - message: component-specific failure description
      - suggestion: actionable improvement suggestion (1-2 sentences)
    - Use hard-coded suggestion templates per component
    - Example: "Add more context about the target audience" for Contextual
  - [x] 2.9 Implement score aggregation and grade calculation
    - Sum all component scores (0-100 total)
    - Calculate grade: <60 = poor, 60-79 = good, 80+ = excellent
    - Create SCARFFScore model with all component details
  - [x] 2.10 Ensure SCARFFValidator tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify each component analyzer works
    - Verify score aggregation is correct
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass ✅
- SCARFFValidator class follows existing validator patterns ✅
- All 5 component analyzers (Specific, Contextual, Actionable, Formatted, Focused) work correctly ✅
- Score aggregation produces correct 0-100 scale ✅
- ValidationIssue objects generated with actionable suggestions ✅
- Hard-coded criteria and suggestion templates implemented ✅

### CLI and Batch Integration

#### Task Group 3: CLI Integration and Batch Validation
**Dependencies:** Task Group 2 (COMPLETED)

- [x] 3.0 Complete CLI and batch integration
  - [x] 3.1 Write 2-8 focused tests for CLI integration
    - Limit to 2-8 highly focused tests maximum
    - Test --no-scaff flag parsing
    - Test BatchValidator integration with SCAFF validation
    - Test that SCAFF validation runs by default
    - Skip exhaustive CLI argument combination testing
  - [x] 3.2 Add --no-scaff flag to validate command in `src/prompt_unifier/cli/commands.py`
    - Add parameter: scaff: bool = typer.Option(True, "--scaff/--no-scaff", help="Enable/disable SCAFF validation")
    - Follow existing typer.Option pattern (similar to --json flag)
    - Default value: True (SCAFF enabled by default)
  - [x] 3.3 Update validate function signature in `src/prompt_unifier/cli/commands.py`
    - Pass scaff flag to BatchValidator or validation logic
    - Maintain backward compatibility with existing parameters
    - Update docstring to document SCAFF flag
  - [x] 3.4 Integrate SCARFFValidator into BatchValidator in `src/prompt_unifier/core/batch_validator.py`
    - Import SCARFFValidator
    - Add scaff_enabled parameter to validate_directory method
    - After format validation, run SCAFF validation if enabled
    - Merge SCAFF warnings into ValidationResult.warnings
    - Attach SCARFFScore to ValidationResult.scaff_score
  - [x] 3.5 Update BatchValidator.validate_directory method
    - For each file, run PromptValidator.validate_file (existing)
    - If scaff_enabled, run SCARFFValidator.validate_content
    - Merge SCAFF ValidationIssues into result.warnings
    - Set result.scaff_score from SCARFFValidator output
    - Maintain separation: format validation (errors) vs SCAFF validation (warnings)
  - [x] 3.6 Update ValidationSummary aggregation
    - Include SCAFF warning counts in total_warnings
    - Ensure SCAFF warnings don't affect success status (warnings don't block)
    - SCAFF validation results visible in summary
  - [x] 3.7 Ensure CLI integration tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify --no-scaff flag works
    - Verify SCAFF validation runs by default
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass ✅
- --no-scaff flag added and works correctly ✅
- SCAFF validation enabled by default in validate command ✅
- BatchValidator integrates SCAFF validation after format validation ✅
- SCAFF warnings merged into ValidationResult.warnings ✅
- SCAFF scores attached to ValidationResult.scaff_score ✅
- Backward compatibility maintained ✅

### Rich Output Formatting

#### Task Group 4: SCAFF Score Display in Rich Output
**Dependencies:** Task Groups 1-3 (ALL COMPLETED)

- [x] 4.0 Complete Rich output formatting for SCAFF
  - [x] 4.1 Write 2-8 focused tests for Rich formatting
    - Limit to 2-8 highly focused tests maximum
    - Test _display_scaff_score method output
    - Test _display_scafff_issue formatting
    - Test score color coding (red/yellow/green based on grade)
    - Skip exhaustive formatting variation testing
  - [x] 4.2 Add SCAFF section to RichFormatter in `src/prompt_unifier/output/rich_formatter.py`
    - Create _display_scaff_score method
    - Display format: "SCAFF Score: {score}/100 ({grade})"
    - Color coding: <60 red, 60-79 yellow, 80+ green
    - Include component breakdown table
  - [x] 4.3 Create _display_scafff_component_table method
    - Display table with columns: Component | Score | Status
    - Use Rich Table formatting
    - Show all 5 components with their scores (0-20 each)
    - Status symbols: checkmark for passed, X for failed
  - [x] 4.4 Update _display_issue method to handle SCAFF warnings
    - Check if issue.code starts with "SCAFF_"
    - Use WARNING_COLOR (yellow) for SCAFF issues
    - Use warning symbol (warning emoji) for SCAFF issues
    - Display suggestion prominently
  - [x] 4.5 Integrate SCAFF display into format_summary method
    - After displaying file results, check if result.scaff_score exists
    - If exists, call _display_scaff_score with score details
    - Display SCAFF component table
    - Add separator line after SCAFF section
  - [x] 4.6 Update _display_summary_table to include SCAFF statistics
    - Add line: "SCAFF Warnings: {count}" if SCAFF validation ran
    - Use WARNING_COLOR for SCAFF warning count
    - Maintain existing summary structure
  - [x] 4.7 Ensure Rich formatting tests pass
    - Run ONLY the 2-8 tests written in 4.1
    - Verify SCAFF score displays correctly
    - Verify component table renders properly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 4.1 pass ✅
- SCAFF score prominently displayed with color coding ✅
- Component breakdown table shows all 5 SCAFF components ✅
- SCAFF warnings formatted with warning symbol and yellow color ✅
- SCAFF section integrated into validation summary output ✅
- Rich formatting follows existing RichFormatter patterns ✅

### Testing and Integration

#### Task Group 5: Test Review & Gap Analysis
**Dependencies:** Task Groups 1-4 (ALL COMPLETED)

- [x] 5.0 Review existing tests and fill critical gaps only
  - [x] 5.1 Review tests from Task Groups 1-4
    - Review the 2-8 tests written for models layer (Task 1.1)
    - Review the 2-8 tests written for SCAFF validator (Task 2.1)
    - Review the 2-8 tests written for CLI integration (Task 3.1)
    - Review the 2-8 tests written for Rich formatting (Task 4.1)
    - Total existing tests: approximately 8-32 tests
  - [x] 5.2 Analyze test coverage gaps for SCAFF feature only
    - Identify critical end-to-end workflows lacking coverage
    - Check validation pipeline: file -> format validation -> SCAFF validation -> Rich output
    - Check --no-scaff flag disables SCAFF validation properly
    - Focus ONLY on gaps related to this spec's feature requirements
    - Do NOT assess entire application test coverage
    - Prioritize integration tests over additional unit tests
  - [x] 5.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on end-to-end workflows:
      - Complete validation flow with SCAFF enabled
      - Complete validation flow with --no-scaff flag
      - SCAFF score aggregation across multiple files
      - JSON output format includes SCAFF scores
      - Rich output displays SCAFF sections correctly
    - Focus on integration points between layers
    - Do NOT write comprehensive coverage for all scenarios
    - Skip edge cases unless business-critical
  - [x] 5.4 Run feature-specific tests only
    - Run ONLY tests related to SCAFF feature (tests from 1.1, 2.1, 3.1, 4.1, and 5.3)
    - Expected total: approximately 18-42 tests maximum
    - Do NOT run the entire application test suite
    - Verify critical workflows pass
    - Verify backward compatibility (existing validate command still works)
  - [x] 5.5 Verify backward compatibility
    - Run existing validation tests to ensure no regression
    - Verify existing --json output still works
    - Verify existing --type filtering still works
    - SCAFF validation should not break existing features

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 18-42 tests total) ✅
- Critical end-to-end workflows for SCAFF feature are covered ✅
- No more than 10 additional tests added when filling testing gaps ✅
- Testing focused exclusively on SCAFF feature requirements ✅
- Backward compatibility verified (existing features still work) ✅
- No regressions in existing validation functionality ✅

## Execution Order

Recommended implementation sequence:
1. Models Layer (Task Group 1) - Create SCAFF data models and extend ValidationResult ✅ COMPLETED
2. Core Validation Logic (Task Group 2) - Implement SCARFFValidator with 5 component analyzers ✅ COMPLETED
3. CLI and Batch Integration (Task Group 3) - Add --no-scaff flag and integrate with BatchValidator ✅ COMPLETED
4. Rich Output Formatting (Task Group 4) - Extend RichFormatter for SCAFF score display ✅ COMPLETED
5. Test Review & Gap Analysis (Task Group 5) - Fill critical test coverage gaps and verify end-to-end workflows ✅ COMPLETED

## Implementation Notes

**Key Patterns to Follow:**
- ValidationResult extension pattern (add optional fields)
- Validator pattern from PromptValidator class
- BatchValidator integration pattern (run after format validation)
- RichFormatter display methods pattern (_display_* methods)
- Typer CLI option pattern (--flag/--no-flag boolean options)

**Hard-Coded SCAFF Criteria:**
- Specific: Keywords ("must", "should", metrics), measurable goals
- Contextual: Background sections, "why"/"context" keywords
- Actionable: Action verbs ("create", "implement", "test")
- Formatted: Markdown structure (headings, lists, sections)
- Focused: Content length (500-2000 words optimal), topic coherence

**Suggestion Templates (Hard-Coded):**
- Specific: "Add specific requirements with measurable criteria"
- Contextual: "Include background information and user context"
- Actionable: "Add concrete action steps or implementation tasks"
- Formatted: "Organize content with clear headings and sections"
- Focused: "Narrow scope to a single focused topic"

**Testing Strategy:**
- 2-8 focused tests per task group during development
- Run only newly written tests during development (not entire suite)
- Final test review group adds max 10 strategic tests for gaps
- Total expected tests: 18-42 tests for SCAFF feature
- Verify backward compatibility with existing validation tests
