"""
A real test suite for two of the example apps, using artemis.testing -
run it with:

    pip install pytest
    pytest tests/

This isn't a toy - these are the same kinds of checks you'd write for
your own app. No window opens; everything runs against a fake page.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "examples"))

from artemis.testing import TestApp

import counter
import todo


def test_counter_starts_at_zero():
    t = TestApp(counter.app).build()
    assert t.has_text("0")


def test_counter_increments():
    counter.count.value = 0  # reset shared state between tests
    t = TestApp(counter.app).build()
    t.click(t.find_button("+"))
    assert t.has_text("1")


def test_counter_decrements():
    counter.count.value = 0
    t = TestApp(counter.app).build()
    t.click(t.find_button("\u2212"))  # the minus sign used in counter.py
    assert t.has_text("-1")


def test_counter_reset():
    counter.count.value = 5
    t = TestApp(counter.app).build()
    t.click(t.find_button("Reset"))
    assert t.has_text("0")


def test_todo_starts_empty():
    todo.tasks.value = []
    t = TestApp(todo.app).build()
    assert t.has_text("Nothing here yet - add something below.")


def test_todo_add_task():
    todo.tasks.value = []
    todo.new_task.value = ""
    t = TestApp(todo.app).build()

    task_input = next(c for c in t.all_controls() if getattr(c, "label", None) == "New task")
    t.type_into(task_input, "Buy milk")
    t.click(t.find_button("Add"))

    assert t.has_text("Buy milk")
    assert not t.has_text("Nothing here yet - add something below.")


def test_async_data_loads_once_and_undo_toast_works():
    import async_data_demo as ad

    ad.package_info.reset()
    ad.removed_items.clear()

    t = TestApp(ad.app).build()
    assert t.has_text("Widgets")

    remove_btn = next(
        c for c in t.all_controls()
        if hasattr(c, "on_click") and getattr(c, "icon", None) == ad.art.flet.Icons.CLOSE
    )
    t.click(remove_btn)

    assert not t.has_text("Widgets")
    dialog = t.last_dialog()
    assert dialog.action == "Undo"

    dialog.on_action(None)
    assert "Widgets" not in ad.removed_items
