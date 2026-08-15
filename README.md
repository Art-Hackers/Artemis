# Artemis

**Build Android, iOS, desktop, and web apps in Python — with almost none of the boilerplate.**

Artemis, provided by Art-Hackers is a batteries-included layer on top of [Flet](https://flet.dev) (Flutter, for Python). Flet gives you the raw building blocks; Artemis gives you the everyday app-shell parts — theming, navigation, forms, state, dialogs, testing — as a small set of plain functions instead of something you assemble by hand in every new project.

```python
import artemis as art

app = art.App("Hello", theme="ocean")

@app.page("/")
def home(page):
    return art.Column([
        art.Title("Hello, Artemis"),
        art.Button("Say hi", on_click=lambda e: app.toast("Hi!")),
    ], center=True)

app.run()
```

Run that and you get a real, native-feeling window (not a webview) with a proper Material 3 color scheme, correct fonts, and modern rounded controls — from eleven lines. Build the same file for Android and it's a real Android app, because underneath, it's Flet and Flutter the whole way down. Artemis doesn't fork Flet or invent a new rendering engine — it removes repetition.

## Install

```bash
pip install artemis-ui
```

```python
import artemis as art
```

Want charts, or automatic conversion of a custom logo into a Windows icon? Those are optional extras:

```bash
pip install "artemis-ui[charts]"    # for art.LineChart / BarChart / PieChart
pip install "artemis-ui[icons]"     # for converting a custom logo.png into a Windows .ico
```

## Scaffold a new project

```bash
pip install artemis-ui
artemis new "My App"
cd "My App"
pip install -e .
python main.py
```

`artemis new` sets up a working starter app, and a GitHub Actions workflow that builds your app for Android, iOS, Windows, macOS, Linux, and Web the moment you push — so producing a real install-able app on every platform never requires setting up Flutter, the Android SDK, or Xcode on your own machine. See [Building & CI/CD](docs/12-building-and-ci.md).

## What you get

**Theming.** 31 named color palettes, or full manual control over background/surface/text/accent colors — each one Material 3-correct in both light and dark mode automatically.

```python
art.App("My App", theme="sunset")
art.App("My App", background="#0B1220", surface="#161F32", text="#E5E7EB", primary="#818CF8")
```

**Navigation that behaves like a real app.** A genuine back-stack (not a page swap) with automatic back arrows, working hardware/browser back buttons, route parameters, route guards, a bottom tab bar, and a side drawer.

```python
@app.page("/user/:id", guard=lambda: logged_in.value, redirect="/login")
def profile(page, params):
    return art.Text(f"User #{params['id']}")

app.go("/user/42")
app.back()
```

**State that just works, with a persistent and an async variant when you need them.**

```python
count = art.State(0)
theme_pref = art.PersistentState("theme", default="indigo")   # survives an app restart
products = art.AsyncData(lambda: art.fetch_json(url))          # loads once, not on every re-render
```

**Forms with real validation.**

```python
email = art.Field("", art.validators.required(), art.validators.email())
form = art.Form(email=email)
art.Input(label="Email", field=email)
art.Button("Submit", on_click=form.submit(handle_submit))
```

**Dialogs, toasts, pickers, and shortcuts** — `app.alert(...)`, `app.confirm(...)`, `app.toast(..., action="Undo")`, `app.pick_date(...)`, `app.on_key("ctrl+s", ...)`, clipboard access, and more, each a one-line call instead of manual control wiring.

**A wide widget set** — `Text`, `Button` (with an automatic loading spinner), `Input`, `Switch`, `Slider`, `Dropdown`, `Column`/`Row`/`Grid`, `Tabs`, `Card`, `ListTile`, `Avatar`, charts, and more — every one a plain Flet control under the hood, so anything Artemis doesn't wrap is one `import flet` away.

**Automatic branding.** A default app icon on first run, replaced instantly if you drop your own `logo.png` in `assets/` — and a dev-only splash screen for web apps that appears on `localhost` and disappears the moment the same code is actually deployed, with nothing to remember to turn off.

**A testing toolkit.** Test your app's logic — clicks, typed input, navigation, dialogs — without opening a window:

```python
from artemis.testing import TestApp

t = TestApp(app).build()
t.click(t.find_button("+"))
assert t.has_text("1")
```

## Documentation

The README above is the tour. The full reference — every widget, every parameter, every subsystem, with runnable examples — lives in [this repo](https://github.com/Art-Hackers/Artemis-Docs)

## The mental model, briefly

A page is a plain function that returns a control tree:

```python
@app.page("/")
def home(page):
    return art.Text("hello")
```

When a button is clicked, Artemis re-runs the current screen's function and redraws it — you don't call `page.update()` yourself. Text inputs are the one exception, so typing doesn't lose focus or cursor position; bind them to a `State` instead.

## Examples

The `examples/` folder has a complete, runnable app for nearly every feature above — a counter, a todo list, a themed dashboard with live charts, a login form, drawer navigation, keyboard shortcuts, and more:

```bash
python examples/counter.py
python examples/dashboard.py
```

## Good to know before you start

- **Screens re-render on every interaction, not just the one that changed.** This keeps the mental model simple (your page function is always a fresh, correct description of the screen) at a small performance cost. Fine for typical app sizes; if you're rendering thousands of rows at once, consider pagination.
- **There is no file picker.** Flet's underlying `FilePicker` control has a real, unresolved upstream registration bug that made it unreliable across machines and Python versions — rather than ship something that silently works for some people and not others, Artemis doesn't wrap it.
- **Charts need an extra install** (`pip install artemis-ui[charts]`) — kept optional so it's not forced on projects that don't need it.
- **Python 3.14 has some rough edges with Flet right now.** Python 3.12 or 3.13 are the most stable targets.
- **Packaging for Android/iOS/desktop genuinely requires Flutter.** That's how Flet works, not something Artemis can avoid — but it auto-installs itself, and the CI workflow every `artemis new` project ships with means your own machine may never need it at all.

## License

MIT — see [`LICENSE`](LICENSE).
