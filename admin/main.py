from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers.auth_router import router as auth_router


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
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)

app.include_router(auth_router)

