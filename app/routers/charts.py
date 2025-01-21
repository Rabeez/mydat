from typing import Annotated

import polars as pl
from fastapi import APIRouter, Form, Request
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
from app.dependencies.utils import UserDep
from app.middlewares.custom_logging import logger
from app.templates.renderer import render

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
    chart_selection_radio: Annotated[str, Form()],
    chart_src_selector: Annotated[str, Form()],
) -> HTMLResponse:
    logger.debug(f"CHART: {user_id} -> {chart_selection_radio}:{chart_src_selector}")

    g = app_state.get_user_graph(user_id, db)
    src_table = g.get_node_data(chart_src_selector)

    # NOTE: Uses first file/table as initial DF for new chart creation
    main_df = src_table.data
    assert isinstance(main_df, pl.DataFrame)

    try:
        chart_kind = ChartKind[chart_selection_radio.upper()]
    except KeyError as e:
        logger.error(f"Failed to parse ChartKind: '{chart_selection_radio}'")
        raise ValueError(f"Failed to parse ChartKind: '{chart_selection_radio}'") from e

    match chart_kind:
        case ChartKind.SCATTER:
            chart_data = ChartScatter.default(main_df)
        case ChartKind.BAR:
            chart_data = ChartBar.default(main_df)
        case ChartKind.HISTOGRAM:
            chart_data = ChartHistogram.default(main_df)
        case ChartKind.HEATMAP:
            chart_data = ChartHeatmap.default(main_df)

    user_charts_for_naming = g.get_nodes_by_kind(kind=KindNode.CHART, subkind=chart_kind)
    new_chart = GraphNode(
        name=f"Chart_{chart_kind}_{len(user_charts_for_naming) + 1}",
        kind=KindNode.CHART,
        subkind=chart_kind,
        data=chart_data,
    )
    chart_id = g.add_node(new_chart)
    g.add_edge(chart_src_selector, chart_id)
    logger.warning(g)

    fig = chart_data.make_fig(main_df)
    chart_html: str = fig.to_html(full_html=False)
    user_charts = g.get_nodes_by_kind(kind=KindNode.CHART)

    return render(
        {
            "template_name": "page_chart.jinja",
            "context": {
                "request": request,
                "chart": new_chart,
                "chart_id": chart_id,
                "actual_chart": chart_html,
            },
        },
        {
            "template_name": "base.jinja",
            "context": {
                "request": request,
                "charts": user_charts,
            },
            "block_name": "sidebar_chart_list",
        },
    )


@router.post("/update", response_class=HTMLResponse)
async def update_chart(
    request: Request,
    user_id: UserDep,
    db: SessionDep,
    chart_id: str,
    dimension_name: str,
    dimension_value: Annotated[str, Form()],
) -> HTMLResponse:
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
