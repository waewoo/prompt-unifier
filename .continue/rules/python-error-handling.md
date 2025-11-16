---
name: Python Error Handling and Logging Standards
description: Best practices for exception handling, error propagation, and logging
  in Python applications
globs:
- '*.py'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- python
- error-handling
- logging
- exceptions
- debugging
author: prompt-manager
language: python
---
# Python Error Handling and Logging Standards

## Overview

This document defines standards for error handling, exception management, and logging in Python applications. Proper error handling ensures robustness, debuggability, and excellent user experience.

## Exception Handling

### Core Principles

1. **Be Specific**: Catch specific exceptions, not generic `Exception`
2. **Fail Fast**: Validate inputs early and fail immediately on invalid data
3. **Clean Propagation**: Let exceptions propagate when you can't handle them meaningfully
4. **Context Preservation**: Use `raise from` to maintain exception chains
5. **Resource Cleanup**: Always clean up resources (use context managers)

### Exception Hierarchy

#### Custom Exceptions

Define custom exceptions for domain-specific errors:

```python
class ApplicationError(Exception):
    """Base exception for all application errors."""
    pass


class ValidationError(ApplicationError):
    """Raised when data validation fails."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.field = field


class ResourceNotFoundError(ApplicationError):
    """Raised when a requested resource doesn't exist."""

    def __init__(self, resource_type: str, resource_id: int | str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(message)


class AuthenticationError(ApplicationError):
    """Raised when authentication fails."""
    pass


class PermissionDeniedError(ApplicationError):
    """Raised when user lacks required permissions."""

    def __init__(self, action: str, resource: str):
        self.action = action
        self.resource = resource
        message = f"Permission denied: cannot {action} {resource}"
        super().__init__(message)
```

### Exception Catching Best Practices

#### ✅ Good Exception Handling

```python
def read_config_file(path: Path) -> dict:
    """Read and parse configuration file.

    Args:
        path: Path to configuration file

    Returns:
        Parsed configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid YAML
    """
    try:
        content = path.read_text()
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {path}")
        raise  # Re-raise, caller should handle

    try:
        config = yaml.safe_load(content)
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in config file: {path}")
        raise ValueError(f"Invalid configuration format: {e}") from e

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a YAML object/dict")

    return config
```

#### ❌ Poor Exception Handling

```python
# Don't catch generic Exception
def bad_example1():
    try:
        risky_operation()
    except Exception:  # Too broad!
        pass  # Silently swallowing errors!

# Don't catch without re-raising when you can't handle
def bad_example2():
    try:
        important_operation()
    except ValueError as e:
        print(f"Error: {e}")  # Logged but not handled!
        # Should re-raise or handle properly

# Don't lose exception context
def bad_example3():
    try:
        parse_data(raw_data)
    except ValueError:
        raise RuntimeError("Parsing failed")  # Lost original exception!
```

### Exception Chaining

Use `raise from` to preserve exception context:

```python
def fetch_user_data(user_id: int) -> dict:
    """Fetch user data from API.

    Raises:
        ResourceNotFoundError: If user doesn't exist
        ConnectionError: If API is unreachable
    """
    try:
        response = requests.get(f"{API_URL}/users/{user_id}")
        response.raise_for_status()
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise ResourceNotFoundError("User", user_id) from e
        raise
    except requests.ConnectionError as e:
        logger.error(f"API connection failed: {e}")
        raise ConnectionError("Unable to reach user API") from e

    return response.json()
```

### Multiple Exception Types

```python
def process_file(path: Path) -> ProcessedData:
    """Process data file with comprehensive error handling."""
    try:
        data = read_file(path)
        validated = validate_data(data)
        return transform_data(validated)

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise

    except PermissionError:
        logger.error(f"Permission denied reading file: {path}")
        raise

    except ValidationError as e:
        logger.warning(f"Validation failed for {path}: {e}")
        raise

    except Exception as e:
        # Catch-all only for unexpected errors
        logger.exception(f"Unexpected error processing {path}")
        raise RuntimeError(f"Failed to process file: {path}") from e
```

### Context Managers for Cleanup

Always use context managers for resource management:

```python
# ✅ Good - Automatic cleanup
def process_file(path: Path) -> str:
    """Process file with automatic resource cleanup."""
    with open(path) as f:
        return f.read().upper()


# ✅ Good - Custom context manager
from contextlib import contextmanager
from typing import Generator

@contextmanager
def database_transaction(db: Database) -> Generator[Transaction, None, None]:
    """Context manager for database transactions with automatic rollback."""
    transaction = db.begin()
    try:
        yield transaction
        transaction.commit()
        logger.info("Transaction committed successfully")
    except Exception as e:
        transaction.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise


# Usage
def transfer_funds(from_account: int, to_account: int, amount: float) -> None:
    """Transfer funds between accounts with transaction safety."""
    with database_transaction(db) as txn:
        debit(from_account, amount, txn)
        credit(to_account, amount, txn)
```

### Suppressing Exceptions (Rarely)

Only suppress exceptions when truly appropriate:

```python
from contextlib import suppress

# Acceptable use case: cleanup operations
def cleanup_temp_files(temp_dir: Path) -> None:
    """Clean up temporary files, ignoring errors."""
    with suppress(FileNotFoundError, PermissionError):
        shutil.rmtree(temp_dir)
    logger.debug(f"Cleaned up temporary directory: {temp_dir}")


# Better alternative with explicit handling
def cleanup_temp_files_explicit(temp_dir: Path) -> None:
    """Clean up temporary files with explicit error handling."""
    try:
        shutil.rmtree(temp_dir)
        logger.debug(f"Cleaned up temporary directory: {temp_dir}")
    except FileNotFoundError:
        logger.debug(f"Temp directory already removed: {temp_dir}")
    except PermissionError as e:
        logger.warning(f"Cannot remove temp directory: {temp_dir} - {e}")
```

## Logging

### Logging Setup

#### Module-level Logger

```python
import logging
from pathlib import Path

# Get logger for this module
logger = logging.getLogger(__name__)


def configure_logging(log_file: Path | None = None, level: str = "INFO") -> None:
    """Configure application logging.

    Args:
        log_file: Optional path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper())

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_formatter = logging.Formatter(
        fmt="%(levelname)s: %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all details
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
```

### Log Levels

Use appropriate log levels:

- **DEBUG**: Detailed diagnostic information for developers
- **INFO**: General informational messages about application flow
- **WARNING**: Warning about potential issues, but application continues
- **ERROR**: Error occurred, but application can continue
- **CRITICAL**: Critical error, application may not be able to continue

```python
def process_orders(orders: list[Order]) -> ProcessingResult:
    """Process batch of orders with comprehensive logging."""
    logger.info(f"Starting to process {len(orders)} orders")

    processed = 0
    failed = 0

    for order in orders:
        logger.debug(f"Processing order {order.id}")

        try:
            validate_order(order)
            result = submit_order(order)
            processed += 1
            logger.info(f"Order {order.id} processed successfully")

        except ValidationError as e:
            failed += 1
            logger.warning(f"Order {order.id} validation failed: {e}")

        except PaymentError as e:
            failed += 1
            logger.error(f"Payment failed for order {order.id}: {e}")

        except Exception as e:
            failed += 1
            logger.exception(f"Unexpected error processing order {order.id}")
            # logger.exception automatically includes stack trace

    logger.info(
        f"Order processing complete. "
        f"Processed: {processed}, Failed: {failed}"
    )

    return ProcessingResult(processed=processed, failed=failed)
```

### Structured Logging

Use structured logging for better searchability:

```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)


def authenticate_user(username: str, ip_address: str) -> User | None:
    """Authenticate user with structured logging."""
    logger.info(
        "authentication_attempt",
        username=username,
        ip_address=ip_address
    )

    user = get_user(username)
    if not user:
        logger.warning(
            "authentication_failed",
            reason="user_not_found",
            username=username,
            ip_address=ip_address
        )
        return None

    logger.info(
        "authentication_successful",
        user_id=user.id,
        username=username,
        ip_address=ip_address
    )

    return user
```

### Best Practices

#### ✅ Good Logging

```python
# Use f-strings for formatting
logger.info(f"User {user_id} logged in from {ip_address}")

# Use lazy evaluation for expensive operations
logger.debug("Request data: %s", expensive_serialization(data))

# Include context in error logs
logger.error(
    f"Failed to send email to {recipient}",
    extra={"email": recipient, "template": template_name}
)

# Use logger.exception for unexpected errors (includes stack trace)
try:
    risky_operation()
except Exception:
    logger.exception("Unexpected error in risky_operation")
```

#### ❌ Poor Logging

```python
# Don't use print statements
print(f"Processing user {user_id}")  # Use logger.info

# Don't log sensitive information
logger.info(f"User password: {password}")  # NEVER log passwords!
logger.debug(f"Credit card: {cc_number}")  # NEVER log PII!

# Don't concatenate strings (use f-strings or lazy %)
logger.info("User " + str(user_id) + " logged in")  # Inefficient

# Don't catch and only log
try:
    important_operation()
except ValueError as e:
    logger.error(f"Error: {e}")  # Should re-raise or handle!
```

### Sensitive Data Filtering

```python
import re
from typing import Any

def sanitize_log_data(data: dict[str, Any]) -> dict[str, Any]:
    """Remove sensitive information from log data."""
    sensitive_fields = {"password", "token", "api_key", "secret", "credit_card"}

    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_fields:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        else:
            sanitized[key] = value

    return sanitized


# Usage
logger.info(f"User data: {sanitize_log_data(user_data)}")
```

## Error Recovery Strategies

### Retry Logic

```python
import time
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar('T')

def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry function on failure with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts: {func.__name__}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            # Should not reach here, but for type checker
            raise last_exception  # type: ignore

        return wrapper
    return decorator


# Usage
@retry_on_failure(
    max_attempts=3,
    delay=1.0,
    exceptions=(requests.ConnectionError, requests.Timeout)
)
def fetch_api_data(url: str) -> dict:
    """Fetch data from API with automatic retry on network errors."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Circuit Breaker Pattern

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: datetime | None = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker reset to CLOSED state")

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
```

## References

- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [PEP 3134 - Exception Chaining](https://peps.python.org/pep-3134/)
- [Python Exception Handling Best Practices](https://realpython.com/python-exceptions/)
- [Structlog Documentation](https://www.structlog.org/)