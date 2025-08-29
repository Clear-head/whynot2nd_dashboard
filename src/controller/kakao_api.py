from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
import httpx
from dotenv import load_dotenv
import os

from src.database.roadkill_3 import conn_engine, lat_lon_stat_info


router = APIRouter()

@router.get("/api/kakao/get-data")
async def get_data():
    """
    지도에 표시할 마커 데이터를 반환하는 API

    Returns:
        JSON 형태의 데이터 배열
        각 데이터는 다음 구조를 가집니다:
        - latitude: float (위도)
        - longitude: float (경도)
        - contents: str (도로명 주소 또는 위치 정보)
        - state: int (상태 - 0: 발견, 1: 재발견, 2: 사체 발견)
    """
    conn = conn_engine()
    data = lat_lon_stat_info(conn)
    return JSONResponse(content=data)


@router.get("/api/kakao/maps-sdk")
async def proxy_kakao_maps_sdk():

    load_dotenv()
    KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_API_KEY}"
            )
            return Response(
                content=response.content,
                media_type="application/javascript"
            )

    except Exception as e:
        raise Exception (f"[KAKAO API] get api key ERROR: {e}")
