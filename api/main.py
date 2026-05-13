"""FastAPI application — REST API + static SPA server."""

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from api.schemas import (
    AttemptRequest,
    AttemptResponse,
    QuizVerb,
    SeedResponse,
    StatsResponse,
)
from app.database import get_db, run_migrations
from app.models import Verb
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


# ── SPA fallback — must be registered LAST ───────────────────────────────────


@app.get("/", include_in_schema=False)
def serve_spa():
    return FileResponse(str(STATIC_DIR / "index.html"))


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
