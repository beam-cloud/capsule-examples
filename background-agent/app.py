import cpsl

from pages import runs_page
from tasks import run_monitor

app = cpsl.App(
    name="{{ project_slug }}",
    image=cpsl.Image(python_packages=["baml-py==0.220.0", "pydantic>=2.13.2"]),
    secrets=["ANTHROPIC_API_KEY"],
)

runs = app.collection(
    "runs",
    columns=["topic", "priority", "summary", "created_at"],
    scope="owner",
    sortable=True,
)


@app.page("Runs", icon="activity")
def page():
    return runs_page(runs)


@app.task()
async def monitor_topic(topic: str = "customer activity"):
    result = await run_monitor(topic)
    await runs.insert_one(result)
    return result


@app.schedule("0 14 * * *")
async def daily_monitor():
    await monitor_topic("daily product signals")


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    topic = (msg.text or "customer activity").strip()
    handle = await monitor_topic.submit(topic=topic)
    await session.show_task(handle, message=f"Monitoring: {topic}")
