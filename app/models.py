"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Verb(Base):
    """Stores an irregular verb with its three forms."""

    __tablename__ = "verbs"

    id = Column(Integer, primary_key=True, index=True)
    base = Column(String(50), unique=True, nullable=False, index=True)
    past = Column(String(50), nullable=False)
    participle = Column(String(50), nullable=False)

    # Spanish meaning shown during the quiz
    meaning = Column(String(150), nullable=True)

    # Optional alternative forms (e.g. "learned / learnt")
    past_alt = Column(String(50), nullable=True)
    participle_alt = Column(String(50), nullable=True)

    attempts = relationship("UserAttempt", back_populates="verb", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Verb base={self.base!r} past={self.past!r} participle={self.participle!r}>"

    def check_answer(self, past_input: str, participle_input: str) -> bool:
        """Return True if both answers match the stored forms (case-insensitive).
        Also accepts alternative forms when present.
        """
        past_ok = past_input.strip().lower() in self._valid_forms(self.past, self.past_alt)
        part_ok = participle_input.strip().lower() in self._valid_forms(self.participle, self.participle_alt)
        return past_ok and part_ok

    @staticmethod
    def _valid_forms(primary: str, alt: str | None) -> set[str]:
        forms = {primary.lower()}
        if alt:
            forms.add(alt.lower())
        return forms


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

    def __repr__(self) -> str:
        return (
            f"<UserAttempt verb_id={self.verb_id} correct={self.is_correct}>"
        )
