from typing import Optional

from fastapi import APIRouter, requests
from pydantic import BaseModel

router = APIRouter()


class GrafanaContent(BaseModel):
    panel_id: int
    menu_1: str
    menu_2: str
    menu_3: Optional[str] = None


@router.post("/api/dashboard/panel-1")
async def panel_1(content: GrafanaContent):

    base_url = "http://localhost:3000/d-solo/38eedacf-2392-420d-8c4f-83a81cc1c579/graph"
    panel_url = f"{base_url}?orgId=1&panelId={content.panel_id}&from={content.menu_1}&to={content.menu_2}&refresh=1m&__feature.dashboardSceneSolo=true"
    return panel_url

@router.post("/api/dashboard/panel-2")
async def panel_2():
    pass