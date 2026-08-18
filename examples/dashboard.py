"""
Shows off route params, charts, a responsive layout, and a theme
preference that survives an app restart.

    python examples/dashboard.py

(Charts need the optional flet-charts package: pip install flet-charts)
"""

import artemis as art

app = art.App("Dashboard", theme="ocean", window_size=(420, 700))

# remembers the chosen theme across restarts - stored in .artemis_data/
theme_pref = art.PersistentState("dashboard_theme", default="ocean")
app.theme_name = theme_pref.value

sales_by_month = [12, 19, 14, 24, 22, 30]
month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

products = {"Widgets": 42, "Gadgets": 18, "Orders": 7}


def switch_theme(name):
    theme_pref.value = name
    app.set_theme(name)


@app.page("/")
def home(page):
    mobile_layout = art.Column(
        [
            art.Title("This Year"),
            art.LineChart(sales_by_month, labels=month_labels, height=180),
            art.Text("Tap a product for details", muted=True),
            art.ListTile(title="Widgets", trailing=art.flet.Icon(art.flet.Icons.CHEVRON_RIGHT),
                         on_click=lambda e: app.go("/product/widgets")),
            art.ListTile(title="Gadgets", trailing=art.flet.Icon(art.flet.Icons.CHEVRON_RIGHT),
                         on_click=lambda e: app.go("/product/gadgets")),
        ],
        gap=12,
    )

    desktop_layout = art.Row(
        [
            art.Column([art.Title("This Year"), art.LineChart(sales_by_month, labels=month_labels, height=220)], expand=True),
            art.Column([art.Title("By Product"), art.PieChart(products, height=220)], expand=True),
        ],
        gap=24,
    )

    return art.Column(
        [
            art.responsive(page, mobile=mobile_layout, desktop=desktop_layout, desktop_at=700),
            art.Divider(),
            art.Row([
                art.Text("Theme:", muted=True),
                art.Button("Ocean", variant="text", on_click=lambda e: switch_theme("ocean")),
                art.Button("Forest", variant="text", on_click=lambda e: switch_theme("forest")),
                art.Button("Grape", variant="text", on_click=lambda e: switch_theme("grape")),
            ]),
        ],
    )


@app.page("/product/:name", title="Product")
def product_detail(page, params):
    name = params["name"].capitalize()
    return art.Column([
        art.Title(name),
        art.Text(f"Units sold: {products.get(name, '—')}"),
        art.Button("Back", variant="text", on_click=lambda e: app.back()),
    ])


if __name__ == "__main__":
    app.run()
