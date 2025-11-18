import json
import os
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.order_state import OrderState


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

        callback_data = update["callback_query"]["data"]
        return callback_data == "approve_order"

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]

        messenger.answer_callback_query(update["callback_query"]["id"])

        messenger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PAYMENT)

        pizza_name = order_json.get("pizza_name", "Unknown")
        pizza_size = order_json.get("pizza_size", "Unknown")
        drink = order_json.get("drink", "Unknown")

        pizza_prices = {
            "Small (25cm)": 50000,  # 500.00 RUB
            "Medium (30cm)": 65000,  # 650.00 RUB
            "Large (35cm)": 80000,  # 800.00 RUB
            "Extra Large (40cm)": 95000,  # 950.00 RUB
        }
        drink_price = 10000  # 100.00 RUB (if drink is selected and not "No drinks")

        pizza_price = pizza_prices.get(pizza_size, 50000)
        prices = [
            {"label": f"Pizza: {pizza_name} ({pizza_size})", "amount": pizza_price}
        ]

        if drink and drink != "No drinks":
            prices.append({"label": f"Drink: {drink}", "amount": drink_price})

        order_payload = json.dumps(
            {
                "telegram_id": telegram_id,
                "pizza_name": pizza_name,
                "pizza_size": pizza_size,
                "drink": drink,
            }
        )

        messenger.send_invoice(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            title="Pizza Order",
            description=f"Pizza: {pizza_name}, Size: {pizza_size}, Drink: {drink}",
            payload=order_payload,
            provider_token=os.getenv("YOOKASSA_TOKEN"),
            currency="RUB",
            prices=prices,
        )

        return HandlerStatus.STOP
