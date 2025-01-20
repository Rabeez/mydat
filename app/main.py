import plotly.io as pio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# TODO: export function and explicity call `register_theme()` in this file
import app.dependencies.chart_theme  # Register custom plotly theme
from app.dependencies.utils import (
    lifespan,
)
from app.middlewares.custom_logging import LogClientIPMiddleware
from app.routers import (
    charts,
    files,
    fragments,
    graph,
    pages,
    root,
)

pio.templates.default = "catppuccin-mocha"


application = FastAPI(
    title="MyDAT",
    lifespan=lifespan,
)
application.mount("/static", StaticFiles(directory="app/static"), name="static")
application.add_middleware(LogClientIPMiddleware)

application.include_router(root.router)
application.include_router(pages.router)
application.include_router(fragments.router)
application.include_router(files.router)
application.include_router(charts.router)
application.include_router(graph.router)


# TODO: add global exception handler to run `logger.error` and return ORJSONResponse with status and msg automatically to simplify application code
# app.add_exception_handler()
