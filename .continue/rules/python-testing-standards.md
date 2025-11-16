---
name: Python Testing Standards
description: Comprehensive testing standards and best practices for Python projects
  using pytest
globs:
- test_*.py
- '*_test.py'
alwaysApply: false
category: standards
version: 1.0.0
tags:
- python
- testing
- pytest
- tdd
- quality-assurance
- coverage
author: prompt-manager
language: python
---
# Python Testing Standards

## Overview

This document defines testing standards for Python projects. All code must have comprehensive test coverage following these guidelines to ensure reliability and maintainability.

## Testing Philosophy

### Core Principles
1. **Test Behavior, Not Implementation**: Tests should validate what code does, not how it does it
2. **Tests as Documentation**: Tests should clearly demonstrate how to use the code
3. **Fast Feedback**: Tests should run quickly to enable frequent execution
4. **Isolation**: Each test should be independent and not rely on execution order
5. **Comprehensive Coverage**: Aim for 85%+ code coverage with meaningful tests

## Test Organization

### Directory Structure
```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       ├── services.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_api_integration.py
│   │   └── test_database_integration.py
│   └── e2e/
│       └── test_user_workflows.py
└── pyproject.toml
```

### Test File Naming
- **Unit tests**: `test_<module_name>.py` (e.g., `test_user_service.py`)
- **Integration tests**: `test_<feature>_integration.py`
- **E2E tests**: `test_<workflow>_e2e.py`
- Mirror source structure in test directory

### Test Function Naming

Use descriptive names following this pattern:
```
test_<function_name>_<condition>_<expected_result>
```

**Examples**:
```python
def test_calculate_total_with_valid_items_returns_sum():
    pass

def test_validate_email_with_invalid_format_raises_value_error():
    pass

def test_get_user_by_id_when_not_found_returns_none():
    pass

def test_authenticate_user_with_correct_password_returns_user_object():
    pass
```

## Test Structure

### AAA Pattern (Arrange-Act-Assert)

Every test should follow this structure:

```python
def test_create_user_with_valid_data_saves_to_database():
    """Test that valid user data is correctly saved to database."""
    # Arrange - Set up test data and preconditions
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "age": 25
    }
    repository = UserRepository(database_connection)

    # Act - Execute the function being tested
    result = repository.create_user(user_data)

    # Assert - Verify the expected outcome
    assert result.id is not None
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert repository.get_by_id(result.id) == result
```

### Test Classes for Grouping

Group related tests in classes:

```python
class TestUserAuthentication:
    """Test suite for user authentication functionality."""

    def test_authenticate_with_valid_credentials_returns_user(self):
        """Test successful authentication with correct credentials."""
        pass

    def test_authenticate_with_invalid_password_returns_none(self):
        """Test authentication fails with wrong password."""
        pass

    def test_authenticate_with_locked_account_raises_account_locked_error(self):
        """Test that locked accounts cannot authenticate."""
        pass


class TestPasswordHashing:
    """Test suite for password hashing utilities."""

    def test_hash_password_returns_different_hash_each_time(self):
        """Test password hashing uses salt (different hashes for same password)."""
        pass
```

## Fixtures

### Fixture Scope

Choose appropriate scope for fixtures:

- **function** (default): New instance for each test
- **class**: Shared within test class
- **module**: Shared within test module
- **session**: Shared across entire test session

```python
# conftest.py
import pytest
from myapp.database import Database
from myapp.models import User

@pytest.fixture(scope="session")
def database_connection():
    """Provide database connection for entire test session."""
    conn = Database.connect("sqlite:///:memory:")
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def sample_user():
    """Provide a fresh sample user for each test."""
    return User(
        username="testuser",
        email="test@example.com",
        age=30
    )

@pytest.fixture
def authenticated_client(sample_user):
    """Provide authenticated API client for testing."""
    client = APIClient()
    client.login(sample_user)
    return client
```

### Fixture Composition

Build complex fixtures from simpler ones:

```python
@pytest.fixture
def database():
    """Provide in-memory database."""
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()

@pytest.fixture
def user_repository(database):
    """Provide user repository with database."""
    return UserRepository(database)

@pytest.fixture
def sample_users(user_repository):
    """Provide several sample users in database."""
    users = [
        User(username="alice", email="alice@example.com"),
        User(username="bob", email="bob@example.com"),
        User(username="charlie", email="charlie@example.com"),
    ]
    for user in users:
        user_repository.save(user)
    return users
```

## Parametrization

### Testing Multiple Inputs

Use `@pytest.mark.parametrize` for testing multiple scenarios:

```python
import pytest

@pytest.mark.parametrize("email,expected_valid", [
    ("user@example.com", True),
    ("user.name@example.co.uk", True),
    ("user+tag@example.com", True),
    ("invalid.email", False),
    ("@example.com", False),
    ("user@", False),
    ("", False),
    (None, False),
])
def test_validate_email_format(email, expected_valid):
    """Test email validation with various formats."""
    result = validate_email(email)
    assert result == expected_valid
```

### Parametrizing Fixtures

```python
@pytest.fixture(params=["sqlite", "postgresql", "mysql"])
def database_connection(request):
    """Test with multiple database backends."""
    db_type = request.param
    conn = connect_database(db_type)
    yield conn
    conn.close()

def test_user_query_works_across_databases(database_connection):
    """Test that user queries work with all database types."""
    # This test runs 3 times, once for each database
    repo = UserRepository(database_connection)
    user = repo.get_by_id(1)
    assert user is not None
```

## Mocking

### When to Mock

Mock external dependencies:
- **Database queries** (for unit tests)
- **HTTP/API requests**
- **File system operations**
- **External services** (email, payment gateways)
- **Time-dependent functions**
- **Random number generation**

### Using unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock
import pytest

@patch('myapp.services.requests.get')
def test_fetch_user_data_from_api_handles_success(mock_get):
    """Test API data fetch handles successful response."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mock_get.return_value = mock_response

    # Act
    result = fetch_user_data(user_id=1)

    # Assert
    assert result["name"] == "Alice"
    mock_get.assert_called_once_with("https://api.example.com/users/1")


@patch('myapp.services.datetime')
def test_is_expired_with_past_date_returns_true(mock_datetime):
    """Test expiration check with mocked current time."""
    # Arrange
    mock_datetime.now.return_value = datetime(2024, 1, 15, 12, 0, 0)
    token = Token(expires_at=datetime(2024, 1, 10, 12, 0, 0))

    # Act
    result = token.is_expired()

    # Assert
    assert result is True
```

### Pytest-mock Plugin

Prefer `pytest-mock` for cleaner syntax:

```python
def test_send_email_calls_smtp_server(mocker):
    """Test email sending uses SMTP correctly."""
    # Arrange
    mock_smtp = mocker.patch('smtplib.SMTP')
    mock_instance = mock_smtp.return_value

    # Act
    send_email("test@example.com", "Subject", "Body")

    # Assert
    mock_instance.send_message.assert_called_once()
```

## Test Coverage

### Coverage Requirements

- **Minimum coverage**: 85% for all code
- **Critical paths**: 100% coverage (authentication, payment, security)
- **New code**: Must maintain or increase overall coverage

### Running Coverage

```bash
# Run tests with coverage
pytest --cov=myapp --cov-report=html --cov-report=term

# Coverage thresholds in pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=myapp --cov-fail-under=85"
```

### What to Cover

**Must Cover:**
- All public APIs and entry points
- Error handling and edge cases
- Business logic and calculations
- Data validation and transformations

**Can Skip:**
- Trivial getters/setters
- Framework boilerplate
- Third-party library code
- Explicitly marked as no-cover

```python
def trivial_getter(self):
    return self._value  # pragma: no cover

def experimental_feature(self):
    # pragma: no cover
    # This feature is experimental and not yet tested
    pass
```

## Test Categories

### Unit Tests

Test individual functions/methods in isolation:

```python
def test_calculate_discount_with_valid_code_applies_percentage():
    """Unit test for discount calculation logic."""
    # No database, no external calls, pure logic
    original_price = 100.0
    discount_code = "SAVE20"

    result = calculate_discount(original_price, discount_code)

    assert result == 80.0
```

### Integration Tests

Test interaction between components:

```python
def test_user_service_creates_user_and_sends_welcome_email(
    database_connection, email_service
):
    """Integration test for user creation workflow."""
    # Tests UserService, UserRepository, and EmailService together
    service = UserService(database_connection, email_service)

    user = service.create_user("test@example.com", "password")

    assert user.id is not None
    assert email_service.sent_emails[0].recipient == "test@example.com"
```

### End-to-End Tests

Test complete user workflows:

```python
def test_complete_user_registration_workflow(api_client):
    """E2E test for user registration process."""
    # Test entire workflow from API perspective
    response = api_client.post("/api/register", json={
        "email": "newuser@example.com",
        "password": "SecurePass123!" # pragma: allowlist secret
    })

    assert response.status_code == 201

    # Verify email was sent
    activation_link = get_last_email_link()
    response = api_client.get(activation_link)

    assert response.status_code == 200

    # Verify can login
    response = api_client.post("/api/login", json={
        "email": "newuser@example.com",
        "password": "SecurePass123!" # pragma: allowlist secret
    })

    assert response.status_code == 200
    assert "token" in response.json()
```

## Best Practices

### ✅ Do

- Write tests before fixing bugs (reproduce first)
- Test edge cases and boundary conditions
- Use descriptive test names and docstrings
- Keep tests simple and focused (one behavior per test)
- Use fixtures for common setup
- Mock external dependencies
- Assert specific values, not just truthy/falsy
- Test error conditions and exceptions

### ❌ Don't

- Write tests that depend on execution order
- Share mutable state between tests
- Test implementation details (private methods usually)
- Have tests with no assertions
- Catch exceptions without re-raising (unless testing error handling)
- Use sleep() for timing (use proper waiting/mocking)
- Hardcode sensitive data in tests

## Exception Testing

### Testing Expected Exceptions

```python
import pytest

def test_divide_by_zero_raises_zero_division_error():
    """Test that dividing by zero raises appropriate error."""
    with pytest.raises(ZeroDivisionError):
        result = 10 / 0

def test_invalid_user_age_raises_value_error_with_message():
    """Test validation raises error with specific message."""
    with pytest.raises(ValueError, match=r"Age must be between.*"):
        User(name="Test", age=-5)

def test_function_raises_multiple_possible_exceptions():
    """Test function can raise different exceptions."""
    with pytest.raises((ValueError, TypeError)):
        risky_function(None)
```

## Performance Testing

### Marking Slow Tests

```python
import pytest

@pytest.mark.slow
def test_large_dataset_processing():
    """Test processing of large dataset (marked as slow)."""
    data = generate_large_dataset(1_000_000)
    result = process_data(data)
    assert len(result) > 0

# Run without slow tests:
# pytest -m "not slow"
```

### Timeout for Tests

```python
@pytest.mark.timeout(5)
def test_api_request_completes_within_timeout():
    """Test API request doesn't hang indefinitely."""
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200
```

## Continuous Integration

### pytest Configuration

**pyproject.toml**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
addopts = [
    "--strict-markers",
    "--cov=myapp",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=85",
    "-v",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
]
```

### CI Pipeline

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run tests
        run: poetry run pytest

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-mock Plugin](https://pytest-mock.readthedocs.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Test-Driven Development (TDD)](https://testdriven.io/test-driven-development/)