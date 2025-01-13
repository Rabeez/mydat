from __future__ import annotations  # Enables forward references

from dataclasses import asdict, dataclass
from enum import StrEnum, auto, unique
from typing import Any, Callable, Self


@unique
class NodeKind(StrEnum):
    DATA = auto()
    ANALYSIS = auto()


@unique
class AnalysisMethod(StrEnum):
    FILTER = auto()
    CALCULATE = auto()
    AGGREGATE = auto()
    JOIN = auto()


@dataclass
class Node:
    id: str
    kind: NodeKind
    method: AnalysisMethod | None
    name: str

    parent: list[Node] | None = None
    child: Node | None = None


Graph = list[Node]


def node2dict(n: Node) -> dict[str, str]:
    d = asdict(n)
    d["kind"] = d["kind"].value
    del d["parent"]
    del d["child"]
    return d
