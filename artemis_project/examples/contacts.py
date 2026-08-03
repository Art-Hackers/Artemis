"""
Shows the newer additions:
  - ListTile + Avatar for contact/settings-style rows
  - Loader / ProgressBar for loading states
  - app.alert(...) / app.confirm(...) dialogs

    python examples/contacts.py
"""

import artemis as art

app = art.App("Contacts", theme="ocean", window_size=(380, 640))

people = ["Alice Kim", "Diego Torres", "Priya Nair", "Sam O'Brien"]


def confirm_delete(name):
    def handler(e):
        app.confirm(
            f"Remove {name}?",
            "You can always add them back later.",
            on_confirm=lambda e: app.toast(f"{name} removed"),
        )
    return handler


@app.page("/", title="Contacts")
def home(page):
    rows = [
        art.ListTile(
            title=name,
            subtitle="Tap the icon to remove",
            leading=art.Avatar(text=name[0]),
            trailing=art.flet.IconButton(art.flet.Icons.DELETE_OUTLINE, on_click=confirm_delete(name)),
        )
        for name in people
    ]

    return art.Column(
        [
            art.Title("Contacts"),
            art.Column(rows, gap=4, scroll=True, expand=True),
            art.Divider(),
            art.Row([art.Loader(size=20), art.Text("Syncing...", muted=True)]),
            art.ProgressBar(value=0.65),
            art.Button("What does this button do?", variant="text",
                       on_click=lambda e: app.alert("Nothing yet", "This is just here to show app.alert().")),
        ],
        gap=12,
    )


if __name__ == "__main__":
    app.run()
