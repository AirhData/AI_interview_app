FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

ENV HF_HOME=/tmp/cache \
    TRANSFORMERS_CACHE=/tmp/cache \
    HF_HUB_CACHE=/tmp/cache/hub \
    SENTENCE_TRANSFORMERS_HOME=/tmp/cache/sentence_transformers

ENV XDG_DATA_HOME="/app/.local/share"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY . .

RUN mkdir -p /tmp/cache/hub \
             /tmp/cache/sentence_transformers \
             /tmp/vector_store \
             /app/.local/share && \
    chmod -R 777 /tmp /app/.local

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]