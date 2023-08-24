
from fastapi.templating import Jinja2Templates


class Settings:
    SECRET_KEY: str = "4251ff00da7a0409d395ad48712e57be18ff9bd5c6ed66bcf0e04e29038151fb"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS = 14
    COOKIE_NAME = "access_token"
    FILE_NAME = '../config/config.yml'


settings = Settings()

templates = Jinja2Templates(directory="templates")

