FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .
COPY models/ models/
COPY data/ data/

# Railway sets PORT env var
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}
