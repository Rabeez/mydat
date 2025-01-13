import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import pandas as pd
import polars as pl
from fastapi import Request, Response
from fastapi.templating import Jinja2Templates

from app.chartspec import (
    Chart,
    ChartKind,
)
from app.graphspec import (
    Graph,
    Node,
    NodeKind,
)
from app.middlewares.custom_logging import logger

templates = Jinja2Templates(directory="app/templates")


@dataclass
class FileDetails:
    name: str
    filename: str
    filesize: int
    df: pl.DataFrame


def files2nodes(files: list[FileDetails]) -> Graph:
    nodes = []
    for _id, f in enumerate(files):
        n = Node(
            id=str(_id),
            kind=NodeKind.DATA,
            method=None,
            name=f.name,
        )
        nodes.append(n)
    return nodes


@dataclass
class ChartDetails:
    name: str
    kind: ChartKind
    file_idx: int
    data: Chart


@dataclass
class UserData:
    files: list[FileDetails]
    charts: list[ChartDetails]
    graph: Graph


def generate_table(
    html_table_id: str,
    colnames: list[str],
    rows: list[list[Any]],
    row_actions: list[dict[str, str]] | None = None,
) -> str:
    if row_actions is None:
        row_actions = []

    return templates.get_template("fragment_table.jinja").render(
        {
            "html_id": html_table_id,
            "colnames": colnames + [""] * len(row_actions),
            "rows": rows,
            "row_actions": row_actions,
        },
    )


def make_table_html(df: pl.DataFrame | pd.DataFrame, html_id: str) -> str:
    # NOTE: class 'table-pin-rows' causes a z-order bug where table header is drawn over the sidebar
    table_html_classes = "dataframe table"
    if isinstance(df, pl.DataFrame):
        gen_html = df._repr_html_()
        left = gen_html.index("<table")
        right = gen_html.index("</table>")
        replace_from = '<table border="1" class="dataframe">'
        replace_to = f'<table class="{table_html_classes}" id="{html_id}">'
        final = gen_html[left : right + len("</table>")].replace(replace_from, replace_to)
        return final
    else:
        return df.to_html(
            header=True,
            index=True,
            index_names=False,
            bold_rows=False,
            border=0,
            justify="left",
            table_id=html_id,
            classes=table_html_classes,
        )


def get_user_id(request: Request, response: Response) -> str:
    cookie_name = "user_id"
    user_id = request.cookies.get(cookie_name)
    if not user_id:
        user_id = str(uuid.uuid4())
        response.set_cookie(key=cookie_name, value=user_id, httponly=True)
    return user_id


user_data: dict[str, UserData] = defaultdict(lambda: UserData([], [], []))
