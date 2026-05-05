import html
import textwrap

import cpsl
import cpsl.ui as ui


SAMPLE_VIDEO_URL = "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"

app = cpsl.App(
    name="{{ project_slug }}",
    image=cpsl.Image(),
    channels=[cpsl.Chat()],
    keep_warm_seconds=30,
)

app.shell(home="chat", show_sidebar=True, show_pages=False)


def _ensure_media_lists(session: cpsl.Session) -> None:
    session.data.setdefault("generated_images", [])
    session.data.setdefault("generated_videos", [])


def _image_svg(prompt: str, index: int) -> bytes:
    safe = html.escape(prompt[:80] or "Generated image")
    hue = (index * 47) % 360
    return textwrap.dedent(
        f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">
          <defs>
            <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="hsl({hue}, 80%, 58%)"/>
              <stop offset="100%" stop-color="hsl({(hue + 90) % 360}, 72%, 42%)"/>
            </linearGradient>
          </defs>
          <rect width="1200" height="800" rx="48" fill="url(#bg)"/>
          <circle cx="970" cy="160" r="110" fill="rgba(255,255,255,0.18)"/>
          <circle cx="210" cy="650" r="160" fill="rgba(0,0,0,0.16)"/>
          <text x="80" y="120" fill="white" font-family="Inter, system-ui, sans-serif" font-size="38" font-weight="700">Generated image #{index}</text>
          <foreignObject x="80" y="210" width="980" height="360">
            <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Inter, system-ui, sans-serif; font-size: 64px; font-weight: 800; line-height: 1.08; color: white;">
              {safe}
            </div>
          </foreignObject>
        </svg>
        """
    ).strip().encode()


@app.data("generated_images")
def generated_images(session: cpsl.Session):
    return session.data.get("generated_images", [])


@app.data("generated_videos")
def generated_videos(session: cpsl.Session):
    return session.data.get("generated_videos", [])


@app.chat_page(mode="single", scope="owner", sidebar_label="Studio")
def chat_page():
    return ui.Page([
        ui.Row(
            [
                ui.Column(
                    [
                        ui.Text("Generated images", style="heading"),
                        ui.Text("Images append here as soon as each item is persisted.", style="muted"),
                        ui.ImageGallery(data="generated_images", title="Image gallery"),
                    ],
                    fill=True,
                    gap=12,
                ),
                ui.ChatPanel(
                    title="Generate",
                    placeholder="Describe an image or video idea...",
                ),
                ui.Column(
                    [
                        ui.Text("Generated videos", style="heading"),
                        ui.Text("Videos use the same session data + realtime refresh path.", style="muted"),
                        ui.VideoGallery(data="generated_videos", title="Video gallery"),
                    ],
                    fill=True,
                    gap=12,
                ),
            ],
            columns=[1, 1.15, 1],
            min_widths=[240, 360, 240],
            gap=16,
            fill=True,
            align="stretch",
        )
    ])


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    prompt = (msg.text or "colorful media study").strip()
    _ensure_media_lists(session)

    image_number = len(session.data["generated_images"]) + 1
    image = await session.media.image(
        _image_svg(prompt, image_number),
        filename=f"generated-image-{image_number}.svg",
        mime_type="image/svg+xml",
        caption=prompt,
        alt=prompt,
    )
    session.data["generated_images"].append(image)

    video_number = len(session.data["generated_videos"]) + 1
    video = await session.media.video(
        SAMPLE_VIDEO_URL,
        caption=f"Sample video for: {prompt}",
        filename=f"generated-video-{video_number}.mp4",
    )
    session.data["generated_videos"].append(video)

    await session.reply(
        "Added one image and one video to the galleries. "
        "Refresh is implicit: appending to session data updates the page."
    )
