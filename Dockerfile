FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY scripts/ ./scripts/

# Run as a non-root user (security fix). The app writes its SQLite DB at
# runtime, so give that user a writable data dir and point DB_PATH at it —
# without this the container exits on startup because it cannot create the DB.
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /data
ENV DB_PATH=/data/demobank.db

USER appuser

EXPOSE 3000

CMD ["python", "-m", "app.server"]
