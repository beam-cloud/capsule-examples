# Media Studio

A Capsule chat app that turns user requests into image prompts with BAML, calls fal.ai, and displays generated media in chat.

## Secrets

Required:

```bash
capsule secret create FAL_KEY=...
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

Swap the fal model, add brand style presets, or store generated media metadata in a collection.
