FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE /app/
COPY src /app/src
COPY examples /app/examples
COPY skills /app/skills
COPY scripts /app/scripts
COPY docs /app/docs

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e '.[mcp,protein,reports]'

ENV PYTHONPATH=/app/src

HEALTHCHECK CMD sciagent doctor || exit 1
CMD ["sciagent", "demo", "--out", "runs/docker_demo"]
