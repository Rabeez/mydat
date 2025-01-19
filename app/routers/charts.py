from typing import Annotated

import polars as pl
from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse

from app.db.session import SessionDep
from app.dependencies.specs.chart import (
    ChartBar,
    ChartHeatmap,
    ChartHistogram,
    ChartKind,
    ChartScatter,
    DataChart,
    DimensionValue,
)
from app.dependencies.specs.graph import GraphNode, KindNode
from app.dependencies.state import app_state
from app.dependencies.utils import (
    UserDep,
    templates,
)
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/charts",
    tags=["charts"],
    dependencies=[],
)


@router.post("/create", response_class=HTMLResponse)
async def create_new_chart(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    chart_kind: str,
) -> Response:
    logger.debug(f"CHART: {user_id}")

    g = app_state.get_user_graph(user_id, db)
    user_files = g.get_nodes_by_kind(kind=KindNode.TABLE)

    # NOTE: Uses first file/table as initial DF for new chart creation
    _id = 0
    main_df = user_files[_id][1].data
    assert isinstance(main_df, pl.DataFrame)

    try:
        chart_kind = ChartKind[chart_kind.upper()]
    except KeyError as e:
        logger.error(f"Failed to parse ChartKind: '{chart_kind}'")
        raise ValueError(f"Failed to parse ChartKind: '{chart_kind}'") from e

    match chart_kind:
        case ChartKind.SCATTER:
            chart_data = ChartScatter.default(main_df)
        case ChartKind.BAR:
            chart_data = ChartBar.default(main_df)
        case ChartKind.HISTOGRAM:
            chart_data = ChartHistogram.default(main_df)
        case ChartKind.HEATMAP:
            chart_data = ChartHeatmap.default(main_df)

    user_charts = g.get_nodes_by_kind(kind=KindNode.CHART, subkind=chart_kind)
    new_chart = GraphNode(
        name=f"Chart_{chart_kind}_{len(user_charts) + 1}",
        kind=KindNode.CHART,
        subkind=chart_kind,
        data=chart_data,
    )
    chart_id = g.add_node(new_chart)
    g.add_edge(user_files[_id][0], chart_id)
    logger.warning(g)

    fig = chart_data.make_fig(main_df)
    chart_html: str = fig.to_html(full_html=False)
    new_chart_page: str = templates.get_template("page_chart.jinja").render(
        {
            "request": request,
            "userid": user_id,
            "chart": new_chart,
            "chart_id": chart_id,
            "actual_chart": chart_html,
        },
    )
    user_charts = g.get_nodes_by_kind(kind=KindNode.CHART)

    user_charts = g.get_nodes_by_kind(KindNode.CHART)
    updated_sidebar_charts_list: str = templates.get_template("fragment_charts_list.jinja").render(
        {
            "request": request,
            "userid": user_id,
            "charts": user_charts,
        },
    )
    full_content = new_chart_page + "\n" + updated_sidebar_charts_list
    return HTMLResponse(content=full_content)


@router.post("/update", response_class=HTMLResponse)
async def update_chart(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    chart_id: str,
    dimension_name: str,
    dimension_value: Annotated[str, Form()],
) -> Response:
    g = app_state.get_user_graph(user_id, db)

    current_chart = g.get_node_data(chart_id)
    _, chart_parent_data = g.get_parents(chart_id)[0]

    current_dim: DimensionValue = getattr(current_chart.data, dimension_name)
    current_dim.selected = dimension_value
    setattr(current_chart.data, dimension_name, current_dim)

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
