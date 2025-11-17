---
name: Software Design Principles
description: Fundamental principles for designing robust, maintainable, and scalable
  software systems.
globs:
- '**/*'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- design
- principles
- solid
- dry
- kiss
- yagni
- architecture
- standards
- global
author: prompt-unifier
language: en
---
# Software Design Principles

This document outlines fundamental software design principles that should guide the development of all codebases, regardless of language or technology stack. Adhering to these principles leads to more maintainable, scalable, and robust systems.

## 1. DRY (Don't Repeat Yourself)

- **Principle**: Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.
- **Benefit**: Reduces redundancy, simplifies maintenance, and minimizes the risk of inconsistencies when changes are made.
- **Application**: Abstract common logic into functions, classes, modules, or reusable components (e.g., Terraform modules, Ansible roles, Helm charts).

## 2. KISS (Keep It Simple, Stupid)

- **Principle**: Most systems work best if they are kept simple rather than made complex. Simplicity should be a key goal in design, and unnecessary complexity should be avoided.
- **Benefit**: Easier to understand, test, debug, and maintain. Reduces the likelihood of bugs.
- **Application**: Choose the simplest solution that meets the requirements. Avoid premature optimization or over-engineering.

## 3. YAGNI (You Ain't Gonna Need It)

- **Principle**: Do not add functionality until it is necessary.
- **Benefit**: Prevents wasted effort on features that may never be used, reduces complexity, and keeps the codebase focused on current requirements.
- **Application**: Implement only what is required for the current iteration or problem. Resist the urge to build for hypothetical future needs.

## 4. SOLID Principles

SOLID is an acronym for five design principles intended to make software designs more understandable, flexible, and maintainable.

### S - Single Responsibility Principle (SRP)
- **Principle**: A class or module should have only one reason to change. It should have only one job.
- **Benefit**: Improves cohesion, reduces coupling, and makes components easier to test and maintain.
- **Application**: Functions should do one thing well. Classes should manage one aspect of the system.

### O - Open/Closed Principle (OCP)
- **Principle**: Software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification.
- **Benefit**: Allows new functionality to be added without altering existing, tested code, reducing the risk of introducing bugs.
- **Application**: Use interfaces, abstract classes, and dependency injection to allow for new implementations without changing core logic.

### L - Liskov Substitution Principle (LSP)
- **Principle**: Objects in a program should be replaceable with instances of their subtypes without altering the correctness of that program.
- **Benefit**: Ensures that inheritance hierarchies are correctly designed and that polymorphism works as expected.
- **Application**: Subclasses should extend the behavior of their base classes without breaking existing contracts.

### I - Interface Segregation Principle (ISP)
- **Principle**: Clients should not be forced to depend on interfaces they do not use. Many client-specific interfaces are better than one general-purpose interface.
- **Benefit**: Reduces coupling and prevents clients from being affected by changes to methods they don't care about.
- **Application**: Create fine-grained interfaces rather than monolithic ones.

### D - Dependency Inversion Principle (DIP)
- **Principle**:
    1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
    2. Abstractions should not depend on details. Details should depend on abstractions.
- **Benefit**: Decouples modules, making them easier to test, change, and reuse.
- **Application**: Use dependency injection. Depend on interfaces or abstract classes rather than concrete implementations.

## 5. Clean Architecture / Layered Architecture

- **Principle**: Organize code into layers with clear boundaries, where inner layers define policies and outer layers handle implementation details. The core business logic should be independent of frameworks, UI, and databases.
- **Benefit**:
    - **Independence**: Independent of Frameworks, UI, Database, and external agencies.
    - **Testability**: Business rules can be tested without the UI, database, or web server.
    - **Flexibility**: Easier to swap out external components (e.g., change database, UI framework).
- **Common Layers**:
    - **Entities**: Business objects and rules.
    - **Use Cases**: Application-specific business rules.
    - **Interface Adapters**: Convert data from external sources (DB, Web) into a format usable by use cases and entities.
    - **Frameworks & Drivers**: Web framework, database, UI, external APIs.