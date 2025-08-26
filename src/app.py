import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import httpx
from dotenv import load_dotenv
import os


app = FastAPI()
templates = Jinja2Templates(directory="../resource/pages")


@app.post("/api/getData")
async def get_data(request: Request):
    pass


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):

    return templates.TemplateResponse("index.html", {
        "request": request
        # "items": items
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