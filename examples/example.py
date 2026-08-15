"""
Kitchen sink - one app touching almost everything Artemis can do:

  - custom theming (background/surface/text/primary overrides + a
    live palette switcher)
  - a real navigation stack with route params (app.go / app.back)
  - a persistent bottom tab bar
  - a responsive layout (different arrangement on phone vs desktop width)
  - form validation (Field / Form / validators)
  - persistent state that survives an app restart
  - charts (needs: pip install flet-charts)
  - glass + gradient panels, ListTile/Avatar, toast/alert/confirm dialogs

Run it with:

    python kitchen_sink.py

(charts need the optional flet-charts package - if it's not installed,
the Stats tab will show a friendly message instead of crashing)
"""

import artemis as art

# --- persistent preferences: survive an app restart, stored as plain JSON
# in a .artemis_data/ folder next to this script ---
theme_pref = art.PersistentState("kitchen_sink_theme", default="indigo")

app = art.App(
    "Kitchen Sink",
    theme=theme_pref.value,
    background="#0B1220",
    surface="#161F32",
    text="#E5E7EB",
    window_size=(400, 720),
)

# --- a tiny in-memory "database" for the Contacts tab ---
contacts = ["Alice Kim", "Diego Torres", "Priya Nair"]

# --- a form for the Settings tab ---
name_field = art.Field("", art.validators.required())
email_field = art.Field("", art.validators.required(), art.validators.email())
settings_form = art.Form(name=name_field, email=email_field)


def switch_theme(name):
    theme_pref.value = name
    app.set_theme(name)


def save_profile(values):
    app.toast(f"Saved profile for {values['name']}")


def confirm_remove(person):
    def handler(e):
        app.confirm(
            f"Remove {person}?",
            "This can't be undone.",
            on_confirm=lambda e: (contacts.remove(person), app.toast(f"{person} removed"), app.refresh()),
        )
    return handler


# ---------------------------------------------------------------- Home ---

@app.page("/", title="Home")
def home(page):
    mobile = art.Column(
        [
            art.Box(
                art.Column([
                    art.Text("Frosted glass panel", color="white", bold=True),
                    art.Text("blur + translucent fill, one keyword", color="white", size=12),
                ]),
                glass=True,
                pad=20,
            ),
            art.Box(
                art.Text("Gradient panel", color="white", bold=True),
                gradient=["#6366F1", "#A855F7"],
                pad=20,
            ),
            art.Button("View a contact", on_click=lambda e: app.go(f"/contact/{contacts[0]}")),
        ],
        gap=14,
    )

    desktop = art.Row(
        [
            art.Box(
                art.Column([
                    art.Text("Frosted glass panel", color="white", bold=True),
                    art.Text("blur + translucent fill, one keyword", color="white", size=12),
                ]),
                glass=True, pad=20, expand=True,
            ),
            art.Box(
                art.Text("Gradient panel", color="white", bold=True),
                gradient=["#6366F1", "#A855F7"], pad=20, expand=True,
            ),
        ],
        gap=16,
    )

    return art.Column([
        art.Title("Welcome"),
        art.Text("This layout changes based on window width - try resizing.", muted=True),
        art.responsive(page, mobile=mobile, desktop=desktop, desktop_at=700),
    ], gap=16)


# ------------------------------------------------------------- Contacts ---

@app.page("/contacts", title="Contacts")
def contacts_list(page):
    rows = [
        art.ListTile(
            title=person,
            subtitle="Tap the icon to remove",
            leading=art.Avatar(text=person[0]),
            trailing=art.flet.IconButton(art.flet.Icons.DELETE_OUTLINE, on_click=confirm_remove(person)),
            on_click=lambda e, p=person: app.go(f"/contact/{p}"),
        )
        for person in contacts
    ] or [art.Text("No contacts left.", muted=True)]

    return art.Column([art.Title("Contacts"), art.Column(rows, gap=4, scroll=True, expand=True)], gap=12, expand=True)


@app.page("/contact/:name", title="Contact")
def contact_detail(page, params):
    return art.Column([
        art.Row([art.Avatar(text=params["name"][0], size=56), art.Title(params["name"])]),
        art.Text("Route params in action - this screen was reached via app.go() with a real back arrow above."),
        art.Button("Back", variant="text", on_click=lambda e: app.back()),
    ], gap=16)


# ---------------------------------------------------------------- Stats ---

@app.page("/stats", title="Stats")
def stats(page):
    try:
        chart = art.LineChart([12, 19, 14, 24, 22, 30], labels=["Jan", "Feb", "Mar", "Apr", "May", "Jun"], height=200)
        pie = art.PieChart({"Rent": 1200, "Food": 400, "Fun": 200}, height=200)
        chart_section = art.Column([art.Text("Monthly", muted=True), chart, art.Text("Spending", muted=True), pie], gap=8)
    except RuntimeError as e:
        chart_section = art.Box(art.Text(str(e)), glass=True, pad=16)

    return art.Column([art.Title("Stats"), chart_section], gap=12, scroll=True, expand=True)


# -------------------------------------------------------------- Settings ---

@app.page("/settings", title="Settings")
def settings(page):
    return art.Column(
        [
            art.Title("Settings"),
            art.Input(label="Name", field=name_field),
            art.Input(label="Email", field=email_field),
            art.Button("Save profile", on_click=settings_form.submit(save_profile)),
            art.Divider(),
            art.Text("Theme", muted=True),
            art.Row([
                art.Button("Indigo", variant="text", on_click=lambda e: switch_theme("indigo")),
                art.Button("Forest", variant="text", on_click=lambda e: switch_theme("forest")),
                art.Button("Sunset", variant="text", on_click=lambda e: switch_theme("sunset")),
            ], wrap=True),
            art.Button("Say hi", variant="outline", on_click=lambda e: app.alert("Hello", "Just an alert dialog.")),
        ],
        gap=12,
    )


# a persistent bottom tab bar across the four top-level screens above
app.bottom_nav([
    {"label": "Home", "icon": art.flet.Icons.HOME, "route": "/"},
    {"label": "Contacts", "icon": art.flet.Icons.PEOPLE, "route": "/contacts"},
    {"label": "Stats", "icon": art.flet.Icons.BAR_CHART, "route": "/stats"},
    {"label": "Settings", "icon": art.flet.Icons.SETTINGS, "route": "/settings"},
])


if __name__ == "__main__":
    app.run()