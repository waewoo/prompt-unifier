# CI Pipeline Specification

## Stages
- `lint-python`, `lint-markdown`, `type-check`, `test`, `build`, `publish`

## Requirements
- Pipeline executes on merge requests and main branch (except publish).  
- `publish` stage runs only on tags and requires `PYPI_TOKEN`.  
- Artifacts and coverage reports are stored and accessible.  
- Cache dependencies for performance.  
- Fail fast on failure with clear feedback.

## Scenarios
- Lint stage fails on style violations.  
- Tests must reach ≥ 85% coverage or fail.
