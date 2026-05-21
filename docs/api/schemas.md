# Pydantic Schemas

Data validation and serialization models.

## Overview

[Pydantic](https://docs.pydantic.dev/) automatically validates request/response data based on type hints. Found in `api/schemas.py`.

## Request Schemas

### AttemptRequest

User's submitted quiz answer.

```python
class AttemptRequest(BaseModel):
    verb_id: int = Field(..., gt=0)
    past_given: str
    participle_given: str
```

**Example**:
```json
{
  "verb_id": 42,
  "past_given": "read",
  "participle_given": "read"
}
```

**Validation**:
- `verb_id` must be a positive integer (`gt=0`)
- `past_given` must be a string (required)
- `participle_given` must be a string (required)

**Errors if**:
- Missing any required field → 422 Unprocessable Entity
- `verb_id <= 0` → 422 (must be positive)
- `verb_id` is not a number → auto-conversion fails

---

## Response Schemas

### QuizVerb

Verb data sent to the browser for a quiz question.

```python
class QuizVerb(BaseModel):
    id: int
    base: str
    meaning: str | None
```

**Example**:
```json
{
  "id": 1,
  "base": "go",
  "meaning": "ir"
}
```

**Fields**:
- `id` — Database ID (used for submissions)
- `base` — Base form (infinitive) — what the quiz shows the user
- `meaning` — Spanish translation for context (optional)

**Note**: Does **NOT** include `past` or `participle` — those are hidden during the quiz!

---

### AttemptResponse

Result of submitting a quiz answer.

```python
class AttemptResponse(BaseModel):
    correct: bool
    correct_past: str
    correct_participle: str
    also_accepted: str | None
```

**Examples**:

=== "Correct Answer"
    ```json
    {
      "correct": true,
      "correct_past": "read",
      "correct_participle": "read",
      "also_accepted": null
    }
    ```

=== "Incorrect Answer"
    ```json
    {
      "correct": false,
      "correct_past": "went",
      "correct_participle": "gone",
      "also_accepted": null
    }
    ```

=== "With Alternative Forms"
    ```json
    {
      "correct": true,
      "correct_past": "learned",
      "correct_participle": "learned",
      "also_accepted": "learned / learnt → learned / learnt"
    }
    ```

**Fields**:
- `correct` — Boolean: was the answer correct?
- `correct_past` — The correct past tense form
- `correct_participle` — The correct past participle form
- `also_accepted` — Alternative acceptable forms (if any)

---

### StatsResponse

User statistics and progress.

```python
class HardestVerb(BaseModel):
    verb: str
    errors: int


class StatsResponse(BaseModel):
    total: int
    correct: int
    wrong: int
    accuracy: float
    hardest_verbs: list[HardestVerb]
```

**Example**:
```json
{
  "total": 47,
  "correct": 32,
  "wrong": 15,
  "accuracy": 68.09,
  "hardest_verbs": [
    {"verb": "go", "errors": 5},
    {"verb": "take", "errors": 3},
    {"verb": "read", "errors": 2}
  ]
}
```

**Fields**:
- `total` — Total attempts across all quizzes
- `correct` — Number of correct answers
- `wrong` — Number of incorrect answers
- `accuracy` — Percentage (0-100), rounded to 1 decimal
- `hardest_verbs` — List of `HardestVerb` objects (up to 5 verbs with most errors)

**Calculations**:
```python
accuracy = (correct / total) * 100  if total > 0 else 0.0
wrong = total - correct
```

---

### SeedResponse

Result of seeding the database with verbs.

```python
class SeedResponse(BaseModel):
    added: int
    updated: int
```

**Example**:
```json
{
  "added": 50,
  "updated": 50
}
```

**Fields**:
- `added` — Number of new verbs inserted
- `updated` — Number of existing verbs refreshed

**Behavior**:
- First seed: `added=100, updated=0`
- Subsequent seeds: `added=0, updated=100` (all exist)

---

## Type Hints & Validation

### Optional Fields

```python
meaning: str | None  # Can be string or None
also_accepted: str | None  # Can be string or None
```

In JSON:
```json
{
  "meaning": "ir",
  "also_accepted": null
}
```

### Typed Models

```python
hardest_verbs: list[HardestVerb]  # List of typed objects
```

Each `HardestVerb` has:
- `verb: str` — The verb's base form
- `errors: int` — Number of incorrect attempts

### Automatic Type Conversion

Pydantic automatically converts JSON types to Python types:

| JSON | Python | Pydantic Converts |
|------|--------|-------------------|
| `42` | `int` | ✓ |
| `"42"` | `int` | ✓ (if possible) |
| `null` | `None` | ✓ |
| `"true"` | `bool` | ✓ |
| `[]` | `list` | ✓ |

---

## Validators

### Built-in Field Constraints

```python
from pydantic import Field

class AttemptRequest(BaseModel):
    verb_id: int = Field(..., gt=0)  # Must be positive
    past_given: str
    participle_given: str
```

Using `Field(gt=0)` is equivalent to a custom validator but more concise — Pydantic enforces it automatically.

### Future Validators

Potential additions:

```python
from pydantic import field_validator

class AttemptRequest(BaseModel):
    verb_id: int = Field(..., gt=0)
    past_given: str
    participle_given: str

    @field_validator("past_given", "participle_given")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()
```

---

## Serialization

When Pydantic models are returned from FastAPI endpoints, they're automatically serialized to JSON:

```python
# Python
attempt = AttemptResponse(
    correct=True,
    correct_past="read",
    correct_participle="read",
    also_accepted=None
)

# Auto-converted to JSON by FastAPI
{
  "correct": true,
  "correct_past": "read",
  "correct_participle": "read",
  "also_accepted": null
}
```

---

## JSON Schema

Pydantic automatically generates JSON Schema, available at:

```
GET /openapi.json
```

Example (partial):
```json
{
  "AttemptRequest": {
    "type": "object",
    "properties": {
      "verb_id": {"type": "integer"},
      "past_given": {"type": "string"},
      "participle_given": {"type": "string"}
    },
    "required": ["verb_id", "past_given", "participle_given"]
  }
}
```

---

## Integration with FastAPI

### Request Validation

```python
@app.post("/api/attempts")
def submit_attempt(attempt: AttemptRequest):  # Pydantic validates
    # Only reaches here if validation passed
    # attempt.verb_id, attempt.past_given guaranteed to be correct types
    return AttemptResponse(...)
```

### Response Validation & Documentation

```python
@app.get("/api/stats", response_model=StatsResponse)
def get_stats_endpoint():
    # Return value must match StatsResponse schema
    # FastAPI auto-generates /docs swagger from this
    return StatsResponse(...)
```

---

## Error Responses

If validation fails, Pydantic returns 422 Unprocessable Entity:

```
Request: POST /api/attempts
Body: {"verb_id": "not_a_number"}

Response: 422 Unprocessable Entity
{
  "detail": [
    {
      "loc": ["body", "verb_id"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

---

## Testing Schemas

Unit tests validate schemas:

```python
def test_attempt_request_valid():
    data = {"verb_id": 1, "past_given": "read", "participle_given": "read"}
    attempt = AttemptRequest(**data)
    assert attempt.verb_id == 1

def test_attempt_request_invalid():
    data = {"verb_id": "invalid"}
    with pytest.raises(ValidationError):
        AttemptRequest(**data)
```

---

---

## Vocabulary Schemas

### VocabQuizWord

Word data sent to the browser for a vocabulary quiz question.

```python
class VocabQuizWord(BaseModel):
    id: int
    english: str
    spanish: str
    category: str
```

**Example**:
```json
{
  "id": 1,
  "english": "beautiful",
  "spanish": "hermoso/a",
  "category": "Adjectives"
}
```

**Note**: The quiz shows `spanish` to the user and expects `english` as the answer.

---

### VocabAttemptRequest

User's submitted vocabulary answer.

```python
class VocabAttemptRequest(BaseModel):
    word_id: int = Field(..., gt=0)
    answer_given: str
```

**Example**:
```json
{
  "word_id": 1,
  "answer_given": "beautiful"
}
```

---

### VocabAttemptResponse

Result of submitting a vocabulary answer.

```python
class VocabAttemptResponse(BaseModel):
    correct: bool
    correct_answer: str
```

**Example**:
```json
{
  "correct": true,
  "correct_answer": "beautiful"
}
```

---

### VocabCategory

Category summary for the vocabulary menu.

```python
class VocabCategory(BaseModel):
    name: str
    count: int
```

**Example**:
```json
{
  "name": "Adjectives",
  "count": 150
}
```

---

### HardestWord

A single entry in the hardest-words vocabulary ranking.

```python
class HardestWord(BaseModel):
    word: str
    spanish: str
    errors: int
```

**Example**:
```json
{
  "word": "beautiful",
  "spanish": "hermoso/a",
  "errors": 5
}
```

---

### VocabStatsResponse

Vocabulary quiz statistics.

```python
class VocabStatsResponse(BaseModel):
    total: int
    correct: int
    wrong: int
    accuracy: float
    hardest_words: list[HardestWord]
```

**Example**:
```json
{
  "total": 47,
  "correct": 32,
  "wrong": 15,
  "accuracy": 68.09,
  "hardest_words": [
    {"word": "beautiful", "spanish": "hermoso/a", "errors": 5}
  ]
}
```

---

### VocabSeedResponse

Result of seeding vocabulary words.

```python
class VocabSeedResponse(BaseModel):
    added: int
    updated: int
```

**Example**:
```json
{
  "added": 1867,
  "updated": 0
}
```

---

## See Also

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Request Bodies](https://fastapi.tiangolo.com/tutorial/body/)
- [API Endpoints Reference](endpoints.md)
