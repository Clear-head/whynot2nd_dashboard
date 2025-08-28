from starlette.responses import RedirectResponse

from database import stream_rows, conn_engine, ensure_table_roadkill_info
import controller.kakao_api as kakao_api
import controller.raspberry_pi_api as raspberry_pi_api
import controller.grafana_api as grafana_api

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles



conn = conn_engine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 시작 시 백그라운드에서 stream_rows 실행"""
    asyncio.create_task(stream_rows(conn))
    yield


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="../resource/pages")
app.mount("/pages", StaticFiles(directory="../resource/pages"), name="pages")
app.include_router(kakao_api.router)
app.include_router(grafana_api.router)
app.include_router(raspberry_pi_api.router)

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


@app.get("/fail")
async def fail(request: Request):
    return templates.TemplateResponse("fail.html", {"request": request})



#   예외 핸들러
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled exception: {exc}")
    return RedirectResponse(url="/fail")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code >= 500:
        return RedirectResponse(url="/fail")
    raise exc


if __name__ == "__main__":
    import uvicorn

    ensure_table_roadkill_info(conn)
    uvicorn.run(app, host="127.0.0.1", port=4321)