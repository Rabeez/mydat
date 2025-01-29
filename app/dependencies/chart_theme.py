import plotly.graph_objects as go
import plotly.io as pio
from catppuccin import PALETTE


def register_custom_theme(theme: str) -> str:
    theme_name = f"catppuccin-{theme}"
    colors = getattr(PALETTE, theme).colors
    bg = colors.base.hex
    text = colors.text.hex
    axes = colors.surface2.hex
    axes2 = colors.surface0.hex
    grid = colors.surface2.hex
    grad_div = [
        [0.0, "#f38ba8"],  # red
        [0.1, "#ef9fc3"],
        [0.2, "#e9b4d7"],
        [0.3, "#e4c7e5"],
        [0.4, "#e4d9ec"],
        [0.5, "#e1dcef"],
        [0.6, "#deddf0"],
        [0.7, "#cfd1f2"],
        [0.8, "#bcc7f5"],
        [0.9, "#a5bdf7"],
        [1.0, "#89b4fa"],  # blue
    ]
    grad_seq = [
        [0.0, "#94e2d5"],  # teal
        [0.1111111111111111, "#97e5c7"],
        [0.2222222222222222, "#9de7b4"],
        [0.3333333333333333, "#acea9c"],
        [0.4444444444444444, "#cded95"],
        [0.5555555555555556, "#ebef8f"],
        [0.6666666666666666, "#f2de8b"],
        [0.7777777777777778, "#f5ce88"],
        [0.8888888888888888, "#f7c087"],
        [1.0, "#fab387"],  # peach
    ]

    pio.templates[theme_name] = go.layout.Template(
        layout={
            "annotationdefaults": {"arrowcolor": text, "arrowhead": 0, "arrowwidth": 1},
            "autotypenumbers": "strict",
            "coloraxis": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
            "colorscale": {
                "diverging": grad_div,
                "sequential": grad_seq,
                "sequentialminus": grad_seq,
            },
            "colorway": [
                colors.blue.hex,
                colors.peach.hex,
                colors.green.hex,
                colors.red.hex,
                colors.mauve.hex,
                colors.maroon.hex,
                colors.pink.hex,
                colors.rosewater.hex,
                colors.teal.hex,
                colors.lavender.hex,
            ],
            "font": {"color": text},
            "geo": {
                "bgcolor": bg,
                "lakecolor": axes2,
                "landcolor": axes2,
                "showlakes": True,
                "showland": True,
                "subunitcolor": grid,
            },
            "hoverlabel": {"align": "left"},
            "hovermode": "closest",
            "mapbox": {"style": "dark"},
            "paper_bgcolor": bg,
            "plot_bgcolor": bg,
            "polar": {
                "angularaxis": {"gridcolor": grid, "linecolor": grid, "ticks": ""},
                "bgcolor": bg,
                "radialaxis": {"gridcolor": grid, "linecolor": grid, "ticks": ""},
            },
            "scene": {
                "xaxis": {
                    "backgroundcolor": bg,
                    "gridcolor": grid,
                    "gridwidth": 2,
                    "linecolor": grid,
                    "showbackground": True,
                    "ticks": "",
                    "zerolinecolor": axes,
                },
                "yaxis": {
                    "backgroundcolor": bg,
                    "gridcolor": grid,
                    "gridwidth": 2,
                    "linecolor": grid,
                    "showbackground": True,
                    "ticks": "",
                    "zerolinecolor": axes,
                },
                "zaxis": {
                    "backgroundcolor": bg,
                    "gridcolor": grid,
                    "gridwidth": 2,
                    "linecolor": grid,
                    "showbackground": True,
                    "ticks": "",
                    "zerolinecolor": axes,
                },
            },
            "shapedefaults": {"line": {"color": text}},
            "sliderdefaults": {
                "bgcolor": axes,
                "bordercolor": bg,
                "borderwidth": 1,
                "tickwidth": 0,
            },
            "ternary": {
                "aaxis": {"gridcolor": grid, "linecolor": grid, "ticks": ""},
                "baxis": {"gridcolor": grid, "linecolor": grid, "ticks": ""},
                "bgcolor": bg,
                "caxis": {"gridcolor": grid, "linecolor": grid, "ticks": ""},
            },
            "title": {"x": 0.05},
            "updatemenudefaults": {"bgcolor": grid, "borderwidth": 0},
            "xaxis": {
                "automargin": True,
                "gridcolor": axes2,
                "linecolor": grid,
                "ticks": "",
                "title": {"standoff": 15},
                "zerolinecolor": axes2,
                "zerolinewidth": 2,
            },
            "yaxis": {
                "automargin": True,
                "gridcolor": axes2,
                "linecolor": grid,
                "ticks": "",
                "title": {"standoff": 15},
                "zerolinecolor": axes2,
                "zerolinewidth": 2,
            },
        },
    )
    return theme_name
