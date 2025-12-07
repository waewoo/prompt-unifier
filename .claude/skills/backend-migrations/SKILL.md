---
name: Backend Migrations
description: Create and manage database migration files that safely evolve the database schema with proper up/down migrations, data migrations, and rollback strategies. Use this skill when creating new database migration files, when modifying existing database schemas, when adding or removing tables or columns, when changing column types or constraints, when creating database indexes, when implementing data migrations to transform existing data, or when working with migration tools like Alembic or Django migrations. Apply when generating migration files, when writing migration up/down operations, when handling migration dependencies, when performing schema changes in production, or when rolling back failed migrations.
---

# Backend Migrations

This Skill provides Claude Code with specific guidance on how to adhere to coding standards as they relate to how it should handle backend migrations.

## When to use this skill

- When creating new database migration files using Alembic, Django migrations, or similar tools
- When modifying existing database schemas to add new features
- When adding or removing database tables
- When adding, removing, or modifying table columns
- When changing column data types, constraints, or default values
- When creating, modifying, or removing database indexes for performance
- When implementing data migrations to transform or migrate existing data
- When working with migration files in `migrations/`, `alembic/versions/`, or similar directories
- When generating migration files from model changes
- When writing custom migration up and down operations
- When handling migration dependencies and ordering
- When performing schema changes safely in production environments
- When rolling back failed migrations or reverting schema changes

## Instructions

For details, refer to the information provided in this file:
[backend migrations](../../../agent-os/standards/backend/migrations.md)
