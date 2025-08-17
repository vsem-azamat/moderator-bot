# Testing Guide

This document provides comprehensive guidance for testing the moderator-bot project. Our testing strategy follows industry best practices with multiple test levels and comprehensive coverage.

## 📋 Testing Strategy

### Test Pyramid

Our testing approach follows the test pyramid with:

- **Unit Tests (70%)** - Fast, isolated tests for individual components
- **Integration Tests (20%)** - Test interactions between components
- **End-to-End Tests (10%)** - Full workflow tests

### Test Categories

- **Unit Tests** (`tests/unit/`) - Test individual functions, classes, and methods
- **Integration Tests** (`tests/integration/`) - Test database operations and service integrations
- **End-to-End Tests** (`tests/e2e/`) - Test complete user workflows
- **Performance Tests** (`tests/performance/`) - Test performance and scalability

## 🚀 Quick Start

### Running Tests

```bash
# Install dependencies
uv sync --dev

# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit          # Unit tests only
uv run pytest tests/integration   # Integration tests only
uv run pytest tests/e2e          # End-to-end tests only

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run performance tests
uv run pytest tests/performance -m "performance and not slow"
```

### Test Markers

We use pytest markers to categorize tests:

```bash
# Run by marker
uv run pytest -m unit           # Unit tests
uv run pytest -m integration    # Integration tests
uv run pytest -m e2e           # End-to-end tests
uv run pytest -m performance   # Performance tests
uv run pytest -m "not slow"    # Exclude slow tests
```

## 🏗️ Test Structure

### Directory Layout

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── factories.py             # Test data factories
├── unit/                    # Unit tests
│   ├── test_domain_entities.py
│   ├── test_value_objects.py
│   ├── test_user_service.py
│   └── test_moderation_service.py
├── integration/             # Integration tests
│   ├── test_user_repository.py
│   └── test_chat_repository.py
├── e2e/                     # End-to-end tests
│   └── test_user_workflow.py
└── performance/             # Performance tests
    └── test_repository_performance.py
```

### Test Fixtures

Key fixtures available in all tests:

- `session` - Database session for tests
- `user_repository` - User repository instance
- `chat_repository` - Chat repository instance
- `admin_repository` - Admin repository instance
- `sample_user_data` - Sample user data dictionary
- `sample_chat_data` - Sample chat data dictionary

## ✨ Test Factories

We use factory patterns for creating test data:

```python
from tests.factories import UserFactory, ChatFactory, AdminFactory

# Create single entities
user = UserFactory.create(username="testuser")
chat = ChatFactory.create_with_welcome("Welcome message")
admin = AdminFactory.create_inactive()

# Create batches
users = UserFactory.create_batch(10)
chats = ChatFactory.create_batch(5, is_forum=True)

# Create specialized entities
blocked_user = UserFactory.create_blocked()
forum_chat = ChatFactory.create_forum()
```

## 🧪 Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.user_service import UserService
from tests.factories import UserFactory

class TestUserService:
    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_user_repository: AsyncMock) -> UserService:
        return UserService(mock_user_repository)

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self,
        user_service: UserService,
        mock_user_repository: AsyncMock
    ):
        # Arrange
        user_id = 123456789
        expected_user = UserFactory.create(id=user_id)
        mock_user_repository.get_by_id.return_value = expected_user

        # Act
        result = await user_service.get_user_by_id(user_id)

        # Assert
        assert result == expected_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
```

### Integration Test Example

```python
import pytest
from app.domain.repositories import IUserRepository
from tests.factories import UserFactory

@pytest.mark.integration
class TestUserRepositoryIntegration:
    async def test_save_and_get_user(
        self,
        user_repository: IUserRepository
    ):
        # Arrange
        user = UserFactory.create()

        # Act
        saved_user = await user_repository.save(user)
        retrieved_user = await user_repository.get_by_id(user.id)

        # Assert
        assert saved_user.id == user.id
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
```

### End-to-End Test Example

```python
import pytest
from app.application.services.user_service import UserService

@pytest.mark.e2e
class TestUserWorkflowE2E:
    async def test_complete_user_lifecycle(
        self,
        user_repository: IUserRepository
    ):
        user_service = UserService(user_repository)

        # Create user
        user = await user_service.create_or_update_user(
            user_id=123456789,
            username="testuser"
        )

        # Block user
        blocked_user = await user_service.block_user(user.id)
        assert blocked_user.is_blocked is True

        # Unblock user
        unblocked_user = await user_service.unblock_user(user.id)
        assert unblocked_user.is_blocked is False
```

## 📊 Test Coverage

### Coverage Requirements

- **Minimum Coverage**: 60%
- **Target Coverage**: 90%+
- **Critical Paths**: 100% (domain entities, core services)

### Checking Coverage

```bash
# Generate coverage report
uv run pytest --cov=app --cov-report=html

# View HTML report
open htmlcov/index.html

# Check specific thresholds
uv run pytest --cov=app --cov-fail-under=60
```

### Coverage Configuration

Coverage settings in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__main__.py",
    "*/migrations/*",
]

[tool.coverage.report]
show_missing = true
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

## 🔧 Testing Best Practices

### 1. Test Organization

- **One test class per production class**
- **Descriptive test names** that explain what is being tested
- **Group related tests** in classes
- **Use meaningful assertions** with clear error messages

### 2. Test Data

- **Use factories** instead of hardcoded data
- **Create minimal test data** needed for the test
- **Isolate test data** - each test should be independent
- **Clean up after tests** - use fixtures for setup/teardown

### 3. Mocking Guidelines

- **Mock external dependencies** (databases, APIs, file systems)
- **Don't mock the system under test**
- **Use AsyncMock for async functions**
- **Verify mock interactions** when behavior matters

### 4. Async Testing

```python
# Always mark async tests
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None

# Use AsyncMock for async dependencies
@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=IUserRepository)
```

### 5. Error Testing

```python
# Test exception scenarios
@pytest.mark.asyncio
async def test_user_not_found_raises_exception(user_service):
    with pytest.raises(UserNotFoundException) as exc_info:
        await user_service.get_user_by_id(999999)

    assert exc_info.value.user_id == 999999
```

## 🚀 Performance Testing

### Running Performance Tests

```bash
# Quick performance tests
uv run pytest tests/performance -m "performance and not slow"

# Full performance suite (slow)
uv run pytest tests/performance -m "performance" --maxfail=1

# With profiling
uv run pytest tests/performance --profile --profile-svg
```

### Performance Test Guidelines

- **Use realistic data sizes**
- **Test concurrent operations**
- **Monitor memory usage**
- **Set reasonable performance thresholds**
- **Mark slow tests** with `@pytest.mark.slow`

## 🏃‍♂️ Continuous Integration

### GitHub Actions

Our CI pipeline runs:

1. **Code Quality Checks**
   - Linting with ruff
   - Type checking with mypy
   - Security scanning

2. **Test Execution**
   - Unit tests
   - Integration tests
   - End-to-end tests
   - Coverage reporting

3. **Performance Testing** (on main branch)
   - Performance benchmarks
   - Memory usage analysis

### Pre-commit Hooks

Install pre-commit hooks:

```bash
uv run pre-commit install
```

This will run before each commit:
- Code formatting
- Linting
- Type checking
- Quick test suite

## 🐛 Debugging Tests

### Common Issues

1. **Database State** - Tests affecting each other
   ```python
   # Solution: Use proper fixtures and rollbacks
   @pytest.fixture
   async def session():
       async with session_factory() as session:
           yield session
           await session.rollback()
   ```

2. **Async/Await Issues** - Missing async markers
   ```python
   # Wrong
   def test_async_function():
       result = await some_function()

   # Correct
   @pytest.mark.asyncio
   async def test_async_function():
       result = await some_function()
   ```

3. **Mock Configuration** - Incorrect mock setup
   ```python
   # Use proper specs
   mock_repo = AsyncMock(spec=IUserRepository)

   # Verify calls
   mock_repo.save.assert_called_once_with(expected_user)
   ```

### Debug Tools

```bash
# Run with verbose output
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Show local variables on failure
uv run pytest -l

# Run specific test with debugging
uv run pytest tests/unit/test_user_service.py::TestUserService::test_get_user_by_id -v -s
```

## 📈 Test Metrics

### Key Metrics We Track

- **Test Coverage** - Code coverage percentage
- **Test Speed** - Average test execution time
- **Test Reliability** - Flaky test detection
- **Performance Benchmarks** - Operation throughput

### Monitoring

- **Coverage reports** uploaded to Codecov
- **Performance trends** tracked over time
- **Test reliability** monitored in CI

## 🎯 Testing Checklist

Before submitting a PR, ensure:

- [ ] All tests pass locally
- [ ] New features have corresponding tests
- [ ] Test coverage meets minimum threshold (80%)
- [ ] Integration tests cover happy path and error cases
- [ ] Performance-critical code has performance tests
- [ ] Tests are properly documented and maintainable
- [ ] Pre-commit hooks pass
- [ ] CI pipeline passes

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

*This testing guide is part of the moderator-bot project. Keep it updated as testing practices evolve.*
