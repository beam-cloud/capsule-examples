# Capsule App Developement Guide

Use this guide when building, debugging, or iterating on `capsule.new` apps with the `cpsl` Python SDK and `capsule` CLI. Favor public APIs exported from `cpsl`.

## Mental Model

One `cpsl.App` is the source of truth for the product you're building. `capsule serve` and `capsule deploy` read the same app definition: runtime image, chat handlers, pages, data handlers, collections, settings, tasks, schedules, integrations, channels, secrets, filesystems, and pricing.

Each deployed app has app-scoped users. In handlers, `session.user` is the current user of this app, not a global Capsule workspace user. Each app user runs in an isolated managed runtime with the declared image, packages, secrets, integrations, and mounted filesystems.

Put new features in the smallest Capsule surface that fits:

- Use `@app.message()` for conversational routing.
- Use collections for durable queryable records.
- Use settings for app, owner, or user configuration.
- Use pages for operator UI, dashboards, review queues, and controls.
- Use tasks for long work and side effects.
- Use schedules for recurring work.
- Use filesystems for durable files, uploads, generated artifacts, and large intermediates.
- Use workflows for named, session-backed flows launched from the sidebar.

## Day-To-Day Loop

```bash
uv add cpsl
capsule login
capsule create my-app
cd my-app
uv sync
capsule secret create ANTHROPIC_API_KEY=sk-ant-...
capsule serve app.py:app # to iterate with hot-reload
capsule deploy app.py:app # to deploy
```

The default template is `default`, a clean starter app with BAML chat plus core Capsule surfaces. Use `quickstart` for a BAML-backed assistant with packaged context; use `background-agent` for scheduled or on-demand agent loops plus a results page.

Entry points are always `file.py:symbol`, such as `app.py:app` or `app.py:MyApp`. During `serve`, Capsule uploads the project, boots a live runtime, and hot-reloads Python, TSX/TS/JS, CSS, JSON, YAML, images, Markdown, and HTML.

Runtime dependencies belong in `cpsl.Image(...)`. Installing a package only in the local virtualenv is not enough for hosted `serve` or `deploy`.

The default runtime base image is `python:3.13-slim`.

## Functional App Default

Prefer functional style for new apps and examples. It is shorter and keeps deploy configuration explicit on `App(...)`.

```python
import cpsl

app = cpsl.App(
    name="research-copilot",
    image=cpsl.Image(python_packages=["baml-py==0.220.0", "pydantic>=2.13.2"]),
    secrets=["ANTHROPIC_API_KEY"],
)

SYSTEM_PROMPT = "You are a concise Capsule assistant."


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    text = (msg.text or "").strip()
    if not text:
        await session.reply("Send me a question.")
        return

    from baml_client import b

    await session.notify("Thinking...")
    await session.stream_reply_from(
        b.stream.AnswerQuestion(
            question=text,
            context="",
            system_prompt=SYSTEM_PROMPT,
        )
    )
```

Run it with:

```bash
capsule serve app.py:app
```

Put prompts, clients, and typed outputs in `baml_src/`, generate `baml_client`, and prefer `session.stream_reply_from(b.stream.SomeFunction(...))` for model responses. A minimal BAML backing file looks like:

```baml
client<llm> Anthropic {
  provider anthropic
  options {
    model claude-sonnet-4-20250514
    api_key env.ANTHROPIC_API_KEY
  }
}

function AnswerQuestion(question: string, context: string, system_prompt: string) -> string {
  client Anthropic
  prompt #"
    {{ _.role("system") }}
    {{ system_prompt }}

    Context:
    {{ context }}

    {{ _.role("user") }}
    {{ question }}
  "#
}
```

Regenerate after editing `baml_src/`:

```bash
baml-cli generate --from baml_src
```

Only use direct provider SDKs when the app intentionally avoids BAML. For those APIs, `session.chat_messages(msg)` produces alternating `user` / `assistant` messages.

## Session Output Helpers

Use `session.reply(...)` for a complete response and `session.notify(...)` for lightweight status. Stream long answers so the UI stays alive:

```python
@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    async with session.stream_reply() as reply:
        reply.write("Starting report...\n")
        async for token in model_stream:
            reply.write(token)
```

For BAML-style or other async model streams that yield strings or cumulative snapshots, use the one-liner:

```python
full_text = await session.stream_reply_from(model_stream)
```

Show generated images or saved artifacts inline. Local paths are uploaded automatically; URLs and data URLs also work.

```python
@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    image_path = "/data/plots/summary.png"
    await session.show_image(image_path, alt="Summary chart", width=720)
```

Show a browser pane when the app launches or controls a web workflow. Use `url=` for external pages, or `port=` for a server running inside the sandbox.

```python
@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    if "open docs" in (msg.text or "").lower():
        await session.show_browser(
            url="https://capsule.new",
            title="Capsule Docs",
            mode="copilot",
        )
        return

    if "preview app" in (msg.text or "").lower():
        await session.show_browser(port=5173, path="/", title="Local Preview", mode="split")
        return

    if "hide browser" in (msg.text or "").lower():
        await session.hide_browser()
        return
```

Use `session.show_task(handle, message=...)`, `session.show_integration(...)`, and `session.prompt_file(...)` when chat should expose task state, connection prompts, or uploads instead of plain text.

## Production-Shaped Slice

This compact example shows the common shape: collection, setting, data handler, page, task, schedule, and message handler.

```python
import cpsl
import cpsl.ui as ui

app = cpsl.App(
    name="support-ops",
    image=cpsl.Image(),
    channels=[cpsl.Channel("support-telegram")],
    filesystems={"/data": cpsl.FileSystem("support-ops")},
)

threads = app.collection(
    "threads",
    columns=[
        cpsl.Column("subject"),
        cpsl.Column("sender", type="email"),
        cpsl.Column("status", type="status"),
        cpsl.Column("priority"),
    ],
    scope="app",
    sortable=True,
    filterable=True,
    paginate=25,
)

app.setting("show_closed_threads", scope="app", type=bool, default=False)


@app.data("mailbox_metrics", access="authenticated")
async def mailbox_metrics(ctx: cpsl.RequestContext):
    rows = await threads.find(limit=500)
    return {
        "total_threads": len(rows),
        "needs_review": len([row for row in rows if row.get("status") == "needs-review"]),
        "authenticated": ctx.authenticated,
    }


@app.page("Overview", icon="layout-dashboard", access="authenticated")
def overview():
    return ui.Page(
        [
            ui.Row(
                [
                    ui.Metric("Threads", data="mailbox_metrics", field="total_threads"),
                    ui.Metric("Needs Review", data="mailbox_metrics", field="needs_review"),
                ]
            ),
            ui.Card("Settings", [ui.Toggle("Show closed threads", setting="show_closed_threads")]),
            ui.Table(threads),
        ]
    )


@app.task(retries=2, timeout=300, lock="mailbox:sync")
async def sync_threads(session: cpsl.Session | None = None):
    if session:
        await session.notify("Syncing mailbox...")
    await threads.insert_one(
        {
            "subject": "Renewal review",
            "sender": "ops@example.com",
            "status": "needs-review",
            "priority": "high",
        }
    )
    return {"synced": 1}


@app.schedule("0 * * * *")
async def hourly_sync():
    await sync_threads.submit()


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    if "sync" in (msg.text or "").lower():
        handle = await sync_threads.submit(session=session)
        await session.show_task(handle, message="Mailbox sync started")
        return

    count = await threads.count()
    await session.reply(f"There are {count} support threads. Ask me to sync.")
```

## State And Data

Choose the lightest state layer that fits:

- `session.data`: per-conversation state.
- `await session.get/set/delete(key, scope="session" | "user" | "owner" | "app")`: persistent KV.
- `app.collection(...)`: durable records with CRUD and table metadata.
- `app.setting(...)`: scoped configuration that can be read from Python and edited in UI.

Collection scopes are `app`, `user`, `owner`, and `session`. App-scoped collections can be used directly through their `CollectionRef`; user, owner, and session scoped collections are usually accessed through `session.db` so the live session supplies identity.

```python
contacts = app.collection("contacts", columns=["name", "email"], scope="app")
bookmarks = app.collection("bookmarks", columns=["title", "url"], scope="user")


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    await contacts.insert_one({"name": "Ada", "email": "ada@example.com"})
    await session.db.bookmarks.insert_one({"title": "Capsule", "url": "https://capsule.new"})
    await contacts.update_one({"email": "ada@example.com"}, {"name": "Ada Lovelace"})
```

Plain update dicts become `$set` patches. Operator updates also work:

```python
await contacts.update_one({"email": "ada@example.com"}, {"$inc": {"touches": 1}})
```

Do not mix plain keys and operator keys in the same update document.

## Pages, UI DSL, And Frontend

Use Python DSL pages for dashboards, metrics, settings, tables, charts, and task boards:

```python
@app.page("Tasks", icon="list-check", access="authenticated")
def tasks_page():
    return cpsl.ui.Page([cpsl.ui.TaskBoard(title="Tasks")])
```

Full `cpsl.ui` page and workflow component signatures are listed in the API reference below.


Use React pages when the page becomes an application surface:

```python
app.add_page(
    "Mailbox",
    icon="mail",
    component="pages/mailbox.tsx",
    packages=["lucide-react@0.344.0"],
    access="authenticated",
)
```

React pages use `@capsule/page` helpers such as `useCapsule`, `useData`, `useCollection`, and `useTheme`:

```tsx
import { useCapsule, useData } from "@capsule/page"

export default function Mailbox() {
  const { user, login } = useCapsule()
  const metrics = useData("mailbox_metrics")

  if (!user) return <button onClick={login}>Sign in</button>
  return <pre>{JSON.stringify(metrics.data, null, 2)}</pre>
}
```

Expose computed JSON to DSL and React pages with `@app.data(...)`. Add `ctx: cpsl.RequestContext` when the handler needs caller identity, auth state, or connected integrations.

## Tasks, Files, And Integrations

Tasks become descriptors with `.submit(...)`, `.schedule(...)`, `.find(...)`, `.count(...)`, and `.cancel(...)`. Use `process=True` for subprocess isolation, `timeout=` to bound work, `retries=` for transient failures, and `lock=` to avoid duplicates.

```python
@app.task(retries=3, timeout=600, lock="owner:{owner_id}", process=True)
async def rebuild_index(owner_id: str):
    return {"owner_id": owner_id, "rebuilt": True}
```

Mount durable filesystems through the app and use normal file APIs in handlers, tasks, and workflows:

```bash
capsule fs create reports
```

```python
app = cpsl.App(
    name="reports",
    image=cpsl.Image(),
    filesystems={"/data": cpsl.FileSystem("reports")},
)


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    upload = await session.prompt_file(
        message="Upload a CSV",
        accept=".csv,text/csv",
        path="/data/uploads",
    )
    await session.reply(f"Uploaded {upload.name} to {upload.path}")
```

Use secrets for app-owned credentials and integrations for end-user connections:

```bash
capsule secret create ANTHROPIC_API_KEY=sk-ant-...
capsule channel create support-telegram --type telegram -c bot_token=123:ABC
```

```python
app = cpsl.App(
    name="support-ops",
    image=cpsl.Image(python_packages=["baml-py==0.220.0", "pydantic>=2.13.2"]),
    secrets=["ANTHROPIC_API_KEY"],
    channels=[cpsl.Channel("support-telegram")],
)

app.add_integration(
    "github",
    client_id=cpsl.Secret.from_name("GITHUB_CLIENT_ID"),
    client_secret=cpsl.Secret.from_name("GITHUB_CLIENT_SECRET"),
    scopes=["repo"],
)


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    if "github" not in session.integrations:
        await session.show_integration("github", reason="Connect GitHub for repository analysis")
```

Prefer named `cpsl.Channel("name")` resources. Built-in web chat is implicit; `cpsl.Chat()` mostly exists for backward compatibility. Inline `Telegram`, `Slack`, and `WhatsApp` channel declarations are deprecated.

## Workflows

Use workflows when users should start a named flow from the sidebar and continue in a session-backed chat.

```python
wf = app.workflow(
    "Research Company",
    scope="user",
    icon="search",
    description="Collect context and draft a brief.",
)


@wf.ui()
def workflow_ui():
    return cpsl.ui.WorkflowShell(
        "Research Company",
        children=[
            cpsl.ui.FormSection(
                "Input",
                children=[cpsl.ui.TextInput("Company", name="company", required=True)],
            ),
            cpsl.ui.ActionBar(children=[cpsl.ui.SubmitButton("Start", primary=True)]),
        ],
    )


@wf.start()
async def start(session: cpsl.Session, input: cpsl.WorkflowInput):
    await session.reply(f"Researching {input.company}")


@wf.action("approve")
async def approve(session: cpsl.Session, input: cpsl.WorkflowInput):
    await session.reply(f"Approved {input.get('company', 'request')}")


@wf.message()
async def continue_research(session: cpsl.Session, msg: cpsl.Message):
    await session.reply(f"Continuing with: {msg.text}")
```

## API Reference

These signatures are checked against the SDK. Instance method signatures omit `self`; `async` entries must be awaited. Prefer this section when editing generated apps.

```python
# App definition and deploy config
App(name: str, *, image: Image | None = None, channels: list | None = None, secrets: list[str] | None = None, filesystems: dict[str, FileSystem] | None = None, cpu: float = 0.25, memory: int = 512, price: int = 0, pricing_type: str = "one_time") -> None  # use to declare the app and functional runtime
App.cls(*, image: Image, price: int = 0, pricing_type: str = "one_time", channels: list | None = None, secrets: list[str] | None = None, filesystems: dict[str, FileSystem] | None = None, cpu: float = 0.25, memory: int = 512) -> Callable  # use to declare class-based runtime config
App.collection(name: str, *, columns: list[str | Column] | None = None, scope: str = "app", sortable: bool = False, filterable: bool = False, paginate: int = 0) -> CollectionRef  # use for durable queryable records
Column(key: str, type: str = "text", label: str | None = None, format: str | None = None) -> Column  # use for typed table columns; type: text/number/currency/date/link/email/status/tags/boolean
App.setting(name: str, *, scope: str = "app", type: type = str, default: Any = None, options: list[str] | None = None, label: str | None = None) -> None  # use for configurable app/user/owner knobs
App.theme(*, preset=None, logo=None, logo_background=None, tagline=None, primary=None, accent=None, background=None, foreground=None, sidebar=None, surface=None, border=None, muted=None, danger=None, success=None, font_sans=None, font_mono=None, radius=None) -> None  # use to brand the hosted UI
App.add_integration(integration_type: str, *, client_id: str | Secret = "", client_secret: str | Secret = "", scopes: list[str] | None = None, fields: list[str] | None = None) -> None  # use when end users must connect OAuth/secret credentials
App.add_page(name: str, *, icon: str = "file", component: str, packages: list[str] | None = None, order: int | None = None, access: str = "public") -> None  # use for custom React pages
App.page(name: str, *, icon: str = "file", order: int | None = None, access: str = "public") -> Callable  # use for Python DSL pages
App.data(name: str, *, access: str = "public") -> Callable  # use to expose JSON to DSL and React pages
App.workflow(name: str, *, scope: str = "user", icon: str = "workflow", description: str = "") -> Workflow  # use for named sidebar flows backed by sessions
async App.get(key: str, default: Any = None) -> Any  # use to read app-global KV state
async App.set(key: str, value: Any) -> None  # use to write app-global KV state
async App.delete(key: str) -> None  # use to remove app-global KV state
async app.settings.get(key: str) -> Any  # use to read a declared setting
async app.settings.set(key: str, value: Any) -> None  # use to update a declared setting
async app.settings.get_all(keys: list[str] | None = None) -> dict[str, Any]  # use to bulk-read declared settings

# Functional decorators; class-based equivalents are cpsl.boot(), cpsl.message(), etc.
App.boot() -> Callable  # use to initialize runtime resources once
App.shutdown() -> Callable  # use to clean up before runtime shutdown
App.enter() -> Callable  # use to initialize a new session
App.exit() -> Callable  # use to clean up a closing session
App.message() -> Callable  # use as the main inbound chat/API handler
App.schedule(cron: str) -> Callable  # use for recurring cron work
App.endpoint(method: str = "GET", path: str = "/", authorized: bool = True) -> Callable  # use for lightweight HTTP handlers
App.asgi(path: str = "/app") -> Callable  # use to mount FastAPI/Starlette-style apps
App.task(retries: int = 0, timeout: int = 0, lock: str | None = None, retry_for: list[type[Exception]] | None = None, callback_url: str | None = None, process: bool = False) -> Callable  # use for background work in functional apps
boot() -> Callable  # use as class-based boot decorator
shutdown() -> Callable  # use as class-based shutdown decorator
enter() -> Callable  # use as class-based session-enter decorator
exit() -> Callable  # use as class-based session-exit decorator
message() -> Callable  # use as class-based message decorator
task(retries: int = 0, timeout: int = 0, lock: str | None = None, retry_for: list[type[Exception]] | None = None, callback_url: str | None = None, process: bool = False) -> Callable  # use for class-based background work
schedule(cron: str) -> Callable  # use as class-based cron decorator
endpoint(method: str = "GET", path: str = "/", authorized: bool = True) -> Callable  # use as class-based HTTP endpoint decorator
asgi(path: str = "/app") -> Callable  # use as class-based ASGI mount decorator

# Session and request context
session.id  # use to identify the live conversation
session.user  # use to access app-scoped user identity
session.channel  # use to branch by chat/api/telegram/slack/whatsapp
session.history  # use for recent message history
session.data  # use for per-session mutable state
session.integrations  # use to read connected user credentials
session.db  # use to access user/owner/session-scoped collections
async Session.get(key: str, default: Any = None, *, scope: str = "session") -> Any  # use to read scoped KV state
async Session.set(key: str, value: Any, *, scope: str = "session") -> None  # use to write scoped KV state
async Session.delete(key: str, *, scope: str = "session") -> None  # use to delete scoped KV state
async Session.reply(text: str) -> None  # use for complete text replies
async Session.notify(text: str) -> None  # use for lightweight progress updates
async Session.stream(chunks: AsyncIterator[str]) -> None  # use to pipe an async text iterator
Session.stream_reply() -> ReplyStream  # use for manual incremental streaming
Session.chat_messages(current: Message, *, cls: Any = None) -> list  # use for non-BAML SDK chat history formatting
async Session.stream_reply_from(stream: Any) -> str  # use for BAML/model streams
async Session.show(block: Block) -> None  # use for custom structured chat blocks
async Session.show_task(handle_or_id: Any, *, message: str | None = None) -> None  # use to render live task cards
async Session.show_integration(integration_type: str, *, reason: str = "") -> None  # use to show non-blocking connect prompts
async Session.show_browser(*, port: int = 0, url: str = "", title: str = "", path: str = "/", mode: str = "split") -> None  # use to show external URLs or sandbox ports; mode: split/copilot/preview
async Session.hide_browser() -> None  # use to close the browser pane
async Session.set_title(title: str) -> None  # use to name the session/workflow run
async Session.show_image(source: str, *, alt: str = "", width: int | None = None) -> None  # use to display generated or remote images
async Session.prompt_file(*, message: str = "Please upload a file", accept: str = "", path: str | None = None, timeout: float = 300.0) -> FileUpload  # use to request uploads
async Session.prompt_integration(integration_type: str, *, reason: str = "", timeout: float = 300.0) -> IntegrationCredentials  # use when a flow cannot continue without credentials
current_session() -> Session | None  # use to get handler context outside direct session args
ctx: RequestContext  # use as a data/endpoint handler arg for user, integrations, authenticated, request
msg: Message  # use as a message handler arg; fields: text, sender, channel_type, timestamp, attachments
attachment: Attachment  # use from msg.attachments; fields: name, content_type, url, size
async Attachment.download(path: str) -> str  # use to save a message attachment locally
async FileUpload.download(path: str) -> str  # use to save a FileUpload from prompt_file()

# Collections, tasks, and workflows
async CollectionRef.insert_one(document: dict) -> dict  # use to create one record
async CollectionRef.insert_many(documents: list[dict]) -> list[dict]  # use to create records in bulk
async CollectionRef.find_one(filter: dict | None = None) -> dict | None  # use to fetch a single matching record
async CollectionRef.find(filter: dict | None = None, limit: int = 0, skip: int = 0, sort: dict | None = None) -> list[dict]  # use to query records
async CollectionRef.update_one(filter: dict, update: dict) -> dict  # use to patch one record; plain updates auto-$set; do not mix with operators
async CollectionRef.delete_one(filter: dict) -> dict  # use to delete one matching record
async CollectionRef.count(filter: dict | None = None) -> int  # use to count matching records
async TaskDescriptor.submit(session: Session | None = None, **kwargs: Any) -> TaskHandle  # use to start background work now
async TaskDescriptor.schedule(session: Session | None = None, delay: str | timedelta | None = None, **kwargs: Any) -> TaskHandle  # use to run later; delay: "5s", "30m", "1h", "3d", or timedelta
async TaskDescriptor.find(status: str | None = None, session_id: str | None = None, limit: int = 100, offset: int = 0, **kwargs: Any) -> list[TaskHandle]  # use to list matching task runs
async TaskDescriptor.count(status: str | None = None, **kwargs: Any) -> int  # use to count matching task runs
async TaskDescriptor.cancel(status: str | None = None, **kwargs: Any) -> int  # use to cancel matching pending/scheduled/retry runs
async TaskHandle.status() -> str  # use to poll one task state
async TaskHandle.refresh() -> None  # use to extend a running task timeout
async TaskHandle.cancel() -> None  # use to cancel one pending/scheduled/retry task
Workflow.ui() -> Callable  # use to register a workflow launcher UI
Workflow.start() -> Callable  # use to handle workflow launch
Workflow.action(name: str) -> Callable  # use to handle named workflow submits
Workflow.message() -> Callable  # use to handle freeform chat inside a workflow
WorkflowInput(data: dict | None = None) -> WorkflowInput  # use to wrap workflow form/action payloads
WorkflowInput.__getitem__(key: str) -> Any  # use for required workflow input fields
WorkflowInput.__getattr__(key: str) -> Any  # use for convenient workflow input attribute access
WorkflowInput.get(key: str, default: Any = None) -> Any  # use for optional workflow input fields
WorkflowInput.to_dict() -> dict[str, Any]  # use to serialize workflow input

# UI DSL and workflow launcher components
cpsl.ui.Page(children)  # use as the root of a Python DSL page
cpsl.ui.Row(children)  # use for horizontal layout
cpsl.ui.Column(children)  # use for vertical layout
cpsl.ui.Card(title=None, children=None)  # use to group related UI
cpsl.ui.Text(content, *, style=None)  # use for headings/body/muted text
cpsl.ui.Divider()  # use to separate page sections
cpsl.ui.Metric(label, *, data=None, field=None, value=None, format=None)  # use for KPIs; format: number/currency/percent
cpsl.ui.Table(collection=None, *, data=None, rows=None, columns=None, sortable=False, filterable=False, paginate=0)  # use for collection/data/inline tables
cpsl.ui.Chart(*, data=None, chart_type="line", x=None, y=None)  # use for charts; chart_type: line/bar/pie/scatter/area
cpsl.ui.Toggle(label, *, setting)  # use for boolean setting controls
cpsl.ui.TextInput(label="", *, name=None, setting=None, multiline=False, placeholder=None, required=False)  # use for settings or workflow text fields
cpsl.ui.NumberInput(label="", *, name=None, setting=None, min=None, max=None, step=None, required=False)  # use for numeric settings or workflow fields
cpsl.ui.Select(label="", *, name=None, setting=None, options=None, default=None, required=False)  # use for enum-like settings or workflow fields
cpsl.ui.TaskBoardColumn(label, statuses)  # use to customize task board columns
cpsl.ui.TaskBoard(*, title=None, filter=None, columns=None, refresh_ms=5000)  # use to show task state on pages
cpsl.ui.WorkflowShell(title="", *, children=None)  # use as the root of a workflow launcher
cpsl.ui.FormSection(label="", *, children=None)  # use to group workflow fields
cpsl.ui.TextArea(*, name, label="", placeholder="", required=False, rows=4)  # use for multiline workflow input
cpsl.ui.FileInput(*, name, label="", accept=None, required=False, multiple=False)  # use for workflow file uploads
cpsl.ui.ImageInput(*, name, label="", required=False, multiple=False)  # use for workflow image uploads
cpsl.ui.UrlInput(*, name, label="", placeholder="", required=False)  # use for a single URL workflow field
cpsl.ui.UrlListInput(*, name, label="", placeholder="")  # use for multiple URL workflow fields
cpsl.ui.CheckboxGroup(*, name, label="", options=None, default=None)  # use for multi-select workflow fields
cpsl.ui.SubmitButton(label, *, action="start", primary=False)  # use to trigger start or a named workflow action
cpsl.ui.ActionBar(*, children=None)  # use to lay out workflow submit buttons
cpsl.ui.RunStatus()  # use to show current workflow run status
cpsl.ui.RunList(*, empty_message="No runs yet")  # use to list workflow runs
cpsl.ui.EmptyState(message="", *, icon="")  # use for empty workflow/page states

# Resources and client
cpsl.Image(*, python_packages=None, apt_packages=None, commands=None)  # use to define runtime dependencies/setup
image.add_python_packages(packages)  # use to add pip packages or requirements.txt
image.add_apt_packages(packages)  # use to add apt packages
image.add_commands(commands)  # use to run setup shell commands
cpsl.Channel(name)  # use to attach named Telegram/Slack/WhatsApp resources
cpsl.FileSystem(name)  # use to mount durable named storage
fs.smart_source(integration, name, *, guidance="", output_format="folder", file_ext="", filename_format="", cache_ttl=0)  # use for inferred Airstore source views
fs.source_query(integration, name, *, filter, output_format="folder", file_ext="", filename_format="", cache_ttl=0)  # use for explicit Airstore source filters
fs.mcp(name, *, command=None, args=None, url=None, env=None, transport=None)  # use to expose an MCP server under /tools
fs.tool(name, **config)  # use to expose a configured workspace tool
cpsl.Secret.from_name(name)  # use to reference a platform secret
secret.value  # use to resolve a secret at runtime
cpsl.Client(token=None, gateway_url=None)  # use for programmatic workspace/app calls
client.list_apps()  # use to enumerate workspace apps
client.get_app(name_or_id)  # use to inspect a deployed app
client.chat(app, text, session_id=None)  # use for synchronous smoke tests
client.stream(app, text, session_id=None)  # use for streaming smoke tests
client.create_checkout(app, return_url="")  # use to create paid-app checkout links
client.list_payments(app)  # use to inspect app payments
client.get_earnings(app)  # use to inspect app earnings
```

## Class-Based Apps

Use class-based style only when instance state on `self` helps. Do not mix it with functional handlers.

```python
import cpsl

app = cpsl.App(name="classy")


@app.cls(
    image=cpsl.Image(python_packages=["baml-py==0.220.0", "pydantic>=2.13.2"]),
    secrets=["ANTHROPIC_API_KEY"],
)
class ClassyApp:
    @cpsl.boot()
    def setup(self):
        self.system_prompt = "You are a concise Capsule assistant."

    @cpsl.message()
    async def handle(self, session: cpsl.Session, msg: cpsl.Message):
        from baml_client import b

        await session.stream_reply_from(
            b.stream.AnswerQuestion(
                question=(msg.text or "").strip(),
                context="",
                system_prompt=self.system_prompt,
            )
        )
```

Functional decorators map directly to class decorators: `@app.message()` becomes `@cpsl.message()`, `@app.task(...)` becomes `@cpsl.task(...)`, and the same pattern applies to `boot`, `shutdown`, `enter`, `exit`, `schedule`, `endpoint`, and `asgi`.

Invalid combinations:

- `cpsl.App(..., image=...)` plus `@app.cls(...)`.
- Functional `@app.message()` / `@app.task()` plus class methods decorated with `@cpsl.message()` / `@cpsl.task()`.

## Smoke Tests And Inspection

Use the CLI for resource inspection: `capsule app list`, `capsule app get <app-id>`, `capsule secret list`, `capsule fs list`, and `capsule channel list`.

Use `cpsl.Client` for quick deployed-app smoke tests:

```python
import cpsl

client = cpsl.Client()
reply = client.chat("support-ops", "ping")
print(reply.text)

for chunk in client.stream("support-ops", "write a summary"):
    print(chunk.text, end="")
```

## Gotchas Checklist

- Keep new app code on the public `cpsl` surface: `App`, `Image`, `Session`, `Message`, `Client`, `FileSystem`, `Secret`, `Workflow`, `ui`, decorators, and collection/settings APIs.
- Pick functional or class-based style once per app.
- Functional apps require `image=` on `cpsl.App(...)`.
- Add Python runtime packages to `cpsl.Image(python_packages=[...])`; local-only installs do not deploy.
- Declare deployed credentials as Capsule secrets and include their names on `App(..., secrets=[...])`.
- Use `cpsl.Secret.from_name(...)` when passing secret references to integrations or other config.
- Use named `cpsl.Channel("name")` resources for Telegram, Slack, and WhatsApp.
- Use `session.db.<collection>` for user, owner, and session scoped collections inside live sessions.
- Do not use a collection before the app/runtime has bound it during serve or deploy.
- Do not mix plain update fields with `$set`, `$inc`, or other operators in one `update_one` document.
- Use `RequestContext` in `@app.data()` and `@app.endpoint()` when no `Session` is available.
- Use `current_session()` inside task-style code only when you need the active session and no `session` argument is available.
- If local behavior differs from deployed behavior, check SDK/runtime versions and `Image(...)` dependencies first.
