"""
Shows:
  - a side navigation drawer (app.set_drawer)
  - async event handlers - on_click just works with an `async def`
    function, no extra wiring (clipboard uses this under the hood)
  - app.copy() / app.paste()
  - a Grid layout
  - a custom page transition style

    python examples/drawer_and_clipboard.py
"""

import artemis as art

app = art.App("Drawer Demo", theme="teal", transitions="cupertino", window_size=(400, 700))

clipboard_text = art.State("")


def handle_paste(text):
    clipboard_text.value = text or ""
    app.toast("Pasted from clipboard")


@app.page("/", title="Home")
def home(page):
    return art.Column(
        [
            art.Title("Clipboard"),
            art.Row([
                art.Button("Copy a link", variant="outline", on_click=lambda e: app.copy("https://example.com/shared")),
                art.Button("Paste", variant="outline", on_click=app.paste(handle_paste)),
            ]),
            art.Text(clipboard_text.value or "Nothing pasted yet.", muted=True),
            art.Divider(),
            art.Text("Open the drawer (top-left icon) to switch screens.", muted=True),
        ],
        gap=12,
    )


@app.page("/gallery", title="Gallery")
def gallery(page):
    tiles = [art.Card(art.Text(f"Item {i}", center=True)) for i in range(9)]
    return art.Column([art.Title("Gallery"), art.Grid(tiles, columns=3, expand=True)], gap=12, expand=True)


app.set_drawer([
    {"label": "Home", "icon": art.flet.Icons.HOME, "route": "/"},
    {"label": "Gallery", "icon": art.flet.Icons.GRID_VIEW, "route": "/gallery"},
])


if __name__ == "__main__":
    app.run()
