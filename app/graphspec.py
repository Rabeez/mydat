from __future__ import annotations  # Enables forward references

from dataclasses import asdict, dataclass
from enum import StrEnum, auto, unique


@dataclass
class Node:
    id: str
    name: str
    parent: list[Node]
    child: list[Node]


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


def node2dict(n: Node) -> dict[str, str]:
    d = asdict(n)
    del d["parent"]
    del d["child"]
    if isinstance(n, AnalysisNode):
        d["method"] = d["method"].value
    return d
