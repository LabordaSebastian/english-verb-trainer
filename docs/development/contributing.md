# Contributing Guide

How to contribute to the English Verb Trainer project.

## Welcome! 👋

We're excited you want to contribute. This guide explains the process.

---

## Code of Conduct

- Be respectful to all contributors
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

---

## Getting Started

### 1. Fork the Repository

Click "Fork" on GitHub to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/english-verb-trainer.git
cd english-verb-trainer
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/LabordaSebastian/english-verb-trainer.git
git fetch upstream
```

### 4. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming:
- `feature/` — new feature
- `fix/` — bug fix
- `docs/` — documentation
- `chore/` — maintenance

---

## Making Changes

### 1. Set Up Development Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
pip install pre-commit
pre-commit install
```

### 2. Make Your Changes

Edit code, add tests, update docs.

### 3. Run Tests & Linting

```bash
# Format code
ruff format .

# Check lint
ruff check . --fix

# Type checking
mypy app/ api/

# Run tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=app --cov-report=term-missing
```

All must pass before committing.

### 4. Commit with Conventional Commits

Follow this format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat** — New feature
- **fix** — Bug fix
- **docs** — Documentation
- **style** — Code style (formatting, semicolons, etc.)
- **refactor** — Code refactoring
- **perf** — Performance improvement
- **test** — Adding/updating tests
- **chore** — Maintenance (dependencies, config)
- **ci** — CI/CD changes

### Examples

```bash
git commit -m "feat(quiz): add verb filtering by difficulty"
git commit -m "fix(cli): handle missing database connection gracefully"
git commit -m "docs: add architecture documentation"
git commit -m "test: add coverage for edge cases"
git commit -m "refactor(api): extract validation to separate module"
```

### With Details

```
git commit -m "feat(quiz): add verb filtering by difficulty

- Users can now filter verbs by difficulty level
- Added difficulty column to Verb model
- Updated quiz endpoint to support ?difficulty=hard

Closes #42"
```

---

## Pull Request Process

### 1. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 2. Create Pull Request

On GitHub:
- **Title**: Follow conventional commits
- **Description**: Explain what, why, and how
- **Link issues**: "Closes #42"

### PR Template

```markdown
## Description

What does this PR do?

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing

How did you test this?

- [ ] Added unit tests
- [ ] Ran existing tests
- [ ] Manual testing

## Checklist

- [ ] Code follows style guidelines (ruff)
- [ ] Type hints added (mypy)
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Coverage maintained (70%+)
- [ ] Commit messages are clear
```

### 3. Review Process

- Maintainers review changes
- May request updates
- Address feedback
- Push changes (auto-updates PR)

### 4. Merge

Maintainer merges when approved.

---

## What to Contribute

### Good First Issues

Look for "good first issue" label:
```
https://github.com/LabordaSebastian/english-verb-trainer/labels/good%20first%20issue
```

### Feature Ideas

- New quiz modes
- Statistics visualizations
- Performance improvements
- Documentation improvements

### Bug Reports

Found a bug? Open an issue with:
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment** (OS, Python version, etc.)

---

## Code Style Guidelines

### Python Style

Follow [PEP 8](https://pep8.org/):

```python
# ✅ Good
def validate_answer(user_input: str, correct_answer: str) -> bool:
    """Validate if user's answer is correct.

    Args:
        user_input: The user's submitted answer
        correct_answer: The correct answer

    Returns:
        True if answers match (case-insensitive), False otherwise
    """
    return user_input.lower() == correct_answer.lower()


# ❌ Bad
def validate(x,y):
    return x.lower()==y.lower()  # Missing spaces, no docstring
```

### Type Hints

```python
# ✅ Good
from typing import Optional

def get_verb(db: Session, base: str) -> Optional[Verb]:
    return db.query(Verb).filter_by(base=base).first()

# ❌ Bad
def get_verb(db, base):
    return db.query(Verb).filter_by(base=base).first()
```

### Docstrings

```python
# ✅ Good
def calculate_accuracy(correct: int, total: int) -> float:
    """Calculate accuracy percentage.

    Args:
        correct: Number of correct answers
        total: Total number of attempts

    Returns:
        Accuracy as percentage (0-100)

    Raises:
        ValueError: If total is 0
    """
    if total == 0:
        raise ValueError("Total must be greater than 0")
    return (correct / total) * 100
```

### Comments

```python
# ✅ Good - explains WHY
# Use GROUP BY instead of N+1 query for performance
hardest = db.query(Verb.base, func.count(...)).group_by(Verb.base)

# ❌ Bad - explains WHAT (code already does this)
# Group by verb base
```

---

## Testing Requirements

### Unit Tests Required For

- New functions
- Bug fixes
- Logic changes

### Test Template

```python
def test_new_feature():
    """Test that new feature works as expected."""
    # Arrange
    setup_data()

    # Act
    result = function_under_test()

    # Assert
    assert result == expected_value
```

### Coverage Minimum

- 70% overall
- 80% for new code
- 90% for critical paths

Check coverage:
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Documentation

### When to Update Docs

- New features
- Changed behavior
- New endpoints
- Bug fixes affecting users

### How to Update Docs

1. Edit `.md` files in `docs/`
2. Follow existing format
3. Test with MkDocs:
   ```bash
   mkdocs serve
   # Opens http://localhost:8000/docs
   ```

### Documentation Standards

- Clear and concise
- Code examples included
- Links to related docs
- Include diagrams where helpful

---

## Performance Considerations

### Before Optimization

- Add tests first
- Benchmark current behavior
- Profile to find bottlenecks

### Optimization Guidelines

```python
# ✅ Good - justified, benchmarked
# Using set lookup O(1) instead of list search O(n)
valid_forms = {primary.lower(), alt.lower() if alt else None}
return user_input.lower() in valid_forms

# ❌ Bad - premature optimization without justification
```

---

## Security Considerations

### When Contributing

- No hardcoded secrets
- Validate input
- Use parameterized queries (SQLAlchemy does this)
- Sanitize output (Pydantic does this)

### Security Sensitive Changes

- Mark PR as `security`
- Request maintainer review
- Don't disclose vulnerabilities publicly before fix

---

## Release Process (for maintainers)

Releases follow semantic versioning: `MAJOR.MINOR.PATCH`

```bash
# Create version tag
git tag v1.0.0

# Push to trigger CD
git push origin v1.0.0

# CD workflow:
# 1. Runs tests
# 2. Builds Docker image
# 3. Pushes to registry
# 4. Creates GitHub release
```

---

## Common Questions

### Q: I don't know where to start

**A**: Look for "good first issue" or pick a small documentation fix.

### Q: How long until my PR is reviewed?

**A**: Usually 1-3 days. Feel free to comment if it's taking longer.

### Q: Can I work on multiple issues?

**A**: Yes! Create separate branches for each.

### Q: Do I need permission to fork?

**A**: No, anyone can fork. That's the whole point!

### Q: My PR was rejected. What now?

**A**: It's ok! Read feedback, make changes, resubmit. Everyone learns this way.

---

## Resources

- [GitHub Documentation](https://docs.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## Thanks! 🙏

Every contribution makes the project better. Thank you for helping!

---

Questions? Open an issue or discussion on GitHub.
