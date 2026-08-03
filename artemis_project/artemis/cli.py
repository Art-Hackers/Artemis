"""
The `artemis` command line tool. Right now it does one thing:

    artemis new myapp

...and that one thing is worth having - a starter `main.py` and
`pyproject.toml` beat a blank folder every time.
"""

import argparse
import sys
from pathlib import Path

MAIN_TEMPLATE = '''"""
{title} - made with Artemis.
"""

import artemis as art

app = art.App("{title}", theme="indigo")


@app.page("/")
def home(page):
    return art.Column(
        [
            art.Title("Welcome to {title}"),
            art.Text("Edit main.py to get started - app.run() at the bottom is your entry point."),
            art.Button("Say hi", on_click=lambda e: app.toast("Hi from {title}!")),
        ],
        center=True,
        expand=True,
    )


if __name__ == "__main__":
    app.run()
'''

PYPROJECT_TEMPLATE = '''[project]
name = "{slug}"
version = "0.1.0"
description = "Built with Artemis."
requires-python = ">=3.9"
dependencies = [
    "artemis-ui",
]
'''

GITIGNORE_TEMPLATE = """__pycache__/
*.pyc
.artemis_data/
build/
"""


def cmd_new(args):
    title = args.name
    slug = title.lower().replace(" ", "-")
    target = Path(args.name)

    if target.exists() and any(target.iterdir()):
        print(f"'{target}' already exists and isn't empty - pick a different name or clear it out first.")
        sys.exit(1)

    target.mkdir(parents=True, exist_ok=True)
    (target / "assets").mkdir(exist_ok=True)
    (target / "main.py").write_text(MAIN_TEMPLATE.format(title=title))
    (target / "pyproject.toml").write_text(PYPROJECT_TEMPLATE.format(slug=slug, title=title))
    (target / ".gitignore").write_text(GITIGNORE_TEMPLATE)

    print(f"Created {target}/")
    print()
    print("Next steps:")
    print(f"  cd {target}")
    print("  pip install -e .")
    print("  python main.py")


def main():
    parser = argparse.ArgumentParser(prog="artemis", description="Scaffold and manage Artemis apps.")
    subparsers = parser.add_subparsers(dest="command")

    new_parser = subparsers.add_parser("new", help="Create a new Artemis app in its own folder")
    new_parser.add_argument("name", help="Project folder / app name")
    new_parser.set_defaults(func=cmd_new)

    args = parser.parse_args()
    if not getattr(args, "command", None):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
