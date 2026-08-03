"""
Theming for Artemis.

The base trick is Material 3's "seed color" system - give Flutter one
color and it derives an entire coherent palette (surfaces, text colors,
hover states, the works) for both light and dark mode automatically.
That's why a two-line Artemis app doesn't look like a default grey Flet
app: `theme="sunset"` alone gets you there.

For anyone who wants more control than "pick a vibe", every piece of
that derived palette can be overridden individually and Flet will keep
using the seed for everything you didn't touch - see `build_theme()`
below. That's not an Artemis trick, it's how Flet's ColorScheme actually
works; Artemis just exposes it as a few plain keyword arguments instead
of making you build a ColorScheme object by hand.
"""

import flet as ft

PALETTES = {
    # cool
    "indigo": "#6366F1",
    "ocean": "#0EA5E9",
    "sky": "#38BDF8",
    "cobalt": "#2563EB",
    "royal": "#4F46E5",
    "teal": "#14B8A6",
    "cyan": "#06B6D4",
    "slate": "#64748B",
    "steel": "#475569",
    "midnight": "#1E293B",
    "graphite": "#334155",
    # green
    "forest": "#10B981",
    "mint": "#34D399",
    "emerald": "#059669",
    "lime": "#84CC16",
    "olive": "#4D7C0F",
    # warm
    "sunset": "#FB7185",
    "rose": "#F43F5E",
    "cherry": "#E11D48",
    "crimson": "#DC2626",
    "amber": "#F59E0B",
    "gold": "#EAB308",
    "orange": "#F97316",
    "coral": "#FB923C",
    "clay": "#B45309",
    "sand": "#D4A373",
    # bold
    "grape": "#A855F7",
    "violet": "#8B5CF6",
    "magenta": "#D946EF",
    "fuchsia": "#C026D3",
    "plum": "#86198F",
}

# a couple of nicer default fonts than the platform default, if the user
# doesn't specify one. Google Fonts names - Flet will fetch them for you.
DEFAULT_FONT = "Poppins"


def build_theme(name="indigo", font=None, background=None, surface=None, text=None, primary=None):
    """
    `name` picks the seed color (a PALETTES name or any hex string) that
    drives automatic light/dark generation - that alone is enough for
    most apps. For finer control, layer any of these on top:

        background - the color behind everything (Theme.scaffold_bgcolor)
        surface    - the color of cards/boxes sitting on that background
        text       - the default foreground/text color on that surface
        primary    - the accent color used for buttons, switches, etc.

    Each one you set becomes a fixed, absolute color in both light and
    dark mode (that's the point of overriding it); anything you leave as
    None still comes from the seed, light/dark included.
    """
    seed = resolve_color(name)
    font = font or DEFAULT_FONT

    overrides = {}
    if primary:
        overrides["primary"] = resolve_color(primary)
    if surface:
        overrides["surface"] = resolve_color(surface)
    if text:
        overrides["on_surface"] = resolve_color(text)
        overrides["on_surface_variant"] = resolve_color(text)

    color_scheme = ft.ColorScheme(**overrides) if overrides else None
    bg = resolve_color(background) if background else None

    def make():
        return ft.Theme(
            color_scheme_seed=seed,
            color_scheme=color_scheme,
            font_family=font,
            use_material3=True,
            scaffold_bgcolor=bg,
            card_bgcolor=resolve_color(surface) if surface else None,
        )

    return make(), make()


def resolve_color(value):
    """Lets widget helpers accept either a palette name or a raw color string."""
    return PALETTES.get(value, value) if isinstance(value, str) else value
