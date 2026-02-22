---
name: readme-writer
description: Creates comprehensive, well-structured README files for software projects
  covering purpose, setup, usage, and contribution guidelines.
mode: architect
license: MIT
---
# README Writer Skill

## When to Use

Apply this skill when:
- The user asks to create or write a README for a project
- The user asks to improve, update, or complete an existing README
- A new project is set up and documentation is requested
- The user asks "what should my README contain?"

Do NOT apply when the user is asking for API documentation, code comments, or inline docstrings.

## Structure

```
# Project Name
One-line description of what the project does and who it is for.

## Why This Exists
What problem does it solve? Why was it built?

## Features
- Feature 1
- Feature 2

## Requirements
List runtime and system dependencies.

## Installation
Step-by-step commands to get it running.

## Usage
Show the most common use case first, then options.

## Configuration
Document environment variables and config files.

## Development
How to set up the dev environment and run tests.

## Contributing
How to submit changes.

## License
```

## Writing Guidelines

### Opening Description
One sentence, active voice, no jargon:
- ✅ `prompt-unifier manages AI prompt templates with version control and deployment.`
- ❌ `This repository contains a solution leveraging modern paradigms for AI prompt lifecycle management.`

### Code Blocks
Always specify the language for syntax highlighting:
````markdown
```bash
make app-run ARGS="--help"
```
````

### Installation Section
Use a numbered list for sequential steps:
```markdown
## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/org/project.git
   cd project
   ```

2. Install dependencies
   ```bash
   make env-install
   ```

3. Copy and edit configuration
   ```bash
   cp .env.example .env
   ```
```

### Usage Section
Start with the simplest possible example, then show advanced options:
```markdown
## Usage

### Quick Start
```bash
project run input.csv
```

### Options
| Flag | Description | Default |
|------|-------------|---------|
| `--output` | Output file path | `stdout` |
| `--verbose` | Enable debug logging | `false` |
```

### Badges (optional but useful)
Place after the title, before the description:
```markdown
![CI](https://gitlab.com/org/project/badges/main/pipeline.svg)
![Coverage](https://gitlab.com/org/project/badges/main/coverage.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

## What to Avoid

- Do **not** duplicate content from code comments or docstrings
- Do **not** describe implementation details — describe behaviour
- Do **not** list every possible option — link to full docs instead
- Do **not** write future tense ("will support") — only document what exists today