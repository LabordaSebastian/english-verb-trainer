# Data Flow & Request Lifecycle

Detailed walkthrough of how data moves through the system.

## Complete Request Lifecycle: Quiz Answer Submission

### Scenario: User answers a quiz question via web UI

```
┌────────────────────────────────────────────────────────────┐
│ 1. USER INTERACTION (Frontend)                             │
└────────────────────────────────────────────────────────────┘

  User sees: "Base verb: READ"
  User types: "read read" (past + participle)
  User clicks: "Submit"

                    ▼

┌────────────────────────────────────────────────────────────┐
│ 2. HTTP REQUEST (Fetch API)                                │
└────────────────────────────────────────────────────────────┘

  POST /api/attempts
  Content-Type: application/json

  Body:
  {
    "verb_id": 42,
    "past_given": "read",
    "participle_given": "read"
  }

                    ▼

┌────────────────────────────────────────────────────────────┐
│ 3. FASTAPI ENDPOINT (api/main.py)                          │
└────────────────────────────────────────────────────────────┘

  @app.post("/api/attempts")
  def submit_attempt(attempt: AttemptRequest, db: Session):

  Step 1: Parse request
  - Pydantic validates JSON against AttemptRequest schema
  - Converts to Python types: verb_id: int, past_given: str

  Step 2: Get database session
  - SQLAlchemy SessionLocal factory creates session
  - Connected to PostgreSQL

  Step 3: Fetch verb from DB
  - SQL: SELECT * FROM verbs WHERE id = 42
  - Result: Verb(id=42, base="read", past="read", ...)

                    ▼

┌────────────────────────────────────────────────────────────┐
│ 4. BUSINESS LOGIC (app/quiz.py)                            │
└────────────────────────────────────────────────────────────┘

  validate_and_log(db, verb, "read", "read")

  Step 1: Validate answer
  - Call: verb.check_answer("read", "read")
  - Method: compare_case_insensitive(past_input, verb.past)
  - Result: (True, True) → correct!

  Step 2: Create UserAttempt record
  - UserAttempt(
      verb_id=42,
      past_given="read",
      participle_given="read",
      is_correct=True,
      attempted_at=datetime.now()
    )

  Step 3: Log to database
  - db.add(attempt)
  - db.commit()
  - SQL INSERT: INSERT INTO user_attempts (...) VALUES (...)

  Step 4: Return result
  - Return: True (correct)

                    ▼

┌────────────────────────────────────────────────────────────┐
│ 5. RESPONSE (FastAPI)                                      │
└────────────────────────────────────────────────────────────┘

  AttemptResponse(
    correct=True,
    correct_past="read",
    correct_participle="read",
    also_accepted=None
  )

  Pydantic serializes to JSON:
  {
    "correct": true,
    "correct_past": "read",
    "correct_participle": "read",
    "also_accepted": null
  }

  HTTP Response:
  Status: 200 OK
  Content-Type: application/json

                    ▼

┌────────────────────────────────────────────────────────────┐
│ 6. UI UPDATE (Frontend)                                    │
└────────────────────────────────────────────────────────────┘

  JavaScript receives response
  - Check: response.correct === true
  - Show: Correct feedback with verb forms
  - Move to next question
```

## Database Query Flow

### Getting a Quiz (GET /api/verbs/quiz)

```
Request: GET /api/verbs/quiz?count=10

1. FastAPI endpoint receives count=10
   ↓
2. Calls: get_shuffled_verbs(db, limit=10)
   ↓
3. SQLAlchemy Query:
   SELECT * FROM verbs
   Result: List of 100 Verb objects
   ↓
4. Python random.shuffle() on the list
   ↓
5. Return first 10 items: verbs[:10]
   ↓
6. For each verb, create QuizVerb:
   QuizVerb(id=verb.id, base=verb.base, meaning=verb.meaning)
   ↓
7. Return: List[QuizVerb]
   ↓
8. Pydantic serializes to JSON
   ↓
9. Response: 200 OK with [QuizVerb, ...]
```

### Getting Stats (GET /api/stats)

```
Request: GET /api/stats

1. Call: get_stats(db)
   ↓
2. Query 1: Count total attempts
   SELECT COUNT(*) FROM user_attempts
   Result: total = 47
   ↓
3. Query 2: Count correct attempts
   SELECT COUNT(*) FROM user_attempts WHERE is_correct = TRUE
   Result: correct = 32
   ↓
4. Query 3: Find hardest verbs
   SELECT verb.base, COUNT(*) as errors
   FROM user_attempts
   JOIN verbs ON user_attempts.verb_id = verbs.id
   WHERE is_correct = FALSE
   GROUP BY verb.base
   ORDER BY errors DESC
   LIMIT 5
   ↓
5. Result: [
      {verb: "go", errors: 5},
      {verb: "take", errors: 3},
      ...
   ]
   ↓
6. Calculate accuracy: (32/47) * 100 = 68.1%
   ↓
7. Return: {
      total: 47,
      correct: 32,
      wrong: 15,
      accuracy: 68.1,
      hardest_verbs: [...]
   }
```

## CLI Request Flow

### Running: python main.py quiz

```
1. main.py → app.command() decorator
   ↓
2. Typer calls quiz() function
   ↓
3. _init_db() → Create tables if needed
   ↓
4. SessionLocal() → Get database connection
   ↓
5. Display banner
   ↓
6. get_shuffled_verbs(db, limit=10)
   SQL: SELECT * FROM verbs
   ↓
7. For each verb (question_list):
   a) Display: "Base verb: READ"
   b) Prompt: "Your answer: "
   c) User input: "read read"
   d) validate_and_log(db, verb, "read", "read")
      - Check answer
      - Log to DB: INSERT INTO user_attempts
   e) Show result: ✅ or ❌
   ↓
8. Calculate: correct_count / total * 100
   ↓
9. Display: "Result: 8/10 correct (80%)"
   ↓
10. db.close()
```

## Seeding Database

### Running: python main.py seed

```
1. _init_db() → Create tables if needed
   ↓
2. seed_verbs(db)
   ↓
3. For each verb in IRREGULAR_VERBS tuple:
   a) Query: SELECT * FROM verbs WHERE base = 'go'
   b) If found (existing):
      - UPDATE verbs SET past=..., participle=...
      - Increment updated counter
   c) If not found:
      - CREATE Verb object
      - db.add(verb)
      - Increment added counter
   ↓
4. db.commit() → Persist all changes
   ↓
5. Return (added, updated)
   ↓
6. Display: "✅ 50 verb(s) added, 50 updated."
```

## Transaction Flow

### ACID Properties in SQLAlchemy

```
BEGIN TRANSACTION
│
├─ Step 1: Fetch verb from database
│  SELECT * FROM verbs WHERE id = 42
│  (Read Lock)
│
├─ Step 2: Check answer in Python
│  verb.check_answer("read", "read")
│  (No database involved)
│
├─ Step 3: Insert attempt
│  INSERT INTO user_attempts (...) VALUES (...)
│  (Write Lock)
│
├─ Step 4: Commit
│  db.commit()
│
└─ COMMIT / ROLLBACK

Atomicity:   Either all steps succeed or none
Consistency: Database remains valid state
Isolation:   Other connections don't see uncommitted data
Durability:  Data persists even if server crashes
```

## Error Handling Flow

### Invalid Answer Submission

```
Request: POST /api/attempts
Body: {verb_id: 999, past_given: "x", participle_given: "y"}

1. FastAPI receives request
   ↓
2. Pydantic validates schema
   All fields present ✓
   Types correct ✓
   ↓
3. Fetch verb: db.query(Verb).filter(id=999).first()
   Result: None (verb not found)
   ↓
4. Check: if not verb
   ↓
5. Raise: HTTPException(status_code=404, detail="Verb not found")
   ↓
6. FastAPI converts to HTTP response
   ↓
7. Response: 404 Not Found
   {
     "detail": "Verb id=999 not found"
   }
   ↓
8. JavaScript catches error
   ↓
9. UI displays: "Error: Verb not found"
```

### Database Connection Failure

```
main.py → _init_db()
   ↓
Try: Base.metadata.create_all(bind=engine)
   ↓
Except: OperationalError
   (PostgreSQL not running or unreachable)
   ↓
Catch: print error message
   "❌ Cannot connect to PostgreSQL"
   "Make sure the container is running"
   ↓
Raise: typer.Exit(code=1)
   ↓
CLI exits with status code 1
```

## Performance Considerations

### Query Optimization

```
❌ Inefficient:
for verb_id in [1, 2, 3, ..., 100]:
    verb = db.query(Verb).filter(id=verb_id).first()  # N+1 problem!

✅ Efficient:
verbs = db.query(Verb).all()  # 1 query
```

### Connection Pooling

```
SQLAlchemy automatically manages:
- Connection pool (default 5 connections)
- Connection reuse for subsequent queries
- Automatic connection cleanup
```

### Caching Opportunities

Currently no caching. In the future:
- Cache: List of all verbs (rarely changes)
- Cache: User stats (updated only when new attempt)
- Cache-Invalidation: On each new attempt

## Data Consistency

### Foreign Key Constraint

```
user_attempts.verb_id REFERENCES verbs.id

Benefit: Can't have orphaned attempts
If verb deleted: CASCADE delete removes attempts
If attempt created: Must have valid verb_id
```

### Unique Constraint

```
verbs.base UNIQUE NOT NULL

Benefit: Can't have duplicate verb entries
Prevents: Two "read" verbs in database
```
