import polars as pl
from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse

from app.db.session import SessionDep
from app.dependencies.specs.analysis import (
    AnalysisAggregate,
    AnalysisCalculate,
    AnalysisFilter,
    AnalysisJoin,
    FilterOperation,
    FilterPredicate,
    KindAnalysis,
)
from app.dependencies.specs.graph import KindNode
from app.dependencies.state import app_state
from app.dependencies.utils import UserDep
from app.middlewares.custom_logging import logger
from app.templates.renderer import render

router = APIRouter(
    prefix="/fragments",
    tags=["fragments"],
    dependencies=[],
)


@router.get("/modal", response_class=HTMLResponse)
async def get_modal_filter(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    node_subkind: str,
) -> HTMLResponse:
    logger.debug(f"Fetching fragment filter modal for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    user_files = g.get_nodes_by_kind(kind=KindNode.TABLE)

    try:
        node_subkind = KindAnalysis[node_subkind.upper()]
    except KeyError as e:
        raise ValueError(f"Failed to parse KindAnalysis: '{node_subkind}'") from e

    match node_subkind:
        case KindAnalysis.FILTER:
            node_data = AnalysisFilter.default()
        case KindAnalysis.CALCULATE:
            node_data = AnalysisCalculate.default()
        case KindAnalysis.AGGREGATE:
            node_data = AnalysisAggregate.default()
        case KindAnalysis.JOIN:
            node_data = AnalysisJoin.default()
    # title = f"New {node_subkind.value.title()} Node"

    return render(
        {
            "template_name": "fragment_modals.jinja",
            "context": {
                "request": request,
                "filter_ops": FilterOperation.list_all(),
                "files": user_files,
                "data": node_data,
            },
            "block_name": "modal_filter",
        },
    )


@router.get("/gc_filter_src", response_class=HTMLResponse)
async def update_dropdown(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    new_filter_src: str,
) -> HTMLResponse:
    logger.debug(f"Fetching fragment filter src dropdown for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    node_data = g.get_node_data(new_filter_src).data
    assert isinstance(node_data, pl.DataFrame)
    cols = node_data.columns

    pred = FilterPredicate.default()
    pred.col.options = cols

    return render(
        {
            "template_name": "fragment_modals.jinja",
            "context": {
                "request": request,
                "pred": pred,
            },
            "block_name": "gc_filter_src",
        },
    )


@router.get("/new_filter_predicate", response_class=HTMLResponse)
async def add_filter_pred_row(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    chosen_table_id: str,
) -> HTMLResponse:
    logger.debug(f"Fetching fragment predicate row for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    if len(chosen_table_id) == 0:
        cols = []
    else:
        node_data = g.get_node_data(chosen_table_id).data
        assert isinstance(node_data, pl.DataFrame)
        cols = node_data.columns

    pred = FilterPredicate.default()
    pred.col.options = cols

    return render(
        {
            "template_name": "fragment_modals.jinja",
            "context": {
                "request": request,
                "filter_ops": FilterOperation.list_all(),
                "pred": pred,
            },
            "block_name": "filter_pred_row",
        },
    )
