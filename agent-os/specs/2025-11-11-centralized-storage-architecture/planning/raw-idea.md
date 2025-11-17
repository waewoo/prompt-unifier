# Raw Idea: Centralized Storage Architecture

## Feature Description

Refactor Git integration to use centralized storage directory (~/.prompt-unifier/storage by default) instead of storing prompts/rules in project directory. Add storage_path field to config.yaml, support --storage-path flag in init and sync commands for custom storage locations, and ensure .prompt-unifier/config.yaml remains local to each project while prompts/rules are stored centrally and shared across projects.

## Roadmap Reference

Item 3.5 - Centralized Storage Architecture
