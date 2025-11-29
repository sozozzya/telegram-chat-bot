import json
import asyncio
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.order_state import OrderState
from bot.constants.prices import PIZZA_PRICES


class PizzaSelection(Handler):
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

        if state != OrderState.WAIT_FOR_PIZZA_NAME:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("pizza_")

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

        pizza_name = callback_data.replace("pizza_", "").replace("_", " ").title()
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]
        callback_query_id = update["callback_query"]["id"]

        # Выполнить обновления БД и answer_callback_query параллельно
        await asyncio.gather(
            storage.update_user_order_json(telegram_id, {"pizza_name": pizza_name}),
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_SIZE),
            messenger.answer_callback_query(callback_query_id),
        )

        text = (
            f"Great choice! 🍕\n"
            f"You selected *{pizza_name}*\n"
            f"Now choose your pizza size 📏"
        )

        # Удалить сообщение и отправить новое параллельно
        await asyncio.gather(
            messenger.delete_message(chat_id=chat_id, message_id=message_id),
            messenger.send_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text=text,
                parse_mode="Markdown",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {
                                    "text": f"🍕 Small (25cm) — {PIZZA_PRICES['Small (25cm)'] // 100} ₽",
                                    "callback_data": "size_small",
                                },
                            ],
                            [
                                {
                                    "text": f"🍕➡️ Medium (30cm) — {PIZZA_PRICES['Medium (30cm)'] // 100} ₽",
                                    "callback_data": "size_medium",
                                },
                            ],
                            [
                                {
                                    "text": f"🍕🍕 Large (35cm) — {PIZZA_PRICES['Large (35cm)'] // 100} ₽",
                                    "callback_data": "size_large",
                                },
                            ],
                            [
                                {
                                    "text": f"🍕🍕👑 Extra Large (40cm) — {PIZZA_PRICES['Extra Large (40cm)'] // 100} ₽",
                                    "callback_data": "size_extra_large",
                                },
                            ],
                        ],
                    },
                ),
            ),
        )
        return HandlerStatus.STOP
