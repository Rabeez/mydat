import uuid
from pathlib import Path
from typing import Annotated

import fastapi
import polars as pl
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile
from fastapi.responses import HTMLResponse

from app.dependencies import (
    FileDetails,
    generate_table,
    get_user_id,
    templates,
    user_data,
)
from app.graphspec import DataNode
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/files",
    tags=["files"],
    dependencies=[],
)


@router.post("/upload")
async def receive_file(
    uploaded_file: UploadFile,
    user_id: Annotated[str, Depends(get_user_id)],
) -> Response:
    logger.debug(f"Uploading: {user_id}, {uploaded_file.filename}, {uploaded_file}")

    contents = await uploaded_file.read()
    file_df = pl.read_csv(contents)
    logger.debug(f"Dataframe processed of shape: {file_df.shape}")

    if not (uploaded_file.filename and uploaded_file.size):
        logger.error("Invalid file data")
        raise HTTPException(fastapi.status.HTTP_400_BAD_REQUEST, "Invalid file data")

    user_data[user_id].files.append(
        FileDetails(
            Path(uploaded_file.filename).stem,
            uploaded_file.filename,
            uploaded_file.size,
            file_df,
        ),
    )

    user_data[user_id].graph.append(
        DataNode(
            str(uuid.uuid4()),
            user_data[user_id].files[-1].name,
            [],
            [],
        )
    )

    # Recreate full files table for user after state is updated
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

    return HTMLResponse(content=table_html, status_code=fastapi.status.HTTP_200_OK)
