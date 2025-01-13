from typing import Annotated

import fastapi
from fastapi import APIRouter, Depends, Response
from fastapi.responses import HTMLResponse, JSONResponse

from app.dependencies import (
    files2nodes,
    generate_table,
    get_user_id,
    user_data,
)
from app.graphspec import (
    Node,
    node2dict,
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
) -> Response:
    logger.debug(f"Fetching graph data for user {user_id}")

    # recreate graph using "files" list and current "graph" data
    # send new JSON and overwrite whole div
    user_files = user_data[user_id].files
    data_nodes = files2nodes(user_files)

    d = {
        "nodes": [
            {"data": {"kind": "data", "id": "table1", "name": "Table 1"}},
            {"data": {"kind": "analysis", "id": "filter1", "name": "Filter Node"}},
            *[{"data": node2dict(n)} for n in data_nodes],
        ],
        "edges": [
            {"data": {"source": "table1", "target": "filter1"}},
            # *[{"data": node2edges(n)} for n in data_nodes],
        ],
    }
    return JSONResponse(d)
