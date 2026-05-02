from __future__ import annotations

import shutil
from pathlib import Path

import cpsl
import cpsl.ui as ui


APP_DIR = Path(__file__).parent
SEED_DIR = APP_DIR / "files"
SOURCES_DIR = Path("/sources")

sources = cpsl.FileSystem("notebook-sources")

app = cpsl.App(
    name="{{ project_slug }}",
    image=cpsl.Image(),
    channels=[cpsl.Chat()],
    filesystems={"/sources": sources},
    keep_warm_seconds=30,
)

app.theme(
    preset="dark",
    tagline="Research workspace with sources",
    primary="#c69a6b",
    accent="#c69a6b",
    background="#060B0D",
    foreground="#fcffff",
    sidebar="#060B0D",
    surface="#0d1313",
    border="#2a2f30",
    muted="#8b9296",
    danger="#a85f66",
    success="#579276",
    font_sans='"Inter", ui-sans-serif, system-ui, sans-serif',
    font_mono='"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace',
    radius="lg",
)

app.shell(home="chat", show_sidebar=True, show_pages=False)


def source_files() -> list[Path]:
    if not SOURCES_DIR.exists():
        return []
    return sorted(
        path
        for path in SOURCES_DIR.rglob("*")
        if path.is_file() and not path.name.startswith(".")
    )


def read_sources(limit_chars: int = 24_000) -> str:
    chunks: list[str] = []
    used = 0
    for path in source_files():
        try:
            text = path.read_text(errors="ignore").strip()
        except OSError:
            continue
        if not text:
            continue
        rel = path.relative_to(SOURCES_DIR)
        chunk = f"## {rel}\n{text}"
        remaining = limit_chars - used
        if remaining <= 0:
            break
        chunks.append(chunk[:remaining])
        used += len(chunk)
    return "\n\n".join(chunks) or "No sources are available yet."


def simple_answer(question: str, context: str) -> str:
    question_words = {
        w.strip(".,:;!?()[]{}").lower() for w in question.split() if len(w) > 3
    }
    paragraphs = [p.strip() for p in context.split("\n\n") if p.strip()]
    matches = [
        p
        for p in paragraphs
        if question_words and any(word in p.lower() for word in question_words)
    ]
    selected = matches[:5] if matches else paragraphs[:4]

    lines = [
        "Based on the sources:",
        "",
        *[f"- {p.replace(chr(10), ' ')[:420]}" for p in selected],
    ]
    if not selected:
        lines.append("- Add or upload sources in the Sources panel, then ask again.")
    return "\n".join(lines)


def source_table_rows() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for path in source_files():
        rel = str(path.relative_to(SOURCES_DIR))
        rows.append({"source": rel, "bytes": path.stat().st_size})
    return rows


@app.data("source_stats")
def source_stats():
    files = source_files()
    return {
        "sources": len(files),
        "bytes": sum(path.stat().st_size for path in files),
    }


@app.data("session_stats")
def session_stats(session: cpsl.Session):
    return {
        "active": "Yes" if session.id else "No",
        "messages": len(session.history),
        "user": session.user.email or "Anonymous",
    }


@app.chat_page()
def chat_page():
    return ui.Page(
        [
            ui.Row(
                [
                    ui.Column(
                        [
                            ui.Text("Sources", style="heading"),
                            ui.Text(
                                "Upload, browse, and manage the files this chat should use.",
                                style="muted",
                            ),
                            ui.FileBrowser(
                                mount="/sources",
                                title="Notebook sources",
                                allow_upload=True,
                                allow_delete=True,
                                allow_rename=True,
                                allow_mkdir=True,
                            ),
                        ]
                    ),
                    ui.ChatPanel(
                        title="Chat",
                        placeholder="Ask about your sources...",
                        height=720,
                    ),
                    ui.Column(
                        [
                            ui.Text("Studio", style="heading"),
                            ui.Text(
                                "Generate study artifacts inside the same active chat session.",
                                style="muted",
                            ),
                            ui.Row(
                                [
                                    ui.Metric("Session", data="session_stats", field="active"),
                                    ui.Metric("Messages", data="session_stats", field="messages"),
                                ]
                            ),
                            ui.ActionCard(
                                "Audio overview",
                                description="Draft a conversational briefing script.",
                                prompt="Create an audio overview script from my sources.",
                                icon="audio-lines",
                            ),
                            ui.ActionCard(
                                "Slide deck",
                                description="Turn the sources into a concise deck outline.",
                                prompt="Create a slide deck outline from my sources.",
                                icon="presentation",
                            ),
                            ui.ActionCard(
                                "Mind map",
                                description="Map the main concepts and relationships.",
                                prompt="Create a mind map from my sources.",
                                icon="network",
                            ),
                            ui.ActionCard(
                                "Quiz",
                                description="Generate questions to test understanding.",
                                prompt="Create a quiz from my sources.",
                                icon="list-checks",
                            ),
                            ui.ActionCard(
                                "Briefing memo",
                                description="Summarize key takeaways and open questions.",
                                prompt="Write a briefing memo from my sources.",
                                icon="file-text",
                            ),
                        ]
                    ),
                ]
            )
        ]
    )


@app.page("Sources", icon="files", access="authenticated")
def sources_page():
    return ui.Page(
        [
            ui.Text("Source inventory", style="heading"),
            ui.Text(
                "The same files are available in the chat page Sources panel.",
                style="muted",
            ),
            ui.Row(
                [
                    ui.Metric("Files", data="source_stats", field="sources"),
                    ui.Metric("Bytes", data="source_stats", field="bytes"),
                ]
            ),
            ui.Table(rows=source_table_rows(), columns=["source", "bytes"]),
        ]
    )


@app.boot()
def seed_sources() -> None:
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    if any(SOURCES_DIR.iterdir()):
        return
    for path in SEED_DIR.glob("*.md"):
        shutil.copy(path, SOURCES_DIR / path.name)


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message) -> None:
    text = (msg.text or "").strip()
    if not text:
        await session.reply("Ask a question about the sources, or use a Studio action.")
        return

    await session.set_title(text[:60])
    context = read_sources()

    lower = text.lower()
    if "audio overview" in lower:
        await session.reply(
            "Audio overview script\n\n"
            "Host A: Today we're looking at the source set in this notebook.\n"
            "Host B: The main ideas are:\n"
            f"{simple_answer(text, context)}"
        )
        return
    if "slide deck" in lower:
        await session.reply(
            "Slide deck outline\n\n"
            "1. Executive summary\n"
            "2. What the sources say\n"
            "3. Key risks and open questions\n"
            "4. Recommended next steps\n\n"
            f"{simple_answer(text, context)}"
        )
        return
    if "mind map" in lower:
        await session.reply(
            "Mind map draft\n\n"
            "- Core topic\n"
            "  - Market structure\n"
            "  - Risk signals\n"
            "  - Source-backed decisions\n"
            "  - Open questions\n\n"
            f"{simple_answer(text, context)}"
        )
        return
    if "quiz" in lower:
        await session.reply(
            "Quiz\n\n"
            "1. What makes liquidity different from volume?\n"
            "2. Which risks are easiest to miss when looking only at headline positions?\n"
            "3. Why should research answers point back to sources?\n\n"
            f"{simple_answer(text, context)}"
        )
        return

    await session.reply(simple_answer(text, context))
