import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import httpx
from dotenv import load_dotenv
import os

app = FastAPI()
templates = Jinja2Templates(directory="../resource/pages")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 시에만 사용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):

    return templates.TemplateResponse("index.html", {
        "request": request
    })


@app.get("/api/raspberry-pi/camera", response_class=HTMLResponse)
async def get_camera(request: Request):
    """

        라즈베리파이에서 서버로 카메라 영상 보내는 API
        from raspberry pi to server

    """
    pass


@app.get("/api/get-camera", response_class=HTMLResponse)
async def get_camera(request: Request):
    """

        라즈베리파이 카메라 영상 가져오는 api
        from server to brawser

    """
    pass


@app.get("/api/kakao/get-data")
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

        data = None

        return JSONResponse(content=data)

    except Exception as e:
        print(f"Error in get_data: {e}")
        return JSONResponse(
            content={"error": "데이터를 가져오는 중 오류가 발생했습니다."},
            status_code=500
        )


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