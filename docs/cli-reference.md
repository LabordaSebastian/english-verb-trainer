# CLI Reference

Complete guide to all command-line interface commands.

## Overview

The English Verb Trainer CLI is built with **Typer**, which provides automatic `--help` documentation.

```bash
# Show all commands
verb-trainer --help

# Show help for a specific command
verb-trainer quiz --help
```

## Commands

### `verb-trainer quiz`

Start an interactive quiz session.

#### Basic Usage

```bash
# Default: 10 random questions
verb-trainer quiz

# Specify number of questions
verb-trainer quiz --rounds 20

# Practice a specific verb
verb-trainer quiz --verb read

# Combine options
verb-trainer quiz --verb go --rounds 15
```

#### Options

| Option | Alias | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--verb TEXT` | `-v` | string | None | Practice a specific base verb (e.g., `--verb read`) |
| `--rounds INT` | `-r` | integer | 10 | Number of questions per session |
| `--help` | | | | Show command help |

#### Example Session

```
$ verb-trainer quiz --verb read --rounds 3

╔══════════════════════════════════════╗
║   🎯  English Irregular Verb Trainer ║
║       DevOps Edition  |  PostgreSQL  ║
╚══════════════════════════════════════╝

  Starting quiz — 3 question(s). Type 'q' to quit.

────────────────────────────────────────

  Question 1/3
  Base verb:  READ
  Meaning:    leer
  Type the  Past Tense  and  Past Participle  separated by a space.
  Your answer > read read

  ✅  Correct!  READ → read → read

────────────────────────────────────────

  Question 2/3
  Base verb:  READ
  Meaning:    leer
  Type the  Past Tense  and  Past Participle  separated by a space.
  Your answer > readed read

  ❌  Wrong!    READ → read → read
             You answered: readed → read

────────────────────────────────────────

  Question 3/3
  Base verb:  READ
  Meaning:    leer
  Type the  Past Tense  and  Past Participle  separated by a space.
  Your answer > read read

  ✅  Correct!  READ → read → read

────────────────────────────────────────

  📊  Result: 2/3 correct (66.7%)
```

#### Key Features

- **Type 'q' to quit** — Exit the quiz at any time
- **Case-insensitive** — Accepts "READ", "read", "Read"
- **Alternative forms** — Accepts "learned" or "learnt"
- **Immediate feedback** — See if you're correct immediately
- **Auto-logging** — Every attempt is recorded in the database

#### Error Handling

```bash
# Incomplete answer (need 2 forms)
Your answer > read
⚠️  Please enter TWO forms: past  participle

# Verb not found
$ verb-trainer quiz --verb unknown
❌  Verb 'unknown' not found in the database.

# Database not running
$ verb-trainer quiz
❌  Cannot connect to PostgreSQL.
    Make sure the container is running:

    docker compose up -d db
```

---

### `verb-trainer stats`

Display your quiz statistics and progress.

#### Usage

```bash
verb-trainer stats
```

#### Output

```
╔══════════════════════════════════════╗
║   🎯  English Irregular Verb Trainer ║
║       DevOps Edition  |  PostgreSQL  ║
╚══════════════════════════════════════╝

  📊  Total attempts : 47
  ✅  Correct        : 32
  ❌  Wrong          : 15
  🎯  Accuracy       : 68.1%

  🔥  Hardest verbs (most mistakes):
      1. GO             — 5 error(s)
      2. TAKE           — 3 error(s)
      3. READ           — 2 error(s)
      4. COME           — 1 error(s)
      5. GIVE           — 1 error(s)
```

#### Interpretation

- **Total attempts** — Total number of answers submitted
- **Correct** — Number of correct answers
- **Wrong** — Number of incorrect answers
- **Accuracy** — Percentage of correct answers
- **Hardest verbs** — Top 5 verbs with most mistakes (helps you practice)

#### Tracking

Stats are automatically accumulated:
- Each quiz answer creates a `UserAttempt` record
- Stats aggregate all attempts across all sessions
- Data persists across CLI invocations
- Cleared only when database is reset (`make down -v`)

---

### `verb-trainer vocab-seed`

Load or refresh the 1867 vocabulary words (across 10 categories) in the database.

#### Usage

```bash
verb-trainer vocab-seed
```

#### Output

```
📖 1867 word(s) added, 0 updated.
```

#### When to Use

| Scenario | Command |
|----------|---------|
| First run after `docker compose up` | Run automatically in entrypoint.sh |
| Manual database reset | `verb-trainer seed` then `verb-trainer vocab-seed` |
| Update word data | Modify `app/vocab_seed.py` then `verb-trainer vocab-seed` |

#### Categories Loaded

| Category | Words | Example |
|----------|-------|---------|
| Pronouns & Determiners | 80 | I, you, this, that |
| Prepositions | 60 | in, on, at, since |
| Conjunctions & Connectors | 50 | and, but, because, since |
| Common Verbs | 200 | ask, call, work, learn |
| Adjectives | 150 | good, new, big, beautiful |
| Adverbs | 100 | not, very, always, still |
| Common Nouns | 200 | time, person, year, place |
| Numbers & Quantifiers | 60 | zero, one, hundred |
| Question Words | 50 | what, who, where, why |
| Common Phrases | 50 | of course, in fact |

#### Upsert Behavior

Uses `(english, category)` as the composite key for dedup — the same English
word can appear in different categories with distinct Spanish meanings.

---

### `verb-trainer seed`

Load or refresh the 100 irregular verbs in the database.

#### Usage

```bash
# Initial seed (first run)
verb-trainer seed

# Refresh verbs (e.g., after updates)
verb-trainer seed
```

#### Output

```
$ verb-trainer seed

🌱 Seeding database...

✅  50 verb(s) added, 50 updated.
```

#### When to Use

| Scenario | Command |
|----------|---------|
| First run after `docker compose up` | Run automatically in entrypoint.sh |
| Manual database reset | `verb-trainer seed` |
| Update verb data | Modify `app/seed.py` then `verb-trainer seed` |

#### Verbs Loaded

The seed file contains 100 irregular verbs:

| # | Verbs | Example |
|---|-------|---------|
| 1-25 | Most common | be, have, do, go, say, get, make, know, think, take |
| 26-50 | Common | see, come, give, find, tell, feel, become, leave, put, mean |
| 51-75 | Intermediate | catch, fight, teach, sell, choose, sleep, win, hang, draw, fly |
| 76-100 | Advanced | wear, throw, steal, hide, shake, wake, rise, bite, swim, sing |

See `app/seed.py` for complete list with meanings (Spanish translations).

#### Upsert Behavior

```
For each verb:
  IF exists in database:
    UPDATE with new forms (in case data was corrected)
  ELSE:
    INSERT new verb
```

This ensures idempotency — running `seed` multiple times is safe.

---

## Global Options

Available on all commands:

```bash
--help              Show help for the command
```

---

## Environment Variables

The CLI reads these environment variables (if set):

| Variable | Default | Example |
|----------|---------|---------|
| `DATABASE_URL` | *(required, no default)* | `postgresql://user:pass@host:5432/db` |
| `ENVIRONMENT` | development | production, staging |

Set variables via:

```bash
# Linux/Mac
export DATABASE_URL=postgresql://...
verb-trainer quiz

# Windows PowerShell
$env:DATABASE_URL="postgresql://..."
verb-trainer quiz

# Or create .env file
echo 'DATABASE_URL=postgresql://...' > .env
verb-trainer quiz
```

---

## Exit Codes

The CLI uses standard exit codes:

| Code | Meaning | Example |
|------|---------|---------|
| `0` | Success | Quiz completed normally |
| `1` | Error | Database connection failed, verb not found |

```bash
$ verb-trainer quiz --verb unknown
# Exit code: 1

$ echo $?  # Check last exit code (Linux/Mac)
# Output: 1
```

---

## Tips & Tricks

### 1. Batch Mode (Run multiple quizzes)

```bash
# Run 3 sessions back-to-back
for i in {1..3}; do verb-trainer quiz --rounds 5; done
```

### 2. Focus on Weak Verbs

```bash
# Check stats to find difficult verbs
verb-trainer stats

# Practice the hardest one (e.g., GO)
verb-trainer quiz --verb go --rounds 10
```

### 3. Generate Test Data

```bash
# Run many quizzes to generate statistics
for i in {1..10}; do
  verb-trainer quiz --rounds 20
done

# View results
verb-trainer stats
```

### 4. Reset Statistics

```bash
# Clear database
docker compose down -v

# Reseed
verb-trainer seed

# Start fresh
verb-trainer quiz
```

---

## Troubleshooting

### "Cannot connect to PostgreSQL"

**Problem**: Trying to run CLI without database

**Solution**:
```bash
# Start the database first
docker compose up -d

# Then run CLI
verb-trainer quiz
```

### "No verbs found"

**Problem**: Database exists but is empty

**Solution**:
```bash
verb-trainer seed
verb-trainer quiz
```

### "Module not found"

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
verb-trainer quiz
```

### Quiz appears slow

**Problem**: Database queries taking time

**Solution**:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart if needed
docker compose restart db
```

---

## Performance Notes

- **Quiz Load Time**: <1 second (database query)
- **Stats Load Time**: <2 seconds (aggregate query)
- **Single Quiz Session**: <5 seconds per question (user input dominates)

---

## See Also

- [API Reference](api/endpoints.md) — REST endpoints
- [Database Models](database/models.md) — Data schema
- [Development Guide](development/setup.md) — Local setup
