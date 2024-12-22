import io
import os
import uuid
from collections import defaultdict
from collections.abc import Awaitable
from typing import Annotated, Callable, NamedTuple

import fastapi
import pandas as pd
from fastapi import Depends, FastAPI, Request, Response, UploadFile
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


user_files: dict[str, list[FileDetails]] = defaultdict(list)


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
    current_user_id = user_id
    logger.debug(f"User identified: {current_user_id}")
    return templates.TemplateResponse(
        request,
        "base_1.html",
        {"request": request, "username": current_user_id},
    )


@app.get("/page_files", response_class=HTMLResponse)
async def get_page_files(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    col_names = ["Name", "Filename", "Size", ""]
    file_listing_df = pd.DataFrame(
        index=range(len(user_files[user_id])), columns=col_names
    )
    delete_col_text = "<a>Delete</a>"
    for i, fd in enumerate(user_files[user_id]):
        file_listing_df.iloc[i, :] = [  # pyright: ignore [reportArgumentType]
            fd.name,
            fd.filename,
            fd.filesize,
            delete_col_text,
        ]
    table_html = file_listing_df.to_html(
        header=True,
        index=True,
        index_names=False,
        bold_rows=False,
        border=0,
        justify="left",
        table_id="files-tabler",
        classes="table table-xs table-pin-rows",
    )

    return templates.TemplateResponse(
        request,
        "page_files.html",
        {"request": request, "username": user_id, "files": table_html},
    )


@app.get("/page_types", response_class=HTMLResponse)
async def get_page_types(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    return templates.TemplateResponse(
        request, "page_types.html", {"request": request, "username": user_id}
    )


@app.get("/page_relationships", response_class=HTMLResponse)
async def get_page_relationships(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
):
    return templates.TemplateResponse(
        request,
        "page_relationships.html",
        {"request": request, "username": user_id},
    )


@app.post("/upload_file")
async def receive_file(
    file: UploadFile,
    user_id: Annotated[str, Depends(get_user_id)],
):
    logger.debug(f"Uploading: {user_id}, {file.filename}, {file}")
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    logger.debug(f"Dataframe processed of shape: {df.shape}")
    assert file.filename and file.size
    user_files[user_id].append(
        FileDetails(os.path.splitext(file.filename)[0], file.filename, file.size, df)
    )
    # return {"files": len(user_files[user_id])}

    col_names = ["Name", "Filename", "Size", ""]
    file_listing_df = pd.DataFrame(
        index=range(len(user_files[user_id])), columns=col_names
    )
    delete_col_text = "<a>Delete</a>"
    for i, fd in enumerate(user_files[user_id]):
        file_listing_df.iloc[i, :] = [  # pyright: ignore [reportArgumentType]
            fd.name,
            fd.filename,
            fd.filesize,
            delete_col_text,
        ]
    table_html = file_listing_df.to_html(
        header=True,
        index=True,
        index_names=False,
        bold_rows=False,
        border=0,
        justify="left",
        table_id="files-tabler",
        classes="table table-xs table-pin-rows",
    )

    return HTMLResponse(content=table_html, status_code=fastapi.status.HTTP_200_OK)
