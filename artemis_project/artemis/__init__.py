"""
Artemis - a stupidly easy way to build Android and desktop apps in Python.

Built on top of Flet (which is itself built on Flutter), Artemis trims
the ceremony down to roughly this:

    import artemis as art

    app = art.App("Hello", theme="ocean")

    @app.page("/")
    def home(page):
        return art.Column([
            art.Title("Hello, Artemis"),
            art.Button("Say hi", on_click=lambda e: print("hi!")),
        ], center=True)

    app.run()

Nothing here is magic - every function in `widgets.py` just returns a
regular Flet control, so anything you already know about Flet (or
Flutter, if you go digging) still applies. Artemis just picks good
defaults and gets rid of the boilerplate.
"""

from .app import App
from .state import State
from .theme import PALETTES
from .widgets import (
    Text,
    Title,
    Button,
    Input,
    Switch,
    Checkbox,
    Slider,
    Dropdown,
    Column,
    Row,
    Box,
    Card,
    Spacer,
    Divider,
    Image,
    BottomNav,
    ListTile,
    Avatar,
    Loader,
    ProgressBar,
    toast,
)

# re-export flet itself under a shorter name, for the moments you need
# something Artemis doesn't wrap yet (icons, colors, a niche control...)
import flet as flet

__version__ = "0.1.0"

__all__ = [
    "App", "State", "PALETTES",
    "Text", "Title", "Button", "Input", "Switch", "Checkbox", "Slider",
    "Dropdown", "Column", "Row", "Box", "Card", "Spacer", "Divider", "Image",
    "BottomNav", "ListTile", "Avatar", "Loader", "ProgressBar", "toast",
    "flet",
]
