import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

import polars as pl
from fastapi import Depends, FastAPI, Request, Response

from app.db.session import create_db_and_tables, get_db_context
from app.dependencies.state import app_state
from app.middlewares.custom_logging import logger


def make_table_html(df: pl.DataFrame, html_id: str) -> str:
    # NOTE: class 'table-pin-rows' causes a z-order bug where table header is drawn over the sidebar
    table_html_classes = "dataframe table"
    gen_html = df._repr_html_()
    left = gen_html.index("<table")
    right = gen_html.index("</table>")
    replace_from = '<table border="1" class="dataframe">'
    replace_to = f'<table class="{table_html_classes}" id="{html_id}">'
    final = gen_html[left : right + len("</table>")].replace(replace_from, replace_to)
    return final


def get_user_id(request: Request, response: Response) -> str:
    cookie_name = "user_id"
    user_id = request.cookies.get(cookie_name)
    if not user_id:
        user_id = str(uuid.uuid4())
        response.set_cookie(key=cookie_name, value=user_id, httponly=True)
        logger.info("Generating new user_id")
    else:
        logger.info("Obtained user_id from cookie")
    return user_id


UserDep = Annotated[str, Depends(get_user_id)]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    try:
        yield
    finally:
        with get_db_context() as db:
            app_state.persist_all_to_db(db)
