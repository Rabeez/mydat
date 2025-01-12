from typing import Annotated

import fastapi
from fastapi import APIRouter, Depends, Response
from fastapi.responses import HTMLResponse

from app.dependencies import (
    generate_table,
    get_user_id,
)
from app.main import user_data
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/fragments",
    tags=["fragments"],
    dependencies=[],
)


@router.get("/types_table", response_class=HTMLResponse)
async def get_types_table(
    user_id: Annotated[str, Depends(get_user_id)],
    types_selector: int,
) -> Response:
    logger.debug(f"Fetching fragment types table for user {user_id}")

    selected_df = user_data[user_id].files[types_selector].df
    table_html = generate_table(
        "types-table",
        selected_df.columns,
        [selected_df.dtypes],
    )
    return HTMLResponse(content=table_html, status_code=fastapi.status.HTTP_200_OK)
