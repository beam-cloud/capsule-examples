# Browser Agent

A workflow-first Capsule app that opens a visible browser pane and runs a simple browser task.

## Secrets

No secrets are required for the default demo. If you add LLM planning, create a provider secret:

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

Point the workflow at a real web app, add authentication via integrations, and replace the demo browser page with your own automation target.
