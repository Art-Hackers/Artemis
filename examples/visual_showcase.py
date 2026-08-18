"""
Shows what Artemis looks like when you reach for more than plain boxes:
a gradient hero banner, dashboard stat cards, gradient icon circles, and
pill-shaped chips - the pieces a real product screen is actually made
of, not just stacked rectangles.

    python examples/visual_showcase.py
"""

import artemis as art

app = art.App("Visual Showcase", theme="midnight", window_size=(420, 760))


@app.page("/")
def home(page):
    return art.Column(
        [
            art.Hero(
                "Good morning, Czax",
                "You have 3 things that need your attention today",
                gradient="cyberpunk",
                icon=art.flet.Icons.WB_CLOUDY,
            ),
            art.Grid(
                [
                    art.StatCard("Revenue", "$12,400", icon=art.flet.Icons.TRENDING_UP, trend="+12%", color="emerald"),
                    art.StatCard("Users", "1,204", icon=art.flet.Icons.PEOPLE, trend="+4%", color="cobalt"),
                    art.StatCard("Churn", "2.1%", icon=art.flet.Icons.TRENDING_DOWN, trend="-0.4%", color="rose"),
                    art.StatCard("Uptime", "99.98%", icon=art.flet.Icons.BOLT, color="amber"),
                ],
                columns=2,
                gap=12,
            ),
            art.Row(
                [
                    art.IconCircle(art.flet.Icons.ROCKET_LAUNCH, gradient="sunset"),
                    art.IconCircle(art.flet.Icons.SHIELD, gradient="ocean"),
                    art.IconCircle(art.flet.Icons.BOLT, gradient="toxic"),
                    art.IconCircle(art.flet.Icons.AUTO_AWESOME, gradient="cyberpunk"),
                ],
                gap=12,
            ),
            art.Box(
                art.Text("Cards can float now too - this one has a soft drop shadow.", color="white"),
                gradient="galaxy",
                shadow="lg",
                pad=20,
            ),
            art.Row(
                [
                    art.Chip("New", color="rose"),
                    art.Chip("Popular", color="amber"),
                    art.Chip("Design", color="grape"),
                    art.Chip("Beta", color="cyan"),
                ],
                wrap=True,
                gap=8,
            ),
        ],
        gap=20,
        scroll=True,
        expand=True,
    )


if __name__ == "__main__":
    app.run(view=art.flet.AppView.WEB_BROWSER)
