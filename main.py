"""English Irregular Verb Trainer — CLI entry point.

Commands:
  python main.py seed          Load 50 irregular verbs into PostgreSQL
  python main.py quiz          Start a random quiz session
  python main.py quiz --verb read   Practice a specific verb
  python main.py stats         Show your progress summary
"""

import sys
from typing import Optional

import typer
from sqlalchemy.exc import OperationalError

from app.database import engine, SessionLocal
from app.models import Base

app = typer.Typer(
    name="verb-trainer",
    help="🎯 English Irregular Verb Trainer — DevOps Edition",
    add_completion=False,
)

# ─── helpers ────────────────────────────────────────────────────────────────

BANNER = """
╔══════════════════════════════════════════════╗
║   🎯  English Irregular Verb Trainer         ║
║       DevOps Edition  |  PostgreSQL + TF     ║
╚══════════════════════════════════════════════╝
"""


def _init_db():
    """Create tables if they do not exist yet."""
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        typer.echo(
            "\n❌  Cannot connect to PostgreSQL.\n"
            "    Make sure the container is running:\n\n"
            "      cd terraform && terraform apply\n\n"
            f"    Error: {e}\n",
            err=True,
        )
        raise typer.Exit(code=1)


def _get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


# ─── commands ───────────────────────────────────────────────────────────────

@app.command()
def seed():
    """Load the 50 most common irregular verbs into the database."""
    _init_db()
    db = SessionLocal()
    try:
        from app.seed import seed_verbs
        added, updated = seed_verbs(db)
        if added:
            typer.echo(f"\n✅  {added} verb(s) added, {updated} updated.\n")
        else:
            typer.echo(f"\nℹ️   All verbs up to date ({updated} refreshed).\n")
    finally:
        db.close()


@app.command()
def quiz(
    verb: Optional[str] = typer.Option(
        None, "--verb", "-v", help="Practice a specific base verb (e.g. --verb read)"
    ),
    rounds: int = typer.Option(
        10, "--rounds", "-r", help="Number of questions per session"
    ),
):
    """Start an interactive quiz session."""
    _init_db()
    db = SessionLocal()
    try:
        from app.quiz import get_verb_by_base, get_shuffled_verbs, validate_and_log

        typer.echo(BANNER)

        # Check DB has verbs
        from app.models import Verb
        total_verbs = db.query(Verb).count()
        if total_verbs == 0:
            typer.echo("⚠️  No verbs found. Run:  python main.py seed\n")
            raise typer.Exit(code=1)

        correct_count = 0
        question_count = 0

        typer.echo(f"  Starting quiz — {rounds} question(s). Type 'q' to quit.\n")
        typer.echo("─" * 48)

        # Build the question list for this session
        if verb:
            # Specific verb mode: repeat it for every round
            single = get_verb_by_base(db, base=verb)
            if single is None:
                typer.echo(f"\n❌  Verb '{verb}' not found in the database.\n")
                raise typer.Exit(code=1)
            question_list = [single] * rounds
        else:
            # Random mode: shuffle all verbs, take up to `rounds` (no repeats)
            question_list = get_shuffled_verbs(db, limit=rounds)
            if not question_list:
                typer.echo("⚠️  No verbs found. Run:  python main.py seed\n")
                raise typer.Exit(code=1)
            if len(question_list) < rounds:
                typer.echo(
                    f"  ℹ️   Only {len(question_list)} verbs available — "
                    f"quiz will have {len(question_list)} question(s).\n"
                )
                rounds = len(question_list)

        for v in question_list:
            question_count += 1
            typer.echo(f"\n  Question {question_count}/{rounds}")
            typer.echo(f"  Base verb:  {v.base.upper()}")
            typer.echo("  Type the  Past Tense  and  Past Participle  separated by a space.")

            raw = typer.prompt("  Your answer").strip()

            if raw.lower() == "q":
                typer.echo("\n  Quiz interrupted. Goodbye!\n")
                break

            parts = raw.split()
            if len(parts) < 2:
                typer.echo("  ⚠️  Please enter TWO forms: past  participle")
                question_count -= 1
                continue

            past_in, part_in = parts[0], parts[1]
            is_correct = validate_and_log(db, v, past_in, part_in)

            if is_correct:
                correct_count += 1
                typer.echo(f"\n  ✅  Correct!  {v.base.upper()} → {v.past} → {v.participle}")
            else:
                typer.echo(f"\n  ❌  Wrong!    {v.base.upper()} → {v.past} → {v.participle}")
                if v.past_alt or v.participle_alt:
                    past_display = f"{v.past} / {v.past_alt}" if v.past_alt else v.past
                    part_display = f"{v.participle} / {v.participle_alt}" if v.participle_alt else v.participle
                    typer.echo(f"             (also accepted: {past_display} → {part_display})")
                typer.echo(f"             You answered: {past_in} → {part_in}")

            typer.echo("─" * 48)

        if question_count > 0:
            pct = round((correct_count / question_count) * 100, 1)
            typer.echo(f"\n  📊  Result: {correct_count}/{question_count} correct ({pct}%)\n")

    finally:
        db.close()


@app.command()
def stats():
    """Show your overall quiz progress and hardest verbs."""
    _init_db()
    db = SessionLocal()
    try:
        from app.quiz import get_stats

        data = get_stats(db)

        typer.echo(BANNER)
        typer.echo(f"  📊  Total attempts : {data['total']}")
        typer.echo(f"  ✅  Correct        : {data['correct']}")
        typer.echo(f"  ❌  Wrong          : {data['wrong']}")
        typer.echo(f"  🎯  Accuracy       : {data['accuracy']}%\n")

        if data["hardest_verbs"]:
            typer.echo("  🔥  Hardest verbs (most mistakes):")
            for i, entry in enumerate(data["hardest_verbs"], 1):
                typer.echo(f"      {i}. {entry['verb'].upper():<15} — {entry['errors']} error(s)")
        else:
            typer.echo("  🎉  No mistakes yet! Keep it up.")

        typer.echo()

    finally:
        db.close()


# ─── entry ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
