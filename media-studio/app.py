import cpsl

from prompts import STYLE_GUIDE

app = cpsl.App(
    name="{{ project_slug }}",
    image=cpsl.Image(
        python_packages=["baml-py==0.220.0", "fal-client>=0.7.0", "pydantic>=2.13.2"]
    ),
    secrets=["FAL_KEY", "ANTHROPIC_API_KEY"],
)

generations = app.collection(
    "generations",
    columns=["prompt", "style", "aspect_ratio", "image_url"],
    scope="owner",
    sortable=True,
)


@app.page("Studio", icon="image")
def studio_page():
    return cpsl.ui.Page(
        [
            cpsl.ui.Text("Media Studio", style="heading"),
            cpsl.ui.Text(
                "Generate images from chat and keep a history.", style="muted"
            ),
            cpsl.ui.Table(
                collection=generations,
                columns=["prompt", "style", "aspect_ratio", "image_url"],
            ),
        ]
    )


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    import fal_client
    from baml_client import b

    spec = await b.ParseImageRequest(message=msg.text or "", style_guide=STYLE_GUIDE)
    await session.notify(f"Generating {spec.style} image...")

    result = fal_client.submit(
        "fal-ai/flux/schnell",
        arguments={"prompt": spec.prompt, "image_size": spec.aspect_ratio},
    ).get()

    image_url = result["images"][0]["url"]
    await generations.insert_one(
        {
            "prompt": spec.prompt,
            "style": spec.style,
            "aspect_ratio": spec.aspect_ratio,
            "image_url": image_url,
        }
    )
    await session.show_image(image_url, alt=spec.prompt)
    await session.reply(f"Generated: {spec.prompt}")
