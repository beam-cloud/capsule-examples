import cpsl
import cpsl.ui as ui


SYSTEM_PROMPT = """
You are the default Capsule starter assistant.
Answer clearly and explain the app structure when asked.
""".strip()


app = cpsl.App(
    name="{{ project_slug }}",
    image=cpsl.Image(python_packages=["baml-py==0.220.0", "pydantic>=2.13.2"]),
    secrets=["ANTHROPIC_API_KEY"],
)

# Settings are editable configuration for your app.
app.setting(
    "assistant_style",
    scope="owner",
    type=str,
    default="concise",
    options=["concise", "friendly", "technical"],
    label="Assistant style",
)

# Collections are durable records that chat, tasks, and pages can share.
notes = app.collection(
    "notes",
    columns=["text", "source"],
    scope="owner",
    filterable=True,
    paginate=10,
)


async def notes_context() -> str:
    rows = await notes.find(limit=10)
    return "\n".join(f"- {row['text']}" for row in rows) or "No saved notes yet."


@app.data("starter_stats")
async def starter_stats():
    return {
        "saved_notes": await notes.count(),
        "assistant_style": await app.settings.get("assistant_style"),
    }


# Pages can be pure Python UI, backed by collections and data handlers.
@app.page("Overview", icon="sparkles")
def overview_page():
    return ui.Page(
        [
            ui.Text("Default Capsule app", style="heading"),
            ui.Text(
                "A compact starter showing chat, BAML, settings, collections, pages, data, and tasks.",
                style="muted",
            ),
            ui.Row(
                [
                    ui.Metric("Saved notes", data="starter_stats", field="saved_notes"),
                    ui.Metric("Style", data="starter_stats", field="assistant_style"),
                ]
            ),
            ui.Card(
                "Settings",
                [
                    ui.Select(
                        "Assistant style",
                        setting="assistant_style",
                        options=["concise", "friendly", "technical"],
                    )
                ],
            ),
            ui.Table(collection=notes, columns=["text", "source"]),
        ]
    )


@app.task(retries=1, timeout=120)
async def run_background_work(prompt: str, session: cpsl.Session | None = None):
    from baml_client import b

    result = await b.DraftTaskResult(
        prompt=prompt,
        context=await notes_context(),
        system_prompt=SYSTEM_PROMPT,
    )
    await notes.insert_one({"text": result, "source": "task"})
    if session:
        await session.reply(result)
    return {"result": result}


# Chat is the main loop. BAML classifies intent; Python calls Capsule primitives.
@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    text = (msg.text or "").strip()
    if not text:
        await session.reply("Ask a question, save a note, or ask me to run a task.")
        return

    from baml_client import b, types

    intent = await b.ClassifyMessage(message=text)

    if intent.action == types.MessageAction.SAVE_NOTE:
        await notes.insert_one({"text": intent.note or text, "source": "chat"})
        await session.reply("Saved that note. You can see it on the Overview page.")
        return

    if intent.action == types.MessageAction.RUN_TASK:
        handle = await run_background_work.submit(session=session, prompt=intent.task_prompt or text)
        await session.show_task(handle, message="Started background work")
        return

    await session.set_title(text[:60])
    await session.notify("Thinking...")
    await session.stream_reply_from(
        b.stream.AnswerQuestion(
            question=intent.question or text,
            context=await notes_context(),
            style=await app.settings.get("assistant_style") or "concise",
            system_prompt=SYSTEM_PROMPT,
        )
    )
