# NotebookLM-Style Capsule App

A focused starter that turns Capsule's default chat into a custom research workspace:

- A sources panel backed by a mounted Capsule filesystem at `/sources`
- A central chat panel using the normal Capsule session mechanics
- A studio panel with prompt actions for audio overviews, slide decks, mind maps, quizzes, and briefing memos
- Session-aware metrics powered by `@app.data(..., session: cpsl.Session)`
- A dark market-research theme that exercises custom subdomain colors

The app seeds a few markdown files into `/sources` on boot. Upload or edit files in the Sources panel, then ask questions in chat.
Studio actions run inside the currently open chat session once a session exists.

## Run

```bash
uv sync
capsule serve app.py:app
```

## Deploy

```bash
capsule deploy app.py:app
```

## Try It

```text
What are the main liquidity risks in these sources?
Create an audio overview script from my sources.
Create a slide deck outline from my sources.
Create a quiz from my sources.
Write a briefing memo from my sources.
```

## Customize

- Edit `app.theme(...)` to change the visual system.
- Add source integrations to `sources = cpsl.FileSystem(...)` for Gmail, Google Drive, or other Airstore-backed source views.
- Use `session: cpsl.Session` in `@app.data` handlers for session-specific panels, metrics, and tables.
- Replace `simple_answer(...)` with your preferred LLM or BAML pipeline when you want production-grade answers with citations.
