FROM python:3.12.3-bookworm

WORKDIR /code

ENV DOTENV=.env \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes pipx

RUN pipx install poetry

ENV PATH="/root/.local/bin:${PATH}"

COPY ./app /code
COPY ./.env /code/.env
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
COPY ./containers/summarybot/launch.sh ./launch.sh
RUN chmod +x ./launch.sh

RUN python -m venv /venv
RUN . /venv/bin/activate && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

ENV PATH="/venv/bin:$PATH"

ENTRYPOINT [ "/code/launch.sh" ]
