import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import auth_router, data_router

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Create a "database" to hold your data. This is just for example purposes. In
# a real world scenario you would likely connect to a SQL or NoSQL database.
# class DataBase(BaseModel):
#     user: List[User]
#
#
# DB = DataBase(
#     user=[
#         User(username="user1@gmail.com", hashed_password=crypto.hash("12345")),
#         User(username="user2@gmail.com", hashed_password=crypto.hash("12345")),
#     ]
# )


app = FastAPI()
# origins = [
#     "http://127.0.0.1:8080",
#     "http://localhost:8080",
#     "http://172.18.0.1"
#     "https://172.18.0.1"
#
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)


# @app.get("/i")
# def read_root(request: Request):
#     client_host = request.client.host
#     return {"client_host": client_host}


app.include_router(auth_router.router)
app.include_router(data_router.router)

