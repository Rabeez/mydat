from dataclasses import asdict, dataclass
from enum import StrEnum, auto, unique
from typing import Any, Callable

import polars as pl


@unique
class ChartKind(StrEnum):
    SCATTER = auto()
    BAR = auto()
    HEATMAP = auto()
    HISTOGRAM = auto()


@dataclass
class ChartScatter:
    """Basic scatter chart."""

    x: str
    y: str
    color: str | None = None
    size: str | None = None
    symbol: str | None = None


@dataclass
class ChartBar:
    """Basic bar chart with aggregated values on y-axis."""

    x: str
    y: str | None = None
    color: str | None = None
    _agg_func: Callable = pl.len


@dataclass
class ChartHistogram:
    """Basic histogram to show uni-variate distribution."""

    x: str
    color: str | None = None


@dataclass
class ChartHeatmap:
    """Basic hatmap/matrix chart with optional cell annotation."""

    x: str
    y: str
    _z: str
    _agg_func: Callable = pl.mean
    annotate: bool = False


Chart = ChartScatter | ChartBar | ChartHistogram | ChartHeatmap


def spec2dict(spec: Chart) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
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
