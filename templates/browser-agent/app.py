import cpsl

from browser import start_demo_server
from workflow import launcher_ui

app = cpsl.App(name="{{ project_slug }}", image=cpsl.Image())
workflow = app.workflow(
    "Run Browser Task",
    icon="globe",
    description="Open a browser and complete a simple visible workflow.",
)


@workflow.ui()
def ui():
    return launcher_ui()


@workflow.start()
async def start(session: cpsl.Session, input: cpsl.WorkflowInput):
    goal = input.payload.get("goal") or "Inspect the page."
    port = start_demo_server()
    await session.set_title(str(goal)[:60])
    await session.show_browser(port=port, title="Browser Agent Demo", mode="copilot")
    await session.reply(
        "Browser is open. This demo serves a small page from inside the runtime. "
        "Replace `browser.py` with your real browser automation logic."
    )
