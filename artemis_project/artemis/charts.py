"""
Charts are an optional Flet add-on package (`flet-charts`) rather than
part of core Flet, and their raw API is verbose even once installed -
you build DataPoint objects, wire up ChartAxis/ChartAxisLabel by hand for
every tick, and so on. These three functions take a plain list or dict
and build all of that for you.

None of this loads unless you actually call one of these functions, so
Artemis doesn't force `flet-charts` on anyone who doesn't need charts.
If you do:

    pip install flet-charts
"""

import flet as ft

from .theme import PALETTES, resolve_color

_DEFAULT_SLICE_COLORS = list(PALETTES.values())


def _charts():
    try:
        import flet_charts as fc
        return fc
    except ImportError as exc:
        raise RuntimeError(
            "Charts need the optional 'flet-charts' package. Install it with:\n"
            "    pip install flet-charts"
        ) from exc


def LineChart(values, labels=None, color=None, curved=True, height=200, **kw):
    """
        art.LineChart([12, 19, 8, 24, 16])
        art.LineChart([12, 19, 8, 24, 16], labels=["Mon", "Tue", "Wed", "Thu", "Fri"])

    `values` is just a list of numbers - Artemis builds the data points
    (x = index) for you. Pass a list of `(x, y)` tuples instead if you
    need non-sequential x values.
    """
    fc = _charts()

    if values and isinstance(values[0], (tuple, list)):
        points = [fc.LineChartDataPoint(x, y) for x, y in values]
    else:
        points = [fc.LineChartDataPoint(i, v) for i, v in enumerate(values)]

    series = fc.LineChartData(
        points=points,
        curved=curved,
        color=resolve_color(color) or ft.Colors.PRIMARY,
        stroke_width=3,
    )

    bottom_axis = None
    if labels:
        bottom_axis = fc.ChartAxis(
            labels=[fc.ChartAxisLabel(value=i, label=ft.Text(str(l), size=10)) for i, l in enumerate(labels)],
        )

    return fc.LineChart(data_series=[series], height=height, bottom_axis=bottom_axis, **kw)


def BarChart(values, labels=None, color=None, height=200, bar_width=20, **kw):
    """
        art.BarChart([12, 19, 8, 24, 16])
        art.BarChart([12, 19, 8], labels=["Q1", "Q2", "Q3"])
    """
    fc = _charts()
    bar_color = resolve_color(color) or ft.Colors.PRIMARY

    groups = [
        fc.BarChartGroup(
            x=i,
            rods=[fc.BarChartRod(from_y=0, to_y=v, width=bar_width, color=bar_color, border_radius=6)],
        )
        for i, v in enumerate(values)
    ]

    bottom_axis = None
    if labels:
        bottom_axis = fc.ChartAxis(
            labels=[fc.ChartAxisLabel(value=i, label=ft.Text(str(l), size=10)) for i, l in enumerate(labels)],
        )

    return fc.BarChart(groups=groups, height=height, bottom_axis=bottom_axis, **kw)


def PieChart(data, height=200, **kw):
    """
        art.PieChart({"Rent": 1200, "Food": 400, "Fun": 200})
        art.PieChart([("Rent", 1200, "#6366F1"), ("Food", 400, "#10B981")])

    `data` is a dict of label -> value, or a list of (label, value) /
    (label, value, color) tuples if you want to pick the colors yourself.
    Falls back to Artemis's own palette colors, cycled, if you don't.
    """
    fc = _charts()
    items = list(data.items()) if isinstance(data, dict) else list(data)

    sections = []
    for i, item in enumerate(items):
        label, value = item[0], item[1]
        color = item[2] if len(item) > 2 else _DEFAULT_SLICE_COLORS[i % len(_DEFAULT_SLICE_COLORS)]
        sections.append(
            fc.PieChartSection(
                value=value,
                title=str(label),
                color=resolve_color(color),
                title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE),
            )
        )

    return fc.PieChart(sections=sections, height=height, **kw)
