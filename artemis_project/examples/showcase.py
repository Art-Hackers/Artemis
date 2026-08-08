"""
Shows off the stuff that's actually different about Artemis vs raw Flet:
  - a real back-stack (app.go / app.back) with an automatic back arrow
  - a persistent bottom tab bar (app.bottom_nav)
  - glass and gradient panels (art.Box(glass=True) / gradient=[...])
  - one-line toasts (app.toast)

    python examples/showcase.py
"""

import artemis as art

app = art.App("Showcase", theme="grape", window_size=(390, 700))


@app.page("/", title="Home")
def home(page):
    return art.Column(
        [
            art.Box(
                art.Column([
                    art.Text("Frosted glass panel", color="white", bold=True),
                    art.Text("blurred backdrop, no manual Blur/BoxShadow wiring", color="white", size=12),
                ]),
                glass=True,
                pad=20,
            ),
            art.Box(
                art.Text("Gradient panel", color="white", bold=True),
                gradient=["#F59E0B", "#EF4444"],
                pad=20,
            ),
            art.Button("Say hi", on_click=lambda e: app.toast("Hi from Artemis!")),
            art.Button("Open details", variant="outline", on_click=lambda e: app.go("/details")),
        ],
        gap=16,
    )


@app.page("/search", title="Search")
def search(page):
    return art.Column([art.Title("Search"), art.Text("Second tab - notice the bottom bar stays put.")])


@app.page("/details", title="Details", appbar=True)
def details(page):
    return art.Column([
        art.Title("Details"),
        art.Text("Pushed with app.go() - the back arrow above is automatic."),
        art.Button("Back", variant="text", on_click=lambda e: app.back()),
    ])


app.bottom_nav([
    {"label": "Home", "icon": art.flet.Icons.HOME, "route": "/"},
    {"label": "Search", "icon": art.flet.Icons.SEARCH, "route": "/search"},
])


if __name__ == "__main__":
    app.run()
