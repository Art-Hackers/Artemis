import artemis as art
from datetime import datetime
import uuid

# Remember the selected theme and stored projects between restarts.
theme_pref = art.PersistentState("aurora_studio_theme", default="violet")
projects_state = art.PersistentState("aurora_studio_projects", default=[])

app = art.App(
    "Aurora Studio",
    theme=theme_pref.value,
    background="#081121",
    surface="#0F1724",
    text="#E7E9FF",
    window_size=(460, 800),
)

# convenience accessor for stored projects
def _projects():
    return projects_state.value or []


# form fields for creating a new project
new_title = art.Field("", art.validators.required())
new_description = art.Field("", art.validators.required(), art.validators.min_length(8))
new_tags = art.Field("")
new_form = art.Form(title=new_title, description=new_description, tags=new_tags)


def set_theme(name):
    theme_pref.value = name
    app.set_theme(name, background=None, surface=None, text=None)


def save_new_project(values):
    projects = _projects()
    project = {
        "id": uuid.uuid4().hex[:8],
        "title": values["title"],
        "description": values["description"],
        "tags": [t.strip() for t in (values.get("tags") or "").split(",") if t.strip()],
        "created": datetime.utcnow().isoformat(),
        "accent": ["#8B5CF6", "#3B82F6"],
    }
    projects.append(project)
    projects_state.value = projects
    app.toast(f"Project '{project['title']}' saved")
    app.go(f"/project/{project['id']}")


def project_card(project):
    return art.Box(
        art.Column([
            art.Text(project["title"], bold=False, size=16),
            art.Text(project.get("description", ""), muted=False, size=12),
            art.Row([
                art.Button("Open", variant="text", on_click=lambda e, p=project: app.go(f"/project/{p['id']}")),
                art.Button("Duplicate", variant="outline", on_click=lambda e, p=project: duplicate_project(p)),
            ], gap=8),
        ], gap=8),
        gradient=project.get("accent"),
        pad=18,
        border_radius=16,
        width=240,
    )


def duplicate_project(p):
    projects = _projects()
    clone = dict(p)
    clone["id"] = uuid.uuid4().hex[:8]
    clone["title"] = f"{p['title']} (copy)"
    projects.append(clone)
    projects_state.value = projects
    app.toast("Duplicated")


@app.page("/", title="Home")
def home(page):
    projects = _projects()
    featured = projects[:4] if projects else []

    hero = art.Box(
        art.Column([
            art.Text("Aurora Studio", size=36, bold=False),
            art.Text("A beautiful workspace for your ideas — sketch, plan, and ship.", size=14, muted=False),
            art.Row([
                art.Button("New Project", on_click=lambda e: app.go("/studio")),
                art.Button("Browse Projects", variant="outline", on_click=lambda e: app.go("/gallery")),
            ], gap=12),
        ], gap=18),
        gradient=["#7C3AED", "#06B6D4"],
        pad=28,
        border_radius=20,
    )

    gallery_strip = art.Row([project_card(p) for p in featured], gap=14, scroll=False)

    stats = art.Row([
        art.Box(art.Column([art.Text(str(len(projects)), bold=False, size=22), art.Text("Projects", muted=False)]), glass=False, pad=16, expand=False),
        art.Box(art.Column([art.Text("—", bold=False, size=22), art.Text("Active", muted=False)]), glass=False, pad=16, expand=False),
    ], gap=12, wrap=False)

    return art.Column([hero, stats, art.Title("Featured projects"), gallery_strip], gap=18, scroll=False, expand=False)


@app.page("/gallery", title="Projects")
def gallery(page):
    projects = _projects()
    cards = [project_card(p) for p in projects] or [art.Text("No projects yet.", muted=False)]
    return art.Column([art.Title("Projects"), art.Row(cards, gap=16, scroll=False)], gap=16, scroll=False, expand=False)


@app.page("/project/:id", title="Project")
def project_detail(page, params):
    pid = params["id"]
    project = next((p for p in _projects() if p["id"] == pid), None)
    if not project:
        return art.Column([art.Title("Not found"), art.Text("This project could not be found.")], gap=12)
    return art.Column([
        art.Row([art.Avatar(text=project['title'][0] if project['title'] else '?', size=56), art.Column([art.Title(project['title']), art.Text(project.get('created',''), muted=False)])], gap=14),
        art.Divider(),
        art.Text(project.get('description','')),
        art.Divider(),
        art.Text("Tags", muted=False),
        art.Row([art.Badge(t, color=None) for t in project.get('tags', [])], gap=8),
        art.Divider(),
        art.Row([art.Button("Back", variant="text", on_click=lambda e: app.back()), art.Button("Edit", on_click=lambda e: app.toast("Edit coming soon"))], gap=10)
    ], gap=12, scroll=False, expand=False)


@app.page("/studio", title="New Project")
def studio(page):
    return art.Column([
        art.Title("New Project"),
        art.Input(label="Title", field=new_title),
        art.Input(label="Short description", field=new_description),
        art.Input(label="Tags (comma separated)", field=new_tags),
        art.Button("Create project", on_click=new_form.submit(save_new_project)),
        art.Divider(),
        art.Text("Theme", muted=False),
        art.Row([art.Button("Violet", variant="outline", on_click=lambda e: set_theme("violet")), art.Button("Ocean", variant="outline", on_click=lambda e: set_theme("ocean")), art.Button("Sunset", variant="outline", on_click=lambda e: set_theme("sunset"))], gap=10, wrap=False),
    ], gap=12, scroll=False, expand=False)


app.bottom_nav([
    {"label": "Home", "icon": art.flet.Icons.HOME, "route": "/"},
    {"label": "Projects", "icon": art.flet.Icons.WALLPAPER, "route": "/gallery"},
    {"label": "New", "icon": art.flet.Icons.CREATE, "route": "/studio"},
])


if __name__ == "__main__":
    app.run()
