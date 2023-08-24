from typing import List, Optional

from fastapi import Request
from pydantic import BaseModel


class User(BaseModel):
    username: str
    hashed_password: str


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.username:
            self.errors.append("Username is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False


class SettingsForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.telegram_token: Optional[str] = None
        self.openai_api_key: Optional[str] = None
        self.tokens_limit_for_new_user: Optional[int] = None
        self.tokens_for_200_gpt3: Optional[int] = None
        self.tokens_for_500_gpt3: Optional[int] = None
        self.tokens_for_1000_gpt3: Optional[int] = None
        self.tokens_for_200_gpt4: Optional[int] = None
        self.tokens_for_500_gpt4: Optional[int] = None
        self.tokens_for_1000_gpt4: Optional[int] = None
        self.token_gpt3: Optional[float] = None
        self.token_gpt4: Optional[float] = None

    async def load_data(self):
        form = await self.request.form()
        self.telegram_token = form.get("telegram_token")
        self.openai_api_key = form.get("openai_api_key")
        self.tokens_limit_for_new_user = int(form.get("tokens_limit_for_new_user"))
        self.tokens_for_200_gpt3 = int(form.get("tokens_for_200_gpt3"))
        self.tokens_for_500_gpt3 = int(form.get("tokens_for_500_gpt3"))
        self.tokens_for_1000_gpt3 = int(form.get("tokens_for_1000_gpt3"))
        self.tokens_for_200_gpt4 = int(form.get("tokens_for_200_gpt4"))
        self.tokens_for_500_gpt4 = int(form.get("tokens_for_500_gpt4"))
        self.tokens_for_1000_gpt4 = int(form.get("tokens_for_1000_gpt4"))
        self.token_gpt3 = float(form.get("token_gpt3"))
        self.token_gpt4 = float(form.get("token_gpt4"))
