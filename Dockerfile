FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd -r django && useradd -r -g django django

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-dev.txt requirements-prod.txt ./

FROM base as development

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN chown -R django:django /app

RUN mkdir -p /app/media /app/staticfiles && \
    chown -R django:django /app/media /app/staticfiles

EXPOSE 8000

USER django

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base as production

RUN pip install --no-cache-dir -r requirements-prod.txt && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R django:django /app

RUN mkdir -p /app/media /app/staticfiles && \
    chown -R django:django /app/media /app/staticfiles

RUN python manage.py collectstatic --noinput

EXPOSE 8000

USER django

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "AnalyseCVProject.wsgi:application"]