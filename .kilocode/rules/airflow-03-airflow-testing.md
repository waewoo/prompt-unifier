# Airflow Testing Standards

Guidelines and best practices for testing Airflow DAGs and custom components.

**Category:** testing | **Tags:** airflow, testing, pytest, standards, quality | **Version:** 1.0.0 | **Author:** prompt-unifier | **Language:** python | **AppliesTo:** tests/dags/**/*.py

# Airflow Testing Standards

This document outlines the standards for testing Airflow DAGs, operators, and business logic to
ensure pipeline reliability and correctness.

## 1. DAG Integrity Tests

These are essential, lightweight tests that should run for every DAG in your repository. They check
for structural and syntactical correctness.

### DAG Bag Loading Test

- **Purpose**: To ensure that the Airflow scheduler can parse your DAG file without errors.
- **Implementation**: Use `airflow.models.dagbag.DagBag` to load all DAGs and check for import
  errors.

```python
# In tests/dags/test_dag_integrity.py
import pytest
from airflow.models.dagbag import DagBag

@pytest.fixture(scope="session")
def dagbag():
    """Provides a session-scoped fixture for the DagBag."""
    return DagBag(dag_folder="dags/", include_examples=False)

def test_no_import_errors(dagbag):
    """Verify that Airflow can import all DAGs without errors."""
    assert not dagbag.import_errors, f"DAG import errors found: {dagbag.import_errors}"
```

### Required DAG Arguments Test

- **Purpose**: To enforce standards, such as ensuring every DAG has an owner and tags.
- **Implementation**: Iterate through the loaded DAGs and assert that required arguments are
  present.

```python
# In tests/dags/test_dag_integrity.py
def test_all_dags_have_required_args(dagbag):
    """Assert that all DAGs have a non-empty 'owner' and 'tags'."""
    for dag_id, dag in dagbag.dags.items():
        assert dag.owner, f"DAG {dag_id} has no owner."
        assert dag.tags, f"DAG {dag_id} has no tags."
```

### Acyclicity Test

- **Purpose**: To ensure there are no circular dependencies in your DAGs.
- **Implementation**: Call the `test_cycle()` method on each DAG object.

```python
# In tests/dags/test_dag_integrity.py
def test_dags_are_acyclic(dagbag):
    """Assert that all DAGs are acyclic (have no dependency cycles)."""
    for dag_id, dag in dagbag.dags.items():
        try:
            dag.test_cycle()
        except Exception as e:
            pytest.fail(f"DAG {dag_id} has a cycle. Error: {e}")
```

## 2. Unit Testing Business Logic

- **Principle**: The core business logic (e.g., the data transformation code called by a
  `PythonOperator`) should be in a separate, importable module and have its own dedicated unit
  tests.
- **Decoupling**: This is the most important aspect of testing Airflow pipelines. The DAG is the
  orchestrator; the logic should be testable independently of Airflow.
- **Mocking**: Use standard Python mocking libraries (like `unittest.mock`) to mock any external
  dependencies (e.g., database connections, API calls).

```python
# In my_project/etl/transform.py
def transform_user_data(df: pd.DataFrame) -> pd.DataFrame:
    df["full_name"] = df["first_name"] + " " + df["last_name"]
    return df

# In tests/unit/test_transform.py
import pandas as pd
from my_project.etl.transform import transform_user_data

def test_transform_user_data():
    # Arrange
    input_df = pd.DataFrame({
        "first_name": ["John"],
        "last_name": ["Doe"],
    })

    # Act
    result_df = transform_user_data(input_df)

    # Assert
    assert "full_name" in result_df.columns
    assert result_df["full_name"].iloc[0] == "John Doe"
```

## 3. Task and Operator Testing

### Testing Task Logic

- **Purpose**: To test the logic of a single Airflow task in isolation.
- **Implementation**: For a `PythonOperator`, you can import the callable function and test it
  directly. For other operators, you may need to instantiate the operator and call its `execute`
  method with a mocked context.

### Mocking Connections and Hooks

- **Principle**: When testing a task that uses an Airflow Hook (e.g., `PostgresHook`), you must mock
  the hook to prevent the test from making real external calls.
- **Implementation**: Use `pytest.mock.patch` or `unittest.mock.patch` to replace the hook class
  with a `MagicMock`.

```python
# In dags/my_dag.py
from airflow.providers.postgres.hooks.postgres import PostgresHook

def get_user_count(**kwargs):
    pg_hook = PostgresHook(postgres_conn_id="my_db")
    count = pg_hook.get_first("SELECT COUNT(*) FROM users")[0]
    return count

# In tests/dags/test_my_dag.py
from unittest.mock import MagicMock

def test_get_user_count_task(mocker):
    # Arrange
    # Patch the PostgresHook class
    mock_hook_instance = MagicMock()
    mock_hook_instance.get_first.return_value = [123] # Mock the return value
    mocker.patch(
        "dags.my_dag.PostgresHook",
        return_value=mock_hook_instance,
    )

    # Act
    from dags.my_dag import get_user_count
    result = get_user_count()

    # Assert
    assert result == 123
    mock_hook_instance.get_first.assert_called_once_with("SELECT COUNT(*) FROM users")
```

## 4. Idempotency Tests

- **Purpose**: To verify that rerunning a task produces the same outcome.
- **Implementation**: This often requires an integration test setup. The basic pattern is:
  1. Set up an initial state (e.g., a target database table is empty).
  2. Run the task once.
  3. Assert the target state is correct (e.g., the table has 10 rows).
  4. Run the exact same task again.
  5. Assert the target state is still correct (e.g., the table still has 10 rows, not 20).

```python
def test_load_to_db_is_idempotent(database_connection):
    """
    Tests that the 'load_to_db' task is idempotent.
    This is an integration test.
    """
    # Arrange
    task = my_dag.get_task("load_to_db")

    # Act 1: Run the task the first time
    task.execute(context={})

    # Assert 1: Check the state
    count1 = database_connection.execute("SELECT COUNT(*) FROM target_table").scalar()
    assert count1 == 100

    # Act 2: Run the task a second time
    task.execute(context={})

    # Assert 2: Check the state again
    count2 = database_connection.execute("SELECT COUNT(*) FROM target_table").scalar()
    assert count2 == 100, "Task is not idempotent; row count changed on second run."
```