from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.dependencies.utils import lifespan
from app.middlewares.custom_logging import LogClientIPMiddleware, LogExceptionMiddleware
from app.routers import (
    charts,
    files,
    fragments,
    graph,
    pages,
    root,
)

# TODO: Use config file for constants (e.g. app name) and use that here
# also pass these to templates (e.g. app name, default theme etc)
application = FastAPI(
    title="MyDAT",
    lifespan=lifespan,
)
application.mount("/static", StaticFiles(directory="app/static"), name="static")
application.add_middleware(LogExceptionMiddleware)
application.add_middleware(LogClientIPMiddleware)
application.include_router(root.router)
application.include_router(pages.router)
application.include_router(fragments.router)
application.include_router(files.router)
application.include_router(charts.router)
application.include_router(graph.router)
