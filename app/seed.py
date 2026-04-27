"""Seed script — loads the 50 most common irregular English verbs into PostgreSQL.

Run via:  python main.py seed
"""

from sqlalchemy.orm import Session

# fmt: off
IRREGULAR_VERBS = [
    # (base, past, participle, past_alt, participle_alt)
    ("be",          "was/were",  "been",       None,       None),
    ("have",        "had",       "had",        None,       None),
    ("do",          "did",       "done",       None,       None),
    ("go",          "went",      "gone",       None,       None),
    ("say",         "said",      "said",       None,       None),
    ("get",         "got",       "gotten",     None,       "got"),
    ("make",        "made",      "made",       None,       None),
    ("know",        "knew",      "known",      None,       None),
    ("think",       "thought",   "thought",    None,       None),
    ("take",        "took",      "taken",      None,       None),
    ("see",         "saw",       "seen",       None,       None),
    ("come",        "came",      "come",       None,       None),
    ("give",        "gave",      "given",      None,       None),
    ("find",        "found",     "found",      None,       None),
    ("tell",        "told",      "told",       None,       None),
    ("feel",        "felt",      "felt",       None,       None),
    ("become",      "became",    "become",     None,       None),
    ("leave",       "left",      "left",       None,       None),
    ("put",         "put",       "put",        None,       None),
    ("mean",        "meant",     "meant",      None,       None),
    ("keep",        "kept",      "kept",       None,       None),
    ("let",         "let",       "let",        None,       None),
    ("begin",       "began",     "begun",      None,       None),
    ("show",        "showed",    "shown",      None,       "showed"),
    ("hear",        "heard",     "heard",      None,       None),
    ("run",         "ran",       "run",        None,       None),
    ("bring",       "brought",   "brought",    None,       None),
    ("write",       "wrote",     "written",    None,       None),
    ("sit",         "sat",       "sat",        None,       None),
    ("stand",       "stood",     "stood",      None,       None),
    ("lose",        "lost",      "lost",       None,       None),
    ("pay",         "paid",      "paid",       None,       None),
    ("meet",        "met",       "met",        None,       None),
    ("set",         "set",       "set",        None,       None),
    ("lead",        "led",       "led",        None,       None),
    ("understand",  "understood","understood",  None,       None),
    ("speak",       "spoke",     "spoken",     None,       None),
    ("read",        "read",      "read",       None,       None),
    ("spend",       "spent",     "spent",      None,       None),
    ("cut",         "cut",       "cut",        None,       None),
    ("send",        "sent",      "sent",       None,       None),
    ("build",       "built",     "built",      None,       None),
    ("grow",        "grew",      "grown",      None,       None),
    ("fall",        "fell",      "fallen",     None,       None),
    ("hold",        "held",      "held",       None,       None),
    ("buy",         "bought",    "bought",     None,       None),
    ("drive",       "drove",     "driven",     None,       None),
    ("break",       "broke",     "broken",     None,       None),
    ("learn",       "learned",   "learned",    "learnt",   "learnt"),
    ("forget",      "forgot",    "forgotten",  None,       "forgot"),
]
# fmt: on


def seed_verbs(db: Session) -> int:
    """Insert verbs if they don't exist yet. Returns number of verbs added."""
    from app.models import Verb  # local import to avoid circular deps

    added = 0
    for base, past, participle, past_alt, participle_alt in IRREGULAR_VERBS:
        exists = db.query(Verb).filter_by(base=base).first()
        if not exists:
            verb = Verb(
                base=base,
                past=past,
                participle=participle,
                past_alt=past_alt,
                participle_alt=participle_alt,
            )
            db.add(verb)
            added += 1

    db.commit()
    return added
