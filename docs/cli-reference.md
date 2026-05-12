# CLI Reference

Complete guide to all command-line interface commands.

## Overview

The English Verb Trainer CLI is built with **Typer**, which provides automatic `--help` documentation.

```bash
# Show all commands
python main.py --help

# Show help for a specific command
python main.py quiz --help
```

## Commands

### `python main.py quiz`

Start an interactive quiz session.

#### Basic Usage

```bash
# Default: 10 random questions
python main.py quiz

# Specify number of questions
python main.py quiz --rounds 20

# Practice a specific verb
python main.py quiz --verb read

# Combine options
python main.py quiz --verb go --rounds 15
```

#### Options

| Option | Alias | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--verb TEXT` | `-v` | string | None | Practice a specific base verb (e.g., `--verb read`) |
| `--rounds INT` | `-r` | integer | 10 | Number of questions per session |
| `--help` | | | | Show command help |

#### Example Session

```
$ python main.py quiz --verb read --rounds 3

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
$ python main.py quiz --verb unknown
❌  Verb 'unknown' not found in the database.

# Database not running
$ python main.py quiz
❌  Cannot connect to PostgreSQL.
    Make sure the container is running:

    cd terraform && terraform apply
```

---

### `python main.py stats`

Display your quiz statistics and progress.

#### Usage

```bash
python main.py stats
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

### `python main.py seed`

Load or refresh the 100 irregular verbs in the database.

#### Usage

```bash
# Initial seed (first run)
python main.py seed

# Refresh verbs (e.g., after updates)
python main.py seed
```

#### Output

```
$ python main.py seed

🌱 Seeding database...

✅  50 verb(s) added, 50 updated.
```

#### When to Use

| Scenario | Command |
|----------|---------|
| First run after `docker compose up` | Run automatically in entrypoint.sh |
| Manual database reset | `python main.py seed` |
| Update verb data | Modify `app/seed.py` then `python main.py seed` |

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
| `DATABASE_URL` | `postgresql://trainer_user:PLACEHOLDER_PASSWORD@localhost:5432/english_trainer` | `postgresql://user:pass@host:5432/db` |
| `ENVIRONMENT` | development | production, staging |

Set variables via:

```bash
# Linux/Mac
export DATABASE_URL=postgresql://...
python main.py quiz

# Windows PowerShell
$env:DATABASE_URL="postgresql://..."
python main.py quiz

# Or create .env file
echo 'DATABASE_URL=postgresql://...' > .env
python main.py quiz
```

---

## Exit Codes

The CLI uses standard exit codes:

| Code | Meaning | Example |
|------|---------|---------|
| `0` | Success | Quiz completed normally |
| `1` | Error | Database connection failed, verb not found |

```bash
$ python main.py quiz --verb unknown
# Exit code: 1

$ echo $?  # Check last exit code (Linux/Mac)
# Output: 1
```

---

## Tips & Tricks

### 1. Batch Mode (Run multiple quizzes)

```bash
# Run 3 sessions back-to-back
for i in {1..3}; do python main.py quiz --rounds 5; done
```

### 2. Focus on Weak Verbs

```bash
# Check stats to find difficult verbs
python main.py stats

# Practice the hardest one (e.g., GO)
python main.py quiz --verb go --rounds 10
```

### 3. Generate Test Data

```bash
# Run many quizzes to generate statistics
for i in {1..10}; do
  python main.py quiz --rounds 20
done

# View results
python main.py stats
```

### 4. Reset Statistics

```bash
# Clear database
docker compose down -v

# Reseed
python main.py seed

# Start fresh
python main.py quiz
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
python main.py quiz
```

### "No verbs found"

**Problem**: Database exists but is empty

**Solution**:
```bash
python main.py seed
python main.py quiz
```

### "Module not found"

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
python main.py quiz
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
