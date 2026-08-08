"""
Shows:
  - art.fetch_json() - a real network call from an async on_click
  - art.Button(loading=...) - an automatic spinner while that call runs
  - route guards - app.page(guard=..., redirect=...)

    python examples/network_and_guards.py
"""

import artemis as art

app = art.App("Network Demo", theme="cobalt", window_size=(380, 640))

logged_in = art.State(False)
loading = art.State(False)
package_info = art.State(None)


async def load_package_info(e):
    data = await art.fetch_json("https://pypi.org/pypi/flet/json")
    package_info.value = {
        "name": data["info"]["name"],
        "version": data["info"]["version"],
        "summary": data["info"]["summary"],
    }


@app.page("/")
def home(page):
    info = package_info.value
    result_view = (
        art.Card(art.Column([
            art.Text(f"{info['name']} v{info['version']}", bold=True),
            art.Text(info["summary"], muted=True),
        ]))
        if info else
        art.Text("Nothing loaded yet.", muted=True)
    )

    return art.Column(
        [
            art.Title("Fetch demo"),
            art.Button("Load package info", on_click=load_package_info, loading=loading),
            result_view,
            art.Divider(),
            art.Title("Route guard demo"),
            art.Switch(label="Logged in", value=logged_in.value, on_change=lambda e: logged_in.set(e.control.value)),
            art.Button("Go to admin screen", variant="outline", on_click=lambda e: app.go("/admin")),
        ],
        gap=14,
    )


@app.page("/admin", title="Admin", guard=lambda: logged_in.value, redirect="/login")
def admin(page):
    return art.Column([
        art.Title("Admin"),
        art.Text("You only see this because logged_in is True."),
        art.Button("Back", variant="text", on_click=lambda e: app.back()),
    ])


@app.page("/login", title="Login")
def login(page):
    return art.Column([
        art.Title("Redirected here"),
        art.Text("The admin screen's guard sent you here because you weren't logged in."),
        art.Button("Back", variant="text", on_click=lambda e: app.back()),
    ])


if __name__ == "__main__":
    app.run()
