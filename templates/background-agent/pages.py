import cpsl


def runs_page(runs):
    return cpsl.ui.Page([
        cpsl.ui.Text("Background Agent", style="heading"),
        cpsl.ui.Text("Scheduled and on-demand runs appear here.", style="muted"),
        cpsl.ui.Table(collection=runs, columns=["topic", "priority", "summary", "created_at"], sortable=True),
    ])
