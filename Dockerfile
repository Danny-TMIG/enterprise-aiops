# --- Stage 1: Build & Dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .[observability]

COPY platform/ ./platform/
COPY daemon/ ./daemon/

# --- Stage 2: Runtime Production Image ---
FROM python:3.11-slim AS runner

WORKDIR /app

RUN useradd -u 10001 -m sovereign && \
    chown -R sovereign:sovereign /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

USER sovereign

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PORT=8000

CMD ["uvicorn", "platform.app.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
