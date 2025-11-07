FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN pip install --upgrade pip \
    && pip install .[dev]

CMD ["python", "-m", "pytest"]
