from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse

from app.db.session import SessionDep
from app.dependencies.specs.chart import get_available_chart_kinds
from app.dependencies.specs.graph import KindNode
from app.dependencies.state import app_state
from app.dependencies.utils import UserDep
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

    # TODO: define typed-dict for every .jinja file and use those for all places where rendering is done
    # this is to ensure that it's easy to be correct from python side and not miss things that are needed in the template
    return render(
        {
            "template_name": "base.jinja",
            "context": {
                "request": request,
                "files": user_files,
                "chart_kinds": chart_kinds,
                "charts": user_charts,
                "graph_json": g.to_cytoscape(),
            },
        },
    )
