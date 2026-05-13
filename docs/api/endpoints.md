# REST API Endpoints

Complete reference for all FastAPI endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently **none** (open API). All endpoints are publicly accessible.

## Response Format

All responses are JSON. Successful responses include the requested data. Errors include a detail message.

---

## Quiz Endpoints

### GET /api/verbs/quiz

Get shuffled verbs for a quiz session.

#### Request

```bash
GET /api/verbs/quiz?count=10
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | integer | 10 | Number of verbs to return |

#### Response (200 OK)

```json
[
  {
    "id": 1,
    "base": "go",
    "meaning": "ir"
  },
  {
    "id": 2,
    "base": "take",
    "meaning": "tomar / llevar"
  }
]
```

#### Response Schema

```python
class QuizVerb(BaseModel):
    id: int                    # Database ID
    base: str                  # Base form (infinitive)
    meaning: str | None        # Spanish meaning (for context)
```

#### Errors

| Status | Reason |
|--------|--------|
| `400` | `count` parameter not an integer |
| `404` | No verbs found in database |

#### Example

=== "cURL"
    ```bash
    curl http://localhost:8000/api/verbs/quiz?count=5
    ```

=== "Python"
    ```python
    import requests

    response = requests.get(
        "http://localhost:8000/api/verbs/quiz",
        params={"count": 5}
    )
    verbs = response.json()
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch("/api/verbs/quiz?count=5");
    const verbs = await response.json();
    ```

#### Notes

- Verbs are shuffled randomly each request
- No verb appears twice in a single response
- Response does **NOT** include correct answers (answer is hidden from UI)
- Each verb's "meaning" provides context during the quiz

---

### POST /api/attempts

Submit an answer and validate it.

#### Request

```bash
POST /api/attempts
Content-Type: application/json

{
  "verb_id": 42,
  "past_given": "read",
  "participle_given": "read"
}
```

#### Request Schema

```python
class AttemptRequest(BaseModel):
    verb_id: int               # ID from quiz endpoint
    past_given: str            # User's answer for past tense
    participle_given: str      # User's answer for past participle
```

#### Response (200 OK)

```json
{
  "correct": true,
  "correct_past": "read",
  "correct_participle": "read",
  "also_accepted": null
}
```

#### Response Schema

```python
class AttemptResponse(BaseModel):
    correct: bool              # Whether answer is correct
    correct_past: str          # Correct past tense form
    correct_participle: str    # Correct past participle form
    also_accepted: str | None  # Alternative forms (e.g., "learned / learnt")
```

#### Errors

| Status | Reason | Example |
|--------|--------|---------|
| `404` | Verb not found | `verb_id: 9999` doesn't exist |
| `422` | Validation error | Missing `past_given` field |

#### Side Effects

- Creates `UserAttempt` record in database
- Records timestamp of attempt
- Logs whether answer was correct

#### Example

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/api/attempts \
      -H "Content-Type: application/json" \
      -d '{
        "verb_id": 42,
        "past_given": "read",
        "participle_given": "read"
      }'
    ```

=== "Python"
    ```python
    import requests

    response = requests.post(
        "http://localhost:8000/api/attempts",
        json={
            "verb_id": 42,
            "past_given": "read",
            "participle_given": "read"
        }
    )
    result = response.json()
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch("/api/attempts", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        verb_id: 42,
        past_given: "read",
        participle_given: "read"
      })
    });
    const result = await response.json();
    ```

#### Notes

- Case-insensitive comparison
- Whitespace trimmed automatically
- Accepts alternative forms (stored in database)
- Every response includes correct answer (for UI feedback)

---

## Statistics Endpoints

### GET /api/stats

Get user statistics and progress.

#### Request

```bash
GET /api/stats
```

#### Response (200 OK)

```json
{
  "total": 47,
  "correct": 32,
  "wrong": 15,
  "accuracy": 68.1,
  "hardest_verbs": [
    {
      "verb": "go",
      "errors": 5
    },
    {
      "verb": "take",
      "errors": 3
    }
  ]
}
```

#### Response Schema

```python
class StatsResponse(BaseModel):
    total: int                 # Total attempts ever
    correct: int               # Correct attempts
    wrong: int                 # Incorrect attempts
    accuracy: float            # Percentage (0-100)
    hardest_verbs: list[dict]  # Top 5 verbs with most errors
```

#### Example

=== "cURL"
    ```bash
    curl http://localhost:8000/api/stats
    ```

=== "Python"
    ```python
    import requests

    response = requests.get("http://localhost:8000/api/stats")
    stats = response.json()
    print(f"Accuracy: {stats['accuracy']}%")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch("/api/stats");
    const stats = await response.json();
    console.log(`Accuracy: ${stats.accuracy}%`);
    ```

#### Notes

- Accuracy = (correct / total) * 100
- Returns 0.0 if no attempts yet
- Hardest verbs sorted by error count (descending)
- Resets only when database is cleared

---

## Admin Endpoints

### POST /api/seed

Load or refresh the irregular verbs database.

#### Request

```bash
POST /api/seed
```

#### Response (200 OK)

```json
{
  "added": 50,
  "updated": 50
}
```

#### Response Schema

```python
class SeedResponse(BaseModel):
    added: int                 # Verbs inserted
    updated: int               # Verbs already existed (refreshed)
```

#### Example

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/api/seed
    ```

=== "Python"
    ```python
    import requests

    response = requests.post("http://localhost:8000/api/seed")
    result = response.json()
    print(f"Added: {result['added']}, Updated: {result['updated']}")
    ```

#### Notes

- Idempotent — safe to call multiple times
- First call: `added=100, updated=0`
- Subsequent calls: `added=0, updated=100` (refresh)
- Runs automatically on app startup (via `entrypoint.sh`)

## Static File Serving

### GET /

Serve the web UI (Single Page Application).

#### Request

```bash
GET http://localhost:8000
```

#### Response (200 OK)

Returns `static/index.html` with the interactive web interface.

#### Notes

- Serves static assets: HTML, CSS, JavaScript
- SPA handles routing client-side
- All API requests go to `/api/*` endpoints

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing the problem"
}
```

### Common Errors

#### 404 Not Found

```json
{
  "detail": "Verb id=9999 not found"
}
```

**Causes**:
- Invalid `verb_id` in POST /api/attempts
- No verbs in database (seed first)

#### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["body", "past_given"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Causes**:
- Missing required fields
- Invalid data types

#### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

**Causes**:
- Database connection failure
- Unexpected exception

---

## API Documentation (Interactive)

### Swagger UI

Interactive API explorer at:

```
http://localhost:8000/docs
```

Try endpoints directly in your browser!

### ReDoc

Alternative documentation at:

```
http://localhost:8000/redoc
```

---

## Rate Limiting

Currently **none** (all requests allowed).

Future phases may implement:
- Per-IP rate limiting
- Per-user rate limiting
- Throttling for abusive requests

---

## Versioning

Current API version: **v1** (implicit)

Future versions (Phase 5+):
```
/api/v1/attempts
/api/v2/attempts  (if breaking changes)
```

---

## See Also

- [Pydantic Schemas](schemas.md) — Request/response models
- [Database Models](../database/models.md) — Data schema
- [CLI Reference](../cli-reference.md) — Terminal interface
