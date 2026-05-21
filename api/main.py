"""FastAPI application — REST API + static SPA server."""

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from api.schemas import (
    AttemptRequest,
    AttemptResponse,
    HardestWord,
    QuizVerb,
    SeedResponse,
    StatsResponse,
    VocabAttemptRequest,
    VocabAttemptResponse,
    VocabCategory,
    VocabQuizWord,
    VocabSeedResponse,
    VocabStatsResponse,
)
from app.database import get_db, run_migrations
from app.models import Verb, VocabAttempt, VocabularyWord
from app.quiz import get_shuffled_verbs, get_stats, validate_and_log

# ── DB init ───────────────────────────────────────────────────────────────────

try:
    run_migrations()
except Exception as e:
    import logging

    logging.critical("Database initialisation failed: %s", e)
    raise

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="English Verb Trainer",
    description="REST API for the English Irregular Verb Trainer",
    version="1.0.0",
)

STATIC_DIR = Path(__file__).parent.parent / "static"


# ── API routes ────────────────────────────────────────────────────────────────


@app.get("/api/verbs/quiz", response_model=list[QuizVerb], tags=["quiz"])
def get_quiz_verbs(count: int = 10, db: Session = Depends(get_db)):
    """Return N shuffled verbs for a quiz session (no correct forms exposed)."""
    verbs = get_shuffled_verbs(db, limit=count)
    result = []
    for v in verbs:
        assert v.id is not None and v.base is not None
        result.append(QuizVerb(id=v.id, base=v.base, meaning=v.meaning))
    return result


@app.post("/api/attempts", response_model=AttemptResponse, tags=["quiz"])
def submit_attempt(attempt: AttemptRequest, db: Session = Depends(get_db)):
    """Validate a user's answer, log the attempt, and return the result."""
    verb = db.query(Verb).filter(Verb.id == attempt.verb_id).first()
    if not verb:
        raise HTTPException(
            status_code=404, detail=f"Verb id={attempt.verb_id} not found"
        )

    correct = validate_and_log(db, verb, attempt.past_given, attempt.participle_given)

    also_accepted = None
    if verb.past_alt or verb.participle_alt:
        past_display = f"{verb.past} / {verb.past_alt}" if verb.past_alt else verb.past
        part_display = (
            f"{verb.participle} / {verb.participle_alt}"
            if verb.participle_alt
            else verb.participle
        )
        also_accepted = f"{past_display} → {part_display}"

    assert verb.past is not None and verb.participle is not None
    return AttemptResponse(
        correct=correct,
        correct_past=verb.past,
        correct_participle=verb.participle,
        also_accepted=also_accepted,
    )


@app.get("/api/stats", response_model=StatsResponse, tags=["stats"])
def get_stats_endpoint(db: Session = Depends(get_db)):
    """Return overall quiz statistics."""
    data = get_stats(db)
    return StatsResponse(**data)


@app.post("/api/seed", response_model=SeedResponse, tags=["admin"])
def seed_endpoint(db: Session = Depends(get_db)):
    """Seed or refresh the 100 irregular verbs in the database."""
    from sqlalchemy.exc import IntegrityError

    from app.seed import seed_verbs

    try:
        added, updated = seed_verbs(db)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Database integrity error during seed"
        ) from None
    return SeedResponse(added=added, updated=updated)


# ── Vocabulary API routes ───────────────────────────────────────────────────


@app.get("/api/vocab/categories", response_model=list[VocabCategory], tags=["vocab"])
def get_vocab_categories(db: Session = Depends(get_db)):
    """Return available vocabulary categories with word counts."""
    from sqlalchemy import func

    rows = (
        db.query(VocabularyWord.category, func.count(VocabularyWord.id))
        .group_by(VocabularyWord.category)
        .all()
    )
    return [VocabCategory(name=row[0], count=row[1]) for row in rows]


@app.get("/api/vocab/quiz", response_model=list[VocabQuizWord], tags=["vocab"])
def get_vocab_quiz_words(
    count: int = 10,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """Return N shuffled vocabulary words for a quiz."""
    query = db.query(VocabularyWord)
    if category:
        query = query.filter(VocabularyWord.category == category)
    words = query.all()
    import random

    random.shuffle(words)
    result = []
    for w in words[:count]:
        assert w.id is not None and w.english is not None
        assert w.spanish is not None and w.category is not None
        result.append(
            VocabQuizWord(
                id=w.id, english=w.english, spanish=w.spanish, category=w.category
            )
        )
    return result


@app.post("/api/vocab/attempts", response_model=VocabAttemptResponse, tags=["vocab"])
def submit_vocab_attempt(attempt: VocabAttemptRequest, db: Session = Depends(get_db)):
    """Validate a vocabulary answer and log the attempt."""
    word = db.query(VocabularyWord).filter(VocabularyWord.id == attempt.word_id).first()
    if not word:
        raise HTTPException(
            status_code=404, detail=f"Vocabulary word id={attempt.word_id} not found"
        )

    assert word.english is not None
    is_correct = attempt.answer_given.strip().lower() == word.english.strip().lower()

    db.add(
        VocabAttempt(
            word_id=attempt.word_id,
            answer_given=attempt.answer_given,
            is_correct=is_correct,
        )
    )
    db.commit()

    assert word.english is not None
    return VocabAttemptResponse(
        correct=is_correct,
        correct_answer=word.english,
    )


@app.get("/api/vocab/stats", response_model=VocabStatsResponse, tags=["vocab"])
def get_vocab_stats(db: Session = Depends(get_db)):
    """Return vocabulary quiz statistics."""
    total = db.query(VocabAttempt).count()
    correct = db.query(VocabAttempt).filter(VocabAttempt.is_correct.is_(True)).count()
    wrong = total - correct
    accuracy = round((correct / total) * 100, 1) if total > 0 else 0.0

    from sqlalchemy import func

    hardest = (
        db.query(
            VocabularyWord.english,
            VocabularyWord.spanish,
            func.count(VocabAttempt.id).label("errors"),
        )
        .join(VocabAttempt, VocabularyWord.id == VocabAttempt.word_id)
        .filter(VocabAttempt.is_correct.is_(False))
        .group_by(VocabularyWord.id)
        .order_by(func.count(VocabAttempt.id).desc())
        .limit(10)
        .all()
    )

    hardest_words = [
        HardestWord(word=row[0], spanish=row[1], errors=row[2]) for row in hardest
    ]

    return VocabStatsResponse(
        total=total,
        correct=correct,
        wrong=wrong,
        accuracy=accuracy,
        hardest_words=hardest_words,
    )


@app.post("/api/vocab/seed", response_model=VocabSeedResponse, tags=["vocab-admin"])
def seed_vocab_endpoint(db: Session = Depends(get_db)):
    """Seed or refresh the 1000 vocabulary words."""
    from sqlalchemy.exc import IntegrityError

    from app.vocab_seed import seed_vocabulary

    try:
        added, updated = seed_vocabulary(db)
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Database integrity error during vocab seed"
        ) from None
    return VocabSeedResponse(added=added, updated=updated)


# ── SPA fallback — must be registered LAST ───────────────────────────────────


@app.get("/", include_in_schema=False)
def serve_spa():
    return FileResponse(str(STATIC_DIR / "index.html"))


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
