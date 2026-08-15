"""
This is the whole widget layer. Each function here just builds and
returns a normal Flet control - there's no hidden class hierarchy to
learn, no base "Widget" class to subclass. If you already know Flet,
you'll recognize everything immediately; if you don't, the defaults
are picked so things look decent without you tuning ten properties.

A couple of things worth knowing:

- `_rerender` gets pointed at App._render_current_route once the app
  actually starts. Button/Switch/Slider/etc wrap whatever `on_click`
  or `on_change` you gave them so that after it runs, the page redraws
  automatically. You just mutate a State and forget about it.
- Input() is the odd one out - see its docstring.
"""

import asyncio

import flet as ft

from .theme import resolve_color

_rerender = None  # wired up by App at startup
_page = None  # ditto - lets toast() and friends work without you passing `page` around


def _after(handler):
    """
    Wraps a handler so a full-page redraw happens right after it runs.

    Works the same whether `handler` is a normal function or an `async
    def` - Flet natively awaits coroutine event handlers on its own event
    loop, so an async on_click (for file pickers, network calls, etc)
    just works here too, redraw included.
    """
    if handler is None:
        return None

    if asyncio.iscoroutinefunction(handler):
        async def wrapped(e):
            await handler(e)
            if _rerender:
                _rerender()
        return wrapped

    def wrapped(e):
        handler(e)
        if _rerender:
            _rerender()

    return wrapped


# ---------------------------------------------------------------- text ---

def Text(value="", size=16, bold=False, italic=False, color=None, center=False, muted=False, **kw):
    return ft.Text(
        str(value),
        size=size,
        weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
        italic=italic,
        color=resolve_color(color) or (ft.Colors.ON_SURFACE_VARIANT if muted else None),
        text_align=ft.TextAlign.CENTER if center else ft.TextAlign.START,
        **kw,
    )


def Title(value, size=28, **kw):
    """Just Text() with sane heading defaults - saves typing size=28, bold=True everywhere."""
    return Text(value, size=size, bold=True, **kw)


# -------------------------------------------------------------- button ---

_BUTTON_KINDS = {
    "filled": ft.FilledButton,
    "elevated": ft.ElevatedButton,
    "outline": ft.OutlinedButton,
    "outlined": ft.OutlinedButton,
    "text": ft.TextButton,
}


def Button(text, on_click=None, variant="filled", icon=None, width=None, expand=False, loading=None, **kw):
    """
    Pass a State via `loading=` to get an automatic spinner: the button
    shows a small loading indicator instead of its label while an async
    on_click is running, and disables itself so it can't be double-tapped.

        saving = art.State(False)
        art.Button("Save", on_click=save_handler, loading=saving)

    Artemis flips `saving.value` to True right before calling your
    handler and back to False right after (success or failure either
    way) - read it elsewhere on the page too if you want a loading state
    to show up in more than one place at once.
    """
    kind = _BUTTON_KINDS.get(variant.lower(), ft.FilledButton)
    is_loading = bool(loading.value) if loading is not None else False

    click_handler = on_click
    if loading is not None and on_click is not None:
        async def click_handler(e):
            loading.value = True
            if _rerender:
                _rerender()
            try:
                result = on_click(e)
                if asyncio.iscoroutine(result):
                    await result
            finally:
                loading.value = False

    return kind(
        content=Loader(size=16, color=ft.Colors.ON_PRIMARY) if is_loading else text,
        icon=icon if not is_loading else None,
        on_click=_after(click_handler),
        width=width,
        expand=expand,
        disabled=is_loading or kw.pop("disabled", False),
        **kw,
    )


# --------------------------------------------------------------- input ---

def Input(label="", value="", bind=None, field=None, password=False, multiline=False, on_change=None, width=None, **kw):
    """
    Text fields don't get the auto-rerender treatment that buttons and
    switches get - redrawing the whole page on every keystroke would
    blow away the cursor position and drop focus, which is miserable to
    type into. Instead, pass a State object via `bind` and Artemis will
    just keep it updated silently as the user types, no redraw:

        name = art.State("")
        art.Input(label="Your name", bind=name)

    Read `name.value` whenever you actually need it (e.g. in a button's
    on_click). If you'd rather handle changes yourself, use `on_change`
    like plain Flet - it's passed straight through, untouched.

    Pass a Field (see forms.py) via `field=` instead of `bind=` to get
    validation for free - the error message shows up under the input
    automatically once the field's been touched, no extra wiring:

        email = art.Field("", art.validators.email())
        art.Input(label="Email", field=email)
    """
    if field is not None:
        bind = field.state

    def handle_change(e):
        if bind is not None:
            bind.value = e.control.value
        if on_change is not None:
            on_change(e)

    def handle_blur(e):
        if field is not None:
            field.touch()
            if _rerender:
                _rerender()

    return ft.TextField(
        label=label,
        value=value if bind is None else bind.value,
        password=password,
        can_reveal_password=password,
        multiline=multiline,
        width=width,
        on_change=handle_change,
        on_blur=handle_blur,
        error=field.error if field is not None else None,
        **kw,
    )


# --------------------------------------------------------------- toggle ---

def Switch(label="", value=False, on_change=None, **kw):
    return ft.Switch(label=label, value=value, on_change=_after(on_change), **kw)


def Checkbox(label="", value=False, on_change=None, **kw):
    return ft.Checkbox(label=label, value=value, on_change=_after(on_change), **kw)


def Slider(value=0, min=0, max=100, on_change=None, label=None, **kw):
    return ft.Slider(value=value, min=min, max=max, label=label, on_change=_after(on_change), **kw)


def Dropdown(options, value=None, on_change=None, label=None, **kw):
    items = [ft.dropdown.Option(o) if isinstance(o, str) else o for o in options]
    return ft.Dropdown(options=items, value=value, label=label, on_change=_after(on_change), **kw)


# -------------------------------------------------------------- layout ---

def Column(controls=None, gap=10, center=False, scroll=False, expand=False, **kw):
    return ft.Column(
        controls=controls or [],
        spacing=gap,
        alignment=ft.MainAxisAlignment.CENTER if center else ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER if center else ft.CrossAxisAlignment.START,
        scroll=ft.ScrollMode.AUTO if scroll else None,
        expand=expand,
        **kw,
    )


def Row(controls=None, gap=10, center=False, wrap=False, expand=False, **kw):
    return ft.Row(
        controls=controls or [],
        spacing=gap,
        alignment=ft.MainAxisAlignment.CENTER if center else ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER if center else ft.CrossAxisAlignment.START,
        wrap=wrap,
        expand=expand,
        **kw,
    )


def Grid(items, columns=2, min_item_width=None, gap=10, expand=True, **kw):
    """
    A responsive-ish grid of cards/tiles - the "gallery of things" layout
    every dashboard or product list needs, without hand-rolling a Row of
    Columns yourself.

        art.Grid([art.Card(art.Text(p)) for p in products], columns=3)

    Pass `min_item_width=200` instead of `columns` for a grid that picks
    its own column count based on available width (handy for the same
    screen to look right on a phone and a wide desktop window).
    """
    return ft.GridView(
        controls=items,
        runs_count=None if min_item_width else columns,
        max_extent=min_item_width,
        spacing=gap,
        run_spacing=gap,
        expand=expand,
        **kw,
    )


def Tabs(tabs, selected=0, on_change=None, expand=True, **kw):
    """
    In-page tabbed content - not navigation between screens (that's
    `bottom_nav`/`set_drawer`), just switching which panel is visible
    within one screen.

        art.Tabs([
            ("Overview", art.Text("...")),
            ("Settings", art.Column([...])),
        ])

    Raw Flet's Tabs needs a separate TabBar + TabBarView wired together
    with a matching `length` you have to keep in sync by hand; this is
    just a list of (label, content) pairs.
    """
    labels = [ft.Tab(label=label) for label, _ in tabs]
    panels = [ft.Container(content=content, padding=12) for _, content in tabs]
    return ft.Tabs(
        length=len(tabs),
        selected_index=selected,
        on_change=_after(on_change),
        expand=expand,
        content=ft.Column(
            [ft.TabBar(tabs=labels), ft.TabBarView(controls=panels, expand=True)],
            expand=expand,
        ),
        **kw,
    )


def Expandable(title, content, subtitle=None, leading=None, expanded=False, **kw):
    """
    A collapsible section - FAQs, settings groups, "show more" details.

        art.Expandable("Shipping details", art.Text("Ships in 2-3 days."))
    """
    return ft.ExpansionTile(
        title=title if not isinstance(title, str) else Text(title, bold=True),
        subtitle=(subtitle if not isinstance(subtitle, str) else Text(subtitle, muted=True)) if subtitle else None,
        leading=leading,
        controls=[content] if not isinstance(content, (list, tuple)) else list(content),
        expanded=expanded,
        **kw,
    )


def Badge(label=None, color=None, **kw):
    """
    A small notification dot/count - not a wrapper, a value you attach to
    another control's `badge` property (most controls have one):

        art.flet.Icon(art.flet.Icons.NOTIFICATIONS, badge=art.Badge("3"))

    Leave `label` as None for a plain dot instead of a number.
    """
    return ft.Badge(label=str(label) if label is not None else None, bgcolor=resolve_color(color), **kw)


def Box(content=None, pad=16, radius=12, bg=None, gradient=None, glass=False, on_click=None, **kw):
    """
    A styled ft.Container - the general-purpose "put a rounded box around
    this" helper. Two extras that raw Flet makes you assemble by hand:

    - `gradient=["#6366F1", "#EC4899"]` - just give it a couple of colors,
      Artemis builds the LinearGradient (top-left to bottom-right) for you.
    - `glass=True` - a frosted-glass panel (blurred backdrop, translucent
      fill, faint border). Looks great sitting on top of an Image or a
      gradient background. Getting this right in plain Flet means reaching
      for Blur, BoxShadow and a semi-transparent bgcolor all separately -
      here it's one flag.
    """
    if "border_radius" in kw:
        radius = kw.pop("border_radius")

    if glass:
        bgcolor = ft.Colors.with_opacity(0.12, ft.Colors.WHITE)
        edge = ft.border.BorderSide(1, ft.Colors.with_opacity(0.25, ft.Colors.WHITE))
        border = ft.border.Border(top=edge, right=edge, bottom=edge, left=edge)
        blur = ft.Blur(sigma_x=20, sigma_y=20)
    else:
        bgcolor = resolve_color(bg)
        border = kw.pop("border", None)
        blur = kw.pop("blur", None)

    grad = None
    if gradient:
        grad = ft.LinearGradient(
            begin=ft.alignment.Alignment.TOP_LEFT,
            end=ft.alignment.Alignment.BOTTOM_RIGHT,
            colors=[resolve_color(c) for c in gradient],
        )

    return ft.Container(
        content=content,
        padding=pad,
        border_radius=radius,
        bgcolor=bgcolor if not grad else None,
        gradient=grad,
        border=border,
        blur=blur,
        ink=on_click is not None,
        on_click=_after(on_click) if on_click else None,
        **kw,
    )


def Card(content=None, pad=16, radius=16, elevation=1, **kw):
    return ft.Card(
        content=ft.Container(content=content, padding=pad, border_radius=radius),
        elevation=elevation,
        **kw,
    )


def Spacer(size=20):
    return ft.Container(height=size, width=size)


def Divider(**kw):
    return ft.Divider(**kw)


# --------------------------------------------------------------- media ---

def Image(src, width=None, height=None, radius=0, fit="cover", **kw):
    fits = {
        "cover": ft.ImageFit.COVER,
        "contain": ft.ImageFit.CONTAIN,
        "fill": ft.ImageFit.FILL,
    }
    return ft.Image(
        src=src,
        width=width,
        height=height,
        border_radius=radius,
        fit=fits.get(fit, ft.ImageFit.COVER),
        **kw,
    )


# ---------------------------------------------------------------- misc ---

def toast(message, bg=None, seconds=3, action=None, on_action=None):
    """
    A one-line snackbar: `art.toast("Saved!")`. No `page` argument needed -
    Artemis already knows which page it's running on. In plain Flet this
    is `page.show_dialog(ft.SnackBar(...))` plus remembering SnackBar is
    a dialog-like control at all, which trips people up constantly.

    Pass `action="Undo"` with `on_action=...` for an action button:

        art.toast("Task deleted", action="Undo", on_action=lambda e: restore(task))
    """
    if _page is None:
        return
    _page.show_dialog(
        ft.SnackBar(
            content=ft.Text(message),
            bgcolor=resolve_color(bg),
            duration=seconds * 1000,
            action=action,
            on_action=_after(on_action) if on_action else None,
        )
    )


def BottomNav(tabs, selected=0, on_change=None, **kw):
    """
    tabs: a list of (label, icon) pairs, e.g.
        [("Home", ft.Icons.HOME), ("Search", ft.Icons.SEARCH), ("Me", ft.Icons.PERSON)]

    This builds the ft.NavigationBar itself - most of the time you'll
    hand this straight to app.bottom_nav(...) rather than placing it in
    a page yourself, so it stays fixed at the bottom across screens.
    """
    destinations = [
        ft.NavigationBarDestination(icon=icon, label=label) for label, icon in tabs
    ]
    return ft.NavigationBar(
        destinations=destinations,
        selected_index=selected,
        on_change=_after(on_change),
        **kw,
    )


def ListTile(title, subtitle=None, leading=None, trailing=None, on_click=None, **kw):
    """
    A row with an optional icon, a title, a subtitle, and something on the
    right - the bread and butter of settings screens, contact lists, todo
    rows, notification feeds, you name it. Strings for `title`/`subtitle`
    get wrapped in Text() automatically; pass a control instead if you
    want to style it yourself.
    """
    return ft.ListTile(
        title=title if not isinstance(title, str) else Text(title),
        subtitle=(subtitle if not isinstance(subtitle, str) else Text(subtitle, muted=True)) if subtitle else None,
        leading=leading,
        trailing=trailing,
        on_click=_after(on_click) if on_click else None,
        **kw,
    )


def Avatar(text=None, src=None, size=40, bg=None, **kw):
    """A round avatar - pass `src` for a photo, or just `text` (e.g. someone's
    initials) for a plain color circle. `size` is the diameter in pixels."""
    return ft.CircleAvatar(
        content=Text(text, bold=True) if text and not src else None,
        foreground_image_src=src,
        bgcolor=resolve_color(bg) or ft.Colors.PRIMARY_CONTAINER,
        radius=size / 2,
        **kw,
    )


def Loader(size=32, color=None, **kw):
    """A small spinning progress ring - drop it in wherever something's
    loading. For a horizontal loading bar instead, use ProgressBar()."""
    return ft.ProgressRing(width=size, height=size, color=resolve_color(color), **kw)


def ProgressBar(value=None, color=None, **kw):
    """A horizontal progress bar. Leave `value` as None for an indeterminate
    "still working on it" animation, or pass 0.0-1.0 for a real percentage."""
    return ft.ProgressBar(value=value, color=resolve_color(color), **kw)
