FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ .

# Default port (Railway overrides via PORT env)
ENV PORT=8000

# Run with shell to expand $PORT
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port \$PORT"
