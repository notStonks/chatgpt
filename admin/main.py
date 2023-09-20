import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import auth_router, data_router

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)

app.include_router(auth_router.router)
app.include_router(data_router.router)

