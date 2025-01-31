from typing import Annotated

import polars as pl
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, ORJSONResponse

from app.db.session import SessionDep
from app.dependencies.specs.analysis import (
    AnalysisAggregate,
    AnalysisCalculate,
    AnalysisFilter,
    AnalysisJoin,
    FilterOperation,
    FilterPredicate,
    KindAnalysis,
    TableCol,
)
from app.dependencies.specs.graph import GraphNode, KindNode
from app.dependencies.specs.table import KindTable
from app.dependencies.state import app_state
from app.dependencies.utils import UserDep, make_table_html
from app.middlewares.custom_logging import logger
from app.templates.renderer import render

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


@router.get("/view")
async def view_node(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    node_id: str,
    node_kind: str,
    node_subkind: str,
) -> HTMLResponse:
    logger.debug(f"Sending node {node_id} data for user {user_id}")

    # NOTE: triggers
    # - user clicks on graph node:
    #   - table, chart, analysis (each analysis subkind has different view)
    #     modal opens with appropriate read-only contents (table head for table, navigate to chart page, filter modal with data filled)
    # - user clicks on create node buttons:
    #   - analysis subkind buttons
    #     modal opens with "blank" contents
    #   - new chart button
    #     same as current (fixed modal triggered which is already in the HTML on startup)

    g = app_state.get_user_graph(user_id, db)

    try:
        node_kind = KindNode[node_kind.upper()]
    except KeyError as e:
        raise ValueError(f"Failed to parse KindNode: '{node_kind}'") from e

    match node_kind:
        case KindNode.TABLE:
            assert node_id != ""
            node_data = g.get_node_data(node_id).data
            assert isinstance(node_data, pl.DataFrame)
            table_html = make_table_html(node_data, f"tbl_{node_id}")
            logger.debug("sending table data")
            # TODO: setup a dummy table modal with similar look&feel to others
            return render(
                {
                    "template_name": "fragment_modals.jinja",
                    "context": {
                        "title": node_id,
                        "table_html": table_html,
                    },
                    "block_name": "modal_table",
                },
            )
        case KindNode.CHART:
            assert node_id != ""
            response = HTMLResponse(
                status_code=status.HTTP_200_OK,
                content="Redirecting to chart page",
            )
            response.headers["HX-Redirect"] = f"/pages/chart?chart_id={node_id}"
            logger.debug("sending chart redirect")
            return response
        case KindNode.ANALYSIS:
            assert node_id != ""
            node_data = g.get_node_data(node_id).data
            node_parent_id, _ = g.get_parents(node_id)[0]
            title = node_id
            logger.debug("sending existing analysis data")

            try:
                node_subkind = KindAnalysis[node_subkind.upper()]
            except KeyError as e:
                raise ValueError(f"Failed to parse KindAnalysis: '{node_subkind}'") from e

            template_block_name = f"modal_{node_subkind.value.lower()}"
            user_files = g.get_nodes_by_kind(kind=KindNode.TABLE)

            # TODO: pass `node_data` object directly to template
            return render(
                {
                    "template_name": "fragment_modals.jinja",
                    "context": {
                        "request": request,
                        "filter_ops": FilterOperation.list_all(),
                        "files": user_files,
                        "parent_id": node_parent_id,
                        "data": node_data,
                    },
                    "block_name": template_block_name,
                },
            )


@router.post("/create/filter")
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
