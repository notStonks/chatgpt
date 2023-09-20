import logging
from datetime import datetime

import telegram
from fastapi import FastAPI, Request
from fastapi.responses import Response

import config
import database
from utils import get_buy_keyboard, get_payment_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = database.Database()

app = FastAPI()


@app.post("/hook/")
async def recWebHook(request: Request):
    try:
        body = await request.json()
        logger.info(body)
        status = body["Status"]
        if status == "CONFIRMED":
            await _confirmed_payment(body["OrderId"], body["Amount"])
        if status == "REJECTED":
            await _rejected_payment(body["OrderId"], body["Amount"])
        return Response(status_code=200, content="OK")
    except Exception as _exec:
        logger.error(f"{_exec}")
        return Response({"Error": "Some error occured."})


async def _confirmed_payment(order_id: str, amount: int):
    """
    Посылает пользователю сообщение, что оплата прошла успешно
    и меняет статус в БД
    """
    try:
        user_id = db.get_order_attribute(order_id, "user_id")
        db.set_order_attribute(order_id, "status", "CONFIRMED")
        chat_id = db.get_user_attribute(user_id, "chat_id")
        current_model = db.get_user_attribute(user_id, "current_model")
        amount = amount // 100
        tokens_amount = config.config_yaml[f"tokens_for_{amount}_{current_model}"]
        db.update_n_remaining_tokens(user_id, tokens_amount, amount)
        db.set_user_attribute(user_id, "payment_date", datetime.now())
        bot = telegram.Bot(config.telegram_token)
        async with bot:
            await bot.send_message(chat_id=chat_id, text=f"Успешно куплено {tokens_amount} токенов")

    except Exception as _exec:
        logger.error(f"{_exec}")
        return Response({"Error": "Some error occured."})


async def _rejected_payment(order_id: str, amount: str):
    """
    Посылает пользователю сообщение в случае непрошедшей оплаты
    и отправляет новую ссылку на повторную оплату
    """
    try:
        amount = int(amount) // 100
        payment_url = get_payment_url(order_id, amount)
        buy_keyboard = get_buy_keyboard(payment_url)

        user_id = db.get_order_attribute(order_id, "user_id")
        db.set_order_attribute(order_id, "status", "REJECTED")
        chat_id = db.get_user_attribute(user_id, "chat_id")

        bot = telegram.Bot(config.telegram_token)
        async with bot:
            await bot.send_message(chat_id=chat_id, text="Произошла ошибка. Попробуйте еще раз", reply_markup=buy_keyboard)

    except Exception as _exec:
        logger.error(f"{_exec}")
