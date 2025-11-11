import json
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class PizzaSize(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_PIZZA_SIZE":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("size_")

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]

        size_mapping = {
            "size_small": "Small (25cm)",
            "size_medium": "Medium (30cm)",
            "size_large": "Large (35cm)",
            "size_extra_large": "Extra Large (40cm)",
        }

        pizza_size = size_mapping.get(callback_data)
        order_json["pizza_size"] = pizza_size

        storage.update_user_order_json(telegram_id, order_json)

        storage.update_user_state(telegram_id, "WAIT_FOR_DRINKS")

        messenger.answer_callback_query(update["callback_query"]["id"])

        messenger.delete_message(chat_id=chat_id, message_id=message_id)

        messenger.send_message(
            chat_id=chat_id,
            text=f"Perfect! 🎯 \nSize {pizza_size} selected.\nWould you like a drink? 🥤",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "🥤 Coca-cola",
                                "callback_data": "drink_coca_cola",
                            },
                            {"text": "🥤 Pepsi", "callback_data": "drink_pepsi"},
                        ],
                        [
                            {
                                "text": "🍊 Orange Juice",
                                "callback_data": "drink_orange_juice",
                            },
                            {
                                "text": "🍏 Apple Juice",
                                "callback_data": "drink_apple_juice",
                            },
                        ],
                        [
                            {"text": "💧 Water", "callback_data": "drink_water"},
                            {"text": "🧊 Iced Tea", "callback_data": "drink_iced_tea"},
                        ],
                        [
                            {
                                "text": "🚫 No drinks",
                                "callback_data": "drink_no_drinks",
                            },
                        ],
                    ],
                },
            ),
        )
        return HandlerStatus.STOP
