from typing import Annotated

import fastapi
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse

from app.dependencies import (
    generate_table,
    get_user_id,
    make_table_html,
    templates,
    user_data,
)
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
        {
            "request": request,
            "userid": user_id,
            "files": user_data[user_id].files,
            "graph_json": {},
        },
    )


@router.get("/maintable", response_class=HTMLResponse)
async def get_page_maintable(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
) -> Response:
    # TODO: REMOVE ENDPOINT
    assert False
    main_df = user_data[user_id].main_file.df
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
    current_chart = user_data[user_id].charts[chart_idx]
    # TODO: Think of a way to avoid recreating this everytime
    chart_df = user_data[user_id].files[current_chart.file_idx].df
    fig = current_chart.data.make_fig(chart_df)

    chart_html: str = fig.to_html(full_html=False)

    return templates.TemplateResponse(
        request,
        "page_chart.jinja",
        {
            "request": request,
            "userid": user_id,
            "files": user_data[user_id].files,
            "chart": current_chart,
            "chart_file_idx": current_chart.file_idx,
            "chart_idx": chart_idx,
            "actual_chart": chart_html,
        },
    )
