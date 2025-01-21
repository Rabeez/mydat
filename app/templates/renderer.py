from typing import Any, NotRequired, TypedDict

import fastapi
from fastapi.responses import HTMLResponse
from jinja2_fragments import render_block
from jinja2_fragments.fastapi import Jinja2Blocks

templates = Jinja2Blocks(directory="app/templates")


class RenderArgs(TypedDict):
    template_name: str
    # TODO: define context typed-dicts for every invocation of render()
    # this is to ensure that it's easy to be correct from python side and not miss things that are needed in the template
    # REFER TO TODO LIST AT END OF THIS FILE
    context: dict[str, Any]
    block_name: NotRequired[str]


def render(*renderables: RenderArgs) -> HTMLResponse:
    # NOTE: Single renderable for normal responses and 2 renderables for HTMX-OOB updates
    assert len(renderables) in [1, 2]

    partials = []
    for renderable in renderables:
        template_name = renderable.get("template_name")
        context = renderable.get("context")
        block_name = renderable.get("block_name", None)

        if block_name is None:
            partial = templates.get_template(template_name).render(context)
        else:
            partial = render_block(
                templates.env,
                template_name,
                block_name,
                **context,
            )
        partials.append(partial)

    return HTMLResponse(
        status_code=fastapi.status.HTTP_200_OK,
        content="\n".join(partials),
    )


# page base:
#     @ page_dataflow  >> normal include for reuse
# 7   @ frag chart list  >> make fragment block
#           charts
# 7   @ frag chart type  >> make inline
#          chart_kind
#     chart_kinds
# page dataflow:
# 7   @ frag gc filter src  >> make fragment block
#         gc filter src
#     files
#     graph_data
# page_chart:
# 7   @ frag chart controls  >> make fragment block
#         chart_id
#         chart
#         actual_chart
#     chart
