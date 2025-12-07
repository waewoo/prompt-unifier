---
name: Backend Models
description: Define and implement database models with clear naming, proper relationships, data integrity constraints, and validation at multiple layers. Use this skill when creating or modifying database model files, ORM model classes, schema definitions, model relationships and associations, database constraints and validations, or migration files that define table structures. Apply when working on files in models/, schemas/, entities/, or database/ directories, when defining SQLAlchemy/Pydantic models, when adding model fields and data types, when configuring database relationships (one-to-many, many-to-many), when implementing model-level validation logic, when adding timestamps or audit fields, when creating database indexes on models, or when working with model mixins and base classes.
---

# Backend Models

This Skill provides Claude Code with specific guidance on how to adhere to coding standards as they relate to how it should handle backend models.

## When to use this skill

- When creating or modifying database model files (e.g., `models/user.py`, `schemas/product.py`)
- When defining ORM model classes using SQLAlchemy, Django ORM, or similar frameworks
- When working with Pydantic models for data validation and serialization
- When creating schema definitions that map to database tables
- When configuring model relationships and associations (foreign keys, one-to-many, many-to-many)
- When implementing database constraints (NOT NULL, UNIQUE, CHECK constraints)
- When adding model-level validation logic and validators
- When working on files in `models/`, `schemas/`, `entities/`, or `database/` directories
- When adding or modifying model fields and choosing appropriate data types
- When implementing timestamps (created_at, updated_at) or audit fields
- When creating database indexes on model fields for query performance
- When working with model mixins, base classes, or abstract models
- When defining cascade behaviors for related objects

## Instructions

For details, refer to the information provided in this file:
[backend models](../../../agent-os/standards/backend/models.md)
