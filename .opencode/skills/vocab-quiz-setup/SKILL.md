---
name: vocab-quiz-setup
description: Patterns for adding a new quiz type (model → seed → API → frontend) to the English Verb Trainer
---

## When to use

Use this skill when you need to add a new quiz modality to the app — for example, a vocabulary quiz, a grammar quiz, or any new question type that needs database models, seed data, API endpoints, and frontend screens.

## Architecture overview

A new quiz feature touches these 5 layers:

```
app/models.py          ← ORM model + attempt log table
app/{new}_seed.py      ← seed data + seed function
app/cli.py             ← CLI command to invoke seed
api/schemas.py         ← Pydantic request/response models
api/main.py            ← FastAPI endpoints (quiz, attempt, stats, seed)
static/index.html      ← SPA screens, JS state/API/quiz logic
docker/entrypoint.sh   ← auto-seed on container start
```

## Step-by-step

### 1. Add ORM models (`app/models.py`)

Add two tables: one for the "question" entities, one for logging user attempts.

**Question entity model** — NO unique constraint on the "display" column if words can repeat across categories:

```python
class VocabularyWord(Base):
    __tablename__ = "vocabulary_words"

    id = Column(Integer, primary_key=True, index=True)
    english = Column(String(100), nullable=False, index=True)  # no unique=True
    spanish = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False, index=True)

    attempts: Mapped[list["VocabAttempt"]] = relationship(
        "VocabAttempt", back_populates="word", cascade="all, delete-orphan"
    )
```

**Attempt log model:**

```python
class VocabAttempt(Base):
    __tablename__ = "vocab_attempts"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("vocabulary_words.id"), nullable=False)
    answer_given = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)

    word: Mapped[Optional["VocabularyWord"]] = relationship(
        "VocabularyWord", back_populates="attempts"
    )
```

### 2. Create seed data + function (`app/{new}_seed.py`)

**Seed data** — list of tuples at module level:

```python
# fmt: off
VOCABULARY_WORDS = [
    ("english", "spanish", "category"),
    ...
]
# fmt: on
```

**Seed function** — CRITICAL: pre-load existing entries into a Python dict to avoid SQLAlchemy's bulk-INSERT batching issue (unflushed rows are invisible to subsequent `filter_by` queries within the same transaction):

```python
def seed_vocabulary(
    db: Session,
    word_list: list[tuple] | None = None,
) -> tuple[int, int]:
    from app.models import VocabularyWord

    words = VOCABULARY_WORDS if word_list is None else word_list

    existing_map: dict[tuple[str, str], VocabularyWord] = {
        (w.english, w.category): w  # type: ignore
        for w in db.query(VocabularyWord).all()
    }

    seen: set[tuple[str, str]] = set()
    added = updated = 0
    new_words: list[VocabularyWord] = []

    for english, spanish, category in words:
        key = (english, category)
        if key in seen:
            continue
        seen.add(key)

        existing = existing_map.get(key)
        if existing:
            if existing.spanish != spanish:
                existing.spanish = spanish
                updated += 1
        else:
            new_words.append(VocabularyWord(...))
            added += 1

    db.add_all(new_words)
    db.commit()
    return added, updated
```

Key rules:
- Use a composite key `(display_value, category)` as the dedup key
- Pre-load ALL existing rows into `existing_map` BEFORE iterating
- Use a `seen` set to skip duplicates within the seed list itself
- DO NOT use `unique=True` on the display column if the same word appears across categories
- If you DO need `unique=True` for some column, use `db.flush()` after each `db.add()` — but this is slow for large seeds

### 3. Add CLI command (`app/cli.py`)

```python
@app.command(name="vocab-seed")
def vocab_seed():
    """Load the vocabulary words into the database."""
    _init_db()
    db = SessionLocal()
    try:
        added, updated = seed_vocabulary(db)
        typer.echo(f"\n  {added} word(s) added, {updated} updated.\n")
    finally:
        db.close()
```

**IMPORTANT**: Import the new model BEFORE calling `_init_db()` so the table is created:

```python
from app.models import Verb, VocabAttempt, VocabularyWord  # VocabularyWord must be imported
from app.vocab_seed import seed_vocabulary
```

### 4. Add Pydantic schemas (`api/schemas.py`)

```python
class VocabQuizWord(BaseModel):
    id: int
    english: str
    spanish: str
    category: str

class VocabAttemptRequest(BaseModel):
    word_id: int = Field(..., gt=0)
    answer_given: str

class VocabAttemptResponse(BaseModel):
    correct: bool
    correct_answer: str

class VocabCategory(BaseModel):
    name: str
    count: int
```

### 5. Add API endpoints (`api/main.py`)

You typically need 4-5 endpoints:

```python
# 1. Categories (for menu)
@router.get("/api/vocab/categories")
def get_vocab_categories(db: Session = Depends(get_db)):
    rows = db.query(VocabularyWord.category, func.count(VocabularyWord.id)) \
        .group_by(VocabularyWord.category).all()
    return [VocabCategory(name=row[0], count=row[1]) for row in rows]

# 2. Quiz words (shuffled)
@router.get("/api/vocab/quiz")
def get_vocab_quiz_words(count=10, category=None, db: Session = Depends(get_db)):
    query = db.query(VocabularyWord)
    if category:
        query = query.filter(VocabularyWord.category == category)
    words = query.all()
    random.shuffle(words)
    return [VocabQuizWord(id=w.id, english=w.english, spanish=w.spanish, category=w.category)
            for w in words[:count]]

# 3. Submit attempt
@router.post("/api/vocab/attempts")
def submit_vocab_attempt(attempt: VocabAttemptRequest, db: Session = Depends(get_db)):
    word = db.query(VocabularyWord).filter(VocabularyWord.id == attempt.word_id).first()
    if not word:
        raise HTTPException(status_code=404, ...)
    is_correct = attempt.answer_given.strip().lower() == word.english.strip().lower()
    db.add(VocabAttempt(word_id=word.id, answer_given=attempt.answer_given, is_correct=is_correct))
    db.commit()
    return VocabAttemptResponse(correct=is_correct, correct_answer=word.english)

# 4. Stats
@router.get("/api/vocab/stats")
def get_vocab_stats(db: Session = Depends(get_db)):
    total = db.query(VocabAttempt).count()
    correct = db.query(VocabAttempt).filter(VocabAttempt.is_correct.is_(True)).count()
    wrong = total - correct
    accuracy = round((correct / total) * 100, 1) if total > 0 else 0.0
    # hardest words query with join + group_by + order_by count desc
    ...

# 5. Seed (admin endpoint, catches IntegrityError → 409, OperationalError → 503, Exception → 500)
@router.post("/api/vocab/seed")
def seed_vocab_endpoint(db: Session = Depends(get_db)):
    try:
        added, updated = seed_vocabulary(db)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="...")
    ...
    return VocabSeedResponse(added=added, updated=updated)
```

### 6. Add frontend screens (`static/index.html`)

**State management:**

```js
const state = {
  // quiz-specific state:
  currentVocabWords: [],
  currentVocabIndex: 0,
  vocabResults: [],
  vocabError: '',
};
```

**API wrappers** — wrapped in `api*` helpers that call `fetch()` and extract `body.detail` on errors via a shared helper:

```js
async function apiErr(r) {
  const body = await r.json().catch(() => ({}));
  return body.detail || `HTTP ${r.status}`;
}

async function apiVocabCategories() { ... }
async function apiVocabQuizWords(count, category) { ... }
async function apiVocabAttempt(word_id, answer_given) { ... }
async function apiVocabStats() { ... }
async function apiVocabSeed() { ... }
```

**Screens** (each screen is a `<div id="screen-{name}" class="screen">`):
- Menu screen: list of categories as buttons
- Quiz screen: shows prompt (Spanish word), text input, submit button
- Result screen: shows score and per-word breakdown
- Stats screen: shows total attempts, accuracy, hardest words

**Quiz flow logic** (example for Spanish→English vocab quiz):

```js
async function startVocabQuiz(category) {
  state.currentVocabWords = await apiVocabQuizWords(10, category);
  state.currentVocabIndex = 0;
  state.vocabResults = [];
  showVocabQuestion();
}

function showVocabQuestion() {
  const word = state.currentVocabWords[state.currentVocabIndex];
  // Display word.spanish, wait for user to type english, then call submitVocabAnswer()
}

async function submitVocabAnswer() {
  const word = state.currentVocabWords[state.currentVocabIndex];
  const result = await apiVocabAttempt(word.id, userInput);
  state.vocabResults.push({ word, correct: result.correct, correctAnswer: result.correct_answer });
  state.currentVocabIndex++;
  if (state.currentVocabIndex < state.currentVocabWords.length) {
    showVocabQuestion();
  } else {
    showVocabResults();
  }
}
```

### 7. Auto-seed in Docker (`docker/entrypoint.sh`)

```sh
echo "📖 Seeding vocabulary words..."
python -m app.cli vocab-seed
```

Place AFTER the irregular verb seed but BEFORE the server starts. The script uses `set -e`, so any seed failure will cause the container to exit.

## Docker rebuild workflow

| Change type | Command |
|-------------|---------|
| Python code or entrypoint | `make rebuild` (runs `docker compose up -d --build`) |
| Static files only | `make up` (volume mount picks changes instantly) |

Docker compose file is at `docker/docker-compose.yml`. Always use `make rebuild` for Python changes.

## Common pitfalls

### SQLAlchemy bulk INSERT batching
`db.add()` does NOT immediately execute SQL. All unflushed rows are batched into a single multi-row `INSERT` on `db.commit()`. If any row violates a unique constraint, **the entire INSERT fails** and the transaction is aborted.

**Fix**: Pre-load existing rows into a Python `dict` keyed by your dedup key before iterating. Never rely on `filter_by(...).first()` to detect duplicates within the same transaction.

### Unique constraint on multi-category words
If the same English word appears in different categories with different Spanish meanings, do NOT use `unique=True` on the `english` column. Instead, deduplicate at the Python level using `(english, category)` as the key.

### Migration without Alembic
The project does NOT use Alembic. Add manual SQL migrations in `app/database.py::run_migrations()`:

```python
with engine.connect() as conn:
    is_unique = conn.execute(
        text("SELECT i.indisunique FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid "
             "WHERE c.relname = 'ix_vocabulary_words_english'")
    ).scalar()
    if is_unique:
        conn.execute(text("DROP INDEX ix_vocabulary_words_english"))
        conn.execute(text("CREATE INDEX ix_vocabulary_words_english ON vocabulary_words (english)"))
        conn.commit()
```

### `noRenderLoop` guard
The frontend uses an `if (noRenderLoop) return;` guard at the top of render functions to prevent re-entrant rendering during state updates. Always check this when adding new render functions.

### Error message display pattern
Success messages auto-hide after 3s. Error messages persist (only removed on manual dismiss or next action). Use `.vocab-msg-success` / `.vocab-msg-error` classes.

### Quiz answer comparison
Always `.strip().lower()` on both sides when comparing text answers.
