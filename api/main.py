"""FastAPI application — REST API + static SPA server."""

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, Verb
from app.quiz import get_shuffled_verbs, get_stats, validate_and_log
from api.schemas import (
    AttemptRequest,
    AttemptResponse,
    QuizVerb,
    SeedResponse,
    StatsResponse,
)

# ── DB init (same safe migration as CLI) ─────────────────────────────────────

Base.metadata.create_all(bind=engine)
with engine.connect() as _conn:
    exists = _conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name='verbs' AND column_name='meaning'"
    )).fetchone()
    if not exists:
        _conn.execute(text("ALTER TABLE verbs ADD COLUMN meaning VARCHAR(150)"))
        _conn.commit()

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="English Verb Trainer",
    description="REST API for the English Irregular Verb Trainer",
    version="1.0.0",
)

STATIC_DIR = Path(__file__).parent.parent / "static"


# ── Dependency ────────────────────────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── API routes ────────────────────────────────────────────────────────────────

@app.get("/api/verbs/quiz", response_model=list[QuizVerb], tags=["quiz"])
def get_quiz_verbs(count: int = 10, db: Session = Depends(get_db)):
    """Return N shuffled verbs for a quiz session (no correct forms exposed)."""
    verbs = get_shuffled_verbs(db, limit=count)
    return [QuizVerb(id=v.id, base=v.base, meaning=v.meaning) for v in verbs]


@app.post("/api/attempts", response_model=AttemptResponse, tags=["quiz"])
def submit_attempt(attempt: AttemptRequest, db: Session = Depends(get_db)):
    """Validate a user's answer, log the attempt, and return the result."""
    verb = db.query(Verb).filter(Verb.id == attempt.verb_id).first()
    if not verb:
        raise HTTPException(status_code=404, detail=f"Verb id={attempt.verb_id} not found")

    correct = validate_and_log(db, verb, attempt.past_given, attempt.participle_given)

    also_accepted = None
    if verb.past_alt or verb.participle_alt:
        past_display = f"{verb.past} / {verb.past_alt}" if verb.past_alt else verb.past
        part_display = f"{verb.participle} / {verb.participle_alt}" if verb.participle_alt else verb.participle
        also_accepted = f"{past_display} → {part_display}"

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
    """Seed or refresh the 50 irregular verbs in the database."""
    from app.seed import seed_verbs
    added, updated = seed_verbs(db)
    return SeedResponse(added=added, updated=updated)


# ── SPA fallback — must be registered LAST ───────────────────────────────────

@app.get("/", include_in_schema=False)
def serve_spa():
    return FileResponse(str(STATIC_DIR / "index.html"))


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
