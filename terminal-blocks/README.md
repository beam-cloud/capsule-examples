# Terminal Blocks

A minimal Capsule app that streams command output into chat as a durable terminal transcript.

## What It Shows

- `session.terminal("diagnostics", title="Diagnostics")` creates or reopens a named terminal transcript for the chat session.
- `term.shell("...")` runs an agent-authored shell command.
- `term.exec("python", "-c", "...")` runs a structured argv command.
- The transcript stays in chat history, so refreshing the page shows the completed command runs.

## Run

```bash
uv sync
capsule serve app.py:app
```

Then send any chat message. The app will run two small diagnostics commands and render their output in a terminal block.

## Deploy

```bash
capsule deploy app.py:app
```
