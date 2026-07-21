FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CYBER_JUNSHI_DB=/data/cyber-junshi.db

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN python -m pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 cyberjunshi \
    && mkdir -p /data \
    && chown cyberjunshi:cyberjunshi /data

USER cyberjunshi
VOLUME ["/data"]

ENTRYPOINT ["cyber-junshi"]
CMD ["serve"]
