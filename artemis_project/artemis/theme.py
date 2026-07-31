"""
Theming for Artemis.

The whole trick here is Material 3's "seed color" system - give Flutter
one color and it derives an entire coherent palette (surfaces, text
colors, hover states, the works) for both light and dark mode. That's
why a two-line Artemis app doesn't look like a default grey Flet app.

Pick a name from PALETTES, or just pass any hex string of your own.
"""

import flet as ft

PALETTES = {
    "indigo": "#6366F1",
    "sunset": "#FB7185",
    "forest": "#10B981",
    "ocean": "#0EA5E9",
    "grape": "#A855F7",
    "amber": "#F59E0B",
    "slate": "#64748B",
    "rose": "#F43F5E",
}

# a couple of nicer default fonts than the platform default, if the user
# doesn't specify one. Google Fonts names - Flet will fetch them for you.
DEFAULT_FONT = "Poppins"


def build_theme(name="indigo", font=None):
    seed = PALETTES.get(name, name)  # falls back to treating `name` as a raw hex color
    font = font or DEFAULT_FONT

    light = ft.Theme(color_scheme_seed=seed, font_family=font, use_material3=True)
    dark = ft.Theme(color_scheme_seed=seed, font_family=font, use_material3=True)

    return light, dark


def resolve_color(value):
    """Lets widget helpers accept either a palette name or a raw color string."""
    return PALETTES.get(value, value) if isinstance(value, str) else value
