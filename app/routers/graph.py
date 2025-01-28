from typing import Annotated

import polars as pl
from fastapi import APIRouter, Form
from fastapi.responses import ORJSONResponse

from app.db.session import SessionDep
from app.dependencies.specs.analysis import (
    AnalysisFilter,
    FilterOperation,
    FilterPredicate,
    KindAnalysis,
    TableCol,
)
from app.dependencies.specs.graph import GraphNode, KindNode
from app.dependencies.specs.table import KindTable
from app.dependencies.state import app_state
from app.dependencies.utils import UserDep
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
    dependencies=[],
)


@router.get("/")
async def get_graph_data(
    user_id: UserDep,
    db: SessionDep,
) -> ORJSONResponse:
    logger.debug(f"Fetching graph data for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    d = g.to_cytoscape()
    return ORJSONResponse(d)


@router.post("/delete")
async def delete_node(
    user_id: UserDep,
    db: SessionDep,
    node_id: Annotated[str, Form()],
) -> ORJSONResponse:
    logger.debug(f"Deleting node {node_id} for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    n_deleted = g.delete_cascade(node_id)

    # TODO: return HTML response to update sidebar list if a chart was deleted

    return ORJSONResponse({"message": f"Total nodes deleted: {n_deleted}"})


@router.post("/create_filter_node")
async def create_filter_node(
    user_id: UserDep,
    db: SessionDep,
    new_filter_src: Annotated[str, Form()],
    gc_filter_src: Annotated[list[str], Form()],
    new_filter_op: Annotated[list[str], Form()],
    new_filter_comp: Annotated[list[str], Form()],
) -> ORJSONResponse:
    logger.debug(f"Fetching graph data for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    src_node_data = g.get_node_data(new_filter_src)
    assert isinstance(src_node_data.data, pl.DataFrame)

    # TODO: implement proper logic to differentiate filter ops based on src col type
    # also convert the `new_filter_comp[]` to the correct type in `val` before comparison
    preds = [
        FilterPredicate(
            TableCol(col, src_node_data.data.columns),
            FilterOperation.from_string(op),
            float(val),
        )
        for col, op, val in zip(gc_filter_src, new_filter_op, new_filter_comp)
    ]
    analysis_op = AnalysisFilter(preds)
    # TODO: pretty bad naming scheme (converts cols array intro raw string)
    filter_node_name = f"{src_node_data.name}_filter_{gc_filter_src}"
    filter_node_id = g.add_node(
        GraphNode(
            name=filter_node_name,
            kind=KindNode.ANALYSIS,
            subkind=KindAnalysis.FILTER,
            data=analysis_op,
        ),
    )
    g.add_edge(new_filter_src, filter_node_id)

    filtered_df = analysis_op.apply(src_node_data.data)
    result_node_id = g.add_node(
        GraphNode(
            name=f"{filter_node_name}_result",
            kind=KindNode.TABLE,
            subkind=KindTable.CALCULATED,
            data=filtered_df,
        ),
    )
    g.add_edge(filter_node_id, result_node_id)

    logger.warning(g)

    d = g.to_cytoscape()
    return ORJSONResponse(d)
