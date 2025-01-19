from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse

from app.db.session import SessionDep
from app.dependencies.state import app_state
from app.dependencies.utils import (
    UserDep,
    templates,
)
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/fragments",
    tags=["fragments"],
    dependencies=[],
)


@router.get("/gc_filter_src", response_class=HTMLResponse)
async def update_dropdown(
    user_id: UserDep,
    db: SessionDep,
    new_filter_src: str,
) -> Response:
    logger.debug(f"Fetching fragment filter src dropdown for user {user_id}")

    g = app_state.get_user_graph(user_id, db)
    cols = g.data.nodes[new_filter_src]["data"].data.columns

    return templates.get_template("fragment_gc_filter_src.jinja").render(
        {
            "gc_filter_src": cols,
        },
    )
