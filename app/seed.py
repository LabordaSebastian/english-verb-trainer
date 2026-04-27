"""Seed script — loads the 50 most common irregular English verbs into PostgreSQL.

Run via:  python main.py seed
"""

from sqlalchemy.orm import Session

# fmt: off
IRREGULAR_VERBS = [
    # (base, past, participle, past_alt, participle_alt, meaning)
    ("be",          "was/were",   "been",       None,       None,       "ser / estar"),
    ("have",        "had",        "had",        None,       None,       "tener / haber"),
    ("do",          "did",        "done",       None,       None,       "hacer"),
    ("go",          "went",       "gone",       None,       None,       "ir"),
    ("say",         "said",       "said",       None,       None,       "decir"),
    ("get",         "got",        "gotten",     None,       None,       "obtener / conseguir"),
    ("make",        "made",       "made",       None,       None,       "hacer / fabricar"),
    ("know",        "knew",       "known",      None,       None,       "saber / conocer"),
    ("think",       "thought",    "thought",    None,       None,       "pensar / creer"),
    ("take",        "took",       "taken",      None,       None,       "tomar / llevar"),
    ("see",         "saw",        "seen",       None,       None,       "ver"),
    ("come",        "came",       "come",       None,       None,       "venir"),
    ("give",        "gave",       "given",      None,       None,       "dar"),
    ("find",        "found",      "found",      None,       None,       "encontrar / hallar"),
    ("tell",        "told",       "told",       None,       None,       "contar / decir"),
    ("feel",        "felt",       "felt",       None,       None,       "sentir / sentirse"),
    ("become",      "became",     "become",     None,       None,       "convertirse / llegar a ser"),
    ("leave",       "left",       "left",       None,       None,       "dejar / salir / partir"),
    ("put",         "put",        "put",        None,       None,       "poner / colocar"),
    ("mean",        "meant",      "meant",      None,       None,       "significar / querer decir"),
    ("keep",        "kept",       "kept",       None,       None,       "mantener / guardar"),
    ("let",         "let",        "let",        None,       None,       "dejar / permitir"),
    ("begin",       "began",      "begun",      None,       None,       "comenzar / empezar"),
    ("show",        "showed",     "shown",      None,       "showed",   "mostrar / enseñar"),
    ("hear",        "heard",      "heard",      None,       None,       "oír / escuchar"),
    ("run",         "ran",        "run",        None,       None,       "correr"),
    ("bring",       "brought",    "brought",    None,       None,       "traer / llevar"),
    ("write",       "wrote",      "written",    None,       None,       "escribir"),
    ("sit",         "sat",        "sat",        None,       None,       "sentarse"),
    ("stand",       "stood",      "stood",      None,       None,       "estar de pie / levantarse"),
    ("lose",        "lost",       "lost",       None,       None,       "perder"),
    ("pay",         "paid",       "paid",       None,       None,       "pagar"),
    ("meet",        "met",        "met",        None,       None,       "conocer / encontrarse con"),
    ("set",         "set",        "set",        None,       None,       "establecer / fijar / poner"),
    ("lead",        "led",        "led",        None,       None,       "liderar / guiar / llevar"),
    ("understand",  "understood", "understood", None,       None,       "entender / comprender"),
    ("speak",       "spoke",      "spoken",     None,       None,       "hablar"),
    ("read",        "read",       "read",       None,       None,       "leer"),
    ("spend",       "spent",      "spent",      None,       None,       "gastar / pasar (tiempo)"),
    ("cut",         "cut",        "cut",        None,       None,       "cortar"),
    ("send",        "sent",       "sent",       None,       None,       "enviar / mandar"),
    ("build",       "built",      "built",      None,       None,       "construir / edificar"),
    ("grow",        "grew",       "grown",      None,       None,       "crecer / cultivar"),
    ("fall",        "fell",       "fallen",     None,       None,       "caer / caerse"),
    ("hold",        "held",       "held",       None,       None,       "sostener / mantener / aguantar"),
    ("buy",         "bought",     "bought",     None,       None,       "comprar"),
    ("drive",       "drove",      "driven",     None,       None,       "manejar / conducir"),
    ("break",       "broke",      "broken",     None,       None,       "romper / quebrar"),
    ("learn",       "learned",    "learned",    "learnt",   "learnt",   "aprender"),
    ("forget",      "forgot",     "forgotten",  None,       "forgot",   "olvidar"),
]
# fmt: on


def seed_verbs(db: Session) -> tuple[int, int]:
    """Upsert verbs — insert new ones and update existing ones.

    Returns (added, updated) counts.
    """
    from app.models import Verb  # local import to avoid circular deps

    added = updated = 0
    for base, past, participle, past_alt, participle_alt, meaning in IRREGULAR_VERBS:
        existing = db.query(Verb).filter_by(base=base).first()
        if existing:
            # Update all fields in case data was corrected
            existing.past = past
            existing.participle = participle
            existing.past_alt = past_alt
            existing.participle_alt = participle_alt
            existing.meaning = meaning
            updated += 1
        else:
            verb = Verb(
                base=base,
                past=past,
                participle=participle,
                past_alt=past_alt,
                participle_alt=participle_alt,
                meaning=meaning,
            )
            db.add(verb)
            added += 1

    db.commit()
    return added, updated
