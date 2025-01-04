import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import polars as pl

gapminder = pl.DataFrame(px.data.gapminder())
df_2007 = gapminder.filter(pl.col("year") == 2007)


pio.templates["draft"] = go.layout.Template(
    layout={
        "annotationdefaults": {"arrowcolor": "#f2f5fa", "arrowhead": 0, "arrowwidth": 1},
        "autotypenumbers": "strict",
        "coloraxis": {"colorbar": {"outlinewidth": 0, "ticks": ""}},
        "colorscale": {
            "diverging": [
                [0, "#8e0152"],
                [0.1, "#c51b7d"],
                [0.2, "#de77ae"],
                [0.3, "#f1b6da"],
                [0.4, "#fde0ef"],
                [0.5, "#f7f7f7"],
                [0.6, "#e6f5d0"],
                [0.7, "#b8e186"],
                [0.8, "#7fbc41"],
                [0.9, "#4d9221"],
                [1, "#276419"],
            ],
            "sequential": [
                [0.0, "#0d0887"],
                [0.1111111111111111, "#46039f"],
                [0.2222222222222222, "#7201a8"],
                [0.3333333333333333, "#9c179e"],
                [0.4444444444444444, "#bd3786"],
                [0.5555555555555556, "#d8576b"],
                [0.6666666666666666, "#ed7953"],
                [0.7777777777777778, "#fb9f3a"],
                [0.8888888888888888, "#fdca26"],
                [1.0, "#f0f921"],
            ],
            "sequentialminus": [
                [0.0, "#0d0887"],
                [0.1111111111111111, "#46039f"],
                [0.2222222222222222, "#7201a8"],
                [0.3333333333333333, "#9c179e"],
                [0.4444444444444444, "#bd3786"],
                [0.5555555555555556, "#d8576b"],
                [0.6666666666666666, "#ed7953"],
                [0.7777777777777778, "#fb9f3a"],
                [0.8888888888888888, "#fdca26"],
                [1.0, "#f0f921"],
            ],
        },
        "colorway": [
            "#636efa",
            "#EF553B",
            "#00cc96",
            "#ab63fa",
            "#FFA15A",
            "#19d3f3",
            "#FF6692",
            "#B6E880",
            "#FF97FF",
            "#FECB52",
        ],
        "font": {"color": "#f2f5fa"},
        "geo": {
            "bgcolor": "rgb(17,17,17)",
            "lakecolor": "rgb(17,17,17)",
            "landcolor": "rgb(17,17,17)",
            "showlakes": True,
            "showland": True,
            "subunitcolor": "#506784",
        },
        "hoverlabel": {"align": "left"},
        "hovermode": "closest",
        "mapbox": {"style": "dark"},
        "paper_bgcolor": "rgb(255,0,0)",
        "plot_bgcolor": "rgb(17,17,17)",
        "polar": {
            "angularaxis": {"gridcolor": "#506784", "linecolor": "#506784", "ticks": ""},
            "bgcolor": "rgb(17,17,17)",
            "radialaxis": {"gridcolor": "#506784", "linecolor": "#506784", "ticks": ""},
        },
        "scene": {
            "xaxis": {
                "backgroundcolor": "rgb(17,17,17)",
                "gridcolor": "#506784",
                "gridwidth": 2,
                "linecolor": "#506784",
                "showbackground": True,
                "ticks": "",
                "zerolinecolor": "#C8D4E3",
            },
            "yaxis": {
                "backgroundcolor": "rgb(17,17,17)",
                "gridcolor": "#506784",
                "gridwidth": 2,
                "linecolor": "#506784",
                "showbackground": True,
                "ticks": "",
                "zerolinecolor": "#C8D4E3",
            },
            "zaxis": {
                "backgroundcolor": "rgb(17,17,17)",
                "gridcolor": "#506784",
                "gridwidth": 2,
                "linecolor": "#506784",
                "showbackground": True,
                "ticks": "",
                "zerolinecolor": "#C8D4E3",
            },
        },
        "shapedefaults": {"line": {"color": "#f2f5fa"}},
        "sliderdefaults": {
            "bgcolor": "#C8D4E3",
            "bordercolor": "rgb(17,17,17)",
            "borderwidth": 1,
            "tickwidth": 0,
        },
        "ternary": {
            "aaxis": {"gridcolor": "#506784", "linecolor": "#506784", "ticks": ""},
            "baxis": {"gridcolor": "#506784", "linecolor": "#506784", "ticks": ""},
            "bgcolor": "rgb(17,17,17)",
            "caxis": {"gridcolor": "#506784", "linecolor": "#506784", "ticks": ""},
        },
        "title": {"x": 0.05},
        "updatemenudefaults": {"bgcolor": "#506784", "borderwidth": 0},
        "xaxis": {
            "automargin": True,
            "gridcolor": "#283442",
            "linecolor": "#506784",
            "ticks": "",
            "title": {"standoff": 15},
            "zerolinecolor": "#283442",
            "zerolinewidth": 2,
        },
        "yaxis": {
            "automargin": True,
            "gridcolor": "#283442",
            "linecolor": "#506784",
            "ticks": "",
            "title": {"standoff": 15},
            "zerolinecolor": "#283442",
            "zerolinewidth": 2,
        },
    },
)

pio.templates.default = "draft"
fig = px.scatter(
    df_2007,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    log_x=True,
    size_max=60,
    title="Gapminder 2007",
)
fig.show()
