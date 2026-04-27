FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/       ./app/
COPY api/       ./api/
COPY static/    ./static/
COPY main.py    .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

# Default DATABASE_URL — override via environment / docker-compose
ENV DATABASE_URL=postgresql://trainer_user:trainer_pass_2024@db:5432/english_trainer

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
