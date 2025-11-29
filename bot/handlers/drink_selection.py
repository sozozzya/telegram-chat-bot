import json
import asyncio
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.order_state import OrderState
from bot.constants.prices import PIZZA_PRICES, DRINK_PRICES


class DrinkSelection(Handler):
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

        if state != OrderState.WAIT_FOR_DRINKS:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]

        drink = callback_data.replace("drink_", "").replace("_", " ").title()
        if drink == "None":
            drink = "No drinks"

        order_json["drink"] = drink
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]
        callback_query_id = update["callback_query"]["id"]

        # Выполнить обновления БД и answer_callback_query параллельно
        await asyncio.gather(
            storage.update_user_order_json(telegram_id, order_json),
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_ORDER_APPROVE),
            messenger.answer_callback_query(callback_query_id),
        )

        pizza_name = order_json.get("pizza_name", "Unknown")
        pizza_size = order_json.get("pizza_size", "Unknown")

        pizza_price_rub = PIZZA_PRICES.get(pizza_size, 0) // 100
        drink_price_rub = DRINK_PRICES.get(drink, 0) // 100

        order_summary = (
            f"**Do you confirm your order?**\n"
            f"🍕 Pizza: *{pizza_name}*\n"
            f"📏 Size: *{pizza_size}* — *{pizza_price_rub} ₽*\n"
            f"🥤 Drink: *{drink}* — *{drink_price_rub} ₽*\n\n"
            f"💰 Total: *{pizza_price_rub + drink_price_rub} ₽*"
        )

        # Удалить сообщение и отправить новое параллельно
        await asyncio.gather(
            messenger.delete_message(chat_id=chat_id, message_id=message_id),
            messenger.send_message(
                chat_id=chat_id,
                text=order_summary,
                parse_mode="Markdown",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "✅ Confirm",
                                    "callback_data": "approve_order",
                                },
                                {
                                    "text": "🔄 Start Over",
                                    "callback_data": "restart_order",
                                },
                            ]
                        ],
                    }
                ),
            ),
        )
        return HandlerStatus.STOP
