---
name: Ansible Role Standards
description: Best practices for designing, developing, and consuming reusable Ansible
  roles.
globs:
- roles/**
alwaysApply: false
category: standards
version: 1.0.0
tags:
- ansible
- roles
- standards
- reusability
- testing
author: prompt-unifier
language: yaml
---
# Ansible Role Standards

This document outlines the best practices for creating and consuming Ansible roles, which are key to
building modular, reusable, and maintainable automation.

## 1. Role Structure

A well-structured role is easy to understand, use, and maintain. Ansible expects a specific
directory layout for roles.

```
.
├── my_role/
│   ├── defaults/             # Default variables for the role
│   │   └── main.yml
│   ├── handlers/             # Handlers for the role
│   │   └── main.yml
│   ├── tasks/                # Main tasks for the role
│   │   └── main.yml
│   ├── templates/            # Jinja2 templates used by the role
│   │   └── config.j2
│   ├── files/                # Static files copied by the role
│   │   └── script.sh
│   ├── vars/                 # Other variables (higher precedence than defaults)
│   │   └── main.yml
│   ├── meta/                 # Role metadata (dependencies, author)
│   │   └── main.yml
│   ├── tests/                # Role tests (e.g., Molecule)
│   │   └── test_default.py
│   └── README.md             # Role documentation
```

## 2. Role Components

### `tasks/main.yml`

- **Principle**: Contains the main sequence of tasks that the role executes.
- **Modularity**: Break down complex tasks into smaller, included task files (e.g.,
  `tasks/install.yml`, `tasks/configure.yml`) and include them from `main.yml`.

```yaml
# roles/my_role/tasks/main.yml
---
- name: Include installation tasks
  ansible.builtin.include_tasks: install.yml

- name: Include configuration tasks
  ansible.builtin.include_tasks: configure.yml
```

### `defaults/main.yml`

- **Principle**: Define all variables that have default values here. These have the lowest
  precedence.
- **Benefit**: Provides sensible defaults, making the role easier to use out-of-the-box, while
  allowing users to override them.

```yaml
# roles/my_role/defaults/main.yml
---
my_role_port: 8080
my_role_enable_feature_x: true
```

### `vars/main.yml`

- **Principle**: Define variables specific to the role that are not meant to be easily overridden by
  the user (higher precedence than `defaults`).
- **Use Case**: Often used for internal role variables or facts discovered by the role.

### `handlers/main.yml`

- **Principle**: Contains handlers that are notified by tasks and run only when a change occurs.
- **Benefit**: Ensures actions like service restarts are only performed when necessary.

### `templates/`

- **Principle**: Store Jinja2 templates here for generating configuration files dynamically.
- **Benefit**: Allows for dynamic configuration based on variables.

### `files/`

- **Principle**: Store static files that need to be copied to target hosts without modification.

### `meta/main.yml`

- **Principle**: Contains metadata about the role, including author, description, and role
  dependencies.
- **Role Dependencies**: Define other roles that this role depends on. Ansible will ensure these
  dependent roles are executed first.

```yaml
# roles/my_role/meta/main.yml
---
galaxy_info:
  author: Your Name
  description: Installs and configures My Application.
  license: MIT
  min_ansible_version: "2.10"
  platforms:
    - name: Ubuntu
      versions:
        - focal
  galaxy_tags:
    - web
    - application

dependencies:
  - role: common # This role depends on the 'common' role
  - role: nginx
    vars:
      nginx_port: 80
```

## 3. Role Dependencies

- **Principle**: Clearly define dependencies in `meta/main.yml`.
- **Benefit**: Ansible automatically executes dependent roles before the current role, ensuring
  prerequisites are met.
- **Variable Overrides**: Variables defined in a dependent role's `vars` or `defaults` can be
  overridden by the parent role.

## 4. Role Documentation (`README.md`)

- **Principle**: Every role must have a comprehensive `README.md` file.
- **Content**:
  - **Description**: What the role does.
  - **Requirements**: Any specific Ansible version, collections, or external tools.
  - **Role Variables**: Table of all variables (from `defaults/main.yml` and `vars/main.yml`) with
    descriptions, types, and default values.
  - **Dependencies**: List of roles this role depends on.
  - **Example Playbook**: A simple playbook demonstrating how to use the role.

## 5. Role Testing (Molecule)

- **Principle**: Use [Molecule](https://molecule.readthedocs.io/) for testing Ansible roles.
- **Benefit**: Molecule provides a framework for testing roles against various operating systems,
  ensuring idempotence, and validating expected outcomes.
- **Test Scenarios**: Define different test scenarios (e.g., `default`, `install-from-source`) to
  cover various use cases.
- **Idempotence Testing**: Molecule can automatically run a role twice to verify that the second run
  reports no changes, confirming idempotence.

```bash
# Example Molecule command to test a role
molecule test
```