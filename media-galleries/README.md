# Media Galleries

A minimal Capsule app showing realtime image and video galleries on a custom chat page.

## What It Shows

- `ui.ImageGallery(data="generated_images")` binds an image gallery to session-aware data.
- `ui.VideoGallery(data="generated_videos")` binds a video gallery to session-aware data.
- `session.media.image(...)` persists generated image bytes and returns a JSON-safe gallery item.
- `session.media.video(...)` returns a JSON-safe video item with a stable `src` / `download_url`.
- Plain Python mutation updates the page: `session.data["generated_images"].append(item)`.

## Run

```bash
uv sync
capsule serve app.py:app
```

Then send any chat message. The app will generate an SVG image, add a sample video item, and append both to the custom chat page galleries.

## Deploy

```bash
capsule deploy app.py:app
```
