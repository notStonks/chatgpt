from typing import Optional, Any

import pymongo
import uuid
from datetime import datetime

import config


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(config.mongodb_uri)
        self.db = self.client["chatgpt_telegram_bot"]

        self.user_collection = self.db["user"]
        self.dialog_collection = self.db["dialog"]
        self.order_collection = self.db["order"]

    # --- Admin part
    def get_users(self):
        # self.check_if_user_exists(user_id, raise_exception=True)
        user_dict = self.user_collection.find({},
        {"_id": 1, "username": 1, "first_name": 1, "last_name": 1, "payment_date": 1, "n_bought_tokens": 1, "phone": 1})

        return user_dict