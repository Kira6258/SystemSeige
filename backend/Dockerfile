FROM python:3.12-slim

WORKDIR /app

# Install OS dependencies if required by some python packages (like psycopg2 or similar)
# But we're using asyncpg, which has binary wheels.
# Let's install some basic build tools just in case, though 3.12 should have wheels for everything.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
