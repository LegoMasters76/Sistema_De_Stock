FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY requirements-prod.txt .
RUN pip wheel --wheel-dir=/wheels -r requirements-prod.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_ENV=production

WORKDIR /app
RUN groupadd --system django \
    && useradd --system --gid django --home-dir /app django \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R django:django /app

COPY requirements-prod.txt .
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements-prod.txt \
    && rm -rf /wheels

COPY --chown=django:django . .
COPY --chown=django:django docker/entrypoint.sh /usr/local/bin/stockpro-entrypoint
RUN chmod 0555 /usr/local/bin/stockpro-entrypoint

USER django
EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/stockpro-entrypoint"]
CMD ["gunicorn", "SistemaDeStock.wsgi:application", "--bind=0.0.0.0:8000", "--workers=3", "--timeout=60", "--access-logfile=-", "--error-logfile=-"]