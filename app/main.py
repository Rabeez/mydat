from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import plotly.io as pio
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

import app.dependencies.chart_theme  # Register custom plotly theme
from app.db.session import SessionDep, create_db_and_tables, get_db_context
from app.dependencies.specs.chart import get_available_chart_kinds
from app.dependencies.specs.graph import KindNode
from app.dependencies.state import app_state
from app.dependencies.utils import (
    UserDep,
    templates,
)
from app.middlewares.custom_logging import LogClientIPMiddleware, logger
from app.routers import (
    charts,
    files,
    fragments,
    graph,
    pages,
)

pio.templates.default = "catppuccin-mocha"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    try:
        yield
    finally:
        with get_db_context() as db:
            app_state.persist_all_to_db(db)


app = FastAPI(
    title="MyDAT",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(LogClientIPMiddleware)

app.include_router(pages.router)
app.include_router(fragments.router)
app.include_router(files.router)
app.include_router(charts.router)
app.include_router(graph.router)


# TODO: add global exception handler to run `logger.error` and return ORJSONResponse with status and msg automatically to simplify application code
# app.add_exception_handler()


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return FileResponse("app/assets/favicon.ico")


@app.get("/", response_class=HTMLResponse)
async def get_homepage(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
) -> Response:
    g = app_state.get_user_graph(user_id, db)
    user_files = g.get_nodes_by_kind(kind=KindNode.TABLE)

    logger.debug(f"User identified: {user_id} with {len(user_files)} existing files")
    logger.warning(g)

    chart_kinds = get_available_chart_kinds()
    user_charts = g.get_nodes_by_kind(kind=KindNode.CHART)

    # TODO: define typed-dict for every .jinja file and use those for all places where rendering is done
    # this is to ensure that it's easy to be correct from python side and not miss things that are needed in the template
    return templates.TemplateResponse(
        request,
        "base.jinja",
        {
            "request": request,
            "userid": user_id,
            "files": user_files,
            "chart_kinds": chart_kinds,
            "charts": user_charts,
            "graph_json": g.to_cytoscape(),
        },
    )
