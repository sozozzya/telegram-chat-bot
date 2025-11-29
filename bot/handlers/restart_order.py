import json
import asyncio
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.order_state import OrderState


class RestartOrder(Handler):
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
        return callback_data == "restart_order"

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]
        callback_query_id = update["callback_query"]["id"]

        # Выполнить answer_callback_query, delete_message и обновления БД параллельно
        await asyncio.gather(
            messenger.answer_callback_query(callback_query_id),
            messenger.delete_message(chat_id=chat_id, message_id=message_id),
            storage.clear_user_order_json(telegram_id),
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME),
        )

        await messenger.send_message(
            chat_id=chat_id,
            text="Please choose your pizza 🍽️",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "🍅 Margherita",
                                "callback_data": "pizza_margherita",
                            },
                            {
                                "text": "🔥 Pepperoni",
                                "callback_data": "pizza_pepperoni",
                            },
                        ],
                        [
                            {
                                "text": "🌿 Quatro Stagioni",
                                "callback_data": "pizza_quatro_stagioni",
                            },
                        ],
                        [
                            {"text": "🌶️ Diavola", "callback_data": "pizza_diavola"},
                            {
                                "text": "🥓 Prosciutto",
                                "callback_data": "pizza_prosciutto",
                            },
                        ],
                    ],
                }
            ),
        )
        return HandlerStatus.STOP
