from typing import Annotated

import plotly.io as pio
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse

import app.chart_theme
from app.chartspec import get_available_chart_kinds
from app.dependencies import (
    generate_table,
    get_user_id,
    templates,
    user_data,
)
from app.middlewares.custom_logging import LogClientIPMiddleware, logger
from app.routers import (
    charts,
    files,
    fragments,
    pages,
)

pio.templates.default = "catppuccin-mocha"

app = FastAPI()
app.add_middleware(LogClientIPMiddleware)
app.include_router(pages.router)
app.include_router(fragments.router)
app.include_router(files.router)
app.include_router(charts.router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return FileResponse("app/assets/favicon.ico")


@app.get("/", response_class=HTMLResponse)
async def get_homepage(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
) -> Response:
    user_files = user_data[user_id].files
    logger.debug(f"User identified: {user_id} with {len(user_files)} existing files")

    table_html = generate_table(
        "files-table",
        ["Name", "File", "Filesize"],
        [[f.name, f.filename, f.filesize] for f in user_files],
        [
            {"text": "Rename", "endpoint": "/file_rename"},
            {"text": "Delete", "endpoint": "/file_delete"},
        ],
    )

    chart_kinds = get_available_chart_kinds()

    return templates.TemplateResponse(
        request,
        "base.jinja",
        {
            "request": request,
            "userid": user_id,
            "chart_kinds": chart_kinds,
            "files_table": table_html,
            "charts": user_data[user_id].charts,
        },
    )
