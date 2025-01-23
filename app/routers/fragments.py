from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.db.session import SessionDep
from app.dependencies.specs.analysis import FilterOperation
from app.dependencies.state import app_state
from app.dependencies.utils import UserDep
from app.middlewares.custom_logging import logger
from app.templates.renderer import render

router = APIRouter(
    prefix="/fragments",
    tags=["fragments"],
    dependencies=[],
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
    cols = g.data.nodes[new_filter_src]["data"].data.columns

    return render(
        {
            "template_name": "page_dataflow.jinja",
            "context": {
                "request": request,
                "gc_filter_src": cols,
            },
            "block_name": "gc_filter_src",
        },
    )


@router.get("/new_filter_predicate", response_class=HTMLResponse)
async def add_filter_pred_row(
    request: Request,
    user_id: UserDep,
) -> HTMLResponse:
    logger.debug(f"Fetching fragment predicate row for user {user_id}")

    return render(
        {
            "template_name": "page_dataflow.jinja",
            "context": {
                "request": request,
                "filter_ops": [op.value for op in FilterOperation],
            },
            "block_name": "filter_pred_row",
        },
    )
