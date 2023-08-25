from hashlib import sha256

import requests


class TinkoffPayment(object):
    def __init__(self, terminal_key: str, password: str):
        """
        Инициализация терминала

        :param terminal_key: Идентификатор терминала
        :param password: Пароль от терминала
        """
        self.terminal_key = terminal_key
        self.password = password

    def get_signature(self, data: dict) -> str:
        """
        Подпись запроса

        См. документацию: https://oplata.tinkoff.ru/landing/develop/documentation/request_sign

        :param data:
        :return:
        """
        data_list = list()
        for d in sorted(list(data)):
            if d in ['Receipt', 'DATA']:
                continue
            data_list.append(data.get(d))
        return sha256(''.join(data_list).encode()).hexdigest()

    @staticmethod
    def _get_language(language: str) -> str:
        """
        Проверка переданного языкового кода. Доступно два: ru и en

        :param language: язык платежной формы
        :return: Выбранный язык формы или русский язык по умолчанию
        """
        default = 'ru'
        if language.lower() not in ['ru', 'en']:
            return default
        else:
            return language.lower()

    def init(self, order_id, amount, phone=None, ip=None, description=None, language=None,
             sign_request=False, notification_url=None):
        """
        Init - создание платежа

        Параметры:
            order_id: Идентификатор заказа в системе продавца\n
            amount: Сумма в копейках\n
            phone: Номер телефона покупателя\n
            ip: IP-адрес покупателя\n
            description: Описание заказа\n
            language: Язык платежной формы (ru или en)\n
            sign_request: Подпись запроса\n
            notification_url: Адрес для получения http нотификаций\n

        Возвращаемое значение:
            Объект json с ключами\n
            TerminalKey - Идентификатор терминала\n
            Amount - Сумма в копейках\n
            OrderId - Идентификатор заказа в системе продавца\n
            Success - Выполнение платежа\n
            Status - Статус платежа\n
            PaymentId - Идентификатор платежа в системе банка\n
            ErrorCode - Код ошибки\n
            PaymentURL - Ссылка на платежную форму\n
            Message - Краткое описание ошибки\n
            Details - Подробное описание ошибки\n
        """
        request_data = dict()
        request_data['TerminalKey'] = self.terminal_key
        request_data['Amount'] = amount
        request_data['OrderId'] = order_id


        if ip:
            request_data['IP'] = ip
        if description:
            request_data['Description'] = description
        if language:
            request_data['Language'] = self._get_language(language)
        if sign_request:
            request_data['Token'] = self.get_signature(request_data)
        if notification_url:
            request_data['NotificationURL'] = notification_url
        if phone:
            request_data['DATA'] = {'Phone': phone}

        request = requests.post('https://securepay.tinkoff.ru/v2/Init', json=request_data)
        response_data = request.json()

        if not response_data.get('Success'):
            raise PaymentException(response_data)

        return response_data

    def cancel(self, payment_id):
        """
        Cancel - отмена платежа

        Параметры:
            payment_id - Идентификатор платежа в системе банка

        Возвращаемое значение:
            Объект json с ключами:\n
            TerminalKey - Идентификатор терминала\n
            OrderId - Идентификатор заказа в системе продавца\n
            Success - Выполнение платежа\n
            Status - Статус платежа\n
            PaymentId - Уникальный идентификатор транзакции в системе банка\n
            ErrorCode - Код ошибки. Если ошибки не произошло, передайте значение «0»\n
            Message - Краткое описание ошибки\n
            Details - Подробное описание ошибки\n
            OriginalAmount - Сумма до возврата в копейках\n
            NewAmount - Сумма после возврата в копейках\n
        """
        data = dict()
        data['TerminalKey'] = self.terminal_key
        data['PaymentId'] = payment_id
        data['Token'] = self.get_signature(data)

        url = 'https://securepay.tinkoff.ru/v2/Cancel'
        request = requests.post(url, json=data)
        data = request.json()

        if not data.get('Success'):
            raise PaymentException(data)

        return data

    def get_state(self, payment_id, ip=None):
        """
        Возвращает текущий статус платежа.

        Параметры:
            payment_id - Идентификатор платежа в системе банка\n
            ip - IP-адрес покупателя

        Возвращаемое значение:
            Объект json с ключами:\n
            TerminalKey - Идентификатор терминала\n
            OrderId - Идентификатор заказа в системе продавца\n
            Success - Выполнение платежа\n
            Status - Статус платежа\n
            PaymentId - Уникальный идентификатор транзакции в системе банка\n
            ErrorCode - Код ошибки. Если ошибки не произошло, передайте значение «0»\n
            Message - Краткое описание ошибки\n
            Details - Подробное описание ошибки\n
            Amount - Сумма операции в копейках\n

        """
        url = 'https://securepay.tinkoff.ru/v2/GetState'

        data = dict()
        data['TerminalKey'] = self.terminal_key
        data['PaymentId'] = payment_id
        if ip:
            data['IP'] = ip

        data['Token'] = self.get_signature(data)

        request = requests.post(url, json=data)
        data = request.json()

        if not data.get('Success'):
            raise PaymentException(data)
        return data

    def resend(self):
        """
        Resend - отправка недоставленных нотификаций
        Метод предназначен для отправки всех неотправленных нотификаций,
        например, в случае недоступности в какой-либо момент времени сайта
        продавца. Подробнее о нотификациях https://www.tinkoff.ru/kassa/develop/api/notifications/

        Возвращаемое значение:
            Объект json с ключами:\n
            TerminalKey - Идентификатор терминала\n
            Count - Количество сообщений, отправляемых повторно\n
            Success - Выполнение платежа\n
            ErrorCode - Код ошибки. Если ошибки не произошло, передайте значение «0»\n
            Message - Краткое описание ошибки\n
            Details - Подробное описание ошибки\n
        """
        data = dict()
        data['TerminalKey'] = self.terminal_key
        data['Token'] = self.get_signature(data)

        url = 'https://securepay.tinkoff.ru/v2/Resend'

        request = requests.post(url, json=data)
        response = request.json()

        return response


class PaymentException(Exception):
    def __init__(self, error):
        self.raw = error
        self.code = error['ErrorCode']
        self.message = error['Message']
        self.details = error['Details']
        self.success = error['Success']

    def __repr__(self):
        return "<TinkoffException success={} code={} message={} details={}>".format(
            self.success, self.code, self.message, self.details
        )





