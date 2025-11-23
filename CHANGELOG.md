# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.0.2 (2025-11-23)

### Fix

- **ci**: use cz changelog with version to extract current release notes

## v1.0.1 (2025-11-23)

### Fix

- correct CI badge URL and add PyPI project URLs

## v1.0.0 (2025-11-23)

### BREAKING CHANGE

- -v flag now controls verbosity level instead of showing version. use -V or --version for version information.

### Feat

- **protocol**: add relative_path parameter and directory attributes to ToolHandler
- **logging**: implement centralized logging system with global verbose flag

## v0.6.0 (2025-11-22)

### Feat

- **utils**: add cross-platform path normalization for Windows compatibility
- Introduce `list` and `status` CLI commands with rich UI, enabled by a new handler protocol supporting detailed deployment status checks.
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
