# Terminal Blocks

A minimal Capsule app that streams command output into chat as a terminal transcript.

## What It Shows

- `session.show_terminal(title="Diagnostics")` creates a fresh terminal transcript for each chat message.
- `term.shell("...")` runs an agent-authored shell command.
- `term.exec("python", "-c", "...")` runs a structured argv command.
- Both command methods return a result with `exit_code`, `stdout`, `stderr`, and `ok` for follow-up decisions.
- The transcript stays in chat history, so refreshing the page shows the completed command runs.
- Use `session.terminal("diagnostics", title="Diagnostics")` instead when you intentionally want later messages or tasks to append to the same named transcript.

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
