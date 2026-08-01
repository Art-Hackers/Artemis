<img width="1254" height="1254" alt="Artemis" src="https://github.com/user-attachments/assets/365a5d59-dc3c-42e1-8a1b-0bee7962287e" />

# Artemis

Artemis is a lightweight library for building Android and desktop apps in Python with less boilerplate. If you are already comfortable writing Python and want to ship native-feeling applications without switching stacks, this project is designed to feel familiar.

The goal is simple: give you a compact API for the parts of app development that tend to repeat in every project—routing, app shell behavior, state updates, dialogs, themed widgets, and navigation—while still letting you drop down to Flet when you need more control.

## Logo

<img width="512" height="512" alt="logo" src="https://github.com/user-attachments/assets/6783d917-cea5-4d4f-bfe1-9c8cd5853e97" />


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

That same Python file can be run locally and later built for Android or desktop with Flet tooling underneath.

## Installation

Install Artemis from PyPI with:

```bash
pip install artemis-ui
```

Once installed, import it in Python as:

```python
import artemis as art
```

If you are working from a local checkout of the repository instead of the published package, you can install it in editable mode with:

```bash
cd artemis
pip install -e .
```

If you see `ModuleNotFoundError: No module named 'artemis'`, the package is not visible to the interpreter. In practice, that usually means one of these happened:

- the package was not installed
- the install was run from the wrong directory
- you launched the example from inside the `examples/` folder instead of the project root

A reliable local workflow is:

```bash
cd artemis
pip install -e .
python examples/counter.py
```

## Mental model

Artemis is intentionally small. The core concepts are:

- One `App` instance per application.
- Pages are Python functions decorated with `@app.page("/route")`.
- State is managed through `art.State(...)`.
- UI updates are triggered by changing state values rather than manually calling `page.update()`.
- Text inputs are handled specially so focus and cursor position are preserved.

This makes the library feel more like a Pythonic app framework than a thin wrapper around Flet primitives.

## What Artemis adds on top of Flet

Flet gives you low-level controls. Artemis gives you a more productive app-shell experience for the common cases:

- `app.go("/details")` pushes a real navigation view with back handling.
- `app.bottom_nav([...])` creates a persistent tab bar for root-level navigation.
- `art.Box(glass=True)` and `art.Box(gradient=[...])` provide common visual patterns without manually constructing Flet effects.
- `app.toast("Saved!")` gives you snackbar-style feedback in one line.

This is especially useful for small-to-medium internal tools, business apps, and prototypes where you want a polished UI without writing a lot of glue code.

## Available widgets and helpers

Artemis currently includes wrappers for common UI building blocks such as:

- `Text`, `Title`, `Button`, `Input`, `Switch`, `Checkbox`, `Slider`, `Dropdown`
- `Column`, `Row`, `Box`, `Card`, `Spacer`, `Divider`, `Image`
- `BottomNav`, `ListTile`, `Avatar`, `Loader`, `ProgressBar`
- `App`, `State`, `toast`, `alert()`, and `confirm()`

If a control is not yet wrapped, you can still use Flet directly through `import flet` or `art.flet`, and Artemis widgets return standard Flet controls so the two can interoperate cleanly.

## Themes

Artemis ships with built-in palettes such as `indigo`, `sunset`, `forest`, `ocean`, `grape`, `amber`, `slate`, and `rose`. You can also provide your own hex color as `theme="#22D3EE"`.

Theme selection is handled through Material 3-inspired seed colors, so light mode, dark mode, contrast, and hover states are derived automatically. Use `App(..., dark_mode=True/False)` to override the system preference if needed.

## Branding and assets

A new Artemis app will add branding assets to your project’s `assets/` directory when you first run it. These include:

- `logo.png` for the default branding image
- `icon.png` for the installed app icon expected by Flet builds
- `logo.ico` for the Windows dev-preview window icon

If you want to override the defaults, place your own `logo.png` in `assets/` or configure the app like this:

```python
app = art.App("My App", logo="brand.png")
app.run(assets_dir="static")
```

If Pillow is installed, Artemis can also generate a matching `.ico` automatically from your custom PNG.

## Examples

The repository includes a few small reference apps:

- `examples/counter.py` — demonstrates simple state handling and auto-redraw behavior
- `examples/todo.py` — shows dynamic lists, text input binding, and checkboxes
- `examples/showcase.py` — demonstrates navigation, bottom navigation, glass panels, gradients, and toast messages
- `examples/contacts.py` — demonstrates lists, avatars, loaders, progress bars, and dialogs

Run one of them with:

```bash
python examples/counter.py
```

## Build for Android and desktop

Artemis does not replace Flet’s build pipeline. Once your app is ready, you can use Flet’s own build commands:

```bash
flet build apk      # Android
flet build ipa       # iOS
flet build macos      # macOS
flet build windows      # Windows
flet build linux      # Linux
```

## Current limitations

This is still an early release, so the API is intentionally focused. A few things to keep in mind:

- page redraws happen on state-driven updates, which is simple and effective for typical apps but not ideal for very large data sets
- routes are currently flat strings such as `/` and `/settings`
- bottom navigation is designed for a single tab level
- widget coverage is still intentionally narrow and will grow over time
