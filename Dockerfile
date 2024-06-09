FROM python:3.12-slim as base

ARG DEV=false
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN pip install poetry==1.8.1

COPY pyproject.toml poetry.lock ./
RUN if [ $DEV ]; then \
      poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    else \
      poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    fi

FROM base as runtime

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app/src

COPY api ./

RUN find . -type f -name '*.py' -exec sed -i 's/\bapi\.//g' {} +
RUN sed -i 's/from \.utils import send_notification/from utils import send_notification/' main.py

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]