from datetime import datetime
import logging
import uuid
from typing import Optional, Any

import pymongo

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(config.mongodb_uri)
        self.db = self.client["chatgpt_telegram_bot"]

        self.user_collection = self.db["user"]
        self.dialog_collection = self.db["dialog"]
        self.order_collection = self.db["order"]

        self.day_collection = self.db["day"]


    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        if self.user_collection.count_documents({"_id": user_id}) > 0:
            return True
        else:
            if raise_exception:
                raise ValueError(f"User {user_id} does not exist")
            else:
                return False

    def add_new_user(
            self,
            user_id: int,
            chat_id: int,
            username: str = "",
            first_name: str = "",
            last_name: str = "",
            phone: str = "",

    ):
        user_dict = {
            "_id": user_id,
            "chat_id": chat_id,

            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,

            "last_interaction": datetime.datetime.now(),
            "first_seen": datetime.datetime.now(),


            "current_dialog_id": None,
            "current_chat_mode": "assistant",
            "current_model": config.models["available_text_models"][0],

            "n_used_tokens": {
                config.models["available_text_models"][0]: {
                    "n_input_tokens": 0,
                    "n_output_tokens": 0,
                    "n_remaining_tokens": config.tokens_limit_for_new_user
                }
            },

            "n_bought_tokens": {
                config.models["available_text_models"][0]: 0
            },

            # "n_remaining_tokens": 5000,

            "n_generated_images": 0,

            "n_transcribed_seconds": 0.0, # voice message transcription

            "payment_date": None,

            "ban": False
        }

        if not self.check_if_user_exists(user_id):
            self.user_collection.insert_one(user_dict)

    def start_new_dialog(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)
        model = self.get_user_attribute(user_id, "current_model")
        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "user_id": user_id,
            "chat_mode": self.get_user_attribute(user_id, "current_chat_mode"),
            "start_time": datetime.datetime.now(),
            "model": model,
            "messages": []
        }

        # add new dialog
        self.dialog_collection.insert_one(dialog_dict)

        self.update_n_used_tokens(user_id, model, 0, 0)

        # update user's current dialog
        self.user_collection.update_one(
            {"_id": user_id},
            {"$set": {"current_dialog_id": dialog_id}}
        )

        return dialog_id


    def add_new_order(self, user_id: int, amount: int):
        order_id = str(uuid.uuid4())
        id = str(uuid.uuid4())

        order_dict = {
            "_id": id,
            "user_id": user_id,
            "order_id": order_id,
            "amount": amount,
            "status": "NEW",
            "time": datetime.datetime.now()
        }
        self.order_collection.insert_one(order_dict)

        return order_id

    def add_new_day(self,):
        id = str(uuid.uuid4())
        # date = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
        date = datetime.date.today().isoformat()
        n_used_tokens = {}
        for m in config.models["available_text_models"]:
            # if model == m:
            #     n_used_tokens[m] = {
            #         "n_input_tokens": n_input_tokens,
            #         "n_output_tokens": n_output_tokens,
            #     }
            # else:
            n_used_tokens[m] = {
                "n_input_tokens": 0,
                "n_output_tokens": 0,
            }

        day_dict = {
            "_id": id,
            "date": date,
            "n_used_tokens": n_used_tokens
        }

        return self.day_collection.insert_one(day_dict)

    def get_day(self):
        day_dict = self.day_collection.find_one({"date": datetime.date.today().isoformat()})
        if not day_dict:
            day_dict = self.add_new_day()
            day_dict = self.day_collection.find_one({"_id": day_dict.inserted_id})
        return day_dict["_id"], day_dict["n_used_tokens"]

    def update_day(self, id: str, value: Any):
        self.day_collection.update_one({"_id": id}, {"$set": {"n_used_tokens": value}})

    def get_order_attribute(self, order_id: str, key: str):
        order_dict = self.order_collection.find_one({"order_id": order_id})
        return order_dict[key]

    def set_order_attribute(self, order_id: str, key: str, value: Any):
        self.order_collection.update_one({"order_id": order_id},  {"$set": {key: value}})

    def get_user_attribute(self, user_id: int, key: str):
        self.check_if_user_exists(user_id, raise_exception=True)
        user_dict = self.user_collection.find_one({"_id": user_id})

        if key not in user_dict:
            return None

        return user_dict[key]

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.check_if_user_exists(user_id, raise_exception=True)
        self.user_collection.update_one({"_id": user_id}, {"$set": {key: value}})

    def update_n_remaining_tokens(self, user_id: int,  tokens_amount: int):
        n_used_tokens_dict = self.get_user_attribute(user_id, "n_used_tokens")
        model = self.get_user_attribute(user_id, "current_model")

        n_used_tokens_dict[model]["n_remaining_tokens"] += tokens_amount

        self.set_user_attribute(user_id, "n_used_tokens", n_used_tokens_dict)

    def update_n_used_tokens(self, user_id: int, model: str, n_input_tokens: int, n_output_tokens: int):
        n_used_tokens_dict = self.get_user_attribute(user_id, "n_used_tokens")
        # n_remaining_tokens = self.get_user_attribute(user_id, "n_remaining_tokens")

        if model in n_used_tokens_dict:
            n_used_tokens_dict[model]["n_input_tokens"] += n_input_tokens
            n_used_tokens_dict[model]["n_output_tokens"] += n_output_tokens
            n_used_tokens_dict[model]["n_remaining_tokens"] -= n_input_tokens + n_output_tokens

        else:
            n_used_tokens_dict[model] = {
                "n_input_tokens": n_input_tokens,
                "n_output_tokens": n_output_tokens,
                "n_remaining_tokens": config.tokens_limit_for_new_user - n_input_tokens - n_output_tokens
            }

        id, today = self.get_day()

        today[model]["n_input_tokens"] += n_input_tokens
        today[model]["n_output_tokens"] += n_output_tokens
        self.update_day(id, today)

        # n_remaining_tokens -= n_input_tokens + n_output_tokens

        self.set_user_attribute(user_id, "n_used_tokens", n_used_tokens_dict)
        # self.set_user_attribute(user_id, "n_remaining_tokens", n_remaining_tokens)

    def update_n_bought_tokens(self, user_id: int, model: str, quantity: int):
        n_bought_tokens_dict = self.get_user_attribute(user_id, "n_bought_tokens")

        if model in n_bought_tokens_dict:
            n_bought_tokens_dict[model] += quantity
        else:
            n_bought_tokens_dict[model] = quantity

        self.set_user_attribute(user_id, "n_used_tokens", n_bought_tokens_dict)

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        dialog_dict = self.dialog_collection.find_one({"_id": dialog_id, "user_id": user_id})
        return dialog_dict["messages"]

    def set_dialog_messages(self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        self.dialog_collection.update_one(
            {"_id": dialog_id, "user_id": user_id},
            {"$set": {"messages": dialog_messages}}
        )

    # --- Admin part
    def get_user(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)
        user_dict = self.user_collection.find_one({"_id": user_id})

        return user_dict

db = Database()

for i in range(10):
    db.set_order_attribute(i, "status", "CONFIRMED")
