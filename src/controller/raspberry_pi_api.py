from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/api/raspberry-pi/camera", response_class=HTMLResponse)
async def get_camera(request: Request):
    """

        라즈베리파이에서 서버로 카메라 영상 보내는 API
        from raspberry pi to server

    """
    pass


@router.get("/api/get-camera", response_class=HTMLResponse)
async def get_camera(request: Request):
    """

        라즈베리파이 카메라 영상 가져오는 api
        from server to brawser

    """
    pass