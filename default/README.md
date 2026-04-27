# Default Capsule App

A clean starter app for Capsule. It is intentionally small, but it shows the core pieces most apps grow from: chat, BAML, settings, collections, pages, data handlers, and tasks.

## What It Shows

- `cpsl.App(...)` declares the app name, runtime Python packages, secrets, and warm settings.
- `app.setting(...)` adds a configurable assistant style that shows up on the Overview page.
- `app.collection(...)` stores durable notes that chat and pages can both use.
- `@app.page(...)` and `@app.data(...)` build a simple operator-facing page.
- `@app.task(...)` runs longer work in the background and renders a live task card.
- `@app.message()` is the chat loop. It runs for every inbound user message.
- `session.reply(...)` sends a complete response, `session.notify(...)` sends lightweight progress, and `session.stream_reply_from(...)` streams model output.
- `baml_src/` contains the BAML prompt, model client, and intent classifier.
- `baml_client/` is generated from `baml_src/` and imported by `app.py`.

## Secrets

Required:

```bash
capsule secret create ANTHROPIC_API_KEY=sk-ant-...
```

You can also set `ANTHROPIC_API_KEY` locally while serving. Deployed apps need Capsule secrets.

## Run

```bash
uv sync
capsule serve app.py:app
```

If you edit `baml_src/`, regenerate the checked-in client with:

```bash
make baml
```

## Deploy

```bash
capsule deploy app.py:app
```

## Try It

```text
What can this starter do?
Explain how this Capsule app is wired.
Save a note that Capsule apps are defined in app.py.
Run a background task to draft a launch plan.
```

## What To Change Next

Edit `SYSTEM_PROMPT` in `app.py` to change the assistant's behavior. Add more BAML functions in `baml_src/` when you want typed outputs, classification, or tool-specific prompts. Add named channels, filesystems, integrations, or workflows when your app needs those surfaces.
