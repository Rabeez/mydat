import io
import os
import uuid
from collections import defaultdict
from collections.abc import Awaitable
from typing import Annotated, Callable, NamedTuple

import fastapi
import pandas as pd
from fastapi import Depends, FastAPI, Form, Request, Response, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .middlewares.custom_logging import logger

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


class FileDetails(NamedTuple):
    name: str
    filename: str
    filesize: int
    df: pd.DataFrame


class ChartDetails(NamedTuple):
    name: str


class UserData(NamedTuple):
    files: list[FileDetails]
    charts: list[ChartDetails]


user_data: dict[str, UserData] = defaultdict(lambda: UserData([], []))


def get_user_files(user_id: str) -> pd.DataFrame:
    col_names = ["Name", "Filename", "Size", ""]
    file_listing_df = pd.DataFrame(
        index=range(len(user_data[user_id].files)), columns=col_names
    )
    delete_col_text = "<a>Delete</a>"
    for i, fd in enumerate(user_data[user_id].files):
        file_listing_df.iloc[i, :] = [  # pyright: ignore [reportArgumentType]
            fd.name,
            fd.filename,
            fd.filesize,
            delete_col_text,
        ]
    return file_listing_df


def make_table_html(df: pd.DataFrame, html_id: str) -> str:
    return df.to_html(
        header=True,
        index=True,
        index_names=False,
        bold_rows=False,
        border=0,
        justify="left",
        table_id=html_id,
        classes="table table-xs table-pin-rows",
    )


def get_user_id(request: Request, response: Response) -> str:
    cookie_name = "user_id"
    user_id = request.cookies.get(cookie_name)
    if not user_id:
        user_id = str(uuid.uuid4())
        response.set_cookie(key=cookie_name, value=user_id, httponly=True)
    return user_id


@app.middleware("http")
async def log_client_ip(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    if not request.client:
        return
    client_host, client_port = request.client.host, request.client.port
    logger.info(f"Got a request from {client_host}:{client_port}")
    response = await call_next(request)  # Continue to the actual route handler
    return response


@app.get("/", response_class=HTMLResponse)
async def get_homepage(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    file_listing_df = get_user_files(user_id)
    logger.debug(
        f"User identified: {user_id} with {len(file_listing_df)} existing files"
    )
    table_html = make_table_html(file_listing_df, "files-table")

    return templates.TemplateResponse(
        request,
        "base_1.html",
        {
            "request": request,
            "username": user_id,
            "files_table": table_html,
            "charts": user_data[user_id].charts,
        },
    )


@app.get("/page_files", response_class=HTMLResponse)
async def get_page_files(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    file_listing_df = get_user_files(user_id)
    table_html = make_table_html(file_listing_df, "files-table")

    return templates.TemplateResponse(
        request,
        "page_files.html",
        {"request": request, "username": user_id, "files_table": table_html},
    )


@app.get("/page_types", response_class=HTMLResponse)
async def get_page_types(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    return templates.TemplateResponse(
        request,
        "page_types.html",
        {"request": request, "username": user_id, "files": user_data[user_id].files},
    )


@app.get("/page_relationships", response_class=HTMLResponse)
async def get_page_relationships(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    return templates.TemplateResponse(
        request,
        "page_relationships.html",
        {"request": request, "username": user_id, "files": user_data[user_id].files},
    )


@app.post("/upload_file")
async def receive_file(
    uploaded_file: UploadFile,
    user_id: Annotated[str, Depends(get_user_id)],
):
    logger.debug(f"Uploading: {user_id}, {uploaded_file.filename}, {uploaded_file}")

    contents = await uploaded_file.read()
    df = pd.read_csv(io.BytesIO(contents))
    logger.debug(f"Dataframe processed of shape: {df.shape}")

    assert uploaded_file.filename and uploaded_file.size
    user_data[user_id].files.append(
        FileDetails(
            os.path.splitext(uploaded_file.filename)[0],
            uploaded_file.filename,
            uploaded_file.size,
            df,
        )
    )

    file_listing_df = get_user_files(user_id)
    table_html = make_table_html(file_listing_df, "files-table")

    return HTMLResponse(content=table_html, status_code=fastapi.status.HTTP_200_OK)


@app.get("/types_table", response_class=HTMLResponse)
async def get_types_table(
    user_id: Annotated[str, Depends(get_user_id)], types_selector: str
):
    table_html = make_table_html(
        user_data[user_id].files[int(types_selector)].df, "files-table"
    )
    return HTMLResponse(content=table_html, status_code=fastapi.status.HTTP_200_OK)


@app.get("/create_chart", response_class=HTMLResponse)
async def get_chart_page(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    user_data[user_id].charts.append(ChartDetails("dummy"))
    # TODO: Setup oob-swap here
    # main swap target will be page-contents
    # secondary will be sidebar-charts-list with innerHTML swap
    # will probably need to manually render the "page_chart.html" template and str-concat with updated sidebar-charts-list
    # swap-oob attributes will be set on modal submission
    # ALSO close the modal on successfull submit (check before swap)
    return templates.TemplateResponse(
        request,
        "page_chart.html",
        {"request": request, "username": user_id, "files": user_data[user_id].files},
    )
