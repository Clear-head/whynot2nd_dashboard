from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
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

    if not GRAFANA_BASE_URL:
        raise HTTPException(status_code=500, detail="GRAFANA_BASE_URL not configured")


    # URL 인코딩된 값들
    agg_interval_dic = {
        "일": "%EC%9D%BC",
        "월": "%EC%9B%94",
        "년": "%EB%85%84",
        "분기": "%EB%B6%84%EA%B8%B0",
        "반기": "%EB%B0%98%EA%B8%B0"
    }


    if not content.sel_period or content.sel_period == "":
        panel_url = f"{GRAFANA_BASE_URL}&panelId={content.panel_id}&var-agg_interval={agg_interval_dic.get(content.agg_interval, '%EC%9D%BC')}&var-year_sel={content.year_sel}&__feature.dashboardSceneSolo=true"
    else:
        sel_period_value = f"{content.year_sel}-{content.sel_period.zfill(2)}"  # 01, 02 형태로 패딩
        panel_url = f"{GRAFANA_BASE_URL}&panelId={content.panel_id}&var-agg_interval={agg_interval_dic.get(content.agg_interval, '%EC%9D%BC')}&var-year_sel={content.year_sel}&var-sel_period={sel_period_value}&__feature.dashboardSceneSolo=true"

    return {"url": panel_url}