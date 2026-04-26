from datetime import datetime, timezone


async def run_monitor(topic: str) -> dict:
    from baml_client import b

    summary = await b.SummarizeSignal(topic=topic, now=datetime.now(timezone.utc).isoformat())
    return {
        "topic": topic,
        "summary": summary.summary,
        "priority": summary.priority,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
