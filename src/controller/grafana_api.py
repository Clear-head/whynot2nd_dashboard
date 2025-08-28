from typing import Optional

from fastapi.responses import Response
from fastapi import APIRouter
from pydantic import BaseModel

import httpx
from dotenv import load_dotenv
import os

router = APIRouter()


class GrafanaContent(BaseModel):
    panel_id: int
    agg_interval: str
    year_sel: str
    sel_period: Optional[str] = None



@router.post("/api/dashboard/panel")
async def return_panel(content: GrafanaContent):
    load_dotenv()
    GRAFANA_BASE_URL = os.getenv("GRAFANA_BASE_URL")

    print(*content)

    agg_interval_dic = {
        "일": "%EC%9D%BC",
        "월": "%EC%9B%94",
        "년": "%EB%85%84",
        "분기": "%EB%B6%84%EA%B8%B0",
        "반기": "%EB%B0%98%EA%B8%B0"
    }



    panel_url = '<iframe src="http://localhost:3000/d-solo/38eedacf-2392-420d-8c4f-83a81cc1c579/graph?orgId=1&from=1756341474553&to=1756345074553&timezone=browser&refresh=1m&panelId=2&__feature.dashboardSceneSolo=true" width="450" height="200" frameborder="0"></iframe>'
    # if not content.sel_period:
    #     panel_url = f"{GRAFANA_BASE_URL}&panelId={content.panel_id}&var-agg_interval={agg_interval_dic.get(content.agg_interval, "%EC%9D%BC")}&var-year_sel={content.year_sel}&__feature.dashboardSceneSolo=true"
    # else:
    #     sel_period = f"{content.year_sel}-{content.sel_period}"
    #     panel_url = f"{GRAFANA_BASE_URL}&panelId={content.panel_id}&var-agg_interval={agg_interval_dic.get(content.agg_interval, "%EC%9D%BC")}&var-year_sel={content.year_sel}&var-sel_period={sel_period}&__feature.dashboardSceneSolo=true"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                panel_url
            )
            return Response(
                content=response.content,
                media_type="application/javascript"
            )

    except Exception as e:
        raise Exception (f"[GRAFANA API] get api ERROR: {e}")