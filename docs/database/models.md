# Database Models & Schema

SQLAlchemy ORM models and PostgreSQL table structure.

## Overview

The application uses **SQLAlchemy 2.0** as the ORM. Models are defined in `app/models.py` and automatically create tables in PostgreSQL.

## Verb Model

### Definition

```python
class Verb(Base):
    """Stores an irregular verb with its three forms."""

    __tablename__ = "verbs"

    id = Column(Integer, primary_key=True, index=True)
    base = Column(String(50), unique=True, nullable=False, index=True)
    past = Column(String(50), nullable=False)
    participle = Column(String(50), nullable=False)
    meaning = Column(String(150), nullable=True)
    past_alt = Column(String(50), nullable=True)
    participle_alt = Column(String(50), nullable=True)

    attempts = relationship("UserAttempt", back_populates="verb", cascade="all, delete-orphan")
```

### Table Schema

```sql
CREATE TABLE verbs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    base VARCHAR(50) UNIQUE NOT NULL,
    past VARCHAR(50) NOT NULL,
    participle VARCHAR(50) NOT NULL,
    meaning VARCHAR(150),
    past_alt VARCHAR(50),
    participle_alt VARCHAR(50),

    -- Indexes for fast lookups
    INDEX idx_base (base)
);
```

### Columns

| Column | Type | Nullable | Unique | Index | Description |
|--------|------|----------|--------|-------|-------------|
| `id` | INTEGER | ✗ | ✓ | ✓ | Primary key, auto-increment |
| `base` | VARCHAR(50) | ✗ | ✓ | ✓ | Infinitive form (e.g., "go") |
| `past` | VARCHAR(50) | ✗ | | | Simple past (e.g., "went") |
| `participle` | VARCHAR(50) | ✗ | | | Past participle (e.g., "gone") |
| `meaning` | VARCHAR(150) | ✓ | | | Spanish translation (e.g., "ir") |
| `past_alt` | VARCHAR(50) | ✓ | | | Alternative past form (e.g., "learnt") |
| `participle_alt` | VARCHAR(50) | ✓ | | | Alternative participle (e.g., "learnt") |

### Example Data

```
id | base    | past      | participle | meaning      | past_alt | participle_alt
---|---------|-----------|------------|--------------|----------|----------------
1  | be      | was/were  | been       | ser / estar  | NULL     | NULL
2  | go      | went      | gone       | ir           | NULL     | NULL
3  | learn   | learned   | learned    | aprender     | learnt   | learnt
```

### Methods

#### `check_answer(past_input: str, participle_input: str) -> bool`

Validate user's answer (case-insensitive, supports alternatives).

```python
verb = Verb(base="go", past="went", participle="gone", past_alt=None, participle_alt=None)

# Returns True
verb.check_answer("went", "gone")
verb.check_answer("WENT", "GONE")
verb.check_answer("Went", "Gone")

# Returns False
verb.check_answer("goed", "gone")
verb.check_answer("went", "goed")
```

#### Implementation

```python
def check_answer(self, past_input: str, participle_input: str) -> bool:
    past_ok = past_input.strip().lower() in self._valid_forms(
        self.past, self.past_alt
    )
    part_ok = participle_input.strip().lower() in self._valid_forms(
        self.participle, self.participle_alt
    )
    return past_ok and part_ok

@staticmethod
def _valid_forms(primary: str, alt: str | None) -> set[str]:
    forms = {primary.lower()}
    if alt:
        forms.add(alt.lower())
    return forms
```

---

## UserAttempt Model

### Definition

```python
class UserAttempt(Base):
    """Logs every attempt made by the user during a quiz."""

    __tablename__ = "user_attempts"

    id = Column(Integer, primary_key=True, index=True)
    verb_id = Column(Integer, ForeignKey("verbs.id"), nullable=False)
    past_given = Column(String(50), nullable=False)
    participle_given = Column(String(50), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)

    verb = relationship("Verb", back_populates="attempts")
```

### Table Schema

```sql
CREATE TABLE user_attempts (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    verb_id INTEGER NOT NULL,
    past_given VARCHAR(50) NOT NULL,
    participle_given VARCHAR(50) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    CONSTRAINT fk_verb_id FOREIGN KEY (verb_id) REFERENCES verbs(id)
);
```

### Columns

| Column | Type | Nullable | FK | Description |
|--------|------|----------|----|----|
| `id` | INTEGER | ✗ | | Primary key, auto-increment |
| `verb_id` | INTEGER | ✗ | ✓ | Foreign key to verbs table |
| `past_given` | VARCHAR(50) | ✗ | | User's submitted past tense form |
| `participle_given` | VARCHAR(50) | ✗ | | User's submitted past participle form |
| `is_correct` | BOOLEAN | ✗ | | True if answer was correct |
| `attempted_at` | DATETIME | ✗ | | Timestamp of the attempt |

### Example Data

```
id | verb_id | past_given | participle_given | is_correct | attempted_at
---|---------|------------|------------------|------------|-------------------
1  | 2       | went       | gone             | true       | 2025-05-12 10:30:15
2  | 2       | goed       | gone             | false      | 2025-05-12 10:30:45
3  | 1       | was        | been             | true       | 2025-05-12 10:31:00
```

---

## Relationships

### Verb ← → UserAttempt

**One-to-Many**: One verb can have many attempts.

```python
# From Verb
verb = db.query(Verb).filter_by(base="go").first()
attempts = verb.attempts  # List of all UserAttempt records for this verb

# From UserAttempt
attempt = db.query(UserAttempt).first()
verb = attempt.verb  # The associated Verb object
```

### Cascade Behavior

```python
attempts = relationship(
    "UserAttempt",
    back_populates="verb",
    cascade="all, delete-orphan"  # If verb deleted, delete attempts too
)
```

**Example**:
```python
# Delete verb
db.query(Verb).filter_by(base="test_verb").delete()
db.commit()

# All associated UserAttempt records are automatically deleted
attempts = db.query(UserAttempt).filter_by(verb_id=verb.id).count()
# Result: 0
```

---

## Database Initialization

### Creating Tables

Done automatically via:

```python
# In main.py and api/main.py
from app.models import Base
from app.database import engine

Base.metadata.create_all(bind=engine)
```

This:
1. Inspects all `Base` subclasses
2. Compares with database schema
3. Creates missing tables
4. Skips existing tables (idempotent)

### Seeding Data

Verbs are populated via `app/seed.py`:

```python
python main.py seed  # CLI
# or
POST /api/seed       # HTTP endpoint
```

This creates 100 Verb records with Spanish meanings.

---

## Querying Examples

### Get a Single Verb

```python
from sqlalchemy.orm import Session
from app.models import Verb

def get_verb(db: Session, base: str) -> Verb | None:
    return db.query(Verb).filter(Verb.base == base.lower()).first()

# Usage
verb = get_verb(db, "go")
print(verb.past, verb.participle)  # went, gone
```

### Get All Verbs (Shuffled)

```python
import random

def get_shuffled_verbs(db: Session, limit: int | None = None) -> list[Verb]:
    verbs = db.query(Verb).all()
    random.shuffle(verbs)
    if limit:
        verbs = verbs[:limit]
    return verbs

# Usage
quiz_verbs = get_shuffled_verbs(db, limit=10)
```

### Log an Attempt

```python
from app.models import UserAttempt

attempt = UserAttempt(
    verb_id=verb.id,
    past_given="went",
    participle_given="gone",
    is_correct=True
)
db.add(attempt)
db.commit()
```

### Get Statistics

```python
from sqlalchemy import func

def get_stats(db: Session):
    total = db.query(UserAttempt).count()
    correct = db.query(UserAttempt).filter_by(is_correct=True).count()

    hardest = db.query(
        Verb.base,
        func.count(UserAttempt.id).label("errors")
    ).join(
        UserAttempt, UserAttempt.verb_id == Verb.id
    ).filter(
        UserAttempt.is_correct == False
    ).group_by(
        Verb.base
    ).order_by(
        func.count(UserAttempt.id).desc()
    ).limit(5).all()

    return {
        "total": total,
        "correct": correct,
        "wrong": total - correct,
        "accuracy": (correct/total)*100 if total > 0 else 0,
        "hardest_verbs": [{"verb": v.base, "errors": v.errors} for v in hardest]
    }
```

---

## Indexes

Indexes improve query performance:

| Table | Column | Reason |
|-------|--------|--------|
| `verbs` | `base` | Fast lookup by verb name (`WHERE base = ...`) |
| `verbs` | `id` | Primary key (auto-indexed) |

No explicit indexes on `user_attempts` beyond primary key. Future optimization opportunities:
- Index on `verb_id` (for JOINs)
- Index on `is_correct` (for stats queries)

---

## Constraints

### Primary Key

Both tables have auto-incrementing primary keys:
- Unique identifier for each row
- Auto-assigned when inserting

### Unique Constraint

```sql
UNIQUE KEY uk_verbs_base (base)
```

Ensures no duplicate verb base forms:
```python
# This raises IntegrityError
db.add(Verb(base="go", past="went", participle="gone"))
db.add(Verb(base="go", past="went", participle="gone"))  # Duplicate!
db.commit()  # Fails: UNIQUE constraint violated
```

### Foreign Key

```sql
FOREIGN KEY (verb_id) REFERENCES verbs(id)
```

Ensures referential integrity:
```python
# This raises IntegrityError
attempt = UserAttempt(verb_id=9999, ...)  # 9999 doesn't exist
db.add(attempt)
db.commit()  # Fails: Foreign key constraint violated
```

---

## Data Types

| Python | SQLAlchemy | PostgreSQL | Notes |
|--------|------------|-----------|-------|
| `int` | Integer | INTEGER | 32-bit signed |
| `str` | String(50) | VARCHAR(50) | Up to 50 characters |
| `bool` | Boolean | BOOLEAN | True/False |
| `datetime` | DateTime | TIMESTAMP | With timezone |

---

## Performance Notes

### Query Optimization

```python
# ❌ N+1 problem (100+ queries for 100 verbs)
for verb in db.query(Verb).all():
    attempts = verb.attempts  # New query each iteration!

# ✅ Eager loading (1-2 queries)
from sqlalchemy.orm import joinedload
verbs = db.query(Verb).options(joinedload(Verb.attempts)).all()
```

### Pagination (Future)

```python
# For large result sets
page = 1
limit = 10
offset = (page - 1) * limit

verbs = db.query(Verb).offset(offset).limit(limit).all()
```

---

## Migration Strategy (Future)

Current: Simple schema creation on startup (suitable for MVP)

Future (Phase 4+): Proper migrations with Alembic
```bash
alembic init migrations
alembic revision --autogenerate -m "Add new column"
alembic upgrade head
```

---

## See Also

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Data Flow Guide](../architecture/data-flow.md)
- [API Schemas](../api/schemas.md)
