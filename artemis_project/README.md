# Artemis

A stupidly easy way to build Android and desktop apps in Python.

Artemis sits on top of [Flet](https://flet.dev) (which itself sits on
Flutter), and trims day-to-day app building down to something that reads
almost like pseudocode:

```python
import artemis as art

app = art.App("Hello", theme="ocean")

@app.page("/")
def home(page):
    return art.Column([
        art.Title("Hello, Artemis"),
        art.Button("Say hi", on_click=lambda e: print("hi!")),
    ], center=True)

app.run()
```

Run that, and you get a real, native-feeling app - not a wrapped webview -
with a Material 3 color scheme, correct fonts, and rounded modern-looking
controls, for free. Run the *exact same file* on Android with `flet build
apk` and it just works, because under the hood it's still Flet/Flutter the
whole way down.

Artemis isn't trying to replace Flet or compete with it - think of it as
the "batteries included" layer on top: opinionated defaults, a much
smaller vocabulary, and routing/state wired up so you rarely touch
`page.update()` yourself.

## Install

```bash
cd artemis          # the folder with pyproject.toml in it
pip install -e .
```

(Not published to PyPI yet - this is a first pass at the API. The
distribution name is `artemis-ui` to avoid clashing with the handful of
other "artemis" packages already on PyPI; you still `import artemis`.)

**Getting `ModuleNotFoundError: No module named 'artemis'`?** That means
Python can't see the package - almost always because you're running a
script from *inside* `examples/` while `pip install -e .` was never run,
or was run from the wrong folder. Two ways to fix it:

```bash
# Option A - install it properly (recommended, works from anywhere after)
cd artemis
pip install -e .
python examples/counter.py

# Option B - no install, just run it from the project root so Python
# can see the artemis/ folder sitting right next to examples/
cd artemis
python examples/counter.py
```

Either way, run the script from the `artemis/` project root (the one
containing both `artemis/` and `examples/`), not from inside `Examples/`
itself - a script can't `import` a package that's a sibling of its own
folder rather than its parent.

## Branding - no more Flet logo

A brand-new Artemis app doesn't show Flet's own icon. The first time
`app.run()` starts, Artemis drops three files into your project's
`assets/` folder (creating it if needed), none of which ever overwrite
something you've already put there yourself:

- `logo.png` - the source image (Artemis's default crescent-moon mark,
  unless you supply your own)
- `icon.png` - a copy of it, under the exact filename `flet build` looks
  for to generate the *real* installed-app icon (Android launcher icon,
  Windows/macOS icon, etc) - so building your app for real produces a
  properly-branded app on every platform, no config needed
- `logo.ico` - used for the **Windows** dev-preview window/taskbar icon

**Being upfront about a genuine Flet limitation:** while you're just
running `python examples/counter.py` (not a real build), the window icon
can only reliably be overridden on **Windows**, and only via an absolute
path to an actual `.ico` file - a relative path or a `.png` gets silently
ignored by Flet's pre-built desktop client (this is a known Flet quirk,
not something Artemis papers over - see `flet-dev/flet#3438`). Artemis
handles that correctly under the hood: absolute path, real `.ico`, done.
On **macOS**, the dock icon during dev preview is baked into Flet's own
pre-built client and literally can't be changed short of building your
own white-labeled Flet client - not an Artemis limitation, a Flet one.
Either way, `flet build`/`flet pack` (a real build) get the icon right
on every platform via `icon.png` above.

**Want your own logo?** Drop your own `logo.png` in `assets/` and it's
used instead automatically. If Pillow is installed, Artemis also
auto-converts it into a matching `logo.ico` for you so your own branding
shows up in the Windows dev-preview window icon too, not just ours. If
Pillow isn't installed, Artemis falls back to its own default `.ico` for
that one narrow case (`pip install pillow` if you want your PNG
converted automatically) - or just supply your own `logo.ico` directly
and Artemis will leave it alone.

If you want a different filename or a different assets folder entirely:

```python
app = art.App("My App", logo="brand.png")   # looks for assets/brand.png (+ brand.ico)
app.run(assets_dir="static")                 # looks in static/ instead of assets/
```

## The mental model

- **One `App`.** You make one, give it a title and a theme.
- **Pages are just functions.** Decorate a function with `@app.page("/route")`
  and return whatever control tree that screen should show.
- **State is a box, not magic.** `art.State(0)` gives you something you can
  mutate from inside a closure. Change `.value` and the screen updates -
  no signals, no dependency graph to reason about.
- **Buttons/switches/sliders auto-redraw.** After their `on_click` /
  `on_change` fires, Artemis quietly re-runs your page function and
  refreshes the screen. You just change state and move on.
- **Text inputs are the one exception.** Redrawing the whole page on every
  keystroke would drop your cursor position, so `Input()` takes a `bind=`
  State instead and updates it silently, no redraw, no dropped focus.

## What actually makes this different from plain Flet

Flet gives you the primitives; Artemis makes the everyday app-shell stuff
(the part every mobile app needs and every Flet tutorial re-explains from
scratch) a one-liner:

- **A real navigation stack, not a page swap.** `app.go("/details")` pushes
  a proper `flet.View` onto the stack with a back arrow that appears on
  its own. Android's hardware back button and the browser back button both
  pop it correctly - `app.back()` does the same thing in code. Plenty of
  "simple Flet wrapper" libraries just clear `page.controls`, which quietly
  breaks both of those.
- **`app.bottom_nav([...])`** gives you a persistent tab bar across your
  root screens - tap a tab, the root screen swaps; push into a detail view
  with `app.go()` and the tab bar correctly disappears until you go back,
  same as it would in a native app.
- **`art.Box(glass=True)`** - an instant frosted-glass panel (blur, faint
  border, translucent fill). In raw Flet that's `ft.Blur` + `ft.BoxShadow`
  + a manually opacity-adjusted `bgcolor`, three separate imports to get
  one visual effect; here it's a keyword argument.
- **`art.Box(gradient=["#6366F1", "#EC4899"])`** - builds the
  `ft.LinearGradient` for you instead of you constructing one by hand.
- **`app.toast("Saved!")`** - a one-line snackbar. No `page` argument to
  pass around, no remembering that `SnackBar` is technically a dialog-like
  control under the hood.

## What's in the box right now

`Text`, `Title`, `Button`, `Input`, `Switch`, `Checkbox`, `Slider`,
`Dropdown`, `Column`, `Row`, `Box`, `Card`, `Spacer`, `Divider`, `Image`,
`BottomNav`, `ListTile`, `Avatar`, `Loader`, `ProgressBar`, `toast`, plus
`App` and `State`. `App` also gives you `app.alert(title, message)` and
`app.confirm(title, message, on_confirm)` for quick modal dialogs. That's
genuinely most of what a typical small app needs. Anything Artemis
doesn't wrap yet, you can still reach for - `import flet` (or `art.flet`)
is right there, and every Artemis widget returns a plain Flet control, so
mixing the two is completely fine.

## Themes

Six palettes ship out of the box - `indigo`, `sunset`, `forest`, `ocean`,
`grape`, `amber` (plus `slate` and `rose`) - or pass any hex string of
your own as `theme="#22D3EE"`. Each one is a Material 3 "seed color", so
light mode, dark mode, hover states, and text contrast are all derived
automatically. `App(..., dark_mode=True/False)` forces a mode; leave it
out and Artemis follows the system setting.

## Examples

- `examples/counter.py` - the classic, shows State + auto-redraw
- `examples/todo.py` - a small task list, shows `Input(bind=...)`, dynamic
  lists of Cards, and Checkbox toggling
- `examples/showcase.py` - navigation (`app.go`/`app.back`), a bottom tab
  bar, glass + gradient panels, and a toast
- `examples/contacts.py` - `ListTile` + `Avatar` rows, `Loader` /
  `ProgressBar`, and `app.alert()` / `app.confirm()` dialogs

```bash
python examples/counter.py
```

## Shipping to Android / desktop

This is the part Artemis doesn't try to reinvent - it's just Flet, so
Flet's own build tooling applies unchanged:

```bash
flet build apk      # Android
flet build ipa       # iOS
flet build macos      # macOS
flet build windows      # Windows
flet build linux      # Linux
```

## Known rough edges (v0.1, being upfront about it)

- Every button/switch click re-runs the current screen's function and
  redraws it from scratch. It's simple and fast enough for typical apps,
  but if you're rendering something genuinely huge (thousands of rows)
  you'll feel it. Scoped/partial updates are on the list for a v2.
- Routes are flat strings (`"/"`, `"/settings"`) - no route params like
  `"/user/:id"` yet, so pass IDs through a shared `State` instead.
- `bottom_nav()` assumes a single level of tabs; nesting a second tab bar
  inside a pushed screen isn't supported.
- Widget coverage is intentionally narrow for now (see the list above).
  More wrappers are easy to add; `widgets.py` is about 250 lines and each
  function follows the same shape.
