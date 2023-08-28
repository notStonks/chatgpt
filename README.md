Телеграм бот с чат gpt. Основой всего проекта стал телеграм бот https://github.com/karfly/chatgpt_telegram_bot
В этой версии бота добавлены:
 - админка на fastapi с Jinja2
 - покупка токенов через Тинькофф банк
 - внесены изменения в конфиг добавлено несколько ключей
 - модифицирована база данных. Расширена коллекция user, добавлены коллекции: order - данные покупки токенов, 
day - данные потраченных токенов за каждый день.

Технологический стек:
 - python
 - python-telegram-bot
 - fastapi
 - gunicorn
 - uvicorn
 - jinja2
 - pymongo
 - nginx
 - certbot