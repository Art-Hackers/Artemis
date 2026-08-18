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

# This is Flet's own official CI/CD workflow (see the "Continuous
# Integration/Continuous Deployment" section of https://flet.dev/docs/publish/),
# reproduced as-is rather than reinvented, since it's the team that
# actually maintains `flet build` and its platform/dependency quirks.
# Every platform builds on a GitHub-hosted runner - your own machine
# never needs Flutter, the Android SDK, or Xcode installed at all.
# Delete whichever platform entries you don't need.
WORKFLOW_TEMPLATE = """name: Build {title}

on:
  push:
  pull_request:
  workflow_dispatch:

env:
  UV_PYTHON: 3.12
  PYTHONUTF8: 1
  FLET_CLI_NO_RICH_OUTPUT: 1

jobs:
  build:
    name: Build ${{{{ matrix.name }}}}
    runs-on: ${{{{ matrix.runner }}}}
    strategy:
      fail-fast: false
      matrix:
        include:
          # -------- Desktop --------
          - name: linux
            runner: ubuntu-latest
            build_cmd: "flet build linux"
            artifact_path: build/linux
            needs_linux_deps: true
          - name: macos
            runner: macos-latest
            build_cmd: "flet build macos"
            artifact_path: build/macos
            needs_linux_deps: false
          - name: windows
            runner: windows-latest
            build_cmd: "flet build windows"
            artifact_path: build/windows
            needs_linux_deps: false
          # -------- Android --------
          - name: apk
            runner: ubuntu-latest
            build_cmd: "flet build apk"
            artifact_path: build/apk
            needs_linux_deps: false
          # -------- iOS (needs a macOS runner - no way around this, it's Apple's own restriction) --------
          - name: ipa
            runner: macos-latest
            build_cmd: "flet build ipa"
            artifact_path: build/ipa
            needs_linux_deps: false
          # -------- Web --------
          - name: web
            runner: ubuntu-latest
            build_cmd: "flet build web"
            artifact_path: build/web
            needs_linux_deps: false

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup uv
        uses: astral-sh/setup-uv@v6

      - name: Install Linux dependencies
        if: matrix.needs_linux_deps
        shell: bash
        run: |
            sudo apt update --allow-releaseinfo-change
            LINUX_DEPS="$(uv run flet --version --json | jq -r '.linux_dependencies | join(" ")')"
            sudo apt-get install -y --no-install-recommends $LINUX_DEPS
            sudo apt-get clean

      - name: Build app
        shell: bash
        run: |
          uv run ${{{{ matrix.build_cmd }}}} --yes --verbose

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{{{ matrix.name }}}}-build-artifact
          path: ${{{{ matrix.artifact_path }}}}
          if-no-files-found: error
          overwrite: false
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
    (target / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (target / "main.py").write_text(MAIN_TEMPLATE.format(title=title))
    (target / "pyproject.toml").write_text(PYPROJECT_TEMPLATE.format(slug=slug, title=title))
    (target / ".gitignore").write_text(GITIGNORE_TEMPLATE)
    (target / ".github" / "workflows" / "build.yml").write_text(WORKFLOW_TEMPLATE.format(title=title))

    print(f"Created {target}/")
    print()
    print("Next steps:")
    print(f"  cd {target}")
    print("  pip install -e .")
    print("  python main.py")
    print()
    print("When you're ready to build for Android/iOS/desktop/web, push to")
    print("GitHub - .github/workflows/build.yml builds every platform there,")
    print("so your own machine never needs Flutter, the Android SDK, or Xcode.")


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
