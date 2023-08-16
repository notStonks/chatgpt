import logging
from typing import Dict

from fastapi import Depends, APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse, RedirectResponse

from utils.auth_core import (authenticate_user, create_access_token, get_current_user_from_cookie)
from utils.auth_form import User, LoginForm
from utils.settings import settings, templates
import database

db = database.Database()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")
    users = db.get_users()
    # 359835292
    logger.info(users)
    context = {
        "user": user,
        "request": request,
        "users": users
    }

    return templates.TemplateResponse("admin.html", context)
    # return JSONResponse({"users": users})
