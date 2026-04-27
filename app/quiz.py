"""Core quiz logic — verb selection, answer validation, and attempt logging."""

import random

from sqlalchemy.orm import Session

from app.models import Verb, UserAttempt


def get_verb_by_base(db: Session, base: str) -> Verb | None:
    """Look up a specific verb by its base form."""
    return db.query(Verb).filter(Verb.base == base.lower()).first()


def get_shuffled_verbs(db: Session, limit: int | None = None) -> list[Verb]:
    """Return all verbs in random order, optionally capped to `limit`.

    Using a shuffled list (instead of repeated random picks) guarantees
    no verb appears twice in a single quiz session.
    """
    verbs = db.query(Verb).all()
    random.shuffle(verbs)
    if limit is not None:
        verbs = verbs[:limit]
    return verbs


def validate_and_log(
    db: Session,
    verb: Verb,
    past_input: str,
    participle_input: str,
) -> bool:
    """Check the user's answer, log the attempt, and return whether it was correct."""
    correct = verb.check_answer(past_input, participle_input)

    attempt = UserAttempt(
        verb_id=verb.id,
        past_given=past_input.strip(),
        participle_given=participle_input.strip(),
        is_correct=correct,
    )
    db.add(attempt)
    db.commit()
    return correct


def get_stats(db: Session) -> dict:
    """Return a summary of the user's quiz history."""
    total = db.query(UserAttempt).count()
    correct = db.query(UserAttempt).filter_by(is_correct=True).count()
    wrong = total - correct

    # Top 5 verbs with most mistakes
    from sqlalchemy import func
    hardest = (
        db.query(Verb.base, func.count(UserAttempt.id).label("errors"))
        .join(UserAttempt, UserAttempt.verb_id == Verb.id)
        .filter(UserAttempt.is_correct == False)  # noqa: E712
        .group_by(Verb.base)
        .order_by(func.count(UserAttempt.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "accuracy": round((correct / total) * 100, 1) if total > 0 else 0.0,
        "hardest_verbs": [{"verb": r.base, "errors": r.errors} for r in hardest],
    }
