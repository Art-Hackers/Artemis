"""
Shows the dev-mode splash screen: run this in web mode and open it at
http://localhost:8550 - you'll see a brief Artemis-branded splash before
your own app appears. That splash is automatic and dev-only - it's
detected from the browser's actual connecting host, not a flag you have
to remember to flip off before deploying. If this same code ends up
served from a real domain (Cloudflare Pages, anywhere else), the splash
simply never appears, because the host genuinely isn't localhost anymore.

    python examples/web_splash_demo.py

Then open the printed localhost URL in a browser.
"""

import artemis as art

# splash="auto" is the default - shown here explicitly just so it's easy
# to find. Force it with splash=True/False if you want to override the
# auto-detection for some reason (testing the splash itself, for instance).
app = art.App("Web Splash Demo", theme="grape", splash="auto")


@app.page("/")
def home(page):
    return art.Column(
        [
            art.Title("This is your real app"),
            art.Text("The Artemis splash you (maybe) just saw only shows up here, on localhost."),
            art.Text("Deploy this same file anywhere else and it won't appear.", muted=True),
        ],
        center=True,
        expand=True,
    )


if __name__ == "__main__":
    app.run(view=art.flet.AppView.WEB_BROWSER)
