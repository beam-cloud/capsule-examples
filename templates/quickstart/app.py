from pathlib import Path

import cpsl

DOCS = Path(__file__).parent / "files"
PROMPT = """
You are a practical internal assistant for a software company.
Answer from the company docs and saved memories first.
Keep replies concise and directly actionable.
If policy is missing or unclear, say who should confirm it.
Never invent access, HR, expense, customer, or security rules.
""".strip()

# App config: package dependencies and secrets travel with every deploy.
app = cpsl.App(
    name="{{ project_slug }}",
    image=cpsl.Image(
        python_packages=["baml-py==0.220.0", "pydantic>=2.13.2"],
        commands=["baml-cli generate --from baml_src"],
    ),
    channels=[cpsl.Channel("workplace-telegram")],
    secrets=["ANTHROPIC_API_KEY"],
)

# Collections give the agent durable app-level memory.
memories = app.collection(
    "memories",
    columns=["topic", "note", "source"],
    scope="owner",
    sortable=True,
    filterable=True,
)


def company_docs() -> str:
    return "\n\n".join(
        f"## {path.name}\n{path.read_text().strip()}"
        for path in sorted(DOCS.glob("*.md"))
    )


async def memory_context() -> str:
    rows = await memories.find(limit=25)
    if not rows:
        return "No saved workplace memories yet."
    return "\n".join(f"- {row['topic']}: {row['note']}" for row in rows)


# Pages turn the same app into an operator-facing dashboard.
@app.page("Knowledge", icon="files")
def knowledge_page():
    docs = [{"document": p.name, "bytes": p.stat().st_size} for p in sorted(DOCS.glob("*.md"))]
    return cpsl.ui.Page([
        cpsl.ui.Text("Workplace knowledge", style="heading"),
        cpsl.ui.Text("Answers come from company docs plus saved workplace memory.", style="muted"),
        cpsl.ui.Table(rows=docs, columns=["document", "bytes"]),
        cpsl.ui.Text("Saved memories", style="heading"),
        cpsl.ui.Table(collection=memories, columns=["topic", "note", "source"]),
    ])


# Chat is the user surface; teammates can ask questions or teach the agent facts.
@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    text = (msg.text or "").strip()

    if text.lower().startswith("remember "):
        note = text.removeprefix("remember ").strip()
        await memories.insert_one({"topic": "company note", "note": note, "source": "chat"})
        await session.reply("Got it. I saved that as company memory.")
        return

    # BAML keeps LLM output typed and predictable.
    from baml_client import b

    answer = await b.AnswerQuestion(
        question=text,
        context=f"{company_docs()}\n\n## Saved memories\n{await memory_context()}",
        system_prompt=PROMPT,
    )
    await session.reply(answer.answer)
