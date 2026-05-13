FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY app/       ./app/
COPY api/       ./api/
COPY static/    ./static/
COPY main.py    .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

# Create non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

EXPOSE 8000

USER app

ENTRYPOINT ["./entrypoint.sh"]
