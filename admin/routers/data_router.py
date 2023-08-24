import datetime
import logging
from datetime import timedelta
from typing import Union

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

import database
from utils.funcs import update_config, stats_count
from utils.auth_core import (get_current_user_from_cookie)
from utils.forms import User, SettingsForm
from utils.settings import templates, Settings
import ruamel.yaml

db = database.Database()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/admin/settings", response_class=HTMLResponse)
def admin(request: Request):
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")

    config, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(open(Settings.FILE_NAME))

    context = {
        "user": user,
        "request": request,
        "settings": config
    }
    headers = {
        "Content-Type": "application/json"
    }
    return templates.TemplateResponse("settings.html", context)


@router.post("/admin/settings", response_class=HTMLResponse)
async def admin(request: Request):
    form = SettingsForm(request)
    await form.load_data()
    logger.info(form.__dict__)
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")

    config, ind, bsi = ruamel.yaml.util.load_yaml_guess_indent(open(Settings.FILE_NAME))
    update_config(config, form)

    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=ind, sequence=ind, offset=bsi)
    with open(Settings.FILE_NAME, 'w') as fp:
        yaml.dump(config, fp)

    context = {
        "user": user,
        "request": request,
        "settings": form
    }
    headers = {
        "Content-Type": "application/json"
    }
    return RedirectResponse("/admin/settings", status_code=303)


@router.get("/admin/statistic", response_class=HTMLResponse)
def statistic(request: Request):
    try:
        user: User = get_current_user_from_cookie(request)
    except Exception as e:
        return RedirectResponse("/auth/login")

    income, count, days = db.get_statistic()
    sum_used_tokens, sum_used_tokens_rub = stats_count(income, days)

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

    income, count, days = db.get_statistic(start, end)
    sum_used_tokens, sum_used_tokens_rub = stats_count(income, days)

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
