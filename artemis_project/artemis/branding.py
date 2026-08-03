"""
Handles the "why does my app show the Flet logo" problem.

Two separate things are going on here, and they get fixed two different
ways:

1. THE WINDOW/TASKBAR ICON while you're just running `python main.py`.
   This one's annoying: Flet's desktop preview is a pre-built Flutter
   client, and `page.window.icon` only actually takes effect on Windows,
   and only if you give it an ABSOLUTE path to a real .ico file - a
   relative path or a .png/.jpg gets silently ignored (this is a known
   Flet quirk, not a bug in Artemis - see flet-dev/flet#3438). On macOS
   the dock icon during dev preview can't be overridden at all short of
   building your own branded Flet client, so we don't pretend to fix
   that; `flet build`/`flet pack` handle it properly for a real build.

2. THE ACTUAL SHIPPED APP ICON, once you run `flet build apk` (or ipa,
   macos, windows...). This one's the well-behaved one: Flet's build
   tool looks for `assets/icon.png` and generates every platform's real
   icon from it automatically.

Artemis handles both: it drops a default `logo.png` (source image),
`icon.png` (for `flet build`), and `logo.ico` (for the Windows dev-preview
window icon) into your assets folder the first time you run the app -
none of it overwriting a file you've already put there yourself.
"""

import shutil
import sys
from importlib import resources
from pathlib import Path


def _bundled_bytes(name):
    return resources.files("artemis").joinpath("assets", name).read_bytes()


def _make_ico_from_png(png_path: Path, ico_path: Path) -> bool:
    """Best-effort PNG -> ICO conversion for a custom logo, using Pillow if
    it's installed. Returns False (and does nothing) if Pillow isn't
    available - Artemis doesn't want to force a new hard dependency just
    for this, so the bundled default .ico is used as a fallback instead."""
    try:
        from PIL import Image
    except ImportError:
        return False

    try:
        img = Image.open(png_path)
        img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        return True
    except Exception:
        return False


def ensure_branding(assets_dir: Path, logo_name="logo.png"):
    """
    Makes sure the assets folder has what it needs for branding, falling
    back to Artemis's bundled defaults wherever the user hasn't supplied
    their own file. Returns an absolute path to the .ico file to hand to
    `page.window.icon` (only meaningful on Windows - see module docstring).
    """
    assets_dir.mkdir(parents=True, exist_ok=True)

    logo_path = assets_dir / logo_name
    is_default_logo = not logo_path.exists()
    if is_default_logo:
        logo_path.write_bytes(_bundled_bytes("logo.png"))

    # flet build's own convention - separate from logo_name on purpose,
    # since that's the exact filename flet build looks for
    icon_png_path = assets_dir / "icon.png"
    if not icon_png_path.exists():
        shutil.copyfile(logo_path, icon_png_path)

    # the Windows dev-preview window icon needs an actual .ico file
    ico_path = assets_dir / (Path(logo_name).stem + ".ico")
    if not ico_path.exists():
        made_custom_ico = False
        if not is_default_logo:
            # the user supplied their own logo.png - try to convert it so
            # their branding shows up in the window icon too, not just ours
            made_custom_ico = _make_ico_from_png(logo_path, ico_path)
        if not made_custom_ico:
            ico_path.write_bytes(_bundled_bytes("logo.ico"))

    return str(ico_path.resolve())
