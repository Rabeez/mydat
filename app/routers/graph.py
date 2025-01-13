from typing import Annotated

import fastapi
from fastapi import APIRouter, Depends, Response
from fastapi.responses import HTMLResponse

from app.dependencies import (
    generate_table,
    get_user_id,
    user_data,
)
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
    dependencies=[],
)


@router.get("/")
async def get_types_table(
    user_id: Annotated[str, Depends(get_user_id)],
) -> dict:
    logger.debug(f"Fetching graph data for user {user_id}")

    d = {
        "nodes": [
            {"data": {"kind": "data", "id": "table1", "name": "Table 1"}},
            {"data": {"kind": "analysis", "id": "filter1", "name": "Filter Node"}},
        ],
        "edges": [{"data": {"source": "table1", "target": "filter1"}}],
    }
    return d
