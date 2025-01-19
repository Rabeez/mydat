import uuid
from dataclasses import asdict, dataclass, field
from enum import StrEnum, auto
from typing import Any

import networkx as nx
import polars as pl

from app.dependencies.specs.analysis import DataAnalysis, KindAnalysis
from app.dependencies.specs.chart import ChartKind, DataChart
from app.dependencies.specs.table import KindTable

# add node for table(name: str, kind: KindTable, data: pl.DataFrame) -> UUID
# add node for analysis(name: str, method: KindAnalysis, data: Analysis) -> UUID
# add node for chart(name: str, kind: KindChart, data: Chart) -> UUID

# find node (id: UUID) -> object | None

# update node data (id: UUID, data: <specific data obj based on node type>) -> None

# update node parent(id: UUID, new_parent: node) -> None
# ->> needed for changing source table of analysis/chart
# ->> should also trigger new default data value for this node using the new parent node
#     i.e. if source table of a filter changes it should be the default value (blank)
#     i.e. if source table of a chart changes it should get the `default` dimensions

# delete node(id: UUID) -> None
# ->> should cascade across ALL children (AND edges)


class KindNode(StrEnum):
    TABLE = auto()
    ANALYSIS = auto()
    CHART = auto()


SubkindNode = KindTable | KindAnalysis | ChartKind


# TODO: check if this class can be turned into a pydantic model directly
# idea is that the frontend sends JSON which can be marshalled into valid python object via FastAPI depends etc
# and this object can be send straight to the graph class to replace data attribute of a node
# Hypothetically on load etc same object can be returned by an API route and frontend will receive JSON for the cytoscape graph
@dataclass
class GraphNode:
    name: str
    kind: KindNode
    subkind: SubkindNode
    data: pl.DataFrame | DataAnalysis | DataChart

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
        del d["data"]
        return d


@dataclass
class Graph:
    data: nx.DiGraph = field(default_factory=nx.DiGraph)

    def __repr__(self) -> str:
        nodes_info = [
            f"{node}:{data['data'].kind}:{data['data'].subkind}"
            for node, data in self.data.nodes(data=True)
        ]
        return f"{self.__class__.__name__}(" + ", ".join(nodes_info) + ")"

    def to_json(self) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        nodes = [
            {
                "id": node,
                **data["data"].to_json(),
            }
            for node, data in self.data.nodes(data=True)
        ]
        edges = [
            {
                "source": src,
                "target": dst,
            }
            for src, dst in self.data.edges()
        ]
        return nodes, edges

    def to_cytoscape(self) -> dict:
        nodes, edges = self.to_json()
        d = {
            "nodes": [
                *[{"data": n} for n in nodes],
            ],
            "edges": [
                *[{"data": e} for e in edges],
            ],
        }
        return d

    def add_node(self, new_node: GraphNode) -> str:
        new_node_id = str(uuid.uuid4())
        self.data.add_node(new_node_id, data=new_node)
        return new_node_id

    def add_edge(self, src: str, dst: str) -> None:
        self.data.add_edge(src, dst)

    def get_node_data(self, node_id: str) -> GraphNode:
        return self.data.nodes[node_id]["data"]

    def get_parents(self, node_id: str) -> list[tuple[str, GraphNode]]:
        return [(p_id, self.data.nodes[p_id]["data"]) for p_id in self.data.predecessors(node_id)]

    def get_nodes_by_kind(
        self,
        kind: KindNode,
        subkind: SubkindNode | None = None,
    ) -> list[tuple[str, GraphNode]]:
        table_nodes = []
        for node, data in self.data.nodes(data=True):
            if (data["data"].kind == kind) and (subkind is None or data["data"].subkind == subkind):
                table_nodes.append((node, data["data"]))
        return table_nodes

    def delete_cascade(self, node_id: str) -> int:
        working_list = [node_id]
        c = 0
        while len(working_list):
            curr = working_list.pop(0)
            working_list.extend(self.data.successors(curr))
            self.data.remove_node(curr)
            c += 1
        return c
