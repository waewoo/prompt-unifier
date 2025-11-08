# Core Python Packages Usage

## Pydantic

- Use Pydantic models for data validation and settings management.
- Define BaseModel subclasses with typed fields and validators.
- Enable JSON serialization and parsing easily.

## Typer & Click

- Use Typer (built on Click) for building CLI applications with type hints.
- Organize CLI commands cleanly, using decorators and subcommands.
- Support help generation and argument parsing seamlessly.

## Rich

- Use Rich for enhanced terminal output: tables, colors, progress bars, tracebacks.
- Standardize console output formatting for better UX.

## SQLAlchemy & Alembic

- Use SQLAlchemy ORM for database models and queries.
- Organize models in a dedicated `models/` package or `src/yourapp/models/`.
- Use Alembic for managing database schema migrations.
- Store Alembic migration scripts in `migrations/` directory.
- Automate migrations in CI/CD.

## Example usage snippet
```bash
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserModel(Base):
tablename = "users"
id = Column(Integer, primary_key=True)
name = Column(String)

class UserSchema(BaseModel):
id: int
name: str
```