"""Seed script — loads the 100 most common irregular English verbs into PostgreSQL.

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
    # ── Next 50 most common irregular verbs ──────────────────────────────────
    ("catch",       "caught",     "caught",     None,       None,       "atrapar / coger"),
    ("fight",       "fought",     "fought",     None,       None,       "pelear / luchar"),
    ("teach",       "taught",     "taught",     None,       None,       "enseñar / dar clases"),
    ("sell",        "sold",       "sold",       None,       None,       "vender"),
    ("choose",      "chose",      "chosen",     None,       None,       "elegir / escoger"),
    ("sleep",       "slept",      "slept",      None,       None,       "dormir"),
    ("win",         "won",        "won",        None,       None,       "ganar"),
    ("hang",        "hung",       "hung",       None,       None,       "colgar"),
    ("draw",        "drew",       "drawn",      None,       None,       "dibujar"),
    ("fly",         "flew",       "flown",      None,       None,       "volar"),
    ("wear",        "wore",       "worn",       None,       None,       "usar / llevar puesto"),
    ("throw",       "threw",      "thrown",     None,       None,       "lanzar / tirar"),
    ("steal",       "stole",      "stolen",     None,       None,       "robar"),
    ("hide",        "hid",        "hidden",     None,       None,       "esconder / ocultar"),
    ("shake",       "shook",      "shaken",     None,       None,       "agitar / sacudir"),
    ("wake",        "woke",       "woken",      None,       None,       "despertar"),
    ("rise",        "rose",       "risen",      None,       None,       "subir / levantarse"),
    ("bite",        "bit",        "bitten",     None,       None,       "morder"),
    ("swim",        "swam",       "swum",       None,       None,       "nadar"),
    ("sing",        "sang",       "sung",       None,       None,       "cantar"),
    ("ring",        "rang",       "rung",       None,       None,       "sonar / llamar"),
    ("drink",       "drank",      "drunk",      None,       None,       "beber / tomar"),
    ("eat",         "ate",        "eaten",      None,       None,       "comer"),
    ("feed",        "fed",        "fed",        None,       None,       "alimentar"),
    ("lend",        "lent",       "lent",       None,       None,       "prestar"),
    ("bend",        "bent",       "bent",       None,       None,       "doblar / inclinar"),
    ("burn",        "burned",     "burned",     "burnt",    "burnt",    "quemar / arder"),
    ("dream",       "dreamed",    "dreamed",    "dreamt",   "dreamt",   "soñar"),
    ("kneel",       "knelt",      "knelt",      None,       None,       "arrodillarse"),
    ("sweep",       "swept",      "swept",      None,       None,       "barrer"),
    ("weep",        "wept",       "wept",       None,       None,       "llorar"),
    ("creep",       "crept",      "crept",      None,       None,       "arrastrarse / deslizarse"),
    ("leap",        "leaped",     "leaped",     "leapt",    "leapt",    "saltar"),
    ("deal",        "dealt",      "dealt",      None,       None,       "tratar / repartir"),
    ("knit",        "knit",       "knit",       "knitted",  "knitted",  "tejer"),
    ("hit",         "hit",        "hit",        None,       None,       "golpear / pegar"),
    ("hurt",        "hurt",       "hurt",       None,       None,       "doler / lastimar"),
    ("cost",        "cost",       "cost",       None,       None,       "costar"),
    ("spread",      "spread",     "spread",     None,       None,       "extender / difundir"),
    ("shed",        "shed",       "shed",       None,       None,       "derramar / mudar"),
    ("split",       "split",      "split",      None,       None,       "dividir / partir"),
    ("beat",        "beat",       "beaten",     None,       None,       "golpear / vencer"),
    ("forbid",      "forbade",    "forbidden",  None,       None,       "prohibir"),
    ("forgive",     "forgave",    "forgiven",   None,       None,       "perdonar"),
    ("undertake",   "undertook",  "undertaken", None,       None,       "emprender / comprometerse"),
    ("overcome",    "overcame",   "overcome",   None,       None,       "superar / vencer"),
    ("withdraw",    "withdrew",   "withdrawn",  None,       None,       "retirar / retirarse"),
    ("mistake",     "mistook",    "mistaken",   None,       None,       "confundir / equivocarse"),
    ("arise",       "arose",      "arisen",     None,       None,       "surgir / levantarse"),
    ("bind",        "bound",      "bound",      None,       None,       "atar / encuadernar"),
]
# fmt: on


def seed_verbs(
    db: Session,
    verb_list: list[tuple] | None = None,
) -> tuple[int, int]:
    """Upsert verbs — insert new ones and update existing ones.

    Args:
        db: Database session.
        verb_list: List of verb tuples (base, past, participle, past_alt, participle_alt, meaning).
                   Defaults to the built-in IRREGULAR_VERBS list.

    Returns:
        (added, updated) counts.
    """
    from app.models import Verb  # local import to avoid circular deps

    verbs = IRREGULAR_VERBS if verb_list is None else verb_list

    added = updated = 0
    for base, past, participle, past_alt, participle_alt, meaning in verbs:
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
