# Summary Discord Bot

## Dev Environment

Set up a development environment by [installing Poetry](https://python-poetry.org/docs/#installation). The recommended approach is to use `pipx`.

Set up a python virtualenv or use a devcontainer

```bash
python -m venv ./venv && \
    source ./venv/bin/activate && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    cp .env.sample .env
```

Edit the newly created `.env` file with the appropriate options.

### Appendix

Use [Discord Colored Text Generator](https://rebane2001.com/discord-colored-text-generator/) to
adjust colours of text.


# Summary Bot

A Discord bot that generates AI-powered daily digests of server activity and displays Humanitix ticketing data.

## Features

- **Daily AI digest** — summarises the last 24h of conversation per channel, posted to a dedicated thread
- **On-demand summaries** — `/digest` command for any channel, any time period
- **Activity report** — daily message count summary across monitored channels
- **Humanitix integration** — `/tix` and `/tixt` commands display live event/ticket data as image or text
- **Auto-pruner** — automatically deletes old messages from configured channels on a schedule
- **Portal-controlled AI settings** — temperature, model, prompts and spend tracking managed via DadLAN WAN GUI

## Commands

| Command | Description |
|---|---|
| `/digest` | AI summary of the current channel (private by default, supports custom time period) |
| `/activity` | Trigger the daily activity report manually |
| `/tix` | Humanitix event data as animated image |
| `/tixt` | Humanitix event data as text |
| `$activity` | Plain message trigger for activity report |

## Setup

Copy `.env.sample` to `.env` and fill in the required values:

```
DISCORD_TOKEN=
DISCORD_BOT_GUILD_ID=
DISCORD_BOT_CATEGORY_IDS=
DISCORD_POST_MESSAGE_CHANNEL=
SUMMARY_POST_AT_LOCALTIME=08:00
TIMEZONE=Australia/Perth
OPENAI_API_KEY=
DADLAN_WAN_API_KEY=
DADLAN_WAN_API_URL=
```

See `BOT_REFERENCE.md` for the full configuration reference.

## Deployment

```bash
docker compose up -d
```

All commands are registered as guild-specific slash commands on startup.

## Dev Environment

Install [Poetry](https://python-poetry.org/docs/#installation) via `pipx`, then:

```bash
python -m venv ./venv && \
    source ./venv/bin/activate && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    cp .env.sample .env
```

Edit `.env` with your values.
