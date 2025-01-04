import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import polars as pl
from catppuccin import PALETTE

colors = PALETTE.mocha.colors
BG = colors.base.hex
TEXT = colors.text.hex
AXES = colors.surface2.hex
AXES2 = colors.surface0.hex
GRID = colors.surface2.hex


gapminder = pl.DataFrame(px.data.gapminder())
df_2007 = gapminder.filter(pl.col("year") == 2007)

pio.templates["catppuccin-mocha"] = go.layout.Template(
    layout={
        "annotationdefaults": {"arrowcolor": TEXT, "arrowhead": 0, "arrowwidth": 1},
        "autotypenumbers": "strict",
        "coloraxis": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
        "colorscale": {
            "diverging": [
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
            ],
            "sequential": [
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
            ],
            "sequentialminus": [
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
            ],
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
        "font": {"color": TEXT},
        "geo": {
            "bgcolor": BG,
            "lakecolor": AXES2,
            "landcolor": AXES2,
            "showlakes": True,
            "showland": True,
            "subunitcolor": GRID,
        },
        "hoverlabel": {"align": "left"},
        "hovermode": "closest",
        "mapbox": {"style": "dark"},
        "paper_bgcolor": BG,
        "plot_bgcolor": BG,
        "polar": {
            "angularaxis": {"gridcolor": GRID, "linecolor": GRID, "ticks": ""},
            "bgcolor": BG,
            "radialaxis": {"gridcolor": GRID, "linecolor": GRID, "ticks": ""},
        },
        "scene": {
            "xaxis": {
                "backgroundcolor": BG,
                "gridcolor": GRID,
                "gridwidth": 2,
                "linecolor": GRID,
                "showbackground": True,
                "ticks": "",
                "zerolinecolor": AXES,
            },
            "yaxis": {
                "backgroundcolor": BG,
                "gridcolor": GRID,
                "gridwidth": 2,
                "linecolor": GRID,
                "showbackground": True,
                "ticks": "",
                "zerolinecolor": AXES,
            },
            "zaxis": {
                "backgroundcolor": BG,
                "gridcolor": GRID,
                "gridwidth": 2,
                "linecolor": GRID,
                "showbackground": True,
                "ticks": "",
                "zerolinecolor": AXES,
            },
        },
        "shapedefaults": {"line": {"color": TEXT}},
        "sliderdefaults": {
            "bgcolor": AXES,
            "bordercolor": BG,
            "borderwidth": 1,
            "tickwidth": 0,
        },
        "ternary": {
            "aaxis": {"gridcolor": GRID, "linecolor": GRID, "ticks": ""},
            "baxis": {"gridcolor": GRID, "linecolor": GRID, "ticks": ""},
            "bgcolor": BG,
            "caxis": {"gridcolor": GRID, "linecolor": GRID, "ticks": ""},
        },
        "title": {"x": 0.05},
        "updatemenudefaults": {"bgcolor": GRID, "borderwidth": 0},
        "xaxis": {
            "automargin": True,
            "gridcolor": AXES2,
            "linecolor": GRID,
            "ticks": "",
            "title": {"standoff": 15},
            "zerolinecolor": AXES2,
            "zerolinewidth": 2,
        },
        "yaxis": {
            "automargin": True,
            "gridcolor": AXES2,
            "linecolor": GRID,
            "ticks": "",
            "title": {"standoff": 15},
            "zerolinecolor": AXES2,
            "zerolinewidth": 2,
        },
    },
)

pio.templates.default = "catppuccin-mocha"
fig = px.scatter(
    df_2007,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="lifeExp",
    log_x=True,
    size_max=60,
    title="Gapminder 2007",
)
fig.show()
