import polars as pl
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.db.session import SessionDep
from app.dependencies.specs.analysis import FilterOperation
from app.dependencies.specs.chart import DataChart, fig_html
from app.dependencies.specs.graph import KindNode
from app.dependencies.state import app_state
from app.dependencies.utils import UserDep
from app.middlewares.custom_logging import logger
from app.templates.renderer import render

router = APIRouter(
    prefix="/pages",
    tags=["pages"],
    dependencies=[],
)


@router.get("/dataflow", response_class=HTMLResponse)
async def get_page_relationships(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
) -> HTMLResponse:
    logger.debug("Sending dataflow page")

    g = app_state.get_user_graph(user_id, db)
    user_files = g.get_nodes_by_kind(KindNode.TABLE)
    return render(
        {
            "template_name": "page_dataflow.jinja",
            "context": {
                "request": request,
                "files": user_files,
                "filter_ops": [op.value for op in FilterOperation],
                "graph_json": g.to_cytoscape(),
            },
        },
    )


@router.get("/chart", response_class=HTMLResponse)
async def get_chart_page(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    chart_id: str,
) -> HTMLResponse:
    logger.debug("Sending chart page")

    g = app_state.get_user_graph(user_id, db)
    current_chart = g.get_node_data(chart_id)
    _, chart_parent_data = g.get_parents(chart_id)[0]

    # TODO: Think of a way to avoid recreating this everytime
    assert isinstance(current_chart.data, DataChart)
    assert isinstance(chart_parent_data.data, pl.DataFrame)
    fig = current_chart.data.make_fig(chart_parent_data.data)
    chart_html = fig_html(fig)

    return render(
        {
            "template_name": "page_chart.jinja",
            "context": {
                "request": request,
                "chart": current_chart,
                "chart_id": chart_id,
                "actual_chart": chart_html,
            },
        },
    )
