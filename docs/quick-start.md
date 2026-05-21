# Quick Start Guide

Get the English Verb Trainer running in less than 5 minutes.

## Prerequisites

Only one tool required:

- **Docker Desktop** — [Download here](https://www.docker.com/products/docker-desktop/)

## 🚀 One-Command Start

```bash
git clone https://github.com/LabordaSebastian/english-verb-trainer.git
cd english-verb-trainer
docker compose up
```

Open your browser to **http://localhost:8000** and start practicing!

## What Just Happened?

Docker Compose automatically spun up:

1. **PostgreSQL 15** — Database with 100 irregular verbs preloaded
2. **FastAPI Web App** — Interactive SPA interface
3. **Health Checks** — Automatic verification that services are ready

## 💻 CLI Usage (Local Setup)

If you have Python 3.10+ installed locally:

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows PowerShell

# Initialize database
verb-trainer seed

# Start quiz
verb-trainer quiz

# View stats
verb-trainer stats
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `verb-trainer quiz` | Start a random 10-question quiz |
| `verb-trainer quiz --verb read --rounds 20` | Quiz on a specific verb, 20 questions |
| `verb-trainer stats` | View your progress and hardest verbs |
| `verb-trainer seed` | Load/refresh 100 irregular verbs |
| `verb-trainer vocab-seed` | Load/refresh 1867 vocabulary words |

## 🛑 Stopping the Application

```bash
docker compose down
```

Add `-v` flag to remove the database volume:
```bash
docker compose down -v
```

## 🛠️ Using Makefile (Linux/Mac)

```bash
make up       # Start containers
make stop     # Stop containers without removing volumes
make down     # Stop containers and remove volumes
make rebuild  # Rebuild and start containers (use after Python/API changes)
make test     # Run tests
make lint     # Check code style
make quiz     # Start CLI quiz (requires local Python)
make clean    # Remove virtual environment
make help     # See all available commands
```

## 🐛 Troubleshooting

### "Port 8000 already in use"
```bash
# Use a different port
docker compose -f docker-compose.yml -p different_port up -d
# Or kill process using port 8000
sudo lsof -ti:8000 | xargs kill -9
```

### "Cannot connect to PostgreSQL"
```bash
# Check if containers are running
docker ps

# View logs
docker compose logs db
docker compose logs app
```

### "Module not found" (local setup)
```bash
# Reinstall dependencies in virtual environment
source .venv/bin/activate
pip install -r requirements.txt
```

## ✅ Health Check

Verify the app is working:

```bash
# Should list available verbs (seed first via docker compose or verb-trainer seed)
curl http://localhost:8000/api/verbs/quiz?count=5
```

## 📚 Next Steps

- [Explore the Architecture](architecture/overview.md)
- [Read the Full API Reference](api/endpoints.md)
- [View Project Structure](structure.md)
- [Run the Tests](development/testing.md)

## 💡 Tips

- **First time with Docker?** Check [Docker documentation](https://docs.docker.com/)
- **Want to learn more?** See the [Architecture Overview](architecture/overview.md)
- **Contributing code?** Read [Contributing Guide](development/contributing.md)
