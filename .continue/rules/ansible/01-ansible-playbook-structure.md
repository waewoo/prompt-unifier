---
name: Ansible Playbook Structure
description: Standards for structuring Ansible playbooks to ensure readability, maintainability,
  and idempotence.
globs:
- '**/*.yml'
- '**/*.yaml'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- ansible
- playbook
- standards
- configuration-management
author: prompt-unifier
language: yaml
---
# Ansible Playbook Structure

This document outlines best practices for structuring Ansible playbooks, promoting consistency,
reusability, and reliable configuration management.

## 1. Playbook Organization

### Directory Structure

- **Principle**: Organize playbooks and related files in a logical, hierarchical structure.
- **Benefit**: Improves discoverability, reduces conflicts, and simplifies maintenance.

```
.
├── inventory/
│   ├── hosts.ini             # Main inventory file
│   ├── group_vars/           # Group-specific variables
│   │   ├── webservers.yml
│   │   └── databases.yml
│   └── host_vars/            # Host-specific variables
│       └── server1.yml
├── playbooks/
│   ├── site.yml              # Main entry point playbook
│   ├── webservers.yml        # Playbook for webservers
│   └── databases.yml         # Playbook for databases
├── roles/                    # Reusable roles
│   ├── common/
│   │   └── tasks/
│   │       └── main.yml
│   ├── nginx/
│   │   └── tasks/
│   │       └── main.yml
│   └── postgres/
│       └── tasks/
│           └── main.yml
├── ansible.cfg               # Ansible configuration file
└── README.md
```

### Main Playbook (`site.yml`)

- **Principle**: Use a main `site.yml` playbook as the entry point that orchestrates other playbooks
  or roles.
- **Benefit**: Provides a single point of execution and a high-level overview of the entire
  automation process.

```yaml
# playbooks/site.yml
---
- import_playbook: webservers.yml
- import_playbook: databases.yml
```

## 2. Playbook Components

### Hosts

- **Principle**: Clearly define the target hosts or groups for each play.
- **Benefit**: Ensures tasks are executed on the correct machines.

```yaml
---
- name: Configure webservers
  hosts: webservers
  become: true # Run tasks with sudo
  roles:
    - nginx
    - common
```

### Variables (`vars`)

- **Principle**: Define variables at the appropriate scope (play, role, group, host).
- **Benefit**: Promotes reusability and makes playbooks configurable.
- **Hierarchy**: Understand Ansible's variable precedence.
- **Sensitive Data**: Use Ansible Vault for sensitive variables.

```yaml
# playbooks/webservers.yml
---
- name: Configure webservers
  hosts: webservers
  vars:
    nginx_port: 80
  roles:
    - nginx
```

### Tasks (`tasks`)

- **Principle**: Each task should have a clear, descriptive `name`.
- **Idempotence**: Design tasks to be idempotent. Running a task multiple times should result in the
  same system state without causing unintended side effects.
  - **Use Modules**: Prefer Ansible modules that are inherently idempotent (e.g., `apt`, `yum`,
    `file`, `service`, `copy`).
  - **`changed_when`**: Use `changed_when` to explicitly define when a task should report a change,
    especially for `command` or `shell` modules.
  - **`when`**: Use `when` conditions to execute tasks only when necessary.

```yaml
# Good: Idempotent task
- name: Ensure Nginx is installed
  ansible.builtin.apt:
    name: nginx
    state: present

# Good: Using changed_when for a command
- name: Update application config
  ansible.builtin.command: /usr/local/bin/update_config.sh
  changed_when: "'Config updated' in result.stdout"
```

### Handlers (`handlers`)

- **Principle**: Use handlers for actions that should only be triggered when a change occurs (e.g.,
  restarting a service after a configuration file update).
- **Benefit**: Ensures services are only restarted when necessary, reducing downtime.

```yaml
# tasks/main.yml in a role
- name: Copy Nginx configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Restart Nginx

# handlers/main.yml in the same role
- name: Restart Nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
```

## 3. Inventory Management

### Static Inventory (`hosts.ini`)

- **Principle**: Use a static inventory file for smaller, stable environments.
- **Format**: INI or YAML.

```ini
# inventory/hosts.ini
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com
```

### Dynamic Inventory

- **Principle**: For cloud environments or large, frequently changing infrastructure, use dynamic
  inventory scripts or plugins.
- **Benefit**: Automatically discovers hosts, reducing manual effort and errors.
- **Examples**: AWS EC2, Azure RM, GCP Compute Engine inventory plugins.

## 4. Naming Conventions

- **Playbooks**: `snake_case` (e.g., `webservers.yml`, `deploy_app.yml`).
- **Roles**: `snake_case` (e.g., `nginx`, `common`).
- **Tasks**: Descriptive, starting with a verb (e.g., "Ensure Nginx is installed", "Copy application
  configuration").
- **Variables**: `snake_case` (e.g., `nginx_port`, `app_version`).
- **Groups**: `snake_case` (e.g., `webservers`, `databases`).