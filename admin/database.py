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
    def get_users(self, page: int, limit: int):
        # self.check_if_user_exists(user_id, raise_exception=True)
        user_dict = (self.user_collection.
                     find({},
                          {"_id": 1, "username": 1,
                           "first_name": 1, "last_name": 1,
                           "payment_date": 1, "n_bought_tokens": 1,
                           "phone": 1, "ban": 1}).skip((page - 1) * limit).limit(limit))

        return user_dict, self.user_collection.count()

    def get_user(self, user_id: int):
        # self.check_if_user_exists(user_id, raise_exception=True)
        user_dict = user_dict = self.user_collection.find_one({"_id": user_id},
        {"_id": 1, "username": 1, "first_name": 1, "last_name": 1, "payment_date": 1, "n_used_tokens": 1, "n_bought_tokens": 1, "phone": 1, "ban": 1})

        return user_dict

    def get_user_attribute(self, user_id: int, key: str):
        user_dict = self.user_collection.find_one({"_id": user_id})

        if key not in user_dict:
            return None

        return user_dict[key]

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.user_collection.update_one({"_id": user_id}, {"$set": {key: value}})

    def set_n_remaining_tokens(self, user_id: int, model: str,  tokens_amount: int):
        n_used_tokens_dict = self.get_user_attribute(user_id, "n_used_tokens")

        n_used_tokens_dict[model]["n_remaining_tokens"] = tokens_amount

        self.set_user_attribute(user_id, "n_used_tokens", n_used_tokens_dict)

    def get_statistic(self):
        income = self.order_collection.find({"status": "CONFIRMED"}, {"amount": 1})
        used_tokens = self.user_collection.find({}, {"n_used_tokens": 1})
        return income, used_tokens
