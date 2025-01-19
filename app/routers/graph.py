from typing import Annotated

import fastapi
import polars as pl
from fastapi import APIRouter, Depends, Form, Response
from fastapi.responses import HTMLResponse, ORJSONResponse

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
    get_user_id,
)
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
    dependencies=[],
)


@router.get("/")
async def get_graph_data(
    user_id: Annotated[str, Depends(get_user_id)],
    db: SessionDep,
) -> Response:
    logger.debug(f"Fetching graph data for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    d = g.to_cytoscape()
    return ORJSONResponse(d)


@router.post("/create_filter_node")
async def create_filter_node(
    user_id: Annotated[str, Depends(get_user_id)],
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
    logger.warning(g)

    d = g.to_cytoscape()
    return ORJSONResponse(d)
