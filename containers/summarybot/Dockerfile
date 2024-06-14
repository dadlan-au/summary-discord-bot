FROM python:3.12.3-bookworm

WORKDIR /code

ENV DOTENV=.env \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes pipx wget gnupg unzip && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && \
#     unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
#     chmod +x /usr/local/bin/chromedriver && \
#     rm /tmp/chromedriver.zip

RUN pipx install poetry

ENV PATH="/root/.local/bin:${PATH}"

COPY ./app /code
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
COPY ./containers/summarybot/launch.sh ./launch.sh
RUN chmod +x ./launch.sh

RUN python -m venv /venv
RUN . /venv/bin/activate && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY ./.env /code/.env
ENV PATH="/venv/bin:$PATH"

ENTRYPOINT [ "/code/launch.sh" ]
