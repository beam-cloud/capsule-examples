import cpsl


def launcher_ui():
    return cpsl.ui.WorkflowShell(
        "Browser Task",
        children=[
            cpsl.ui.FormSection(
                "Task",
                children=[
                    cpsl.ui.UrlInput(name="url", label="Target URL", placeholder="https://example.com"),
                    cpsl.ui.TextArea(name="goal", label="Goal", placeholder="Summarize what is on this page."),
                ],
            ),
            cpsl.ui.ActionBar(children=[cpsl.ui.SubmitButton("Start browser task", primary=True)]),
        ],
    )
