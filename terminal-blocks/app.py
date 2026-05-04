import cpsl


app = cpsl.App(
    name="{{ project_slug }}",
    image=cpsl.Image(),
)


@app.message()
async def handle(session: cpsl.Session, msg: cpsl.Message):
    """Run a tiny diagnostics transcript in chat."""
    requested = (msg.text or "diagnostics").strip()
    term = await session.show_terminal(title="Diagnostics")

    await term.shell("python --version && pwd")
    details = await term.exec(
        "python",
        "-c",
        (
            "import os, sys; "
            "print('structured exec works'); "
            "print(f'python={sys.executable}'); "
            "print(f'cwd={os.getcwd()}')"
        ),
    )

    first_line = (details.stdout.strip().splitlines() or ["diagnostics complete"])[0]
    await session.reply(f"Done running diagnostics for: {requested}\n\n{first_line}")
