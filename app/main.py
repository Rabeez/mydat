import io
from collections import defaultdict
from collections.abc import Awaitable
from typing import Callable, Annotated
import uuid

import pandas as pd
from fastapi import FastAPI, Request, Response, UploadFile, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .middlewares.custom_logging import logger

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


COOKIE_NAME = "user_id"
user_files: dict[str, list[pd.DataFrame]] = defaultdict(list)


def get_user_id(request: Request, response: Response) -> str:
    user_id = request.cookies.get(COOKIE_NAME)
    if not user_id:
        user_id = str(uuid.uuid4())
        response.set_cookie(key=COOKIE_NAME, value=user_id, httponly=True)
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
    return templates.TemplateResponse(
        request, "page_files.html", {"request": request, "username": user_id}
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
    user_files[user_id].append(df)
    return {"files": len(user_files[user_id])}
