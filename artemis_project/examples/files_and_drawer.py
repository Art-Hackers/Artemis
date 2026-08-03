"""
Shows the newest additions:
  - a side navigation drawer (app.set_drawer)
  - async event handlers (file picker, clipboard) - on_click just works
    with an `async def` function, no extra wiring
  - app.pick_files() / app.copy() / app.paste()
  - a Grid layout
  - a custom page transition style

    python examples/files_and_drawer.py
"""

import artemis as art

app = art.App("Files", theme="teal", transitions="cupertino", window_size=(400, 700))

picked_files = art.State([])
clipboard_text = art.State("")


def handle_files(files):
    picked_files.value = [f.name for f in files]
    if files:
        app.toast(f"Picked {len(files)} file(s)")


def handle_paste(text):
    clipboard_text.value = text or ""
    app.toast("Pasted from clipboard")


@app.page("/", title="Files")
def home(page):
    file_rows = [art.ListTile(title=name, leading=art.flet.Icon(art.flet.Icons.INSERT_DRIVE_FILE))
                 for name in picked_files.value] or [art.Text("No files picked yet.", muted=True)]

    return art.Column(
        [
            art.Title("Pick some files"),
            art.Button("Choose files", on_click=app.pick_files(handle_files, allow_multiple=True)),
            art.Column(file_rows, gap=4),
            art.Divider(),
            art.Title("Clipboard"),
            art.Row([
                art.Button("Copy a link", variant="outline", on_click=lambda e: app.copy("https://example.com/shared")),
                art.Button("Paste", variant="outline", on_click=app.paste(handle_paste)),
            ]),
            art.Text(clipboard_text.value or "Nothing pasted yet.", muted=True),
        ],
        gap=12,
    )


@app.page("/gallery", title="Gallery")
def gallery(page):
    tiles = [art.Card(art.Text(f"Item {i}", center=True)) for i in range(9)]
    return art.Column([art.Title("Gallery"), art.Grid(tiles, columns=3, expand=True)], gap=12, expand=True)


app.set_drawer([
    {"label": "Files", "icon": art.flet.Icons.FOLDER, "route": "/"},
    {"label": "Gallery", "icon": art.flet.Icons.GRID_VIEW, "route": "/gallery"},
])


if __name__ == "__main__":
    app.run()
