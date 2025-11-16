---
name: Python API Client Design
description: Best practices for designing robust and resilient API clients in Python.
globs:
- '**/*.py'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- python
- api
- client
- requests
- standards
- resilience
author: prompt-manager
language: python
---
# Python API Client Design

This document provides best practices for designing Python clients that interact with external HTTP APIs. Adhering to these standards ensures that API interactions are robust, resilient, performant, and maintainable.

## 1. Use Session Objects

- **Principle**: Use a `requests.Session` object (for synchronous code) or an `httpx.AsyncClient` (for asynchronous code) instead of making direct calls like `requests.get()`.
- **Benefit**:
  - **Connection Pooling**: Session objects reuse the underlying TCP connection, which significantly improves performance for applications that make multiple requests to the same host.
  - **Configuration**: Allows you to configure default headers, authentication, and other settings for a group of requests.

```python
# Good: Using a Session object
import requests

class MyApiClient:
    def __init__(self, base_url: str, api_key: str):
        self.session = requests.Session()
        self.session.base_url = base_url
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def get_item(self, item_id: int):
        response = self.session.get(f"/items/{item_id}")
        response.raise_for_status()
        return response.json()

# Bad: Not using a Session object
def get_item_bad(item_id: int):
    # A new TCP connection is established for every call, which is inefficient.
    response = requests.get(f"https://api.example.com/items/{item_id}")
    # ...
```

## 2. Implement Retry Logic with Exponential Backoff

- **Principle**: Network requests can fail for transient reasons (e.g., temporary network glitch, rate limiting). Automatically retry failed requests.
- **Exponential Backoff**: Increase the delay between retries exponentially to avoid overwhelming the server.
- **Implementation**: Use a library like `tenacity` or implement a custom decorator. Only retry on specific, safe-to-retry errors (e.g., 5xx server errors, connection errors), not on 4xx client errors.

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from requests.exceptions import RequestException

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry_error_callback=lambda retry_state: retry_state.outcome.result()
)
def make_resilient_request(url: str):
    response = requests.get(url)
    # Only retry on server errors or connection issues
    if 500 <= response.status_code < 600:
        response.raise_for_status()
    return response
```

## 3. Handle HTTP Status Codes Gracefully

- **Principle**: Your code must check the HTTP status code of the response and handle it appropriately.
- **`raise_for_status()`**: Use `response.raise_for_status()` to automatically raise an `HTTPError` for 4xx and 5xx responses.
- **Specific Handling**: Catch specific status codes for more granular logic (e.g., handle `404 Not Found` differently from `403 Forbidden`).

```python
def get_resource(resource_id: int):
    try:
        response = session.get(f"/resources/{resource_id}")
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None # Or raise a custom ResourceNotFoundError
        elif e.response.status_code == 403:
            raise PermissionError("Permission denied for this resource.")
        else:
            # Re-raise for other HTTP errors
            raise
```

## 4. Use Custom Exceptions

- **Principle**: Create a hierarchy of custom exceptions for your API client.
- **Benefit**: Allows consumers of your client to handle specific API-related errors gracefully, without having to parse generic `HTTPError` exceptions.

```python
class ApiClientError(Exception):
    """Base exception for this API client."""
    pass

class AuthenticationError(ApiClientError):
    """Raised for 401 or 403 errors."""
    pass

class ResourceNotFoundError(ApiClientError):
    """Raised for 404 errors."""
    pass
```

## 5. Centralize Configuration and Authentication

- **Configuration**: Do not hardcode URLs, endpoints, or other configuration. Pass them into the client's constructor or load them from a central configuration source.
- **Authentication**: Encapsulate authentication logic within the client. The caller should not have to worry about how to add an API key or refresh a token.

## 6. Timeouts

- **Principle**: Always specify a `timeout` for all network requests.
- **Reason**: Prevents your application from hanging indefinitely if the remote server is unresponsive.
- **Implementation**: Set a `timeout` in seconds on the request call (e.g., `requests.get(url, timeout=10)`).

```python
try:
    response = session.get("/slow-endpoint", timeout=5)
except requests.Timeout:
    # Handle timeout error
    raise ApiClientError("The request timed out.")
```