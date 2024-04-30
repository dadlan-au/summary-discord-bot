# Summary Discord Bot

## Dev Environment

Set up a development environment by [installing Poetry](https://python-poetry.org/docs/#installation). The recommended approach is to use `pipx`.

Set up a python virtualenv or use a devcontainer

```bash
python -m venv /venv
source /venv/bin/activate && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    cp .env.sample .env
```

Edit the newly created `.env` file with the appropriate options.

### Appendix

Use [Discord Colored Text Generator](https://rebane2001.com/discord-colored-text-generator/) to
adjust colours of text.
