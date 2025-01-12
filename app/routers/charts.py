from typing import Annotated

import polars.selectors as cs
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
)
from app.main import user_data
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
    logger.debug(f"CHART: {user_id} - {user_data[user_id].main_file_idx}")
    main_df = user_data[user_id].main_file.df
    colnames_num = main_df.select(cs.numeric()).columns
    colnames_cat = main_df.select(cs.string(include_categorical=True)).columns
    colnames_mix = colnames_num + colnames_cat

    try:
        chart_kind = ChartKind[chart_kind.upper()]
    except KeyError as e:
        logger.error(f"Failed to parse ChartKind: '{chart_kind}'")
        raise ValueError(f"Failed to parse ChartKind: '{chart_kind}'") from e

    match chart_kind:
        case ChartKind.SCATTER:
            chart_data = ChartScatter(
                x=DimensionValue.from_list(colnames_num, 0),
                y=DimensionValue.from_list(colnames_num, 1),
                color=DimensionValue.from_list(colnames_mix, None),
                size=DimensionValue.from_list(colnames_mix, None),
                symbol=DimensionValue.from_list(colnames_mix, None),
            )
        case ChartKind.BAR:
            chart_data = ChartBar(
                x=DimensionValue.from_list(colnames_cat, 0),
                y=DimensionValue.from_list(colnames_num, None),
                color=DimensionValue.from_list(colnames_cat, None),
            )
        case ChartKind.HISTOGRAM:
            chart_data = ChartHistogram(
                x=DimensionValue.from_list(colnames_num, 0),
                color=DimensionValue.from_list(colnames_cat, None),
            )
        case ChartKind.HEATMAP:
            chart_data = ChartHeatmap(
                x=DimensionValue.from_list(colnames_cat, 0),
                y=DimensionValue.from_list(colnames_cat, 1),
                _z=DimensionValue.from_list(colnames_num, 0),
            )

    user_data[user_id].charts.append(
        ChartDetails(
            f"Chart {len(user_data[user_id].charts) + 1}",
            chart_kind,
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
            "chart": current_chart,
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
    main_df = user_data[user_id].main_file.df
    current_chart = user_data[user_id].charts[chart_idx]

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
            "chart": current_chart,
            "chart_idx": chart_idx,
            "actual_chart": chart_html,
        },
    )
