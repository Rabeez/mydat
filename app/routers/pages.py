from typing import Annotated

import fastapi
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse

from app.dependencies import (
    generate_table,
    get_user_id,
    make_table_html,
    templates,
)
from app.main import user_data
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/pages",
    tags=["pages"],
    dependencies=[],
)


@router.get("/files", response_class=HTMLResponse)
async def get_page_files(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
) -> Response:
    user_files = user_data[user_id].files
    table_html = generate_table(
        "files-table",
        ["Name", "File", "Filesize"],
        [[f.name, f.filename, f.filesize] for f in user_files],
        [
            {"text": "Rename", "endpoint": "/file_rename"},
            {"text": "Delete", "endpoint": "/file_delete"},
        ],
    )

    return templates.TemplateResponse(
        request,
        "page_files.jinja",
        {"request": request, "userid": user_id, "files_table": table_html},
    )


@router.get("/types", response_class=HTMLResponse)
async def get_page_types(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
) -> Response:
    return templates.TemplateResponse(
        request,
        "page_types.jinja",
        {"request": request, "userid": user_id, "files": user_data[user_id].files},
    )


@router.get("/relationships", response_class=HTMLResponse)
async def get_page_relationships(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
) -> Response:
    return templates.TemplateResponse(
        request,
        "page_relationships.jinja",
        {"request": request, "userid": user_id, "files": user_data[user_id].files},
    )


@router.get("/maintable", response_class=HTMLResponse)
async def get_page_maintable(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
) -> Response:
    if (idx := user_data[user_id].main_file_idx) is None:
        logger.error("Main file index not set")
        raise HTTPException(fastapi.status.HTTP_400_BAD_REQUEST, "Main file index not set")

    main_df = user_data[user_id].files[idx].df
    table_html = make_table_html(main_df.head(20), "main-table")
    return templates.TemplateResponse(
        request,
        "page_maintable.jinja",
        {"request": request, "userid": user_id, "main_table_html": table_html},
    )


@router.get("/chart", response_class=HTMLResponse)
async def get_chart_page(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
    chart_idx: int,
) -> Response:
    main_df = user_data[user_id].main_file.df
    current_chart = user_data[user_id].charts[chart_idx]
    # TODO: Think of a way to avoid recreating this everytime
    fig = current_chart.data.make_fig(main_df)

    chart_html: str = fig.to_html(full_html=False)

    return templates.TemplateResponse(
        request,
        "page_chart.jinja",
        {
            "request": request,
            "userid": user_id,
            "chart": current_chart,
            "chart_idx": chart_idx,
            "actual_chart": chart_html,
        },
    )
