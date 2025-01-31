import plotly.graph_objects as go
import plotly.io as pio
from catppuccin import PALETTE

# https://colordesigner.io/gradient-generator
# https://mycolor.space/gradient3
GRADIENTS = {
    # red -> white -> blue
    "diverging": {
        "mocha": [
            "#f38ba8",
            "#ed99c3",
            "#e3a9d8",
            "#d8b8e7",
            "#d0c6f0",
            "#cac8f3",
            "#c4cbf5",
            "#becdf6",
            "#b2c7f7",
            "#a6c0f8",
            "#98baf9",
            "#89b4fa",
        ],
        "latte": [
            "#d20f39",
            "#da4276",
            "#d36ca8",
            "#c590c9",
            "#bcafd9",
            "#b5b2dd",
            "#aeb4e1",
            "#a6b7e4",
            "#8aa3ea",
            "#6c8fef",
            "#4c7bf3",
            "#1e66f5",
        ],
    },
    # teal -> peach
    "sequential": {
        "mocha": [
            "#94e2d5",
            "#99e1c5",
            "#a3dfb5",
            "#b0dba5",
            "#bed696",
            "#cdd08a",
            "#dbc981",
            "#e8c27e",
            "#f2ba80",
            "#fab387",
        ],
        "latte": [
            "#17959b",
            "#009b8c",
            "#23a076",
            "#4aa15a",
            "#709f33",
            "#939900",
            "#b29100",
            "#cc8600",
            "#e77700",
            "#fe640b",
        ],
    },
}


def register_custom_theme(theme: str) -> str:
    theme_name = f"catppuccin-{theme}"
    colors = getattr(PALETTE, theme).colors
    bg = colors.base.hex
    text = colors.text.hex
    axes = colors.surface2.hex
    axes2 = colors.surface0.hex
    grid = colors.surface2.hex
    grad_div = GRADIENTS["diverging"][theme]
    grad_seq = GRADIENTS["sequential"][theme]

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
