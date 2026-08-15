"""
A way to actually test an Artemis app without launching a real window -
useful in CI, and honestly just useful while you're building the thing,
so you're not clicking through the UI by hand after every change.

    from artemis.testing import TestApp

    def test_counter():
        t = TestApp(app)
        t.build()
        assert t.has_text("0")

        t.click(t.find_button("+"))
        assert t.has_text("1")

This works by giving your App a fake Page object that implements just
enough of the real thing (views, overlay, update(), show_dialog(),
clipboard) for your page functions and event handlers to run for real,
then giving you a few ways to inspect and interact with the resulting
control tree. It doesn't spin up Flet's actual client at all - this is
about testing *your app's logic*, not Flet's rendering.
"""

import asyncio
import inspect


class FakeEvent:
    """Stand-in for Flet's event objects - has a `.control` (and optional
    extra attributes for keyboard/other events) the way a real one does."""

    def __init__(self, control=None, **extra):
        self.control = control
        for key, value in extra.items():
            setattr(self, key, value)


class _FakeWindow:
    width = height = None
    icon = None


class _FakeClipboard:
    def __init__(self):
        self._value = None

    async def set(self, value):
        self._value = value

    async def get(self):
        return self._value


class FakePage:
    """A minimal stand-in for flet.Page - enough surface for an Artemis
    App to build views, show dialogs, and handle events against."""

    def __init__(self, route="/", width=375, web=False, url=None):
        self.route = route
        self.width = width
        self.height = 700
        self.title = None
        self.theme = None
        self.dark_theme = None
        self.theme_mode = None
        self.views = []
        self.overlay = []
        self.window = _FakeWindow()
        self.clipboard = _FakeClipboard()
        self.dialogs_shown = []
        self.on_view_pop = None
        self.on_resize = None
        self.on_keyboard_event = None
        self.web = web
        self.url = url

    def update(self, *controls):
        pass

    def show_dialog(self, dialog):
        dialog.open = True
        self.dialogs_shown.append(dialog)

    def run_task(self, fn, *args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))


def _children(control):
    kids = []
    controls = getattr(control, "controls", None)
    if controls:
        kids.extend(controls)
    content = getattr(control, "content", None)
    if content is not None and not isinstance(content, str):
        kids.append(content)
    for attr in ("title", "subtitle", "leading", "trailing"):
        value = getattr(control, attr, None)
        if value is not None and not isinstance(value, str):
            kids.append(value)
    return kids


def _walk(control):
    yield control
    for child in _children(control):
        yield from _walk(child)


class TestApp:
    """Wraps an `artemis.App` with a FakePage and a handful of helpers for
    driving it in a test."""

    __test__ = False  # tells pytest this is a helper class, not a test class to collect

    def __init__(self, app):
        self.app = app
        self.page = FakePage()

    def build(self, route="/"):
        """Starts the app against the fake page - call this first."""
        self.page.route = route
        self.app._build(self.page)
        return self

    def go(self, route):
        self.app.go(route)
        return self

    def back(self):
        self.app.back()
        return self

    def current_route(self):
        return self.page.views[-1].route if self.page.views else None

    def all_controls(self):
        """Every control currently on screen (all views, flattened)."""
        for view in self.page.views:
            for control in view.controls:
                yield from _walk(control)

    def find_text(self, text):
        """Returns the first control whose displayed value equals `text`,
        or None."""
        for control in self.all_controls():
            if getattr(control, "value", None) == text:
                return control
        return None

    def has_text(self, text):
        return self.find_text(text) is not None

    def find_button(self, label):
        """Finds a Button by its label text (works for Artemis's
        Button() - the label is the button's `content`)."""
        for control in self.all_controls():
            if getattr(control, "content", None) == label and hasattr(control, "on_click"):
                return control
        return None

    def click(self, control):
        """Fires a control's on_click, awaiting it if it's async."""
        if control is None:
            raise ValueError("click() got None - did find_button()/find_text() not find anything?")
        handler = getattr(control, "on_click", None)
        if handler is None:
            raise ValueError(f"{control!r} has no on_click handler")
        result = handler(FakeEvent(control=control))
        if inspect.iscoroutine(result):
            asyncio.run(result)

    def type_into(self, control, text):
        """Simulates typing into an Input - sets the value and fires
        on_change, the way a real text field would."""
        control.value = text
        handler = getattr(control, "on_change", None)
        if handler is not None:
            result = handler(FakeEvent(control=control))
            if inspect.iscoroutine(result):
                asyncio.run(result)

    def last_dialog(self):
        """The most recently shown dialog (SnackBar, AlertDialog, etc),
        or None - useful for asserting on toasts/alerts/confirms."""
        return self.page.dialogs_shown[-1] if self.page.dialogs_shown else None
