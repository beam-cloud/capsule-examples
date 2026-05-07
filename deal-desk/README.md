# Deal Desk

A custom React Capsule app that demonstrates:

- `@app.message("deal-desk")` named chat handlers
- `useChat("deal-desk", { threadKey })` from a custom React page
- Owner-scoped stable threads per project
- A three-pane operator layout inspired by deal review tools
- Collection-backed field inspection

## Run

```bash
uv sync
capsule serve app.py:app
```

## Deploy

```bash
capsule deploy app.py:app
```

## Try It

Open the `Deal Desk` page, select a project, and send:

```text
Ask about the lease.
What is the equipment age?
Draft a follow-up to the broker.
```

Each project uses its own stable chat thread:

```tsx
const chat = useChat("deal-desk", {
  threadKey: `project:${deal.id}`,
  initialData: { project_id: deal.id },
})
```
