FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY main.py .

# Default DATABASE_URL — override at runtime with --env
ENV DATABASE_URL=postgresql://trainer_user:trainer_pass_2024@host.docker.internal:5432/english_trainer

ENTRYPOINT ["python", "main.py"]
CMD ["quiz"]
