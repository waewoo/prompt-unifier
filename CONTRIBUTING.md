# How to Contribute

First off, thank you for considering contributing to `prompt-unifier`! Your help is greatly
appreciated. This document provides guidelines to ensure a smooth and effective contribution
process.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Coding and Style Standards](#coding-and-style-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Development and Testing](#development-and-testing)

______________________________________________________________________

## Code of Conduct

This project and everyone participating in it is governed by a
[Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.
Please report unacceptable behavior.

## Ways to Contribute

- **Reporting Bugs**: If you find a bug, please open an issue and provide as much detail as
  possible, including steps to reproduce it.
- **Suggesting Enhancements**: Have an idea for a new feature or an improvement? Open an issue with
  a clear description of your suggestion.
- **Writing Documentation**: Good documentation is crucial. We welcome improvements to the README,
  docstrings, or other docs.
- **Submitting Code**: Fix a bug or implement a new feature by submitting a Pull Request.
- **Adding Tool Handlers**: Want to add support for a new AI tool? See the
  [Adding New Tool Handlers](DEVELOPMENT.md#adding-new-tool-handlers) guide.

## Submitting a Pull Request

1. **Fork & Clone**: Fork the repository and clone it locally.

   ```bash
   git clone https://gitlab.com/waewoo/prompt-unifier.git
   cd prompt-unifier
   ```

1. **Install Dependencies**: Set up your local environment.

   ```bash
   make install
   poetry run pre-commit install
   ```

1. **Create a Branch**: Create a new branch for your changes with a descriptive name.

   ```bash
   # Examples
   git checkout -b fix/deploy-path-error
   git checkout -b feat/add-cursor-handler
   ```

1. **Make Your Changes**: Write your code and add corresponding tests.

1. **Run Quality Checks**: Before committing, ensure all checks pass.

   ```bash
   make check
   ```

1. **Commit Your Changes**: Follow the [Commit Message Guidelines](#commit-message-guidelines).

1. **Push and Open a PR**: Push your branch to your fork and open a Pull Request against the `main`
   branch of the original repository. Provide a clear description of your changes.

## Coding and Style Standards

- **Formatting**: We use [Ruff](https://github.com/astral-sh/ruff) to format our code. Your code
  will be automatically formatted on commit if you have the pre-commit hooks installed. You can also
  run it manually with `make format`.
- **Linting**: We use Ruff to check for style issues. Run `make lint` to check your code.
- **Type Hinting**: All functions must have type hints. We use [mypy](http://mypy-lang.org/) in
  `strict` mode to enforce this. Run `make typecheck` to verify.
- **Line Length**: Maximum line length is 100 characters.

## Commit Message Guidelines

We follow the **Conventional Commits** specification. This helps automate versioning and changelog
generation.

Each commit message should have the format: `<type>(<scope>): <description>`

- **type**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
- **scope** (optional): The part of the codebase you're changing (e.g., `deploy`, `handlers`,
  `config`).
- **description**: A short, imperative-tense description of the change.

**Examples:**

```
feat(handlers): add support for the Cursor AI assistant
fix(deploy): correctly resolve relative paths in nested directories
docs(readme): add installation instructions from PyPI
chore(release): bump version to 0.5.0
```

## Development and Testing

For a detailed guide on setting up the environment, running tests, and understanding the project
architecture, please refer to the
[**DEVELOPMENT.md**](https://gitlab.com/waewoo/prompt-unifier/-/blob/main/DEVELOPMENT.md) file.

### Adding New Tool Handlers

If you want to add support for a new AI tool (like Cursor, Windsurf, or Aider), we have a
comprehensive step-by-step guide that covers:

- Understanding the ToolHandler Protocol
- Creating a complete handler implementation
- Writing tests with pytest
- Integrating with the CLI deploy command

See the
[**Adding New Tool Handlers**](https://gitlab.com/waewoo/prompt-unifier/-/blob/main/DEVELOPMENT.md#adding-new-tool-handlers)
section in DEVELOPMENT.md for the full tutorial.
