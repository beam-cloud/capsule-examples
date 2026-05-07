"""Deal Desk — custom React page with named chat threads.

This example demonstrates the React page runtime, `useChat(...)`, and
owner-scoped stable chat threads for project-style workflows.
"""

import cpsl


app = cpsl.App(
    name="{{ project_slug }}",
    image=cpsl.Image(),
    channels=[cpsl.Chat()],
    keep_warm_seconds=30,
)

app.theme(
    preset="dark",
    tagline="AI-assisted deal review workspace",
    primary="#7c8cff",
    accent="#8fd3ff",
    background="#07080b",
    foreground="#f4f5f8",
    sidebar="#0a0b10",
    surface="#11131a",
    border="#272a36",
    muted="#9aa1b2",
    font_sans='"Inter", ui-sans-serif, system-ui, sans-serif',
    font_mono='"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace',
    radius="lg",
)

app.shell(home="hidden", show_sidebar=True, show_pages=True)

app.add_page(
    "Deal Desk",
    icon="messages-square",
    component="pages/deal-desk.tsx",
)


deals = app.collection(
    "deals",
    columns=[
        cpsl.Column("project_id", label="Project ID"),
        cpsl.Column("property_address", label="Address"),
        cpsl.Column("monthly_gross", type="currency", label="Monthly Gross"),
        cpsl.Column("washer_count", type="number", label="Washers"),
        cpsl.Column("dryer_count", type="number", label="Dryers"),
        cpsl.Column("lease_remaining", label="Lease Remaining"),
        cpsl.Column("water_heater_type", label="Water Heater"),
        cpsl.Column("status", type="status"),
    ],
    scope="owner",
    sortable=True,
    filterable=True,
    paginate=25,
)


SEED_DEALS = [
    {
        "project_id": "3120-linden",
        "property_address": "3120 Linden Ave",
        "monthly_gross": "$20,000",
        "washer_count": 24,
        "dryer_count": 30,
        "lease_remaining": "4 yrs + 5-yr option",
        "water_heater_type": "Gas, 5 yrs old",
        "equipment_age": "Speed Queen 2018 / Huebsch 2016-19",
        "broker_contact": "Carla, Brightwater RE",
        "status": "active",
    },
    {
        "project_id": "42-market",
        "property_address": "42 Market St",
        "monthly_gross": "$14,500",
        "washer_count": 18,
        "dryer_count": 20,
        "lease_remaining": "2 yrs remaining",
        "water_heater_type": "Electric, unknown age",
        "equipment_age": "Mixed, mostly 2017",
        "broker_contact": "Sam, Northline CRE",
        "status": "follow-up",
    },
]


async def ensure_seed_deals():
    existing_ids = {row.get("project_id") for row in await deals.raw_filter({}, limit=100)}
    missing = [deal for deal in SEED_DEALS if deal["project_id"] not in existing_ids]
    if missing:
        await deals.insert_many(missing)


@app.message("deal-desk", label="Deal Desk")
async def deal_chat(session: cpsl.Session, msg: cpsl.Message):
    await ensure_seed_deals()
    project_id = session.data.get("project_id")
    row = await deals.get(project_id=project_id) if project_id else None
    address = row.get("property_address") if row else "this deal"
    text = (msg.text or "").strip()

    if "lease" in text.lower():
        await session.reply(
            f"For {address}, the lease note is: {row.get('lease_remaining', 'unknown')}."
        )
        return
    if "equipment" in text.lower():
        await session.reply(
            f"For {address}, equipment age is: {row.get('equipment_age', 'unknown')}."
        )
        return

    await session.reply(
        f"Reviewing {address}. I can help draft follow-ups, inspect fields, "
        "and track diligence questions. Try asking about lease terms or equipment age."
    )


@app.message()
async def default_chat(session: cpsl.Session, msg: cpsl.Message):
    await session.reply("Open the Deal Desk page and select a project to use named chat threads.")
