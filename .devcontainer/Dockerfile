FROM --platform=amd64 mcr.microsoft.com/devcontainers/base:bookworm

WORKDIR /code

ENV DOTENV=.env \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1
    
RUN apt-get update && \
        apt-get install --no-install-suggests --no-install-recommends --yes \
            wget gnupg unzip fonts-noto-color-emoji curl build-essential software-properties-common apt-transport-https ca-certificates && \
    curl -fSsL https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor | sudo tee /usr/share/keyrings/google-chrome.gpg >> /dev/null && \
    echo deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main | sudo tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir .venv && chown -R vscode:vscode /code

USER vscode 

ARG PYTHON_VERSION=3.12.8

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    . $HOME/.local/bin/env && \
    uv python install ${PYTHON_VERSION} && \
    uv venv --python ${PYTHON_VERSION} && \
    . .venv/bin/activate && \
    uv sync

# ENTRYPOINT [ "/code/launch.sh" ]
