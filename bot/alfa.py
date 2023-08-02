from hashlib import sha256
import requests


class TinkoffPayment(object):
    def __init__(self, user_name: str, password: str):

        self.user_name = user_name
        self.password = password

    @staticmethod
    def _get_language(language: str) -> str:

        default = 'ru'
        if language.lower() not in ['ru', 'en']:
            return default
        else:
            return language.lower()

    def register(self, order_number, amount, phone=None, ip=None, description=None, language=None,
                 dynamic_callback_url=None):
        request_data = dict()
        request_data['userName'] = self.user_name
        request_data['amount'] = amount
        request_data['orderNumber'] = order_number

        if ip:
            request_data['ip'] = ip
        if description:
            request_data['Description'] = description
        if language:
            request_data['language'] = self._get_language(language)
        # if sign_request:
        #     request_data['Token'] = self.get_signature(request_data)
        if dynamic_callback_url:
            request_data['dynamicCallbackUrl'] = dynamic_callback_url
        # if phone:
        #     request_data['DATA'] = {'Phone': phone}

        request = requests.post('https://alfa.rbsuat.com/payment/rest/register.do', json=request_data)
        response_data = request.json()

        if not response_data.get('Success'):
            raise PaymentException(response_data)

        return response_data

    # def cancel(self, payment_id):
    #     """
    #     Cancel - отмена платежа
    #
    #     Параметры:
    #         payment_id - Идентификатор платежа в системе банка
    #
    #     Возвращаемое значение:
    #         Объект json с ключами:\n
    #         TerminalKey - Идентификатор терминала\n
    #         OrderId - Идентификатор заказа в системе продавца\n
    #         Success - Выполнение платежа\n
    #         Status - Статус платежа\n
    #         PaymentId - Уникальный идентификатор транзакции в системе банка\n
    #         ErrorCode - Код ошибки. Если ошибки не произошло, передайте значение «0»\n
    #         Message - Краткое описание ошибки\n
    #         Details - Подробное описание ошибки\n
    #         OriginalAmount - Сумма до возврата в копейках\n
    #         NewAmount - Сумма после возврата в копейках\n
    #     """
    #     data = dict()
    #     data['TerminalKey'] = self.terminal_key
    #     data['PaymentId'] = payment_id
    #     data['Token'] = self.get_signature(data)
    #
    #     url = 'https://securepay.tinkoff.ru/v2/Cancel'
    #     request = requests.post(url, json=data)
    #     data = request.json()
    #
    #     if not data.get('Success'):
    #         raise PaymentException(data)
    #
    #     return data
    #
    # def get_state(self, payment_id, ip=None):
    #     """
    #     Возвращает текущий статус платежа.
    #
    #     Параметры:
    #         payment_id - Идентификатор платежа в системе банка\n
    #         ip - IP-адрес покупателя
    #
    #     Возвращаемое значение:
    #         Объект json с ключами:\n
    #         TerminalKey - Идентификатор терминала\n
    #         OrderId - Идентификатор заказа в системе продавца\n
    #         Success - Выполнение платежа\n
    #         Status - Статус платежа\n
    #         PaymentId - Уникальный идентификатор транзакции в системе банка\n
    #         ErrorCode - Код ошибки. Если ошибки не произошло, передайте значение «0»\n
    #         Message - Краткое описание ошибки\n
    #         Details - Подробное описание ошибки\n
    #         Amount - Сумма операции в копейках\n
    #
    #     """
    #     url = 'https://securepay.tinkoff.ru/v2/GetState'
    #
    #     data = dict()
    #     data['TerminalKey'] = self.terminal_key
    #     data['PaymentId'] = payment_id
    #     if ip:
    #         data['IP'] = ip
    #
    #     data['Token'] = self.get_signature(data)
    #
    #     request = requests.post(url, json=data)
    #     data = request.json()
    #
    #     if not data.get('Success'):
    #         raise PaymentException(data)
    #     return data
    #
    # def resend(self):
    #     """
    #     Resend - отправка недоставленных нотификаций
    #     Метод предназначен для отправки всех неотправленных нотификаций,
    #     например, в случае недоступности в какой-либо момент времени сайта
    #     продавца. Подробнее о нотификациях https://www.tinkoff.ru/kassa/develop/api/notifications/
    #
    #     Возвращаемое значение:
    #         Объект json с ключами:\n
    #         TerminalKey - Идентификатор терминала\n
    #         Count - Количество сообщений, отправляемых повторно\n
    #         Success - Выполнение платежа\n
    #         ErrorCode - Код ошибки. Если ошибки не произошло, передайте значение «0»\n
    #         Message - Краткое описание ошибки\n
    #         Details - Подробное описание ошибки\n
    #     """
    #     data = dict()
    #     data['TerminalKey'] = self.terminal_key
    #     data['Token'] = self.get_signature(data)
    #
    #     url = 'https://securepay.tinkoff.ru/v2/Resend'
    #
    #     request = requests.post(url, json=data)
    #     response = request.json()
    #
    #     return response


class PaymentException(Exception):
    def __init__(self, error):
        self.raw = error
        self.code = error['errorCode']
        self.message = error['errorMessage']
        # self.details = error['Details']
        # self.success = error['Success']

    def __repr__(self):
        return "<TinkoffException code={} message={}>".format(
            self.code, self.message )
