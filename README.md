# Capsule Examples

Starter apps for Capsule.

Docs: [docs.capsule.new](https://docs.capsule.new)

Use them through the CLI:

```bash
capsule create my-app
cd my-app
capsule deploy app.py:app
```

Choose a specific starter with `--template`:

```bash
capsule create starter --template default
capsule create support-bot --template quickstart
capsule create image-studio --template media-studio
capsule create browser-demo --template browser-agent
capsule create research-loop --template background-agent
capsule create research-notebook --template notebook-lm
```

## Examples

- `default` — clean starter app showing the core Capsule surfaces with BAML chat.
- `quickstart` — internal knowledge assistant with BAML, packaged docs, persistent memory, and a named Telegram channel.
- `media-studio` — chat app that turns requests into image prompts, calls fal.ai, and displays generated media.
- `browser-agent` — workflow app that opens a visible browser pane from inside the runtime.
- `background-agent` — scheduled and on-demand agent loop with a results page.
- `notebook-lm` — custom chat surface with a source filesystem browser, chat panel, and study-action studio.

Each directory is a complete Capsule app with its own `README.md`, `template.yaml`, `pyproject.toml`, and root-level `app.py`.
