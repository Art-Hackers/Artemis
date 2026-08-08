"""
Shows the newest additions:
  - in-page Tabs (not navigation - just switching panels on one screen)
  - Expandable (collapsible FAQ-style sections)
  - Badge (the little count/dot on an icon)
  - app.pick_date() / app.pick_time()
  - app.on_key() - a global keyboard shortcut (try Ctrl+S)

    python examples/tabs_and_shortcuts.py
"""

import artemis as art

app = art.App("Tabs & Shortcuts", theme="violet", window_size=(400, 640))

appointment_date = art.State(None)
appointment_time = art.State(None)


def handle_date(d):
    appointment_date.value = d
    app.toast(f"Date set: {d}")


def handle_time(t):
    appointment_time.value = t
    app.toast(f"Time set: {t}")


def handle_save(e):
    app.toast("Saved! (Ctrl+S)")


app.on_key("ctrl+s", handle_save)


@app.page("/")
def home(page):
    overview_tab = art.Column(
        [
            art.Row([
                art.Text("Notifications", size=16),
                art.flet.Icon(art.flet.Icons.NOTIFICATIONS, badge=art.Badge("3", color="rose")),
            ]),
            art.Text("Press Ctrl+S anywhere in this window to trigger the global shortcut.", muted=True),
            art.Expandable(
                "What is this tab for?",
                art.Text("Just a plain content panel - Tabs only switches what's visible, it isn't routing."),
            ),
            art.Expandable(
                "Can I nest more sections?",
                art.Text("Yes - stack as many Expandable() panels as you like."),
            ),
        ],
        gap=12,
    )

    schedule_tab = art.Column(
        [
            art.Button("Pick a date", on_click=app.pick_date(handle_date)),
            art.Text(f"Date: {appointment_date.value or 'not set'}", muted=True),
            art.Button("Pick a time", on_click=app.pick_time(handle_time)),
            art.Text(f"Time: {appointment_time.value or 'not set'}", muted=True),
        ],
        gap=12,
    )

    return art.Column(
        [
            art.Title("Tabs & Shortcuts"),
            art.Tabs([
                ("Overview", overview_tab),
                ("Schedule", schedule_tab),
            ], expand=True),
        ],
        expand=True,
    )


if __name__ == "__main__":
    app.run()
