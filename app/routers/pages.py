import polars as pl
from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse

from app.db.session import SessionDep
from app.dependencies.specs.chart import DataChart
from app.dependencies.specs.graph import KindNode
from app.dependencies.state import app_state
from app.dependencies.utils import (
    UserDep,
    generate_table,
    templates,
)
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/pages",
    tags=["pages"],
    dependencies=[],
)


@router.get("/files", response_class=HTMLResponse)
async def get_page_files(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
) -> Response:
    logger.debug("Sending files page")

    g = app_state.get_user_graph(user_id, db)
    user_files = g.get_nodes_by_kind(kind=KindNode.TABLE)
    table_html = generate_table(
        "files-table",
        ["Name", "File", "Filesize"],
        [[f.name, "asd", 0] for _, f in user_files],
        [
            {"text": "Rename", "endpoint": "/file_rename"},
            {"text": "Delete", "endpoint": "/file_delete"},
        ],
    )

    return templates.TemplateResponse(
        request,
        "page_files.jinja",
        {"request": request, "userid": user_id, "files_table": table_html},
    )


# @router.get("/types", response_class=HTMLResponse)
# async def get_page_types(
#     request: Request,
#     user_id: UserDep,
# ) -> Response:
#     return templates.TemplateResponse(
#         request,
#         "page_types.jinja",
#         {"request": request, "userid": user_id, "files": user_data[user_id].files},
#     )
#


@router.get("/relationships", response_class=HTMLResponse)
async def get_page_relationships(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
) -> Response:
    logger.debug("Sending relationships page")

    g = app_state.get_user_graph(user_id, db)
    user_files = g.get_nodes_by_kind(KindNode.TABLE)
    return templates.TemplateResponse(
        request,
        "page_relationships.jinja",
        {
            "request": request,
            "userid": user_id,
            "files": user_files,
            "graph_json": {},
        },
    )


# @router.get("/maintable", response_class=HTMLResponse)
# async def get_page_maintable(
#     request: Request,
#     user_id: UserDep,
# ) -> Response:
#     # TODO: REMOVE ENDPOINT
#     assert False
#     main_df = user_data[user_id].main_file.df
#     table_html = make_table_html(main_df.head(20), "main-table")
#     return templates.TemplateResponse(
#         request,
#         "page_maintable.jinja",
#         {"request": request, "userid": user_id, "main_table_html": table_html},
#     )
#


@router.get("/chart", response_class=HTMLResponse)
async def get_chart_page(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    chart_id: str,
) -> Response:
    logger.debug("Sending chart page")

    g = app_state.get_user_graph(user_id, db)
    current_chart = g.get_node_data(chart_id)
    _, chart_parent_data = g.get_parents(chart_id)[0]

    # TODO: Think of a way to avoid recreating this everytime
    assert isinstance(current_chart.data, DataChart)
    assert isinstance(chart_parent_data.data, pl.DataFrame)
    fig = current_chart.data.make_fig(chart_parent_data.data)

    chart_html: str = fig.to_html(full_html=False)

    return templates.TemplateResponse(
        request,
        "page_chart.jinja",
        {
            "request": request,
            "userid": user_id,
            "chart": current_chart,
            "chart_id": chart_id,
            "actual_chart": chart_html,
        },
    )
