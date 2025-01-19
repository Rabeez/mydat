from pathlib import Path

import fastapi
import polars as pl
from fastapi import APIRouter, HTTPException, Response, UploadFile
from fastapi.responses import HTMLResponse

from app.db.session import SessionDep
from app.dependencies.specs.graph import GraphNode, KindNode
from app.dependencies.specs.table import KindTable
from app.dependencies.state import app_state
from app.dependencies.utils import (
    UserDep,
    generate_table,
)
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/files",
    tags=["files"],
    dependencies=[],
)


@router.post("/upload")
async def receive_file(
    uploaded_file: UploadFile,
    user_id: UserDep,
    db: SessionDep,
) -> Response:
    logger.debug(f"Uploading: {user_id}, {uploaded_file.filename}, {uploaded_file}")

    contents = await uploaded_file.read()
    file_df = pl.read_csv(contents)
    logger.debug(f"Dataframe processed of shape: {file_df.shape}")

    if not (uploaded_file.filename and uploaded_file.size):
        logger.error("Invalid file data")
        raise HTTPException(fastapi.status.HTTP_400_BAD_REQUEST, "Invalid file data")

    g = app_state.get_user_graph(user_id, db)
    g.add_node(
        GraphNode(
            name=Path(uploaded_file.filename).stem,
            kind=KindNode.TABLE,
            subkind=KindTable.UPLOADED,
            data=file_df,
        ),
    )
    logger.warning(g)

    # Recreate full files table for user after state is updated
    user_files = g.get_nodes_by_kind(KindNode.TABLE)
    table_html = generate_table(
        "files-table",
        ["Name", "File", "Filesize"],
        [[f.name, "fn", 0] for _, f in user_files],
        [
            {"text": "Rename", "endpoint": "/file_rename"},
            {"text": "Delete", "endpoint": "/file_delete"},
        ],
    )

    return HTMLResponse(content=table_html, status_code=fastapi.status.HTTP_200_OK)
