from typing import Dict

from fastapi import Depends, APIRouter, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from utils.auth_core import (authenticate_user, create_access_token)
from utils.forms import LoginForm
from utils.settings import settings, templates

router = APIRouter()


@router.post("token")
def login_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, str]:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"username": user.username})

    # Set an HttpOnly cookie in the response. `httponly=True` prevents
    # JavaScript from reading the cookie.
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=f"Bearer {access_token}",
        samesite="strict",
        secure=False
        # httponly=True
    )
    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}


# --------------------------------------------------------------------------
# Home Page
# --------------------------------------------------------------------------
# @router.get("/", response_class=HTMLResponse)
# def index(request: Request):
#     try:
#         user = get_current_user_from_cookie(request)
#     except:
#         user = None
#     context = {
#         "user": user,
#         "request": request,
#     }
#     return templates.TemplateResponse("index.html", context)


# --------------------------------------------------------------------------
# admin Page
# --------------------------------------------------------------------------
# A admin page that only log in users can access.
# @router.get("/admin", response_class=HTMLResponse)
# def index(request: Request):
#     try:
#         user: User = get_current_user_from_cookie(request)
#     except Exception as e:
#         return RedirectResponse("/auth/login")
#     context = {
#         "user": user,
#         "request": request
#     }
#
#     return templates.TemplateResponse("admin.html", context)


# --------------------------------------------------------------------------
# Login - GET
# --------------------------------------------------------------------------
@router.get("/auth/login", response_class=HTMLResponse)
def login_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


# --------------------------------------------------------------------------
# Login - POST
# --------------------------------------------------------------------------

@router.post("/auth/login", response_class=HTMLResponse)
async def login_post(request: Request):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/admin", status.HTTP_302_FOUND)
            login_for_access_token(response=response, form_data=form)
            form.__dict__.update(msg="Login Successful!")
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Username or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)


# --------------------------------------------------------------------------
# Logout
# --------------------------------------------------------------------------
@router.get("/auth/logout", response_class=HTMLResponse)
def login_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response