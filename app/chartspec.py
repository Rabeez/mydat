from dataclasses import asdict, dataclass
from enum import StrEnum, auto, unique
from typing import Any, Callable, NamedTuple, Self

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


class DimensionValue(NamedTuple):
    selected: str
    options: list[Any]

    @classmethod
    def from_list(cls, l: list[str], init: int = 0) -> Self:
        return cls(l[init], l)


@dataclass
class ChartScatter:
    """Basic scatter chart."""

    x: DimensionValue
    y: DimensionValue
    color: DimensionValue | None = None
    size: DimensionValue | None = None
    symbol: DimensionValue | None = None

    def make_fig(self, df: pl.DataFrame) -> go.Figure:
        # TODO: Incorporate color, size, symbol
        fig = px.scatter(
            df,
            x=self.x.selected,
            y=self.y.selected,
        )
        return fig


@dataclass
class ChartBar:
    """Basic bar chart with aggregated values on y-axis."""

    x: DimensionValue
    y: DimensionValue | None = None
    color: DimensionValue | None = None
    _agg_func: Callable = pl.len

    def make_fig(self, df: pl.DataFrame) -> go.Figure:
        # TODO: Incorporate color
        df_agg = df.group_by(self.x.selected).agg(self._agg_func().alias("Y"))
        fig = px.bar(
            df_agg,
            x=self.x.selected,
            y="Y",
        )
        return fig


@dataclass
class ChartHistogram:
    """Basic histogram to show uni-variate distribution."""

    x: DimensionValue
    color: DimensionValue | None = None

    def make_fig(self, df: pl.DataFrame) -> go.Figure:
        # TODO: Incorporate color
        fig = px.histogram(
            df,
            x=self.x.selected,
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
        mat = (
            df.group_by(
                self.x.selected,
                self.y.selected,
            )
            .agg(self._agg_func(self._z.selected))
            .pivot(
                on=self.x.selected,
                index=self.y.selected,
                values=self._z.selected,
            )
            .drop(cs.by_index(0))
            .to_numpy()
        )

        fig = px.imshow(
            mat,
            labels={
                "x": self.x.selected,
                "y": self.y.selected,
                "color": self._z.selected,
            },
            x=df.select(self.x.selected).to_series().unique().to_list(),
            y=df.select(self.y.selected).to_series().unique().to_list(),
            text_auto=self.annotate,
        )
        return fig


Chart = ChartScatter | ChartBar | ChartHistogram | ChartHeatmap


def spec2dict(spec: Chart) -> dict[str, Any]:
    """Convert chart specification dataclass to a dictionary.

    This is so the dict can be passed to plotting functions with **kwargs pattern.
    Key idea is that specs can have 'internal' attributes that start with underscore.
    These could be used in data pre-processing but are not needed for plotting function
    and are therefore removed from auto-generated dictionary.
    Also, any 'unset' attributes are skipped.
    """
    config_d = asdict(spec)
    to_del = [k for k, v in config_d.items() if k.startswith("_") or v is None]
    for k in to_del:
        del config_d[k]
    return config_d
