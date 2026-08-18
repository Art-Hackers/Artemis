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
    # custom
    "silver": "#C0C0C0",
    "hackergreen": "#00FF41",
    "neonpink": "#FF10F0",
    "cyberpunk": "#B026FF",
    "laser": "#FF0844",
    "electriclime": "#CCFF00",
    # monochrome
    "jetblack": "#0A0A0A",
    "charcoal": "#36454F",
    "snow": "#FAFAFA",
    "pearl": "#F0EAD6",
    # vibrant accents
    "electricblue": "#7DF9FF",
    "acidgreen": "#B0FF00",
    "hotmagenta": "#FF00FF",
    "tangerine": "#F28500",
    # others
    "midnightblue": "#191970",
    "matrix": "#008F11",
    "vaporwave": "#FF71CE",
    "ultraviolet": "#7B2FF7",
    "toxic": "#6AFF00",
    "solaris": "#FFB100",
    "deepspace": "#0B0C2A",
    "supernova": "#FFD500",
    "arctic": "#A0E9FF",
    "amethyst": "#9966CC",
    "crimsonflare": "#FF3131",
}

# Curated two/three-color gradient presets - drop straight into
# `art.Box(gradient="sunrise")`, no need to pick two hex codes yourself
# unless you want to. Each name here also resolves through PALETTES-style
# lookup wherever a gradient is expected.
GRADIENTS = {
    "sunrise": ["#F97316", "#EC4899"],
    "sunset": ["#FB7185", "#A855F7"],
    "ocean": ["#0EA5E9", "#6366F1"],
    "aurora": ["#22D3EE", "#A855F7", "#EC4899"],
    "candy": ["#F472B6", "#818CF8"],
    "mint": ["#34D399", "#0EA5E9"],
    "fire": ["#F59E0B", "#DC2626"],
    "midnight": ["#1E293B", "#0F172A"],
    "cyberpunk": ["#00F0FF", "#B026FF", "#FF10F0"],
    "vaporwave": ["#FF71CE", "#01CDFE", "#B967FF"],
    "matrix": ["#000000", "#008F11", "#00FF41"],
    "galaxy": ["#0B0C2A", "#5B21B6", "#EC4899"],
    "toxic": ["#0A0A0A", "#6AFF00"],
    "gold": ["#FFD500", "#F59E0B"],
    "arctic": ["#A0E9FF", "#FFFFFF"],
    "royal": ["#4F46E5", "#9333EA"],
    "supernova": ["#FFD500", "#FF3131"],
}

# a couple of nicer default fonts than the platform default, if the user
# doesn't specify one. Google Fonts names - Flet will fetch them for you.
DEFAULT_FONT = "Poppins"


def _hex_to_rgb(value):
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def _blend(hex_a, hex_b, t):
    """Blends two hex colors - t=0 is pure hex_a, t=1 is pure hex_b."""
    a, b = _hex_to_rgb(hex_a), _hex_to_rgb(hex_b)
    return _rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


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

    One subtlety worth knowing: Flet/Flutter's automatic light/dark
    generation derives *every* ColorScheme field - including the ones
    used for dividers and borders (`outline`/`outline_variant`) - based
    on which theme slot (light or dark) happens to be active, which
    depends on the *system's* current light/dark setting when you
    haven't forced `dark_mode` yourself. That means a purely seed-derived
    outline color can come out light-mode-appropriate even while your
    `surface`/`text` overrides are deliberately dark, producing a
    visibly mismatched grey divider or border. To avoid that, whenever
    both `surface` and `text` are given, Artemis also derives sensible
    `outline`/`outline_variant` values from them directly, instead of
    leaving those two specifically to seed/brightness guesswork.
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
    if surface and text:
        surface_hex, text_hex = resolve_color(surface), resolve_color(text)
        overrides["outline"] = _blend(surface_hex, text_hex, 0.5)
        overrides["outline_variant"] = _blend(surface_hex, text_hex, 0.24)

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


def resolve_gradient(value):
    """Lets Box(gradient=...) accept a named GRADIENTS preset ("sunset"), a
    list of palette names/hex colors, or a mix of both in one list."""
    if isinstance(value, str):
        value = GRADIENTS.get(value, [value])
    return [resolve_color(c) for c in value]
