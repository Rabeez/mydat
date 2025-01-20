from typing import Annotated

import polars as pl
from fastapi import APIRouter, Form, Response
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
from app.dependencies.state import app_state
from app.dependencies.utils import (
    UserDep,
)
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
) -> Response:
    logger.debug(f"Fetching graph data for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    d = g.to_cytoscape()
    return ORJSONResponse(d)


@router.post("/delete")
async def delete_node(
    user_id: UserDep,
    db: SessionDep,
    node_id: Annotated[str, Form()],
) -> Response:
    logger.debug(f"Deleting node {node_id} for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    n_deleted = g.delete_cascade(node_id)

    return ORJSONResponse({"message": f"Total nodes deleted: {n_deleted}"})


@router.post("/create_filter_node")
async def create_filter_node(
    user_id: UserDep,
    db: SessionDep,
    new_filter_src: Annotated[str, Form()],
    gc_filter_src: Annotated[str, Form()],
    new_filter_op: Annotated[str, Form()],
    new_filter_comp: Annotated[str, Form()],
) -> Response:
    logger.debug(f"Fetching graph data for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    src_node_data = g.get_node_data(new_filter_src)
    assert isinstance(src_node_data.data, pl.DataFrame)

    # TODO: implement proper logic to differentiate filter ops based on src col type
    # also convert the new_filter_comp to the correct type before comparison
    comp_val = float(new_filter_comp)
    filter_node_id = g.add_node(
        GraphNode(
            # TODO: pretty bad naming scheme
            name=f"{src_node_data.name}_filter_{gc_filter_src}",
            kind=KindNode.ANALYSIS,
            subkind=KindAnalysis.FILTER,
            data=AnalysisFilter(
                [
                    FilterPredicate(
                        TableCol(gc_filter_src, src_node_data.data.columns),
                        FilterOperation.from_string(new_filter_op),
                        comp_val,
                    ),
                ],
            ),
        ),
    )
    g.add_edge(new_filter_src, filter_node_id)
    # TODO: create result of filter as CALCULATED table and relevant edge
    logger.warning(g)

    d = g.to_cytoscape()
    return ORJSONResponse(d)
