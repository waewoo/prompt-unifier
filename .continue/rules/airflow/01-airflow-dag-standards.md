---
name: Airflow DAG Standards
description: Core standards for designing and structuring Airflow DAGs to ensure reliability
  and maintainability.
globs:
- dags/**/*.py
alwaysApply: false
category: standards
version: 1.0.0
tags:
- airflow
- dag
- standards
- etl
- orchestration
author: prompt-unifier
language: python
---
# Airflow DAG Standards

This document defines the primary standards for creating robust, maintainable, and efficient Airflow DAGs.

## 1. Core DAG Principles

### Idempotency and Determinism
- **Idempotency**: Every task must be idempotent. Rerunning a task for the same logical date (e.g., for a backfill or after a failure) must produce the same state as the first successful run, with no errors or duplicate data.
- **Determinism**: DAG runs must be deterministic. A DAG run for a specific `logical_date` should always process the same data and produce the same output. Avoid using non-deterministic inputs like `datetime.now()` for data filtering; use the logical date (`{{ ds }}`, `{{ data_interval_start }}`) instead.

### Atomicity
- **Single Responsibility**: Each task should have a single, well-defined purpose (e.g., "extract from source A", "transform user data").
- **Independent Reruns**: Atomic tasks can be rerun independently without affecting unrelated tasks, which is critical for debugging and recovery.

## 2. DAG Structure and Definition

### Avoid Top-Level Code
- **Scheduler Performance**: The Airflow scheduler executes the Python code in DAG files frequently to parse the DAG structure. Any code outside of a task callable (e.g., making API calls, querying a database) will run on every parse, severely impacting scheduler performance.
- **What's Allowed**: Only Airflow DAG and operator definitions, and simple, static Python variable assignments should be at the top level of a DAG file.

```python
# Good: All code is part of the DAG definition or inside a task
with DAG(...) as dag:
    task1 = BashOperator(...)

# Bad: This query runs every time the DAG file is parsed
db_hook = PostgresHook(postgres_conn_id="my_db")
active_users = db_hook.get_pandas_df("SELECT * FROM users WHERE active = true")

with DAG(...) as dag:
    # This is bad practice
    ...
```

### Simple Dependency Structure
- **Readability**: Aim for a clear, linear, or simple fan-out/fan-in dependency structure. Deeply nested or complex branching logic is hard to read and maintain.
- **TaskGroups**: Use `TaskGroup` to visually group related tasks and simplify the top-level graph view.
- **Dependency Operators**: Consistently use the bit-shift operators (`>>` and `<<`) for setting dependencies.

```python
# Good: Clear, linear flow
start >> extract >> transform >> load >> end

# Good: Using a TaskGroup for a complex section
with TaskGroup("validation_checks") as validation_group:
    check_data_quality = ...
    check_row_counts = ...

start >> extract >> validation_group >> load >> end
```

### Naming Conventions
- **`dag_id`**: Must be unique across the Airflow environment.
  - **Format**: `<team_or_project>.<pipeline_name>.<version>`
  - **Example**: `data_eng.user_profiles_etl.v1`
- **`task_id`**: Must be unique within the DAG. Use clear, descriptive `snake_case`.
  - **Good**: `extract_users_from_postgres`, `transform_user_data`
  - **Bad**: `task_1`, `python_op`, `run_this`

## 3. Dynamic DAGs and Data Handling

### Templating and Macros
- **Use Jinja Templating**: Leverage Airflow's built-in Jinja templating for dynamic parameters. Pass logical date macros to your tasks to ensure they are deterministic.
  - `{{ ds }}`: The logical date as `YYYY-MM-DD`.
  - `{{ data_interval_start }}`: The start of the data interval (pendulum object).
  - `{{ var.value.my_airflow_variable }}`: To securely access an Airflow Variable.
  - `{{ conn.my_conn_id.host }}`: To securely access attributes of an Airflow Connection.

### Incremental Data Processing
- **Principle**: Whenever possible, process data incrementally based on the data interval, not all at once. This is more efficient and scalable.
- **Example**: In a daily DAG, filter your source query for records created or updated within the specific data interval.

```sql
-- SQL query in a daily DAG
SELECT *
FROM users
WHERE created_at >= '{{ data_interval_start }}' AND created_at < '{{ data_interval_end }}';
```

## 4. Configuration

### Timezone
- **Always Use Timezone-Aware Datetimes**: All dates, especially the `start_date`, must be timezone-aware.
- **Best Practice**: Use `pendulum` for creating timezone-aware datetimes. The standard convention is to use UTC.

```python
import pendulum

with DAG(
    dag_id="timezone_aware_dag",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    ...
) as dag:
    ...
```

### Default Arguments
- **`catchup`**: Set `catchup=False` by default to prevent the scheduler from launching a large number of DAG runs if the `start_date` is far in the past.
- **`retries`**: Set a sensible default for `retries` (e.g., 1 or 3) to handle transient failures.
- **`owner`**: Always specify an `owner` (e.g., a team name) for accountability.