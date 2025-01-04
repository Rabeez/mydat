import os
import uuid
from collections import defaultdict
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Annotated, Callable, NamedTuple

import fastapi
import pandas as pd
import plotly.express as px
import polars as pl
import polars.selectors as cs
from fastapi import Depends, FastAPI, Request, Response, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .chartspec import (
    Chart,
    ChartBar,
    ChartHeatmap,
    ChartHistogram,
    ChartScatter,
    ChartKind,
    spec2dict,
)
from .middlewares.custom_logging import logger

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


class FileDetails(NamedTuple):
    name: str
    filename: str
    filesize: int
    df: pl.DataFrame


class ChartDetails(NamedTuple):
    name: str
    kind: ChartKind
    data: Chart


@dataclass
class UserData:
    files: list[FileDetails]
    charts: list[ChartDetails]
    main_file_idx: int | None = None

    @property
    def main_file(self) -> FileDetails:
        if self.main_file_idx is None:
            logger.error("Main file index not set")
            raise ValueError("Main file index not set")
        return self.files[self.main_file_idx]


user_data: dict[str, UserData] = defaultdict(lambda: UserData([], [], None))


def get_user_files(user_id: str) -> pl.DataFrame:
    df_data: dict[str, list[str | int]] = {
        "Name": [],
        "Filename": [],
        "Size": [],
        "": [],
    }
    for fd in user_data[user_id].files:
        df_data["Name"].append(fd.name)
        df_data["Filename"].append(fd.filename)
        df_data["Size"].append(fd.filesize)
        df_data[""].append("<a>Delete</a>")
    file_listing_df = pl.DataFrame(df_data)

    return file_listing_df


def make_table_html(df: pl.DataFrame | pd.DataFrame, html_id: str) -> str:
    if isinstance(df, pl.DataFrame):
        gen_html = df._repr_html_()  # pyright: ignore [reportPrivateUsage]
        left = gen_html.index("<table")
        right = gen_html.index("</table>")
        replace_from = '<table border="1" class="dataframe">'
        replace_to = f'<table class="dataframe table table-xs table-pin-rows" id="{html_id}">'
        final = gen_html[left : right + len("</table>")].replace(replace_from, replace_to)
        return final
    else:
        return df.to_html(  # pyright: ignore [reportUnknownMemberType]
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
async def log_client_ip(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
    if not request.client:
        return
    client_host, client_port = request.client.host, request.client.port
    logger.debug(f"Got a request from {client_host}:{client_port}")
    response = await call_next(request)  # Continue to the actual route handler
    return response


@app.get("/", response_class=HTMLResponse)
async def get_homepage(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    file_listing_df = get_user_files(user_id)
    logger.debug(f"User identified: {user_id} with {len(file_listing_df)} existing files")
    table_html = make_table_html(file_listing_df, "files-table")

    # TODO: setup yaml file for config
    chart_kinds = [
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
            "chart_kinds": chart_kinds,
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
    df = pl.read_csv(contents)
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
    # TODO: Link this to relationships page to get the actual main file idx (which might be constructed via joins)
    user_data[user_id].main_file_idx = len(user_data[user_id].files) - 1
    logger.debug(f"UPLOAD: {user_id} - {user_data[user_id].main_file_idx}")

    file_listing_df = get_user_files(user_id)
    table_html = make_table_html(file_listing_df, "files-table")

    return HTMLResponse(content=table_html, status_code=fastapi.status.HTTP_200_OK)


@app.get("/types_table", response_class=HTMLResponse)
async def get_types_table(user_id: Annotated[str, Depends(get_user_id)], types_selector: int):
    df = user_data[user_id].files[types_selector].df
    table_html = make_table_html(
        pl.DataFrame(dict(zip(df.columns, df.dtypes))),
        "files-table",
    )
    return HTMLResponse(content=table_html, status_code=fastapi.status.HTTP_200_OK)


@app.get("/create_chart", response_class=HTMLResponse)
async def create_new_chart(
    request: Request, user_id: Annotated[str, Depends(get_user_id)], chart_kind: str
):
    logger.debug(f"CHART: {user_id} - {user_data[user_id].main_file_idx}")
    df = user_data[user_id].main_file.df
    colnames_numeric = df.select(cs.numeric()).columns
    colnames_cat = df.select(cs.string(include_categorical=True)).columns

    try:
        chart_kind = ChartKind[chart_kind.upper()]
    except KeyError:
        logger.error(f"Failed to parse ChartKind: '{chart_kind}'")
        raise ValueError(f"Failed to parse ChartKind: '{chart_kind}'")

    # TODO: use dropdown selections here to determine full aes
    # OR separate the creation (with default aes) and update_chart into 2 endpoints
    match chart_kind:
        case ChartKind.SCATTER:
            chart_data = ChartScatter(x=colnames_numeric[0], y=colnames_numeric[1])
            fig = px.scatter(df, **spec2dict(chart_data))  # pyright: ignore [reportUnknownMemberType]
        case ChartKind.BAR:
            chart_data = ChartBar(
                x=colnames_cat[0],
            )
            df_agg = df.group_by(chart_data.x).agg(chart_data._agg_func().alias("Y"))
            fig = px.bar(df_agg, y="Y", **spec2dict(chart_data))  # pyright: ignore [reportUnknownMemberType]
        case ChartKind.HISTOGRAM:
            chart_data = ChartHistogram(
                x=colnames_numeric[0],
            )
            fig = px.histogram(df, **spec2dict(chart_data))  # pyright: ignore [reportUnknownMemberType]
        case ChartKind.HEATMAP:
            chart_data = ChartHeatmap(x=colnames_cat[0], y=colnames_cat[1], _z=colnames_numeric[0])
            mat = (
                df.group_by(chart_data.x, chart_data.y)
                .agg(chart_data._agg_func(chart_data._z))
                .pivot(on=chart_data.x, index=chart_data.y, values=chart_data._z)
                .drop(cs.by_index(0))
                .to_numpy()
            )
            fig = px.imshow(
                mat,
                labels={"x": colnames_cat[0], "y": colnames_cat[1], "color": colnames_numeric[0]},
                x=df.select(colnames_cat[0]).unique().to_series().to_list(),
                y=df.select(colnames_cat[1]).unique().to_series().to_list(),
                text_auto=chart_data.annotate,
            )  # pyright: ignore [reportUnknownMemberType]

    user_data[user_id].charts.append(
        ChartDetails(
            f"Chart {len(user_data[user_id].charts) + 1}",
            chart_kind,
            chart_data,
        )
    )

    chart_html: str = fig.to_html(full_html=False)  # pyright: ignore [reportUnknownVariableType, reportUnknownMemberType]

    # TODO: Inject chart type to determine which dropdowns (w/ values) should be drawn
    new_chart_page: str = templates.get_template("page_chart.html").render(
        {
            "request": request,
            "userid": user_id,
            "chart": user_data[user_id].charts[-1],
            "actual_chart": chart_html,
        },
    )
    updated_sidebar_charts_list: str = templates.get_template("fragment_charts_list.html").render(
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
    # TODO: Re-render chart with "current" chosen aes attributes
    return templates.TemplateResponse(
        request,
        "page_chart.html",
        {
            "request": request,
            "userid": user_id,
            "chart": user_data[user_id].charts[chart_idx],
        },
    )
