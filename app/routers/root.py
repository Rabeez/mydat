from typing import Annotated

import plotly.io as pio
from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse, HTMLResponse

from app.db.session import SessionDep
from app.dependencies.chart_theme import register_custom_theme
from app.dependencies.specs.analysis import FilterOperation
from app.dependencies.specs.chart import get_available_chart_kinds
from app.dependencies.specs.graph import KindNode
from app.dependencies.state import app_state
from app.dependencies.utils import Theme, UserDep
from app.middlewares.custom_logging import logger
from app.templates.renderer import render

router = APIRouter(
    tags=["root"],
    dependencies=[],
)


@router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse("app/assets/favicon.ico")


@router.get("/", response_class=HTMLResponse)
async def get_homepage(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
) -> HTMLResponse:
    g = app_state.get_user_graph(user_id, db)
    user_files = g.get_nodes_by_kind(kind=KindNode.TABLE)

    logger.debug(f"User identified: {user_id} with {len(user_files)} existing files")
    logger.warning(g)

    chart_kinds = get_available_chart_kinds()
    user_charts = g.get_nodes_by_kind(kind=KindNode.CHART)

    theme = Theme.DARK
    pio.templates.default = register_custom_theme(theme.value)

    return render(
        {
            "template_name": "base.jinja",
            "context": {
                "request": request,
                "theme": theme,
                "files": user_files,
                "filter_ops": [op.value for op in FilterOperation],
                "chart_kinds": chart_kinds,
                "charts": user_charts,
                "graph_json": g.to_cytoscape(),
            },
        },
    )


@router.post("/toggle_ui_mode", response_class=HTMLResponse)
async def change_ui_mode(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    theme_controller: Annotated[bool, Form()],
) -> HTMLResponse:
    g = app_state.get_user_graph(user_id, db)
    user_files = g.get_nodes_by_kind(kind=KindNode.TABLE)

    logger.debug(f"User identified: {user_id} with {len(user_files)} existing files")
    logger.warning(g)

    chart_kinds = get_available_chart_kinds()
    user_charts = g.get_nodes_by_kind(kind=KindNode.CHART)
    logger.warning(len(user_charts))

    theme = Theme.LIGHT if theme_controller else Theme.DARK
    pio.templates.default = register_custom_theme(theme.value)
    logger.warning(theme)

    x = render(
        {
            "template_name": "base.jinja",
            "context": {
                "request": request,
                "theme": theme,
                "files": user_files,
                "filter_ops": [op.value for op in FilterOperation],
                "chart_kinds": chart_kinds,
                "charts": user_charts,
                "graph_json": g.to_cytoscape(),
            },
            "block_name": "screen_container",
        },
    )
    return x
