from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse

from app.chartspec import (
    ChartBar,
    ChartHeatmap,
    ChartHistogram,
    ChartKind,
    ChartScatter,
    DimensionValue,
)
from app.dependencies import (
    ChartDetails,
    get_user_id,
    templates,
    user_data,
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
    user_id: Annotated[str, Depends(get_user_id)],
    chart_kind: str,
) -> Response:
    logger.debug(f"CHART: {user_id}")
    # NOTE: Uses first file/table as initial DF for new chart creation
    _idx = 0
    main_df = user_data[user_id].files[_idx].df

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

    user_data[user_id].charts.append(
        ChartDetails(
            f"Chart {len(user_data[user_id].charts) + 1}",
            chart_kind,
            _idx,
            chart_data,
        ),
    )

    current_chart = user_data[user_id].charts[-1]
    fig = current_chart.data.make_fig(main_df)

    chart_html: str = fig.to_html(full_html=False)

    new_chart_page: str = templates.get_template("page_chart.jinja").render(
        {
            "request": request,
            "userid": user_id,
            "files": user_data[user_id].files,
            "chart": current_chart,
            "chart_file_idx": current_chart.file_idx,
            "chart_idx": len(user_data[user_id].charts) - 1,
            "actual_chart": chart_html,
        },
    )
    updated_sidebar_charts_list: str = templates.get_template("fragment_charts_list.jinja").render(
        {
            "request": request,
            "userid": user_id,
            "charts": user_data[user_id].charts,
        },
    )
    full_content = new_chart_page + "\n" + updated_sidebar_charts_list
    return HTMLResponse(content=full_content)


@router.post("/update", response_class=HTMLResponse)
async def update_chart(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
    chart_idx: int,
    dimension_name: str,
    dimension_value: Annotated[str, Form()],
) -> Response:
    current_chart = user_data[user_id].charts[chart_idx]
    main_df = user_data[user_id].files[current_chart.file_idx].df

    current_dim: DimensionValue = getattr(current_chart.data, dimension_name)
    current_dim.selected = dimension_value
    setattr(current_chart.data, dimension_name, current_dim)
    user_data[user_id].charts[chart_idx] = current_chart

    fig = current_chart.data.make_fig(main_df)

    chart_html: str = fig.to_html(full_html=False)

    return templates.TemplateResponse(
        request,
        "page_chart.jinja",
        {
            "request": request,
            "userid": user_id,
            "files": user_data[user_id].files,
            "chart": current_chart,
            "chart_file_idx": current_chart.file_idx,
            "chart_idx": chart_idx,
            "actual_chart": chart_html,
        },
    )


@router.post("/change_table", response_class=HTMLResponse)
async def change_chart_table(
    request: Request,
    user_id: Annotated[str, Depends(get_user_id)],
    chart_idx: int,
    chart_file_selector: Annotated[int, Form()],
) -> Response:
    logger.debug(f"User updating chart {chart_idx} with table {chart_file_selector}")

    current_chart = user_data[user_id].charts[chart_idx]
    current_chart.file_idx = chart_file_selector
    new_chart_df = user_data[user_id].files[chart_file_selector].df

    match current_chart.kind:
        case ChartKind.SCATTER:
            chart_data = ChartScatter.default(new_chart_df)
        case ChartKind.BAR:
            chart_data = ChartBar.default(new_chart_df)
        case ChartKind.HISTOGRAM:
            chart_data = ChartHistogram.default(new_chart_df)
        case ChartKind.HEATMAP:
            chart_data = ChartHeatmap.default(new_chart_df)

    user_data[user_id].charts[chart_idx] = ChartDetails(
        current_chart.name,
        current_chart.kind,
        chart_file_selector,
        chart_data,
    )
    new_chart = user_data[user_id].charts[chart_idx]

    fig = new_chart.data.make_fig(new_chart_df)

    chart_html: str = fig.to_html(full_html=False)

    return templates.TemplateResponse(
        request,
        "fragment_chart_controls_and_plot.jinja",
        {
            "request": request,
            "userid": user_id,
            "files": user_data[user_id].files,
            "chart": new_chart,
            "chart_file_idx": new_chart.file_idx,
            "chart_idx": chart_idx,
            "actual_chart": chart_html,
        },
    )
