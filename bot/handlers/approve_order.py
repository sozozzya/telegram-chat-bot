import json
import os
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.order_state import OrderState
from bot.constants.prices import PIZZA_PRICES, DRINK_PRICES


class ApproveOrder(Handler):
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

        if state != OrderState.WAIT_FOR_ORDER_APPROVE:
            return False

        return update["callback_query"]["data"] == "approve_order"

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]

        messenger.answer_callback_query(update["callback_query"]["id"])

        messenger.delete_message(
            chat_id=chat_id,
            message_id=update["callback_query"]["message"]["message_id"],
        )

        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PAYMENT)

        pizza_name = order_json.get("pizza_name", "Unknown")
        pizza_size = order_json.get("pizza_size", "Unknown")
        drink = order_json.get("drink", "No drinks")

        pizza_price = PIZZA_PRICES.get(pizza_size, 0)
        drink_price = DRINK_PRICES.get(drink, 0)

        prices = [
            {"label": f"Pizza: {pizza_name} ({pizza_size})",
             "amount": pizza_price}
        ]
        if drink and drink != "No drinks":
            prices.append({"label": f"Drink: {drink}", "amount": drink_price})

        order_description = f"🍕 Pizza: {pizza_name}, 📏 size: {pizza_size}"
        if drink and drink != "No drinks":
            order_description += f", 🥤 drink: {drink}."

        order_payload = json.dumps(
            {
                "telegram_id": telegram_id,
                "pizza_name": pizza_name,
                "pizza_size": pizza_size,
                "drink": drink,
            }
        )

        messenger.send_invoice(
            chat_id=chat_id,
            title="🧾 Pizza Order",
            description=order_description,
            payload=order_payload,
            provider_token=os.getenv("YOOKASSA_TOKEN"),
            currency="RUB",
            prices=prices,
        )

        return HandlerStatus.STOP
