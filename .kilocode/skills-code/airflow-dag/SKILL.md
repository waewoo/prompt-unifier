---
name: airflow-dag
description: Guides creation of production-ready Apache Airflow DAGs and tasks following
  best practices for idempotency, observability, and maintainability.
mode: code
license: MIT
---
# Airflow DAG Skill

## When to Use

Apply this skill when:
- The user asks to create, write, or scaffold a new Airflow DAG
- The user asks to add a new task or operator to an existing DAG
- The user asks to review a DAG for best practices or production readiness
- The user asks "how should I structure this pipeline in Airflow?"

Do NOT apply when the user is asking about Airflow installation, cluster setup, or non-DAG Python code.

## DAG Structure Template

```python
from datetime import datetime, timedelta
from airflow.decorators import dag, task

DEFAULT_ARGS = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["alerts@example.com"],
}

@dag(
    dag_id="my_pipeline",
    description="Short description of what this DAG does",
    schedule="0 6 * * *",          # cron or @daily / @hourly
    start_date=datetime(2024, 1, 1),
    catchup=False,                  # never True in production unless backfill needed
    default_args=DEFAULT_ARGS,
    tags=["team", "domain"],
)
def my_pipeline():
    @task()
    def extract() -> list[dict]:
        ...

    @task()
    def transform(records: list[dict]) -> list[dict]:
        ...

    @task()
    def load(records: list[dict]) -> None:
        ...

    raw = extract()
    processed = transform(raw)
    load(processed)

my_pipeline()
```

## Mandatory Rules

### Idempotency
Every task must produce the same result when run multiple times with the same inputs.
- Delete before insert (not insert-only)
- Use `{{ ds }}` (execution date) as partition key, never `NOW()`
- Avoid side effects that accumulate on re-run

### No Business Logic in DAG File
DAG files orchestrate — they do not contain data transformation logic.
```python
# BAD — logic in DAG
@task()
def process():
    df = pd.read_csv(...)
    df["total"] = df["price"] * df["qty"]   # business logic
    df.to_parquet(...)

# GOOD — logic in a module
from my_pipeline.transformations import compute_totals

@task()
def process():
    compute_totals()
```

### Parameterisation with `Params`
```python
@dag(params={"env": "prod", "batch_size": 1000})
def my_pipeline():
    @task()
    def run(**context):
        env = context["params"]["env"]
        batch = context["params"]["batch_size"]
```

## Task Design

| Rule | Detail |
|---|---|
| Atomic | Each task does one thing and can be retried independently |
| Small | Prefer 5 small tasks over 1 large task |
| Stateless | Tasks pass data via XCom or external storage, not in-process state |
| Timeouts | Set `execution_timeout` on tasks that could hang |

```python
@task(execution_timeout=timedelta(hours=1))
def long_running_task():
    ...
```

## Sensors

Use sensors to wait for external conditions, not `time.sleep()`:

```python
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id="wait_for_file",
    filepath="/data/input/{{ ds }}/data.csv",
    poke_interval=60,
    timeout=3600,
    mode="reschedule",   # frees the worker slot while waiting
)
```

## Testing a DAG Locally

```bash
# List tasks
airflow tasks list my_pipeline

# Test a single task (does not write to metadata DB)
airflow tasks test my_pipeline extract 2024-01-01

# Trigger a full DAG run
airflow dags trigger my_pipeline --conf '{"env":"staging"}'
```

## Checklist Before Merging

- [ ] `catchup=False` unless backfill is explicitly needed
- [ ] `start_date` is a fixed past date, not `datetime.now()`
- [ ] All tasks are idempotent
- [ ] Retries and `retry_delay` are set
- [ ] DAG has `tags` for filtering in the UI
- [ ] No credentials hardcoded — use Airflow Connections/Variables
- [ ] Unit tests for transformation logic