
FROM python:3.11-buster as builder

RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app
COPY ./lib lib
WORKDIR /app/lib
RUN poetry build
WORKDIR /app
RUN cp ./lib/dist/*.whl .
RUN rm -rf ./lib

COPY ./api/pyproject.toml ./api/poetry.lock ./

RUN poetry remove lib --group dev
RUN poetry add --lock ./lib-*.whl
RUN poetry install --without dev --sync && rm -rf $POETRY_CACHE_DIR

FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# COPY ./api .
COPY ./api/app app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
