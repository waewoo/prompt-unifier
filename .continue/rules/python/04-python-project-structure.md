---
name: Python Project Structure and Packaging
description: Standards for structuring Python applications and libraries to ensure
  consistency and maintainability.
globs:
- pyproject.toml
- setup.cfg
- setup.py
alwaysApply: false
category: standards
version: 1.0.0
tags:
- python
- project
- structure
- packaging
- standards
- poetry
- pyproject
author: prompt-unifier
language: python
---
# Python Project Structure and Packaging

This document outlines the best practices for structuring Python projects. A standardized structure
makes projects easier to navigate, test, package, and maintain.

## 1. Recommended Project Layout (`src/` Layout)

- **Principle**: Place all application source code inside a `src/` directory.
- **Benefit**:
  - **Clarity**: Clearly separates your source code from other project files (tests, docs, config).
  - **Avoids Import Issues**: Prevents accidental imports of local files instead of installed
    packages, which can cause hard-to-debug issues, especially during testing and packaging.
  - **Editable Installs**: Works reliably with editable installs (`pip install -e .`).

```
my_project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── module1.py
│       └── subpackage/
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_module1.py
├── docs/
│   └── index.md
├── .gitignore
├── pyproject.toml
└── README.md
```

## 2. Dependency Management (`pyproject.toml`)

- **Principle**: Use `pyproject.toml` for defining project metadata and dependencies, as specified
  in PEP 621.
- **Tooling**: Use a modern dependency management tool like [Poetry](https://python-poetry.org/) or
  [PDM](https://pdm.fming.dev/). These tools manage virtual environments, handle dependency
  resolution, and build packages from the `pyproject.toml` file.
- **Dependency Groups**: Use dependency groups to separate main dependencies from development
  dependencies (e.g., `pytest`, `ruff`, `mypy`).

```toml
# Example pyproject.toml using Poetry

[tool.poetry]
name = "my-package"
version = "0.1.0"
description = "A sample Python package."
authors = ["Your Name <you@example.com>"]
readme = "README.md"
packages = [{include = "my_package", from = "src"}]

[tool.poetry.dependencies]
python = "^3.9"
httpx = "^0.23.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.2.0"
ruff = "^0.1.0"
mypy = "^0.991"
```

## 3. Packaging and Distribution

- **Build System**: The build system should be declared in `pyproject.toml`. For Poetry, this is
  handled automatically. For other tools like `setuptools` or `flit`, it needs to be specified.
- **Building**: Use the chosen tool's build command (e.g., `poetry build`) to create standard
  distribution packages (a source distribution `.tar.gz` and a wheel `.whl`).
- **Publishing**: Publish packages to a package repository like PyPI (for public packages) or a
  private repository (e.g., Artifactory, Nexus, GitLab Package Registry).

## 4. Entry Points for Applications

- **Principle**: For applications that need to be run as a command-line script, define an entry
  point in `pyproject.toml`.
- **Benefit**: When the package is installed, the tool creates a wrapper script that is
  automatically added to the user's `PATH`, making the application directly runnable.

```toml
# In pyproject.toml under [tool.poetry.scripts]
[tool.poetry.scripts]
my-app = "my_package.main:cli"

# In src/my_package/main.py
def cli():
    """Main command-line entry point."""
    print("Hello, world!")
```

## 5. Configuration Files

- **Centralize Configuration**: As much as possible, centralize tool configuration within
  `pyproject.toml` (e.g., `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`).
- **Benefit**: Reduces the number of dotfiles in the project root, keeping it clean and organized.
- **Exceptions**: Some tools may require their own configuration files (e.g.,
  `.pre-commit-config.yaml`, `ansible.cfg`).