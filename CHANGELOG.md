# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v2.3.2 (2025-12-18)

### Fix

- Correct clean option with tag enabled

## v2.3.1 (2025-12-18)

### Fix

- Reduce Git authentication prompts during sync

## v2.3.0 (2025-12-17)

### Feat

- Add windows support

## v2.2.0 (2025-11-30)

### Feat

- consolidate documentation and CI/CD improvements

### Fix

- **tests**: correct linting errors in unit tests

## v2.1.0 (2025-11-28)

### Feat

- implement MkDocs documentation site

## v2.0.0 (2025-11-28)

### BREAKING CHANGE

- Verification result structure now includes deployment_status field that consumers should handle appropriately.

### Feat

- **validation**: add title extraction and display for validation prompts/rules

### Refactor

- **handlers**: enhance cleanup to return detailed verification results
- **handlers**: enhance deployment reporting with status tracking and improved verification display

## v1.4.0 (2025-11-27)

### Feat

- Enhance SCAFF validator for improved actionable score detection
- **validation**: add SCAFF methodology validation to validate command
- Add Markdown linter and formatter

### Fix

- **cli**: correct version reporting in CLI command

### Refactor

- **security**: Deprecate Safety in favor of Pip-audit and industrialize CI

## v1.3.0 (2025-11-25)

### Feat

- **handlers**: implement Kilo Code tool handler for pure Markdown deployment

### Refactor

- Reduce cognitive complexity in SonarQube reported functions

## v1.2.1 (2025-11-24)

### Fix

- **ci**: Add rules to sonar-scan job to skip on tags

### Refactor

- Fix SonarQube issues and implement unused parameters

## v1.2.0 (2025-11-23)

### Feat

- **ci**: Refine SonarQube integration and CI linting
- Add GitLab CI configuration validation pre-commit hook

### Refactor

- Reduce cognitive complexity and align Ruff with SonarQube

## v1.1.0 (2025-11-23)

### Feat

- Add make update-deps command and update dependencies

## v1.0.3 (2025-11-23)

### Fix

- use shields.io for pipeline badge compatibility with PyPI

## v1.0.2 (2025-11-23)

### Fix

- **ci**: use cz changelog with version to extract current release notes

## v1.0.1 (2025-11-23)

### Fix

- correct CI badge URL and add PyPI project URLs

## v1.0.0 (2025-11-23)

### BREAKING CHANGE

- -v flag now controls verbosity level instead of showing version. use -V or --version for version
  information.

### Feat

- **protocol**: add relative_path parameter and directory attributes to ToolHandler
- **logging**: implement centralized logging system with global verbose flag

## v0.6.0 (2025-11-22)

### Feat

- **utils**: add cross-platform path normalization for Windows compatibility
- Introduce `list` and `status` CLI commands with rich UI, enabled by a new handler protocol
  supporting detailed deployment status checks.
- **deploy**: add multi-tool support to deploy command

## v0.5.1 (2025-11-18)

### Fix

- force release for documentation update

## v0.5.0 (2025-11-18)

### Feat

- Implement Multiple Source Repository Support

## v0.4.0 (2025-11-17)

### Feat

- Rename project from prompt-manager to prompt-unifier

## v0.3.0 (2025-11-16)

### Feat

- **ci**: Add PyPI publishing job to GitLab CI

## v0.2.0 (2025-11-16)

### Feat

- **ci**: Add local GitLab CI testing capabilities and update documentation
- **release**: Implement GitLab Release Automation
- **deploy**: Implement recursive file discovery with subdirectory preservation
- **validate**: ignore README.md files during validation
- **handlers**: Add configurable base paths for tool handlers
- Add Continue handler and Kilocode Memory Bank documentation
- Implement Strategy Pattern for Tool Handlers
- **rules**: Complete rules/context files support with path-based detection
- **format**: Migrate from custom separator to standard YAML frontmatter

### Fix

- **tests**: Resolve recursive deploy test failures in CI
- **tests**: Fix pre-existing test failures and update fixtures
