#!/usr/bin/env python3
"""
start.py — One-command launcher for English Irregular Verb Trainer.

Usage:
    python start.py           # Full setup + quiz
    python start.py --seed    # Only seed the DB
    python start.py --stats   # Show stats instead of quiz

Works on Windows, Linux, and Mac.
Requires: Python 3.10+ and Docker Desktop.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
VENV = ROOT / ".venv"
TERRAFORM_DIR = ROOT / "terraform"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
REQUIREMENTS = ROOT / "requirements.txt"

IS_WINDOWS = platform.system() == "Windows"
PYTHON = VENV / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")
PIP = VENV / ("Scripts/pip.exe" if IS_WINDOWS else "bin/pip")

# ── Helpers ───────────────────────────────────────────────────────────────────

def banner(msg: str, icon: str = "▶") -> None:
    print(f"\n{icon}  {msg}")


def success(msg: str) -> None:
    print(f"   ✅  {msg}")


def info(msg: str) -> None:
    print(f"   ℹ️   {msg}")


def warn(msg: str) -> None:
    print(f"   ⚠️   {msg}", file=sys.stderr)


def die(msg: str) -> None:
    print(f"\n   ❌  {msg}\n", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str], cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command, exit on failure."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
    )
    return result


# ── Steps ─────────────────────────────────────────────────────────────────────

def check_docker() -> None:
    banner("Checking Docker…", "🐳")
    if not shutil.which("docker"):
        die("Docker not found. Install Docker Desktop: https://www.docker.com/products/docker-desktop/")

    result = run(["docker", "info"], capture=True)
    if result.returncode != 0:
        die("Docker is installed but not running. Please start Docker Desktop and try again.")

    success("Docker is running.")


def check_terraform() -> None:
    banner("Checking Terraform…", "🏗️")
    if not shutil.which("terraform"):
        die(
            "Terraform not found.\n"
            "   Install it from: https://developer.hashicorp.com/terraform/install\n"
            "   On Linux: sudo snap install terraform --classic\n"
            "   On Mac:   brew install terraform\n"
            "   On Win:   choco install terraform"
        )
    success("Terraform is available.")


def start_postgres() -> None:
    banner("Starting PostgreSQL via Terraform…", "🐘")

    # Check if container already running
    result = run(
        ["docker", "ps", "--filter", "name=english_trainer_db", "--format", "{{.Names}}"],
        capture=True,
    )
    if "english_trainer_db" in result.stdout:
        success("PostgreSQL container already running.")
        return

    # terraform init (idempotent)
    result = run(["terraform", "init", "-input=false"], cwd=TERRAFORM_DIR, capture=True)
    if result.returncode != 0:
        die(f"terraform init failed:\n{result.stderr}")

    # terraform apply
    result = run(
        ["terraform", "apply", "-auto-approve", "-input=false"],
        cwd=TERRAFORM_DIR,
        capture=True,
    )
    if result.returncode != 0:
        die(f"terraform apply failed:\n{result.stderr}")

    # Wait for Postgres to be ready
    info("Waiting for PostgreSQL to be healthy…")
    for attempt in range(30):
        r = run(
            ["docker", "exec", "english_trainer_db",
             "pg_isready", "-U", "trainer_user", "-d", "english_trainer"],
            capture=True,
        )
        if r.returncode == 0:
            break
        time.sleep(1)
    else:
        die("PostgreSQL container started but is not accepting connections after 30s.")

    success("PostgreSQL is ready.")


def setup_venv() -> None:
    banner("Setting up Python virtual environment…", "🐍")
    if not PYTHON.exists():
        result = run([sys.executable, "-m", "venv", str(VENV)], capture=True)
        if result.returncode != 0:
            die(f"Failed to create venv:\n{result.stderr}")
        success("Virtual environment created.")
    else:
        success("Virtual environment already exists.")

    # Install/update dependencies
    result = run([str(PIP), "install", "-r", str(REQUIREMENTS), "-q"], capture=True)
    if result.returncode != 0:
        die(f"pip install failed:\n{result.stderr}")
    success("Dependencies installed.")


def setup_env() -> None:
    banner("Configuring environment…", "⚙️")
    if not ENV_FILE.exists():
        if ENV_EXAMPLE.exists():
            shutil.copy(ENV_EXAMPLE, ENV_FILE)
            success(".env file created from .env.example.")
        else:
            warn(".env.example not found, skipping.")
    else:
        success(".env already exists.")


def seed_database() -> None:
    banner("Seeding database with 50 irregular verbs…", "🌱")
    result = run([str(PYTHON), "main.py", "seed"], cwd=ROOT, capture=True)
    if result.returncode != 0:
        die(f"Seed failed:\n{result.stderr}")
    output = result.stdout.strip()
    if output:
        success(output.replace("\n", " "))


def launch_quiz(mode: str = "quiz") -> None:
    banner("Launching the quiz! Type 'q' to quit at any time.\n", "🎯")
    # Run interactively (no capture) so the user can type
    os.execv(str(PYTHON), [str(PYTHON), "main.py", mode])


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="English Verb Trainer — One-command launcher")
    parser.add_argument("--seed", action="store_true", help="Only seed the database and exit")
    parser.add_argument("--stats", action="store_true", help="Show stats instead of starting quiz")
    parser.add_argument("--skip-terraform", action="store_true",
                        help="Skip Terraform (use if Postgres is already running externally)")
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════╗
║   🎯  English Irregular Verb Trainer         ║
║       One-Command Setup & Launch             ║
╚══════════════════════════════════════════════╝
""")

    check_docker()

    if not args.skip_terraform:
        check_terraform()
        start_postgres()

    setup_venv()
    setup_env()
    seed_database()

    if args.seed:
        print("\n   ✅  Database seeded. Run  python start.py  to start the quiz.\n")
        return

    mode = "stats" if args.stats else "quiz"
    launch_quiz(mode)


if __name__ == "__main__":
    main()
