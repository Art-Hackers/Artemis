"""
The classic - a counter. Run it with:

    python examples/counter.py

This one shows off State, the auto-rerender on Button clicks, and how
little code it takes to get something that actually looks decent.
"""

import artemis as art

app = art.App("Counter", theme="grape", window_size=(360, 500))

count = art.State(0)


@app.page("/")
def home(page):
    return art.Column(
        [
            art.Text("Artemis", muted=True, size=14),
            art.Title(str(count.value), size=64),
            art.Row(
                [
                    art.Button("−", variant="outline", on_click=lambda e: count.set(count.value - 1)),
                    art.Button("Reset", variant="text", on_click=lambda e: count.set(0)),
                    art.Button("+", on_click=lambda e: count.set(count.value + 1)),
                ],
                center=True,
            ),
        ],
        center=True,
        expand=True,
    )


if __name__ == "__main__":
    app.run()
