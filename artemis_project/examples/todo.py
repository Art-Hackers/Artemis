"""
A small todo list. Shows:
  - Input() bound to a State so typing doesn't trigger a rerender
  - building a dynamic list of Cards from a Python list
  - Checkbox flipping an item's "done" flag

    python examples/todo.py
"""

import artemis as art

app = art.App("Hacker Bro", theme="forest", window_size=(380, 640))

new_task = art.State("")
tasks = art.State([])  # list of {"text": str, "done": bool}


def add_task(e):
    text = new_task.value.strip()
    if not text:
        return
    tasks.value = tasks.value + [{"text": text, "done": False}]
    new_task.value = ""


def toggle_task(index):
    def handler(e):
        items = tasks.value.copy()
        items[index]["done"] = e.control.value
        tasks.value = items
    return handler


@app.page("/")
def home(page):
    task_cards = [
        art.Card(
            art.Row([
                art.Checkbox(value=t["done"], on_change=toggle_task(i)),
                art.Text(t["text"], muted=t["done"]),
            ]),
        )
        for i, t in enumerate(tasks.value)
    ]

    if not task_cards:
        task_cards = [art.Text("Nothing here yet - add something below.", muted=True)]

    return art.Column(
        [
            art.Title("Tasks"),
            art.Row([
                art.Input(label="New task", bind=new_task, width=220),
                art.Button("Add", on_click=add_task),
            ]),
            art.Divider(),
            art.Column(task_cards, gap=8, scroll=True, expand=True),
        ],
        gap=16,
        expand=True,
    )


if __name__ == "__main__":
    app.run()
