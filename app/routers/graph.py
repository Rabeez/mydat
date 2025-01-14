from typing import Annotated

import fastapi
import polars as pl
from fastapi import APIRouter, Depends, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse

from app.dependencies import (
    FileDetails,
    generate_table,
    get_user_id,
    user_data,
)
from app.graphspec import (
    AnalysisMethod,
    AnalysisNode,
    DataNode,
    FilterOps,
    find_node,
    generate_edges,
    node2dict,
)
from app.middlewares.custom_logging import logger

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
    dependencies=[],
)


@router.get("/")
async def get_graph_data(
    user_id: Annotated[str, Depends(get_user_id)],
) -> Response:
    logger.debug(f"Fetching graph data for user {user_id}")

    # recreate graph using "files" list and current "graph" data
    # send new JSON and overwrite whole div
    data_nodes = user_data[user_id].graph

    edges = generate_edges(data_nodes)
    logger.debug(edges)

    d = {
        "nodes": [
            {"data": {"kind": "data", "id": "table1", "name": "Table 1"}},
            {"data": {"kind": "analysis", "id": "filter1", "name": "Filter Node"}},
            *[{"data": node2dict(n)} for n in data_nodes],
        ],
        "edges": [
            {"data": {"source": "table1", "target": "filter1"}},
            *[{"data": e} for e in edges],
        ],
    }
    return JSONResponse(d)


@router.post("/create_filter_node")
async def create_filter_node(
    user_id: Annotated[str, Depends(get_user_id)],
    new_filter_src: Annotated[int, Form()],
    gc_filter_src: Annotated[str, Form()],
    new_filter_op: Annotated[str, Form()],
    new_filter_comp: Annotated[str, Form()],
) -> Response:
    logger.debug(f"Fetching graph data for user {user_id}")

    src_file = user_data[user_id].files[new_filter_src]
    src_df = src_file.df
    _res = find_node(user_data[user_id].graph, src_file.name)
    assert _res is not None
    src_node_idx, src_node = _res

    # TODO: implement proper logic to differentiate filter ops based on src col type
    # also convert the new_filter_comp to the correct type before comparison
    comp_val = float(new_filter_comp)
    match FilterOps.from_string(new_filter_op):
        case FilterOps.LT:
            new_df = src_df.filter(pl.col(gc_filter_src) < comp_val)
        case _:
            raise ValueError

    user_data[user_id].files.append(
        FileDetails(
            f"{src_file.name}_filter_res",
            "<NA>",
            -1,
            new_df,
        ),
    )
    # TODO: this index-based linkage is horrible
    current_next_idx = len(user_data[user_id].graph)
    new_filter_node = AnalysisNode(
        f"{src_file.name}_filter",  # TODO: better more unique name
        [src_node_idx],
        [current_next_idx + 1],
        AnalysisMethod.FILTER,
    )
    new_res_node = DataNode(
        user_data[user_id].files[-1].name,
        [current_next_idx],
        [],
    )

    user_data[user_id].graph.append(new_filter_node)
    user_data[user_id].graph.append(new_res_node)
    data_nodes = user_data[user_id].graph
    logger.warn(data_nodes)

    assert True, "here"
    edges = generate_edges(user_data[user_id].graph)
    logger.debug(edges)

    assert True, "here"
    d = {
        "nodes": [
            {"data": {"kind": "data", "id": "table1", "name": "Table 1"}},
            {"data": {"kind": "analysis", "id": "filter1", "name": "Filter Node"}},
            *[{"data": node2dict(n)} for n in data_nodes],
        ],
        "edges": [
            {"data": {"source": "table1", "target": "filter1"}},
            *[{"data": e} for e in edges],
        ],
    }
    return JSONResponse(d)
