import io
from collections.abc import Awaitable
from typing import Callable

import pandas as pd
from fastapi import FastAPI, Request, Response, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .middlewares.custom_logging import logger

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


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
async def get_homepage(request: Request):
    return templates.TemplateResponse(
        request, "base.html", {"request": request, "username": "Rabeez"}
    )


@app.post("/upload")
async def receive_file(file: UploadFile):
    logger.debug(file.filename, file)
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    logger.debug(df)
    return {"filename": file.filename}
