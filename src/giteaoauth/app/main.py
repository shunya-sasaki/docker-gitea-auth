import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from giteaoauth.utils import CustomLogger
from giteaoauth.utils import GitVersion


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event for the FastAPI application."""
    if Path("./js").exists():
        app.mount("/js", StaticFiles(directory="./js"), name="")
    yield


app = FastAPI(lifespan=lifespan, version=GitVersion)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
routers: list[APIRouter] = []
for router in routers:
    app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    """Render the index page."""
    if Path("./js").exists():
        templates = Jinja2Templates(directory="./js")
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse("NO GUI!")


@app.get("/version/")
def get_version() -> str:
    """Get the version of the application."""
    return app.version


def start() -> None:
    """Run the FastAPI application."""
    if config.workers < 1:
        # TODO
        ncpu = os.cpu_count()
        if ncpu is None:
            workers = 1
        else:
            workers = (ncpu - 5) * 2 + 1
    else:
        workers = config.workers
    uvicorn.run(
        f"src.{GitVersion.package_name()}.app.main:app",
        host=config.host,
        port=config.port,
        workers=workers,
        log_config=CustomLogger.create_config(),  # type: ignore[call-arg],
        log_level=config.log_level,
        reload=False,
    )


def dev() -> None:
    """Run the FastAPI application in development mode."""
    src_dirpath = Path("../src")
    if not src_dirpath.exists():
        includes = [src_dirpath.as_posix()]
    else:
        includes = []
    uvicorn.run(
        f"src.{GitVersion.package_name()}.app.main:app",
        host=config.host,
        port=config.port,
        reload=True,
        reload_includes=includes,
        log_level=config.log_level,
        workers=1,
    )
