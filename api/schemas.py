"""Pydantic schemas for the FastAPI REST layer."""

from pydantic import BaseModel, Field


class QuizVerb(BaseModel):
    """Verb data sent to the browser — no correct answers included."""

    id: int
    base: str
    meaning: str | None


class AttemptRequest(BaseModel):
    """Answer submitted by the user."""

    verb_id: int = Field(..., gt=0, description="Must be a positive integer")
    past_given: str
    participle_given: str


class AttemptResponse(BaseModel):
    """Result of an answer validation."""

    correct: bool
    correct_past: str
    correct_participle: str
    also_accepted: str | None


class HardestVerb(BaseModel):
    """A single verb entry in the hardest-verbs ranking."""

    verb: str
    errors: int


class StatsResponse(BaseModel):
    """Overall quiz statistics."""

    total: int
    correct: int
    wrong: int
    accuracy: float
    hardest_verbs: list[HardestVerb]


class SeedResponse(BaseModel):
    added: int
    updated: int
