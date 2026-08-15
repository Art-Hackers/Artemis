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
    # Custom
    "silver": "#C0C0C0",
    "hackergreen": "#00FF6A",
    "neonpink": "#FF007F",
    "cyberpunk": "#FEE715",
    "laser": "#00FFFF",
    "electriclime": "#CCFF00",
    # Monochrome
    "jetblack": "#0A0A0A",
    "charcoal": "#121212",
    "snow": "#F8FAFC",
    "pearl": "#E2E8F0",
    # Vibrant Accents
    "electricblue": "#0047AB",
    "acidgreen": "#BFFF00",
    "hotmagenta": "#FF00FF",
    "tangerine": "#FF8C00",
    # Other
    "midnightblue": "#191970",
    "matrix": "#03F8C4",          
    "vaporwave": "#FF71CE",      
    "ultraviolet": "#5F27CD",     
    "toxic": "#39FF14",          
    "solaris": "#FFBE0B",         
    "deepspace": "#0B0C10",       
    "supernova": "#FF5722",    
    "arctic": "#64FFDA",          
    "amethyst": "#9C27B0",        
    "crimsonflare": "#FF1744",    
}

DEFAULT_FONT = "Poppins"


def _hex_to_rgb(color):
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    if len(color) != 6:
        raise ValueError(f"Unsupported color value: {color!r}")
    return tuple(int(color[i:i + 2], 16) for i in range(0, 6, 2))


def _rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, channel)):02X}" for channel in rgb)


def _mix_colors(base, mix_with, weight=0.5):
    weight = max(0.0, min(1.0, weight))
    base_rgb = _hex_to_rgb(base)
    other_rgb = _hex_to_rgb(mix_with)
    mixed = tuple(
        round((1 - weight) * base_rgb[i] + weight * other_rgb[i])
        for i in range(3)
    )
    return _rgb_to_hex(mixed)


def _tint_color(color, amount):
    amount = max(-1.0, min(1.0, amount))
    r, g, b = _hex_to_rgb(color)
    if amount >= 0:
        r = round(r + (255 - r) * amount)
        g = round(g + (255 - g) * amount)
        b = round(b + (255 - b) * amount)
    else:
        amount = abs(amount)
        r = round(r * (1 - amount))
        g = round(g * (1 - amount))
        b = round(b * (1 - amount))
    return _rgb_to_hex((r, g, b))


def _text_color_for(background):
    r, g, b = _hex_to_rgb(background)
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return "#111827" if luminance > 0.5 else "#F8FAFC"


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
    surface_color = resolve_color(surface) if surface else None
    text_color = resolve_color(text) if text else None
    primary_color = resolve_color(primary) if primary else None

    overrides = {}
    if surface_color:
        overrides["surface"] = surface_color
        overrides["surface_container"] = _tint_color(surface_color, 0.08)
        overrides["surface_container_low"] = _tint_color(surface_color, -0.10)
        overrides["surface_container_high"] = _tint_color(surface_color, 0.14)
        overrides["surface_container_highest"] = _tint_color(surface_color, 0.22)
        overrides["surface_bright"] = _tint_color(surface_color, 0.18)
        overrides["surface_dim"] = _tint_color(surface_color, -0.18)
        overrides["surface_tint"] = surface_color

    if primary_color:
        overrides["primary"] = primary_color
        overrides["primary_container"] = _tint_color(primary_color, 0.26)
        overrides["on_primary"] = text_color or _text_color_for(primary_color)
        overrides["on_primary_container"] = text_color or _text_color_for(primary_color)

    if text_color:
        overrides["on_surface"] = text_color
        overrides["on_surface_variant"] = text_color
    elif surface_color:
        overrides["on_surface"] = _text_color_for(surface_color)
        overrides["on_surface_variant"] = _text_color_for(surface_color)

    color_scheme = ft.ColorScheme(**overrides) if overrides else None
    bg = resolve_color(background) if background else None

    def make():
        return ft.Theme(
            color_scheme_seed=seed,
            color_scheme=color_scheme,
            font_family=font,
            use_material3=True,
            scaffold_bgcolor=bg,
            card_bgcolor=surface_color,
        )

    return make(), make()


def resolve_color(value):
    """Lets widget helpers accept either a palette name or a raw color string."""
    return PALETTES.get(value, value) if isinstance(value, str) else value
