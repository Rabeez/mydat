from dataclasses import dataclass
from enum import StrEnum, auto, unique
from typing import Any, Callable, Self

import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import polars.selectors as cs


@unique
class ChartKind(StrEnum):
    SCATTER = auto()
    BAR = auto()
    HEATMAP = auto()
    HISTOGRAM = auto()


@dataclass
class DimensionValue:
    selected: str
    options: list[str]
    mandatory: bool

    @classmethod
    def from_list(cls, l: list[str], init: int | None = None) -> Self:
        # Note: `init=None` implies that this is an optional field
        # e.g. color for a scatter plot
        if init is None:
            none_val = ""
            return cls(none_val, [*l, none_val], mandatory=False)
        return cls(l[init], l, mandatory=True)

    def current(self) -> str | None:
        return self.selected if self.selected != "" else None


@dataclass
class ChartScatter:
    """Basic scatter chart."""

    x: DimensionValue
    y: DimensionValue
    color: DimensionValue
    size: DimensionValue
    symbol: DimensionValue

    def make_fig(self, df: pl.DataFrame) -> go.Figure:
        fig = px.scatter(
            df,
            x=self.x.current(),
            y=self.y.current(),
            color=self.color.current(),
            size=self.size.current(),
            symbol=self.symbol.current(),
        )
        return fig


@dataclass
class ChartBar:
    """Basic bar chart with aggregated values on y-axis."""

    # TODO: this needs rethinking, y and agg-func need to both be either not-null or null
    # len only makes sense without y
    # ANY other aggfunc only makes sense with a y (in which case default `mean` makes sense, consistent with heatmap)
    x: DimensionValue
    y: DimensionValue
    color: DimensionValue
    _agg_func: Callable = pl.len

    def make_fig(self, df: pl.DataFrame) -> go.Figure:
        gs = [self.x.current()]
        if self.color.current() is not None:
            gs.append(self.color.current())
        df_agg = df.group_by(gs).agg(self._agg_func().alias("Y"))
        fig = px.bar(
            df_agg,
            x=self.x.current(),
            y="Y",
            color=self.color.current(),
        )
        return fig


@dataclass
class ChartHistogram:
    """Basic histogram to show uni-variate distribution."""

    x: DimensionValue
    color: DimensionValue

    def make_fig(self, df: pl.DataFrame) -> go.Figure:
        # TODO: Incorporate color
        fig = px.histogram(
            df,
            x=self.x.current(),
        )
        return fig


@dataclass
class ChartHeatmap:
    """Basic hatmap/matrix chart with optional cell annotation."""

    x: DimensionValue
    y: DimensionValue
    _z: DimensionValue
    _agg_func: Callable = pl.mean
    annotate: bool = False

    def make_fig(self, df: pl.DataFrame) -> go.Figure:
        # TODO: Incorporate color
        # ALSO rename _z to color?
        _x = self.x.current()
        assert _x is not None
        mat = (
            df.group_by(
                self.x.current(),
                self.y.current(),
            )
            .agg(self._agg_func(self._z.current()))
            .pivot(
                on=_x,
                index=self.y.current(),
                values=self._z.current(),
            )
            .drop(cs.by_index(0))
            .to_numpy()
        )

        fig = px.imshow(
            mat,
            labels={
                "x": self.x.current(),
                "y": self.y.current(),
                "color": self._z.current(),
            },
            x=df.select(self.x.current()).to_series().unique().to_list(),
            y=df.select(self.y.current()).to_series().unique().to_list(),
            text_auto=self.annotate,
        )
        return fig


Chart = ChartScatter | ChartBar | ChartHistogram | ChartHeatmap


def get_available_chart_kinds() -> list[dict[str, Any]]:
    chart_specifications = [
        {
            "name": e.__name__.replace("Chart", ""),
            "description": e.__doc__,
            "dimensions": [
                {
                    "name": n,
                    "is_optional": False,
                }
                for n, _ in e.__annotations__.items()
            ],
        }
        for e in Chart.__args__
    ]
    # NOTE: Alphabetical order for cards in modal
    chart_specifications = sorted(chart_specifications, key=lambda x: x["name"])
    return chart_specifications
