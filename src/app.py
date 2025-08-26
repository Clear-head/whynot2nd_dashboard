import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import httpx
from dotenv import load_dotenv
import os

from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
templates = Jinja2Templates(directory="../resource/pages")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 시에만 사용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/api/getData")
async def get_data(request: Request):
    """
    지도에 표시할 마커 데이터를 반환하는 API

    Returns:
        JSON 형태의 데이터 배열
        각 데이터는 다음 구조를 가집니다:
        - latitude: float (위도)
        - longitude: float (경도)
        - road: str (도로명 주소 또는 위치 정보)
        - state: int (상태 - 0: 발견, 1: 재발견, 2: 사체 발견)
    """
    try:
        # 실제 구현에서는 데이터베이스에서 데이터를 조회해야 합니다
        # 예: data = await fetch_marker_data_from_database()

        data = [
    {
        "latitude": 36.46201132199759,
        "longitude": 127.8490946787158,
        "road": "대전광역시 유성구 대학로 291",
        "status": 0  # 0: 발견, 1: 재발견, 2: 사체 발견
    },
    {
        "latitude": 36.47201132199759,
        "longitude": 127.8590946787158,
        "road": "대전광역시 유성구 봉명동",
        "status": 1
    },
    {
        "latitude": 36.45201132199759,
        "longitude": 127.8390946787158,
        "road": "대전광역시 유성구 구성동",
        "status": 2
    },
    {
        "latitude": 36.48201132199759,
        "longitude": 127.8690946787158,
        "road": "대전광역시 유성구 전민동",
        "status": 0
    },
    {
        "latitude": 36.44201132199759,
        "longitude": 127.8290946787158,
        "road": "대전광역시 유성구 죽동",
        "status": 1
    }]

        return JSONResponse(content=data)

    except Exception as e:
        print(f"Error in get_data: {e}")
        return JSONResponse(
            content={"error": "데이터를 가져오는 중 오류가 발생했습니다."},
            status_code=500
        )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):

    return templates.TemplateResponse("index.html", {
        "request": request
    })



@app.get("/api/kakao/maps-sdk")
async def proxy_kakao_maps_sdk():

    load_dotenv()
    KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

    print(KAKAO_API_KEY)

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
        print(f"[API] get api key ERROR: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4321)