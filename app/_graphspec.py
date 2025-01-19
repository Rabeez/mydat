from __future__ import annotations  # Enables forward references

from dataclasses import asdict, dataclass
from enum import StrEnum, auto, unique
from typing import Self

from app.middlewares.custom_logging import logger


@dataclass
class Node:
    id: str
    parent_idx: list[int]
    child_idx: list[int]


@dataclass
class DataNode(Node):
    pass


@unique
class AnalysisMethod(StrEnum):
    FILTER = auto()
    CALCULATE = auto()
    AGGREGATE = auto()
    JOIN = auto()


@dataclass
class AnalysisNode(Node):
    method: AnalysisMethod


Graph = list[Node]


def find_node(g: Graph, nid: str) -> tuple[int, Node] | None:
    for i, n in enumerate(g):
        if n.id == nid:
            return i, n
    return None


def generate_edges(g: Graph) -> list[dict[str, str]]:
    # {"source": "table1", "target": "filter1"}
    e = []
    for n in g:
        e.extend(
            [
                {
                    "source": g[par_idx].id,
                    "target": n.id,
                }
                for par_idx in n.parent_idx
            ],
        )
        # e.extend(
        #     [
        #         {
        #             "source": n.id,
        #             "target": g[child_idx].id,
        #         }
        #         for child_idx in n.child_idx
        #     ],
        # )
    return e


@unique
class FilterOps(StrEnum):
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    EQ = "=="
    NE = "!="

    @classmethod
    def from_string(cls, value: str) -> Self:
        for label in cls:
            if label.value == value:
                return label
        raise ValueError(f"Could not convert '{value}' to instance of `{Self}`")


def node2dict(n: Node) -> dict[str, str]:
    try:
        d = asdict(n)
    except Exception as e:
        logger.error(str(e))
        logger.error(n)
        raise ValueError from None
    else:
        d["name"] = d["id"]  # NOTE: for text labels in graph
        d["kind"] = "data"
        if isinstance(n, AnalysisNode):
            d["kind"] = "analysis"
            d["method"] = d["method"].value
        return d
