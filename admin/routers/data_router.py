import logging
from typing import Dict, Optional, Annotated, Union

from fastapi import Depends, APIRouter, HTTPException, Request, Response, status, Form
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
    users, count = db.get_users()
    # 359835292
    logger.info(users)
    context = {
        "user": user,
        "request": request,
        "users": users,
        "count": count
    }

    return templates.TemplateResponse("admin.html", context)
    # return JSONResponse({"users": users})


@router.get("/admin/{user_id}")
def user(request: Request, user_id: int):
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")
    user_dict = db.get_user(user_id)
    # 359835292
    logger.info(user_dict)
    for key in user_dict["n_used_tokens"].keys():
        logger.info(user_dict["n_used_tokens"][key].items())
        used_toks = sum(item[1] for item in list(user_dict["n_used_tokens"][key].items())[:-1])
        # remaining_toks = sum(item[1] for item in list(user_dict["n_used_tokens"][key].items())[-1])
        logger.info(list(user_dict["n_used_tokens"][key].items())[-1][1])
        # used_toks = sum(user_dict["n_used_tokens"][key].items())
        # logger.info(used_toks)
        user_dict["n_used_tokens"][key]["used_tokens"] = used_toks
        # user_dict["n_used_tokens"][key]["remaining_tokens"] = list(user_dict["n_used_tokens"][key].items())[-1][1]
        # user_dict["n_remaining_tokens"][key] = remaining_toks

    if "payment_date" in user_dict and user_dict["payment_date"] is not None:
        user_dict["payment_date"] = user_dict["payment_date"].strftime('%m.%d.%Y %H:%M')
    logger.info(user_dict)
    context = {
        "user": user,
        "request": request,
        "user_dict": user_dict
    }

    return templates.TemplateResponse("edit.html", context)


@router.post("/admin/change/{user_id}")
def update_user(request: Request, user_id: int, gpt35turbo: Union[int, None] = Form(default=None), gpt4: Union[int, None] = Form(default=None), ban: bool = Form(False)):
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")
    user_dict = db.get_user(user_id)
    # 359835292
    logger.info(user_dict)
    if gpt35turbo:
        db.set_n_remaining_tokens(user_id, model="gpt-3.5-turbo", tokens_amount=gpt35turbo)
    if gpt4:
        db.set_n_remaining_tokens(user_id, model="gpt-4", tokens_amount=gpt4)

    db.set_user_attribute(user_id, "ban", ban)

    return RedirectResponse(f"/admin/{user_id}", status_code=303)
