import asyncio
import inspect
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import flet as ft

from . import widgets
from .branding import ensure_branding, ensure_splash_asset
from .theme import build_theme

_UNSET = object()  # lets set_theme tell "didn't pass this" apart from "explicitly clear it"


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

    In web mode, when you're running locally (localhost/127.0.0.1) - the
    way you would while developing - Artemis briefly shows its own splash
    screen before your app's first screen, purely so it's obvious to you
    that you're looking at a live dev session and not something already
    published. It never shows once the same code is actually deployed
    somewhere real (Cloudflare Pages, any other real domain) - that
    distinction is detected automatically from the URL the browser
    connected on, not something you toggle by hand at publish time. See
    App(splash=...) below to force it on/off instead of relying on
    auto-detection.
    """

    def __init__(self, title="Artemis App", theme="indigo", font=None,
                 window_size=None, padding=24, dark_mode=None, logo="logo.png",
                 background=None, surface=None, text=None, primary=None, transitions=None,
                 splash="auto", splash_duration=1.1):
        self.title = title
        self.theme_name = theme
        self.font = font
        self.window_size = window_size
        self.padding = padding
        self.dark_mode = dark_mode  # None = follow the system, True/False forces it
        self.logo = logo  # filename inside your assets/ folder - drop your own in to override
        self.transitions = transitions  # None (platform default), or "fade"/"cupertino"/"zoom"/"none"
        self.splash = splash  # "auto" (dev-only, web+localhost), True (always), or False (never)
        self.splash_duration = splash_duration  # seconds the splash stays up before your app appears

        # fine-grained theme overrides - each one becomes a fixed color in
        # both light and dark mode; leave any as None to keep it seed-derived
        self.background = background  # the color behind everything
        self.surface = surface        # the color of cards/boxes on that background
        self.text = text              # the default foreground/text color
        self.primary = primary        # the accent color for buttons, switches, etc.

        self._routes = {}        # route -> {"handler", "title", "appbar"}
        self._tabs = None        # set via bottom_nav()
        self._drawer_items = None  # set via set_drawer()
        self._nav_stack = ["/"]  # our own back-stack, independent of page.route
        self._page = None
        self._icon_path = None
        self._splash_asset = None  # filename inside assets_dir, set during run()
        self._shortcuts = {}  # set via on_key()

    _TRANSITION_MAP = {
        "fade": ft.PageTransitionTheme.FADE_FORWARDS,
        "cupertino": ft.PageTransitionTheme.CUPERTINO,
        "zoom": ft.PageTransitionTheme.ZOOM,
        "none": ft.PageTransitionTheme.NONE,
    }

    def _build_theme_pair(self):
        light, dark = build_theme(
            self.theme_name, self.font,
            background=self.background, surface=self.surface,
            text=self.text, primary=self.primary,
        )
        if self.transitions:
            transition = self._TRANSITION_MAP.get(self.transitions)
            if transition is not None:
                platforms = ft.PageTransitionsTheme(
                    android=transition, ios=transition, linux=transition,
                    macos=transition, windows=transition,
                )
                light.page_transitions = platforms
                dark.page_transitions = platforms
        return light, dark

    # ------------------------------------------------------------ setup ---

    def page(self, route="/", title=None, appbar=True, guard=None, redirect="/"):
        """
        Register a screen. `title` shows in that screen's AppBar (falls
        back to the app title); pass appbar=False for a bare, chrome-less
        screen (splash screens, full-bleed images, that sort of thing).

        Routes can carry named params with a `:name` segment:

            @app.page("/user/:id")
            def profile(page, params):
                return art.Text(f"User #{params['id']}")

        `app.go("/user/42")` will match that route and hand your function
        `{"id": "42"}` as a second argument - Artemis only passes it in if
        your function actually accepts one, so plain `def home(page):`
        handlers keep working untouched.

        `guard`, if given, is a zero-arg function checked right before
        this screen renders - return False and Artemis shows `redirect`
        instead (default `"/"`):

            app.page("/admin", guard=lambda: current_user.is_admin, redirect="/login")

        Handy for "logged in only" screens without repeating the check in
        every single page function.
        """
        def register(fn):
            self._routes[route] = {
                "handler": fn, "title": title, "appbar": appbar, "regex": None,
                "guard": guard, "redirect": redirect,
            }
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

    def set_drawer(self, items):
        """
        A side navigation menu - shows a hamburger icon in the AppBar
        automatically (that's standard Flutter behavior once a screen has
        a drawer, not something Artemis wires up by hand).

            app.set_drawer([
                {"label": "Home", "icon": ft.Icons.HOME, "route": "/"},
                {"label": "Settings", "icon": ft.Icons.SETTINGS, "route": "/settings"},
            ])

        Like bottom_nav, this is for top-level navigation between your
        root screens - better suited to a wide desktop window than
        bottom_nav is, since a side menu doesn't eat vertical space the
        way a bottom bar does. Only shows on root-level screens.
        """
        self._drawer_items = items
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

    def toast(self, message, bg=None, seconds=3, action=None, on_action=None):
        """Shortcut for widgets.toast() - `app.toast("Saved!")`, or with an
        action button: `app.toast("Deleted", action="Undo", on_action=restore)`."""
        widgets.toast(message, bg=bg, seconds=seconds, action=action, on_action=on_action)

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

    def set_theme(self, theme_name=None, dark_mode=_UNSET, background=_UNSET, surface=_UNSET, text=_UNSET, primary=_UNSET):
        """Switch the palette, light/dark mode, and/or any color override
        while the app's running - `app.set_theme("forest")` for a
        settings-screen theme picker, `app.set_theme(dark_mode=True)` for
        a light/dark toggle, or `app.set_theme(primary="#FF0000")` to
        tweak just the accent color. Arguments you don't pass at all keep
        their current value; pass `None` explicitly to clear an override
        back to pure seed-derived color (e.g. `app.set_theme(surface=None)`)."""
        if theme_name is not None:
            self.theme_name = theme_name
        if dark_mode is not _UNSET:
            self.dark_mode = dark_mode
        if background is not _UNSET:
            self.background = background
        if surface is not _UNSET:
            self.surface = surface
        if text is not _UNSET:
            self.text = text
        if primary is not _UNSET:
            self.primary = primary

        if self._page is None:
            return

        light, dark = self._build_theme_pair()
        self._page.theme = light
        self._page.dark_theme = dark
        if self.dark_mode is True:
            self._page.theme_mode = ft.ThemeMode.DARK
        elif self.dark_mode is False:
            self._page.theme_mode = ft.ThemeMode.LIGHT
        else:
            self._page.theme_mode = ft.ThemeMode.SYSTEM
        self._render_views()

    def refresh(self):
        """Manually force a redraw. Buttons/switches/sliders already do this
        for you after their handler runs - this is for the rarer case
        (a background thread finished, a timer fired) where nothing on
        screen technically "clicked" but the state changed anyway."""
        self._render_views()

    # --------------------------------------------------------- clipboard ---

    def copy(self, text):
        """Copy text to the system clipboard - `app.copy(share_url)`."""
        async def do_copy():
            await self._page.clipboard.set(text)
        self._page.run_task(do_copy)

    def paste(self, on_result):
        """Returns an on_click-ready handler that reads the clipboard and
        calls `on_result(text)` - reading the clipboard is asynchronous in
        Flet, so this can't just be a plain property."""
        async def handler(e):
            text = await self._page.clipboard.get()
            on_result(text)
        return handler

    # ------------------------------------------------------ date & time ---

    def pick_date(self, on_result, first_date=None, last_date=None, help_text=None):
        """Returns an on_click-ready handler that opens the native date
        picker and calls `on_result(date)` with a `datetime.date` (or None
        if cancelled)."""
        def handler(e):
            def handle_change(change_event):
                on_result(change_event.control.value)
                self._render_views()

            picker = ft.DatePicker(
                first_date=first_date, last_date=last_date,
                help_text=help_text, on_change=handle_change,
            )
            self._page.show_dialog(picker)
        return handler

    def pick_time(self, on_result, help_text=None):
        """Same idea as pick_date, but for a time - `on_result(time)` gets
        a `datetime.time` (or None if cancelled)."""
        def handler(e):
            def handle_change(change_event):
                on_result(change_event.control.value)
                self._render_views()

            picker = ft.TimePicker(help_text=help_text, on_change=handle_change)
            self._page.show_dialog(picker)
        return handler

    # ------------------------------------------------------- shortcuts ---

    def on_key(self, combo, handler):
        """
        Registers a global keyboard shortcut - handy for desktop apps:

            app.on_key("ctrl+s", lambda e: save())
            app.on_key("escape", lambda e: app.back())

        `combo` is a plain string like "ctrl+s" or "ctrl+shift+n" -
        modifiers are optional, and order doesn't matter ("shift+ctrl+n"
        and "ctrl+shift+n" both work).
        """
        parts = [p.strip().lower() for p in combo.split("+")]
        key, mods = parts[-1], frozenset(parts[:-1])
        self._shortcuts[(key, mods)] = handler

    def _handle_keyboard_event(self, e):
        mods = frozenset(
            name for name, active in (("ctrl", e.ctrl), ("shift", e.shift), ("alt", e.alt), ("meta", e.meta))
            if active
        )
        handler = self._shortcuts.get((e.key.lower(), mods))
        if handler:
            handler(e)
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

    def _build_drawer(self):
        destinations = [
            ft.NavigationDrawerDestination(icon=item["icon"], label=item["label"])
            for item in self._drawer_items
        ]
        current_root = self._nav_stack[0]
        selected = next((i for i, item in enumerate(self._drawer_items) if item["route"] == current_root), 0)

        async def handle_change(e):
            index = e.control.selected_index
            self._nav_stack = [self._drawer_items[index]["route"]]
            await self._page.close_drawer()
            self._render_views()

        drawer = ft.NavigationDrawer(controls=destinations, selected_index=selected, on_change=handle_change)
        return drawer

    def _match_route(self, route):
        """Exact matches win first; otherwise checks registered routes with
        `:param` segments and returns (entry, params_dict)."""
        entry = self._routes.get(route)
        if entry is not None:
            return entry, {}

        for pattern, candidate in self._routes.items():
            if ":" not in pattern:
                continue
            if candidate["regex"] is None:
                regex_str = re.sub(r":([a-zA-Z_][a-zA-Z0-9_]*)", r"(?P<\1>[^/]+)", pattern)
                candidate["regex"] = re.compile(f"^{regex_str}$")
            match = candidate["regex"].match(route)
            if match:
                return candidate, match.groupdict()

        return self._routes.get("/"), {}

    def _build_view(self, route, is_root):
        entry, params = self._match_route(route)
        if entry is None:
            return ft.View(route=route, controls=[ft.Text(f"No page registered for '{route}'")])

        guard = entry.get("guard")
        if guard is not None and not guard():
            route = entry.get("redirect", "/")
            entry, params = self._match_route(route)
            if entry is None:
                return ft.View(route=route, controls=[ft.Text(f"No page registered for '{route}'")])

        handler = entry["handler"]
        accepts_params = len(inspect.signature(handler).parameters) >= 2
        content = handler(self._page, params) if accepts_params else handler(self._page)
        controls = list(content) if isinstance(content, (list, tuple)) else [content]

        appbar = None
        if entry["appbar"]:
            appbar = ft.AppBar(title=ft.Text(entry["title"] or self.title))

        nav_bar = self._build_nav_bar() if (is_root and self._tabs) else None
        drawer = self._build_drawer() if (is_root and self._drawer_items) else None

        return ft.View(
            route=route,
            controls=controls,
            appbar=appbar,
            navigation_bar=nav_bar,
            drawer=drawer,
            padding=self.padding,
        )

    def _render_views(self):
        page = self._page
        page.views.clear()
        for i, route in enumerate(self._nav_stack):
            try:
                view = self._build_view(route, is_root=(i == 0))
            except Exception as exc:
                view = self._error_view(route, exc)
            page.views.append(view)
        page.update()

    def _error_view(self, route, exc):
        """
        Shown instead of a crash when a page function raises. One bad
        screen (bad route param, a None where you expected a value, a
        typo in a dict key) shouldn't take down the entire app - that's
        especially rough on a phone, where there's no traceback in a
        terminal to explain what just happened.

        The real traceback still goes to your console either way - this
        is just what the *user* sees instead of a blank/frozen screen.
        """
        import traceback
        traceback.print_exc()
        return ft.View(
            route=route,
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=40, color=ft.Colors.ERROR),
                ft.Text("Something went wrong on this screen.", size=16),
                ft.Text(f"{type(exc).__name__}: {exc}", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.FilledButton("Go home", on_click=lambda e: self._recover_to_home()),
            ],
            padding=self.padding,
        )

    def _recover_to_home(self):
        self._nav_stack = ["/"]
        self._render_views()

    def _handle_view_pop(self, e):
        # fires when the user taps the AppBar back arrow or hits Android's
        # hardware back button - keep our own stack in sync with Flutter's
        if len(self._nav_stack) > 1:
            self._nav_stack.pop()
            self._render_views()

    def _should_show_splash(self, page):
        """
        "auto" shows the splash only for a web session connected from
        localhost/127.0.0.1 - i.e., you, running `python main.py` while
        developing. Desktop dev-preview (not web at all) never shows it,
        and a real deployment - Cloudflare Pages, any other real domain -
        never shows it either, because the browser's connecting host
        genuinely isn't localhost anymore once it's actually published.
        This is a property of *where the browser connected from*, not
        something that needs updating by hand when you go publish.
        """
        if self.splash is False:
            return False
        if self.splash is True:
            return True

        if not getattr(page, "web", False):
            return False

        host = ""
        try:
            host = urlparse(page.url or "").hostname or ""
        except ValueError:
            host = ""
        return host in ("localhost", "127.0.0.1", "::1", "")

    def _splash_view(self):
        logo = ft.Image(src=self._splash_asset, width=88, height=88) if self._splash_asset else ft.Container(width=88, height=88)
        return ft.View(
            route="__artemis_splash__",
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            logo,
                            ft.Text("Artemis", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("dev preview", size=12, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    alignment=ft.alignment.Alignment.CENTER,
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.Alignment.TOP_LEFT,
                        end=ft.alignment.Alignment.BOTTOM_RIGHT,
                        colors=["#6366F1", "#A855F7"],
                    ),
                ),
            ],
            padding=0,
        )

    async def _show_splash_then_render(self, page, seconds=1.1):
        page.views.clear()
        page.views.append(self._splash_view())
        page.update()
        await asyncio.sleep(seconds)
        self._render_views()

    def _build(self, page: ft.Page):
        self._page = page
        page.title = self.title

        light, dark = self._build_theme_pair()
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
        page.on_resize = lambda e: self._render_views()
        page.on_keyboard_event = self._handle_keyboard_event

        if self._should_show_splash(page):
            page.run_task(self._show_splash_then_render, page, self.splash_duration)
        else:
            self._render_views()

    def run(self, **kwargs):
        """Starts the app. Any kwargs get passed straight through to flet.run -
        e.g. view=ft.AppView.WEB_BROWSER, port=8550, etc - so nothing Flet
        can do becomes off-limits just because you're using Artemis."""
        assets_dir_name = kwargs.get("assets_dir") or "assets"
        script_dir = Path(sys.argv[0]).resolve().parent if sys.argv and sys.argv[0] else Path.cwd()
        assets_path = script_dir / assets_dir_name
        self._icon_path = ensure_branding(assets_path, self.logo)
        self._splash_asset = ensure_splash_asset(assets_path)

        ft.run(self._build, **kwargs)
