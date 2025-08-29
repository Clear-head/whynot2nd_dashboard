from database import stream_rows, conn_engine, ensure_table_roadkill_info
import controller.kakao_api as kakao_api
import controller.grafana_api as grafana_api

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles



conn = conn_engine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(stream_rows(conn))
    yield


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="../resource/pages")
app.mount("/pages", StaticFiles(directory="../resource/pages"), name="pages")
app.include_router(kakao_api.router)
app.include_router(grafana_api.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4321",
        "http://localhost:3000",
        "http://localhost:4321"
    ],
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


if __name__ == "__main__":
    import uvicorn

    ensure_table_roadkill_info(conn)
    uvicorn.run(app, host="127.0.0.1", port=4321)