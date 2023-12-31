import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

import config
from tinkoff import TinkoffPayment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_payment_url(order_id: str, amount: int):
    try:
        payment = TinkoffPayment(terminal_key=str(config.terminal_key), password=config.password)

        payment_result = payment.init(
            order_id, str(amount*100),
            sign_request=True,
            notification_url=config.notification_url,
        )
        payment_url = payment_result['PaymentURL']
        return payment_url

    except AttributeError as _exec:
        logger.error(_exec)
    except Exception as _exec:
        logger.error(f"{_exec}")




def get_buy_keyboard(payment_url: str):
    btn = InlineKeyboardButton(text="Оплатить", url=payment_url)
    inlinekeyboard = InlineKeyboardMarkup([[btn]])

    return inlinekeyboard

