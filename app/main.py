from collections.abc import Awaitable
from typing import Callable

from fastapi import FastAPI, Request, Response
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
