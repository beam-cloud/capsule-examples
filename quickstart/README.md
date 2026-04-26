# Quickstart

A persistent internal knowledge agent for teams. Employees ask questions in chat and get answers from company docs, operating policies, planning notes, and saved company memory.

## Secrets

Required:

```bash
capsule secret create ANTHROPIC_API_KEY=sk-ant-...
```

You can also set `ANTHROPIC_API_KEY` locally while serving. Deployed apps need Capsule secrets.

## Telegram

This template declares a named Telegram channel:

```bash
capsule channel create workplace-telegram --type telegram -c bot_token=123:ABC
```

The web chat still works automatically; Telegram uses the same `@app.message()` handler.

## Run

```bash
uv sync
capsule serve app.py:app --channel workplace-telegram
```

If you edit `baml_src/`, regenerate the checked-in client with:

```bash
make baml
```

## Deploy

```bash
capsule deploy app.py:app
```

## What it demonstrates

- A chat-first assistant that answers from packaged company context.
- Owner-scoped memory stored in a Capsule collection.
- A named Telegram channel for questions from outside the web UI.
- BAML-backed structured answers with escalation guidance.
- A simple dashboard page showing included documents and saved memories.

Try:

```text
remember Enterprise customers need an owner assigned before escalation review
How do I document a customer escalation?
```

## What to change next

Replace `files/` with your own onboarding docs, team policies, planning notes, support playbooks, and customer workflows. Add Slack, Telegram, or WhatsApp when you want the same assistant outside the web UI.
