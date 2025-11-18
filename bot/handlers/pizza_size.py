import json
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.order_state import OrderState
from bot.constants.prices import DRINK_PRICES


class PizzaSize(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != OrderState.WAIT_FOR_PIZZA_SIZE:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("size_")

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        size_mapping = {
            "size_small": "Small (25cm)",
            "size_medium": "Medium (30cm)",
            "size_large": "Large (35cm)",
            "size_extra_large": "Extra Large (40cm)",
        }

        pizza_size = size_mapping.get(callback_data)
        order_json["pizza_size"] = pizza_size

        storage.update_user_order_json(telegram_id, order_json)

        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_DRINKS)

        messenger.answer_callback_query(update["callback_query"]["id"])

        messenger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        text = (
            f"Perfect! 🎯\n"
            f"Selected *{pizza_size}* size\n"
            f"Would you like a drink? 🥤"
        )

        messenger.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text=text,
            parse_mode="Markdown",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": f"🥤 Coca-cola — {DRINK_PRICES['Coca Cola'] // 100} ₽",
                                "callback_data": "drink_coca_cola",
                            },
                            {
                                "text": f"🥤 Pepsi — {DRINK_PRICES['Pepsi'] // 100} ₽",
                                "callback_data": "drink_pepsi",
                            },
                        ],
                        [
                            {
                                "text": f"🍊 Orange Juice — {DRINK_PRICES['Orange Juice'] // 100} ₽",
                                "callback_data": "drink_orange_juice",
                            },
                            {
                                "text": f"🍏 Apple Juice — {DRINK_PRICES['Apple Juice'] // 100} ₽",
                                "callback_data": "drink_apple_juice",
                            },
                        ],
                        [
                            {
                                "text": f"💧 Water — {DRINK_PRICES['Water'] // 100} ₽",
                                "callback_data": "drink_water",
                            },
                            {
                                "text": f"🧊 Iced Tea — {DRINK_PRICES['Iced Tea'] // 100} ₽",
                                "callback_data": "drink_iced_tea",
                            },
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
