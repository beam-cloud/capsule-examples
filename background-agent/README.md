# Background Agent

A Capsule app for scheduled and on-demand agent loops. It writes run results to a collection and displays them on a page.

## Secrets

Required:

```bash
capsule secret create ANTHROPIC_API_KEY=sk-ant-...
```

## Run

```bash
uv sync
capsule serve app.py:app
```

## Deploy

```bash
capsule deploy app.py:app
```

## What to change next

Replace the sample monitor with your own recurring research, reporting, or operations loop.
