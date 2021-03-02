ARG PYTHON_VER

FROM python:${PYTHON_VER}-slim

ENV INVOKE_LOCAL=True

RUN pip install --upgrade pip \
  && pip install poetry

WORKDIR /local
COPY ./ /local/

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi
