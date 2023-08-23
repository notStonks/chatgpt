import datetime
import logging
from datetime import timedelta
from typing import Union

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

import config
import database
from utils.auth_core import (get_current_user_from_cookie)
from utils.auth_form import User
from utils.settings import templates

db = database.Database()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/admin/statistic", response_class=HTMLResponse)
def statistic(request: Request):
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")
    income, used_tokens, count = db.get_statistic()
    income = sum([item["amount"] for item in income])
    used_tokens = [item["n_used_tokens"] for item in used_tokens]
    sum_used_tokens = {}

    for item in used_tokens:
        for key in item.keys():
            sum_used_tokens[key] = (sum_used_tokens.get(key, 0) +
                                    (item[key]["n_input_tokens"] + item[key]["n_output_tokens"]))

    sum_used_tokens_rub = {}

    for key, val in sum_used_tokens.items():
        sum_used_tokens_rub[key] = val * config.config_yaml[f"rub_for_token_{key}"]

    context = {
        "user": user,
        "request": request,
        "count": count,
        "income": income,
        "sum_used_tokens": sum_used_tokens,
        "sum_used_tokens_rub": sum_used_tokens_rub,
        "min_date": datetime.datetime(2023, 8, 3).strftime("%Y-%m-%d"),
        "max_date": datetime.datetime.now().strftime("%Y-%m-%d"),
    }
    return templates.TemplateResponse("statistic.html", context)


@router.post("/admin/statistic", response_class=HTMLResponse)
def statistic(request: Request,
              all_time: Union[str, None] = Form(default=None),
              month: Union[str, None] = Form(default=None),
              start: Union[str, None] = Form(default=None),
              end: Union[str, None] = Form(default=None),
              ):
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")
    logger.info(start)
    logger.info(end)

    if start and end:
        start_str = start
        end_str = end
        start = datetime.datetime(*[int(i) for i in start.split("-")])
        end = datetime.datetime(*[int(i) for i in end.split("-")])
    else:
        start_str = datetime.datetime(2023, 8, 3).strftime("%Y-%m-%d")
        end_str = datetime.datetime.now().strftime("%Y-%m-%d")
    if all_time:
        start = datetime.datetime(2023, 8, 3)
        end = datetime.datetime.now()
    if month:
        start = datetime.datetime.now() - datetime.timedelta(days=30)
        end = datetime.datetime.now()
    income, used_tokens, count = db.get_statistic(start, end)
    income = sum([item["amount"] for item in income])

    used_tokens = [item["n_used_tokens"] for item in used_tokens]
    sum_used_tokens = {}

    for item in used_tokens:
        for key in item.keys():
            sum_used_tokens[key] = (sum_used_tokens.get(key, 0) +
                                    (item[key]["n_input_tokens"] + item[key]["n_output_tokens"]))

    sum_used_tokens_rub = {}

    for key, val in sum_used_tokens.items():
        sum_used_tokens_rub[key] = val * config.config_yaml[f"rub_for_token_{key}"]

    start_str = datetime.datetime(2023, 8, 3).strftime("%Y-%m-%d")
    end_str = datetime.datetime.now().strftime("%Y-%m-%d")

    context = {
        "user": user,
        "request": request,
        "count": count,
        "income": income,
        "sum_used_tokens": sum_used_tokens,
        "sum_used_tokens_rub": sum_used_tokens_rub,
        "min_date": start_str,
        "max_date": end_str,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d")
    }
    return templates.TemplateResponse("statistic.html", context)


@router.get("/admin", response_class=HTMLResponse)
def admin(request: Request, page: int = 1, limit: int = 10):
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")
    users, count = db.get_users(page, limit)
    # 359835292
    logger.info(users)
    pages = count / limit if count % limit == 0 else count // limit + 1
    context = {
        "user": user,
        "request": request,
        "users": users,
        "count": count,
        "current_page": page,
        "pages": pages
    }

    return templates.TemplateResponse("admin.html", context)


@router.get("/admin/{user_id}")
def user(request: Request, user_id: int):
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")

    user_dict = db.get_user(user_id)

    for key in user_dict["n_used_tokens"].keys():
        logger.info(user_dict["n_used_tokens"][key].items())
        used_toks = sum(item[1] for item in list(user_dict["n_used_tokens"][key].items())[:-1])
        logger.info(list(user_dict["n_used_tokens"][key].items())[-1][1])
        user_dict["n_used_tokens"][key]["used_tokens"] = used_toks

    if "payment_date" in user_dict and user_dict["payment_date"] is not None:

        user_dict["payment_date"] = (user_dict["payment_date"] + timedelta(hours=3)).strftime('%m.%d.%Y %H:%M')

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

    logger.info(user_dict)
    if gpt35turbo:
        db.set_n_remaining_tokens(user_id, model="gpt-3.5-turbo", tokens_amount=gpt35turbo)
    if gpt4:
        db.set_n_remaining_tokens(user_id, model="gpt-4", tokens_amount=gpt4)

    db.set_user_attribute(user_id, "ban", ban)

    return RedirectResponse(f"/admin/{user_id}", status_code=303)
