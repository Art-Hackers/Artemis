import sys
from pathlib import Path

import flet as ft

from . import widgets
from .branding import ensure_branding
from .theme import build_theme


class App:
    """
    Your whole app is one of these.

        app = App("Counter", theme="ocean")

        @app.page("/")
        def home(page):
            return art.Text("hi")

        app.run()

    Register as many @app.page("/route") functions as you need - each one
    just returns the control tree for that screen.

    Navigation is a real back-stack under the hood (Flet's `page.views`,
    not just swapping out `page.controls`), which is the part most small
    Flet wrappers skip. That means:

      - app.go("/details") pushes a new screen with a back arrow that
        just works, no wiring required.
      - Android's hardware back button and the browser back button both
        pop the stack correctly instead of doing nothing or closing the app.
      - app.bottom_nav([...]) gives you a persistent tab bar across your
        root screens, the way an actual mobile app behaves, not a website
        with buttons.
    """

    def __init__(self, title="Artemis App", theme="indigo", font=None,
                 window_size=None, padding=24, dark_mode=None, logo="logo.png"):
        self.title = title
        self.theme_name = theme
        self.font = font
        self.window_size = window_size
        self.padding = padding
        self.dark_mode = dark_mode  # None = follow the system, True/False forces it
        self.logo = logo  # filename inside your assets/ folder - drop your own in to override

        self._routes = {}        # route -> {"handler", "title", "appbar"}
        self._tabs = None        # set via bottom_nav()
        self._nav_stack = ["/"]  # our own back-stack, independent of page.route
        self._page = None
        self._icon_path = None

    # ------------------------------------------------------------ setup ---

    def page(self, route="/", title=None, appbar=True):
        """Register a screen. `title` shows in that screen's AppBar (falls
        back to the app title); pass appbar=False for a bare, chrome-less
        screen (splash screens, full-bleed images, that sort of thing)."""
        def register(fn):
            self._routes[route] = {"handler": fn, "title": title, "appbar": appbar}
            return fn
        return register

    def bottom_nav(self, tabs):
        """
        A persistent bottom tab bar for your top-level screens.

            app.bottom_nav([
                {"label": "Home", "icon": ft.Icons.HOME, "route": "/"},
                {"label": "Search", "icon": ft.Icons.SEARCH, "route": "/search"},
                {"label": "You", "icon": ft.Icons.PERSON, "route": "/profile"},
            ])

        Tapping a tab swaps the root screen (it's a tab switch, not a push -
        there's nothing to "go back" to). It only appears on root-level
        screens; if you app.go() deeper into something, the tab bar hides
        the way it would in a real app, and comes back once you app.back().
        """
        self._tabs = tabs
        if self._page is not None:
            self._render_views()

    # --------------------------------------------------------- navigate ---

    def go(self, route):
        """Push a new screen onto the stack. Shows a back arrow automatically."""
        self._nav_stack.append(route)
        self._render_views()

    def back(self):
        """Pop the current screen and return to whatever was under it."""
        if len(self._nav_stack) > 1:
            self._nav_stack.pop()
            self._render_views()

    def toast(self, message, bg=None, seconds=3):
        """Shortcut for widgets.toast() - `app.toast("Saved!")`."""
        widgets.toast(message, bg=bg, seconds=seconds)

    def alert(self, title, message, on_close=None):
        """A one-line "OK" dialog - `app.alert("Heads up", "Something happened.")`."""
        def close(e):
            dialog.open = False
            self._page.update()
            if on_close:
                on_close(e)

        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close)],
        )
        self._page.show_dialog(dialog)

    def confirm(self, title, message, on_confirm, on_cancel=None, confirm_text="Yes", cancel_text="Cancel"):
        """
        A yes/no dialog - fires `on_confirm` (or `on_cancel`) depending on
        which button gets tapped, then closes itself either way:

            app.confirm("Delete task?", "This can't be undone.",
                         on_confirm=lambda e: delete_task())
        """
        def respond(callback):
            def handler(e):
                dialog.open = False
                self._page.update()
                if callback:
                    callback(e)
            return handler

        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(cancel_text, on_click=respond(on_cancel)),
                ft.FilledButton(confirm_text, on_click=respond(on_confirm)),
            ],
        )
        self._page.show_dialog(dialog)

    def refresh(self):
        """Manually force a redraw. Buttons/switches/sliders already do this
        for you after their handler runs - this is for the rarer case
        (a background thread finished, a timer fired) where nothing on
        screen technically "clicked" but the state changed anyway."""
        self._render_views()

    # -------------------------------------------------------- internals ---

    def _build_nav_bar(self):
        destinations = [
            ft.NavigationBarDestination(icon=t["icon"], label=t["label"])
            for t in self._tabs
        ]
        current_root = self._nav_stack[0]
        selected = next((i for i, t in enumerate(self._tabs) if t["route"] == current_root), 0)

        def handle_change(e):
            index = e.control.selected_index
            self._nav_stack = [self._tabs[index]["route"]]
            self._render_views()

        return ft.NavigationBar(destinations=destinations, selected_index=selected, on_change=handle_change)

    def _build_view(self, route, is_root):
        entry = self._routes.get(route) or self._routes.get("/")
        if entry is None:
            return ft.View(route=route, controls=[ft.Text(f"No page registered for '{route}'")])

        content = entry["handler"](self._page)
        controls = list(content) if isinstance(content, (list, tuple)) else [content]

        appbar = None
        if entry["appbar"]:
            appbar = ft.AppBar(title=ft.Text(entry["title"] or self.title))

        nav_bar = self._build_nav_bar() if (is_root and self._tabs) else None

        return ft.View(
            route=route,
            controls=controls,
            appbar=appbar,
            navigation_bar=nav_bar,
            padding=self.padding,
        )

    def _render_views(self):
        page = self._page
        page.views.clear()
        for i, route in enumerate(self._nav_stack):
            page.views.append(self._build_view(route, is_root=(i == 0)))
        page.update()

    def _handle_view_pop(self, e):
        # fires when the user taps the AppBar back arrow or hits Android's
        # hardware back button - keep our own stack in sync with Flutter's
        if len(self._nav_stack) > 1:
            self._nav_stack.pop()
            self._render_views()

    def _build(self, page: ft.Page):
        self._page = page
        page.title = self.title

        light, dark = build_theme(self.theme_name, self.font)
        page.theme = light
        page.dark_theme = dark
        if self.dark_mode is True:
            page.theme_mode = ft.ThemeMode.DARK
        elif self.dark_mode is False:
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM

        if self.window_size:
            page.window.width, page.window.height = self.window_size
        if self._icon_path:
            # only reliably takes effect on Windows dev-preview - see branding.py
            page.window.icon = self._icon_path

        # let widgets.py trigger redraws / toasts from inside handlers
        widgets._rerender = self._render_views
        widgets._page = page

        self._nav_stack = [page.route or "/"]
        page.on_view_pop = self._handle_view_pop
        self._render_views()

    def run(self, **kwargs):
        """Starts the app. Any kwargs get passed straight through to flet.run -
        e.g. view=ft.AppView.WEB_BROWSER, port=8550, etc - so nothing Flet
        can do becomes off-limits just because you're using Artemis."""
        assets_dir_name = kwargs.get("assets_dir") or "assets"
        script_dir = Path(sys.argv[0]).resolve().parent if sys.argv and sys.argv[0] else Path.cwd()
        self._icon_path = ensure_branding(script_dir / assets_dir_name, self.logo)

        ft.run(self._build, **kwargs)
