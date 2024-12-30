from dataclasses import dataclass
import io
import os
import uuid
from collections import defaultdict
from collections.abc import Awaitable
from enum import StrEnum, auto, unique
from typing import Annotated, Callable, NamedTuple

import fastapi
import pandas as pd
from fastapi import Depends, FastAPI, Form, Request, Response, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import plotly.express as px

from .middlewares.custom_logging import logger

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


class FileDetails(NamedTuple):
    name: str
    filename: str
    filesize: int
    df: pd.DataFrame


@unique
class ChartType(StrEnum):
    SCATTER = auto()
    BAR = auto()
    HEATMAP = auto()
    HISTOGRAM = auto()


# TODO: setup tagged-union in chartspec.py for proper management of this
@dataclass
class ChartAesthetics:
    x: str
    y: str
    color: str | None = None


class ChartDetails(NamedTuple):
    name: str
    chart_type: ChartType
    aes: ChartAesthetics


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

    # TODO: setup yaml file for config
    chart_types = [
        {"name": "Scatter", "description": "This is a scatter plot"},
        {"name": "Bar", "description": "This is a bar plot"},
        {"name": "Heatmap", "description": "This is a heatmap plot"},
        {"name": "Histogram", "description": "This is a histogram plot"},
        {"name": "Scatter", "description": "This is a scatter plot"},
        {"name": "Bar", "description": "This is a bar plot"},
        {"name": "Heatmap", "description": "This is a heatmap plot"},
        {"name": "Histogram", "description": "This is a histogram plot"},
        {"name": "Heatmap", "description": "This is a heatmap plot"},
        {"name": "Histogram", "description": "This is a histogram plot"},
    ]

    return templates.TemplateResponse(
        request,
        "base_1.html",
        {
            "request": request,
            "userid": user_id,
            "chart_types": chart_types,
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
        {"request": request, "userid": user_id, "files_table": table_html},
    )


@app.get("/page_types", response_class=HTMLResponse)
async def get_page_types(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    return templates.TemplateResponse(
        request,
        "page_types.html",
        {"request": request, "userid": user_id, "files": user_data[user_id].files},
    )


@app.get("/page_relationships", response_class=HTMLResponse)
async def get_page_relationships(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    return templates.TemplateResponse(
        request,
        "page_relationships.html",
        {"request": request, "userid": user_id, "files": user_data[user_id].files},
    )


# TODO: make this and others? POST
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
        user_data[user_id].files[int(types_selector)].df.dtypes.to_frame().T,
        "files-table",
    )
    return HTMLResponse(content=table_html, status_code=fastapi.status.HTTP_200_OK)


@app.get("/create_chart", response_class=HTMLResponse)
async def create_new_chart(
    request: Request, user_id: Annotated[str, Depends(get_user_id)], chart_type: str
):
    # TODO: use the "main" file here. this needs to be set in relationships view??
    df = user_data[user_id].files[-1].df
    aes = ChartAesthetics(
        x=df.select_dtypes("number").columns[0],
        y=df.select_dtypes("number").columns[1],
    )
    user_data[user_id].charts.append(
        ChartDetails(
            f"Chart {len(user_data[user_id].charts) + 1}",
            ChartType[chart_type.upper()],
            aes,
        )
    )

    fig = px.scatter(df, aes.x, aes.y)

    chart_html = fig.to_html(full_html=False)

    new_chart_page: str = templates.get_template("page_chart.html").render(
        {
            "request": request,
            "userid": user_id,
            "chart": user_data[user_id].charts[-1],
            "actual_chart": chart_html,
        },
    )
    updated_sidebar_charts_list: str = templates.get_template(
        "fragment_charts_list.html"
    ).render(
        {
            "request": request,
            "userid": user_id,
            "charts": user_data[user_id].charts,
        },
    )
    full_content = new_chart_page + "\n" + updated_sidebar_charts_list
    return HTMLResponse(content=full_content)


@app.get("/page_chart", response_class=HTMLResponse)
async def get_chart_page(
    request: Request, user_id: Annotated[str, Depends(get_user_id)], chart_idx: int
):
    return templates.TemplateResponse(
        request,
        "page_chart.html",
        {
            "request": request,
            "userid": user_id,
            "chart": user_data[user_id].charts[chart_idx],
        },
    )
