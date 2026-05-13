# Testing Guide

How to write and run tests for the project.

## Overview

The project uses **pytest** for unit testing with **in-memory SQLite** for test isolation (no PostgreSQL needed).

```
tests/test_quiz.py  → 18+ unit tests
Coverage: 70%+ required
Test time: <1 second
```

---

## Running Tests

### All Tests

```bash
pytest tests/ -v
```

Output:
```
tests/test_quiz.py::TestVerbCheckAnswer::test_correct_lowercase PASSED
tests/test_quiz.py::TestVerbCheckAnswer::test_correct_uppercase PASSED
...
======================== 18 passed in 0.97s ============================
```

### Specific Test

```bash
# Single test
pytest tests/test_quiz.py::TestVerbCheckAnswer::test_correct_lowercase -v

# Test class
pytest tests/test_quiz.py::TestVerbCheckAnswer -v

# Pattern
pytest tests/ -k "test_correct" -v  # Runs tests matching "correct"
```

### With Coverage

```bash
pytest tests/ -v --cov=app --cov-report=term-missing

# HTML report
pytest tests/ -v --cov=app --cov-report=html
open htmlcov/index.html
```

### Verbose Output

```bash
# Show print statements
pytest tests/ -v -s

# Show locals on failure
pytest tests/ -v -l
```

### Stop on First Failure

```bash
pytest tests/ -v -x  # Exit after first failure
pytest tests/ -v --lf  # Run last failed
```

---

## Test Structure

### Test File: `tests/test_quiz.py`

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Verb, UserAttempt
from app.quiz import validate_and_log, get_stats

# ─── Setup ───────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def db():
    """In-memory SQLite session for fast, isolated tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

# ─── Tests ───────────────────────────────────────────────────────

class TestVerbCheckAnswer:
    def test_correct_lowercase(self, db):
        verb = Verb(base="read", past="read", participle="read")
        db.add(verb)
        db.commit()

        assert verb.check_answer("read", "read") is True
```

---

## Fixtures

### Database Fixture

```python
from sqlalchemy.pool import StaticPool

@pytest.fixture
def db():
    """In-memory SQLite for test isolation."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session  # Test uses this
    session.close()  # Cleanup
```

> `StaticPool` is required for tests that use `TestClient` or `CliRunner`,
> since ASGI/Click invocations may run in a different thread. Without it,
> SQLite's in-memory database creates a new empty database per connection,
> causing "no such table" errors.

### Sample Data Fixtures

```python
@pytest.fixture
def sample_verb(db):
    """Create a verb for testing."""
    verb = Verb(base="read", past="read", participle="read")
    db.add(verb)
    db.commit()
    db.refresh(verb)  # Refresh to get ID
    return verb

# Usage in test
def test_something(sample_verb):
    assert sample_verb.id is not None
```

### Multiple Fixtures

```python
@pytest.fixture
def verb_with_alternatives(db):
    """Verb with alternative forms."""
    verb = Verb(
        base="learn",
        past="learned",
        participle="learned",
        past_alt="learnt",
        participle_alt="learnt"
    )
    db.add(verb)
    db.commit()
    return verb

def test_alt_forms(verb_with_alternatives):
    assert verb_with_alternatives.check_answer("learnt", "learnt")
    assert verb_with_alternatives.check_answer("learned", "learned")
```

---

## Test Examples

### Unit Test: Model

```python
class TestVerbModel:
    def test_check_answer_case_insensitive(self, sample_verb):
        """Verb.check_answer should be case-insensitive."""
        assert sample_verb.check_answer("READ", "READ") is True
        assert sample_verb.check_answer("read", "read") is True
        assert sample_verb.check_answer("Read", "Read") is True

    def test_check_answer_accepts_alternatives(self, verb_with_alternatives):
        """Should accept both primary and alternative forms."""
        # Primary forms
        assert verb_with_alternatives.check_answer("learned", "learned")
        # Alternative forms
        assert verb_with_alternatives.check_answer("learnt", "learnt")
        # Mixed
        assert verb_with_alternatives.check_answer("learned", "learnt")
```

### Unit Test: Business Logic

```python
class TestValidateAndLog:
    def test_correct_answer_logged(self, db, sample_verb):
        """validate_and_log should record correct attempts."""
        result = validate_and_log(db, sample_verb, "read", "read")

        assert result is True

        attempt = db.query(UserAttempt).first()
        assert attempt is not None
        assert attempt.is_correct is True
        assert attempt.past_given == "read"

    def test_wrong_answer_logged(self, db, sample_verb):
        """validate_and_log should record incorrect attempts."""
        result = validate_and_log(db, sample_verb, "readed", "readed")

        assert result is False

        attempt = db.query(UserAttempt).first()
        assert attempt.is_correct is False
```

### Unit Test: Statistics

```python
class TestGetStats:
    def test_stats_calculation(self, db, sample_verb):
        """Statistics should calculate accurately."""
        # Create attempts: 2 correct, 1 wrong
        validate_and_log(db, sample_verb, "read", "read")   # Correct
        validate_and_log(db, sample_verb, "readed", "read") # Wrong
        validate_and_log(db, sample_verb, "read", "read")   # Correct

        stats = get_stats(db)

        assert stats["total"] == 3
        assert stats["correct"] == 2
        assert stats["wrong"] == 1
        assert stats["accuracy"] == pytest.approx(66.67, 0.1)
```

---

## Parametrized Tests

### Test Multiple Cases

```python
@pytest.mark.parametrize("past,participle,expected", [
    ("read", "read", True),
    ("READ", "READ", True),
    ("readed", "readed", False),
    ("read", "readed", False),
])
def test_check_answer_cases(sample_verb, past, participle, expected):
    assert sample_verb.check_answer(past, participle) == expected
```

### Matrix Testing

```python
@pytest.mark.parametrize("verb_base", ["read", "go", "take"])
@pytest.mark.parametrize("rounds", [1, 5, 10])
def test_quiz_various_verbs(db, verb_base, rounds):
    """Test quiz with different verbs and round counts."""
    # Create test verbs...
    # Run quiz...
    # Assert...
    pass
```

---

## Mocking & Patching

### Mock External Calls

```python
from unittest.mock import Mock, patch

@patch("app.database.SessionLocal")
def test_quiz_with_mocked_db(mock_session):
    """Mock database calls."""
    mock_session.return_value = Mock()

    # Test code that uses SessionLocal
    # mock_session is the fake
```

### Exception Testing

```python
def test_invalid_verb_id_raises(db):
    """Should raise when verb doesn't exist."""
    with pytest.raises(ValueError):
        get_verb_by_id(db, 9999)
```

---

## Test Organization

### By Module

```
tests/
├── test_api.py            # FastAPI endpoint tests (TestClient)
├── test_cli.py            # Typer CLI command tests (CliRunner)
├── test_quiz.py           # app/quiz.py unit tests
├── test_seed.py           # app/seed.py unit tests
└── conftest.py            # Shared fixtures (db, sample_verb, etc.)
```

### By Class

```python
# Group related tests
class TestVerbModel:
    def test_...

class TestUserAttemptModel:
    def test_...

class TestQuizFunctions:
    def test_...
```

---

## Best Practices

### ✅ DO

- **One assertion per test** (when possible)
  ```python
  def test_correct_answer(self, sample_verb):
      assert sample_verb.check_answer("read", "read") is True
  ```

- **Clear test names** that describe what's tested
  ```python
  def test_check_answer_is_case_insensitive(self):
      # Clear: tests case insensitivity
  ```

- **Use fixtures** for setup
  ```python
  def test_with_fixture(self, sample_verb):
      # sample_verb already created
  ```

- **Test edge cases**
  ```python
  def test_empty_string():
      assert verb.check_answer("", "") is False
  ```

### ❌ DON'T

- **Multiple assertions** (hard to debug)
  ```python
  def test_many_things(self):
      assert a == 1
      assert b == 2
      assert c == 3
  ```

- **Vague test names**
  ```python
  def test_works(self):  # Unclear!
  ```

- **Test implementation details**
  ```python
  def test_internal_variable(self):
      assert obj._internal_var == 5  # Don't test private
  ```

- **Hardcoded values without explanation**
  ```python
  assert len(list) == 42  # Why 42? Explain!
  ```

---

## Coverage Requirements

### Minimum: 70%

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

Output:
```
app/database.py         50%   coverage  [Missing: 16, 36-40, 45-55]
app/models.py          100%   coverage
app/quiz.py            100%   coverage
app/seed.py            100%   coverage
TOTAL                   88%   coverage
```

### Improve Coverage

1. **Identify uncovered lines**
   ```bash
   pytest tests/ --cov=app --cov-report=html
   open htmlcov/app_quiz_py.html  # See missing lines
   ```

2. **Write tests for uncovered lines**
   ```python
   def test_edge_case_on_line_45(self):
       # Write test that exercises line 45
   ```

3. **Rerun coverage**
   ```bash
   pytest tests/ --cov=app --cov-report=term-missing
   ```

---

## Integration Tests (Future)

Once infrastructure is ready:

```python
@pytest.mark.integration
def test_quiz_flow_with_real_postgres(integration_db):
    """Test complete flow with PostgreSQL."""
    # Setup
    verb = Verb(base="go", past="went", participle="gone")
    integration_db.add(verb)
    integration_db.commit()

    # Test
    result = validate_and_log(integration_db, verb, "went", "gone")

    # Assert
    assert result is True
    attempt = integration_db.query(UserAttempt).first()
    assert attempt.is_correct is True
```

Run only integration tests:
```bash
pytest tests/ -m integration
```

---

## CI/CD Testing

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request
- Before releasing (tag push)

View results:
```
https://github.com/YOUR_USERNAME/english-verb-trainer/actions
```

---

## Debugging Tests

### Run with Print Output

```bash
pytest tests/ -v -s

# -s = show prints
```

### Drop into Debugger

```bash
pytest tests/ -v --pdb

# Press 'c' to continue, 'q' to quit
```

### Print Test Info

```python
def test_debug(capsys, sample_verb):
    print(f"Verb: {sample_verb.base}")

    # ... test code ...

    captured = capsys.readouterr()
    print(captured.out)
```

---

## Performance

### Benchmark

```python
import time

def test_get_shuffled_verbs_performance(db):
    """Verify shuffling is fast."""
    start = time.time()
    for _ in range(100):
        get_shuffled_verbs(db, limit=10)
    elapsed = time.time() - start

    assert elapsed < 1.0  # Should be <1 second
```

### Profile

```bash
pytest tests/ --profile
# Generates profile data
```

---

## Continuous Testing

Auto-run tests on file change:

```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run on save
ptw tests/

# Stop: Ctrl+C
```

---

## See Also

- [Development Setup](setup.md)
- [Contributing Guide](contributing.md)
- [pytest Documentation](https://docs.pytest.org/)
