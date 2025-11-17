---
name: Python Concurrency Best Practices
description: Guidelines for writing concurrent and parallel code in Python using threading,
  asyncio, and multiprocessing.
globs:
- '**/*.py'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- python
- concurrency
- asyncio
- threading
- multiprocessing
- standards
author: prompt-unifier
language: python
---
# Python Concurrency Best Practices

This document provides guidelines for writing correct, efficient, and maintainable concurrent code in Python. Concurrency is a complex area where errors can be subtle and hard to debug.

## 1. Choosing the Right Concurrency Model

Select the appropriate model based on the type of task:

- **`asyncio`**:
  - **Use Case**: I/O-bound tasks (e.g., network requests, database queries, reading/writing files). Ideal for applications with many slow, external dependencies.
  - **Benefit**: High performance with thousands of concurrent operations using a single thread.
  - **Gotcha**: The entire call stack must be `async`. Blocking code will stall the event loop.

- **`threading`**:
  - **Use Case**: I/O-bound tasks where you cannot use `asyncio` (e.g., working with a library that does not support it).
  - **Benefit**: Simpler to integrate into existing blocking codebases.
  - **Gotcha**: Subject to the Global Interpreter Lock (GIL), so it does not provide true parallelism for CPU-bound tasks. Can be complex to manage shared state.

- **`multiprocessing`**:
  - **Use Case**: CPU-bound tasks (e.g., complex calculations, data processing, video encoding).
  - **Benefit**: Bypasses the GIL, providing true parallelism by using multiple CPU cores.
  - **Gotcha**: Higher memory overhead as each process has its own memory space. Inter-process communication is more complex than sharing memory between threads.

## 2. `asyncio` Best Practices

- **Use Async Libraries**: When writing `asyncio` code, use libraries designed for it (e.g., `httpx` instead of `requests`, `asyncpg` instead of `psycopg2`).
- **Avoid Blocking Calls**: Never use blocking I/O calls like `time.sleep()` or `requests.get()` in an `async` function. Use their async equivalents (`await asyncio.sleep()`, `await client.get(...)`).
- **Run Blocking Code in an Executor**: If you must run blocking code, use `loop.run_in_executor()` to run it in a separate thread pool without blocking the event loop.

```python
import asyncio
import requests

async def run_blocking_in_executor():
    loop = asyncio.get_running_loop()
    # Run the blocking 'requests.get' in a thread pool executor
    response = await loop.run_in_executor(
        None,  # Use the default executor
        requests.get,
        "https://example.com"
    )
    return response.status_code
```

- **Use `asyncio.gather`**: To run multiple awaitables concurrently and wait for all to complete, use `asyncio.gather`.

```python
async def main():
    results = await asyncio.gather(
        fetch_data("https://api.example.com/1"),
        fetch_data("https://api.example.com/2"),
    )
    # ... process results
```

## 3. `threading` and `multiprocessing` Best Practices

### Managing Shared State
- **Principle**: Whenever possible, avoid sharing state between threads or processes. If you must share state, protect it with locks.
- **Race Conditions**: A race condition occurs when multiple threads/processes access shared data and at least one of them modifies it. This can lead to unpredictable results.
- **Locks**: Use `threading.Lock` or `multiprocessing.Lock` to ensure that only one thread/process can access a critical section of code at a time.

```python
import threading

class Counter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:  # Use a context manager for the lock
            self.value += 1
```

### Using Thread-Safe Data Structures
- **Queues**: The `queue.Queue` class is thread-safe and is the preferred way to pass data between threads. It handles all the locking for you.

### Using Pools
- **`ThreadPoolExecutor` / `ProcessPoolExecutor`**: For managing a fixed number of worker threads or processes, use the high-level `concurrent.futures` module. It provides a simple interface for submitting tasks and retrieving results.

```python
from concurrent.futures import ThreadPoolExecutor

def my_io_task(url):
    # ... perform a network request ...
    return "done"

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(my_io_task, url) for url in urls]
    for future in concurrent.futures.as_completed(futures):
        print(future.result())
```