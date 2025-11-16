---
name: Airflow Operator Standards
description: Best practices for using and creating Airflow operators, managing connections,
  and handling XComs.
globs:
- dags/**/*.py
- plugins/**/*.py
alwaysApply: false
category: standards
version: 1.0.0
tags:
- airflow
- operators
- pythonoperator
- xcom
- connections
author: prompt-manager
language: python
---
# Airflow Operator Standards

This document provides guidelines for the effective use of built-in operators, custom operators, and data exchange between tasks.

## 1. Operator Selection

### Prefer Provider and Built-in Operators
- **Principle**: Before writing a `PythonOperator`, always check if a built-in or provider operator can accomplish the task.
- **Reason**: Provider operators (e.g., `SnowflakeOperator`, `GCSToBigQueryOperator`) are optimized, maintained, and often provide better integrations, logging, and use of Airflow connections.
- **Example**:
  - **Good**: Use `PostgresToGCSOperator` to transfer data from Postgres to GCS. It's a single, optimized task.
  - **Avoid**: Writing a `PythonOperator` that uses `pandas.read_sql` and then `gcsfs.write` to do the same thing. This reinvents the wheel and is less efficient for large datasets.

### `PythonOperator` Best Practices
- **Keep Callables Lean**: The Python function passed to a `PythonOperator` should be a lightweight wrapper that delegates the heavy lifting to a well-tested function in a separate module.
- **Type Hinting**: The callable should have clear type hints for its arguments.
- **Use `op_kwargs`**: Pass arguments to the callable via the `op_kwargs` dictionary to allow for templating.

```python
# In my_project/etl/user_processing.py
def process_users(logical_date_str: str, batch_size: int) -> int:
    """
    This function contains the actual business logic and is unit-testable.
    """
    # ... heavy processing ...
    return processed_count

# In dags/my_dag.py
from my_project.etl.user_processing import process_users

with DAG(...) as dag:
    run_user_processing = PythonOperator(
        task_id="process_users",
        python_callable=process_users,
        op_kwargs={
            "logical_date_str": "{{ ds }}",
            "batch_size": 5000,
        },
    )
```

## 2. Custom Operators

### When to Create a Custom Operator
- **Reusability**: Create a custom operator when you have a piece of logic that needs to be reused across multiple DAGs.
- **Abstraction**: To provide a simpler, high-level abstraction for a common multi-step pattern.
- **Example**: If you frequently connect to a specific internal API, a `MyApiToS3Operator` could encapsulate the logic for authentication, fetching data, and saving it to S3.

### Custom Operator Design
- **Inheritance**: Your custom operator should inherit from `airflow.models.BaseOperator`.
- **Template Fields**: Define `template_fields` to specify which attributes of your operator should be templated with Jinja.
- **`execute` Method**: The core logic of the operator goes into the `execute` method, which takes `context` as an argument.
- **Use Hooks**: Inside your operator, use Airflow Hooks (`HttpHook`, `PostgresHook`) to interact with external systems. Hooks are the correct way to manage connections and credentials.

```python
# In plugins/my_operators/my_api_operator.py
from airflow.models.base_operator import BaseOperator
from airflow.hooks.http_hook import HttpHook

class MyApiToS3Operator(BaseOperator):
    template_fields = ("endpoint", "s3_key")

    def __init__(self, my_api_conn_id: str, endpoint: str, s3_key: str, **kwargs):
        super().__init__(**kwargs)
        self.my_api_conn_id = my_api_conn_id
        self.endpoint = endpoint
        self.s3_key = s3_key

    def execute(self, context):
        api_hook = HttpHook(method='GET', http_conn_id=self.my_api_conn_id)
        response = api_hook.run(self.endpoint)
        self.log.info(f"API response received with status: {response.status_code}")
        # ... logic to save response.text to S3 at self.s3_key ...
```

## 3. Connection Management

- **Always Use Connection IDs**: Never hardcode credentials, hosts, or tokens. Store them in the Airflow UI as a Connection and reference them by `conn_id`.
- **Hooks**: Use Hooks within operators to interact with connections. Hooks provide a standard interface and handle the logic of retrieving credentials from the connection details.

```python
# Good: Using a hook with a connection ID
def my_callable():
    pg_hook = PostgresHook(postgres_conn_id="my_db_connection")
    df = pg_hook.get_pandas_df("SELECT * FROM users")
    # ...

# Bad: Hardcoding connection details
def my_bad_callable():
    conn = psycopg2.connect(
        host="my-db.example.com", # Don't do this
        user="my_user",           # Don't do this
        password="my_password"    # NEVER do this
    )
    # ...
```

## 4. Data Exchange with XComs (Cross-Communication)

- **Use Sparingly**: XComs are designed for passing small amounts of metadata between tasks (e.g., a record count, a file path, a boolean flag). They are not for passing large datasets.
- **Size Limit**: XCom data is stored in the Airflow metadata database. The default backend (e.g., Postgres, MySQL) has a size limit. Pushing large data (e.g., a pandas DataFrame) will slow down or break your Airflow database.
- **Passing Data**: For passing large datasets between tasks, use an intermediate storage layer like S3, GCS, or a shared file system.
  - **Task 1**: Process data and write it to `s3://my-bucket/data/{{ ds }}/output.parquet`.
  - **Task 1**: Push the S3 path to XComs: `return "s3://my-bucket/data/{{ ds }}/output.parquet"`
  - **Task 2**: Pull the S3 path from XComs and read the data from that path.

### Typed XComs (Airflow 2.4+)
- **Principle**: When using a `PythonOperator`, use standard Python type hints on the return value of your callable. Airflow will use this to enable typed XComs, which can improve serialization and clarity.

```python
# Good: Typed XCom return value
def _get_record_count() -> int:
    return 12345

get_count = PythonOperator(
    task_id="get_count",
    python_callable=_get_record_count,
)

# The value pushed to XComs will be an integer
```