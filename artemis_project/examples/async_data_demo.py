"""
Shows:
  - AsyncData - loads once per screen visit, not on every re-render
  - toast() with an action button (Undo)

    python examples/async_data_demo.py
"""

import artemis as art

app = art.App("Async Data", theme="emerald", window_size=(380, 640))

package_info = art.AsyncData(lambda: art.fetch_json("https://pypi.org/pypi/flet/json"))
removed_items = []


def remove_item(name):
    def handler(e):
        removed_items.append(name)
        app.toast(f"Removed {name}", action="Undo", on_action=undo_remove(name))
        app.refresh()
    return handler


def undo_remove(name):
    def handler(e):
        if name in removed_items:
            removed_items.remove(name)
        app.toast(f"Restored {name}")
    return handler


@app.page("/")
def home(page):
    package_info.render(page)

    if package_info.loading:
        body = art.Row([art.Loader(size=20), art.Text("Loading package info...")])
    elif package_info.error:
        body = art.Text(f"Couldn't load that: {package_info.error}", color="red")
    else:
        info = package_info.value["info"]
        body = art.Card(art.Column([
            art.Text(f"{info['name']} v{info['version']}", bold=True),
            art.Text(info["summary"], muted=True),
        ]))

    items = ["Widgets", "Gadgets", "Doohickeys"]
    rows = [
        art.ListTile(title=name, trailing=art.flet.IconButton(art.flet.Icons.CLOSE, on_click=remove_item(name)))
        for name in items if name not in removed_items
    ] or [art.Text("All items removed.", muted=True)]

    return art.Column(
        [
            art.Title("Loaded once, not on every click"),
            body,
            art.Button("Force refresh", variant="outline", on_click=lambda e: (package_info.reset(), app.refresh())),
            art.Divider(),
            art.Title("Undo toast"),
            art.Column(rows, gap=4),
        ],
        gap=14,
    )


if __name__ == "__main__":
    app.run()
