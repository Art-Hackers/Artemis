"""
Shows off the theming system: a big list of named palettes, plus full
manual control over background/surface/text/primary colors for anyone
who wants an exact custom look rather than a named vibe.

    python examples/theming.py
"""

import artemis as art

# every one of these is valid: theme="teal", theme="#0EA5E9", or the
# fully custom override style used below
app = art.App(
    "Theming",
    theme="indigo",        # seed color - drives buttons, switches, etc.
    background="#0B1220",  # fixed dark background, same in light or dark mode
    surface="#161F32",     # color of cards/boxes sitting on that background
    text="#E5E7EB",        # foreground text color on that surface
    window_size=(380, 640),
)


def pick(name):
    return lambda e: app.set_theme(name, background=None, surface=None, text=None)


@app.page("/")
def home(page):
    return art.Column(
        [
            art.Title("Custom theme", color="#E5E7EB"),
            art.Text("background / surface / text / primary are all explicit here.", muted=True),
            art.Card(art.Text("A card, using the surface + text colors above.")),
            art.Button("Primary button"),
            art.Divider(),
            art.Text("Or switch to a named palette instead:", muted=True),
            art.Row(
                [
                    art.Button("Ocean", variant="outline", on_click=pick("ocean")),
                    art.Button("Grape", variant="outline", on_click=pick("grape")),
                    art.Button("Forest", variant="outline", on_click=pick("forest")),
                ],
                wrap=True,
            ),
        ],
        gap=14,
    )


if __name__ == "__main__":
    app.run()
