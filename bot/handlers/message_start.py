from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.order_state import OrderState
import json
import asyncio


class MessageStart(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        await storage.clear_user_order_json(telegram_id)
        await storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)

        # Выполнить два send_message параллельно
        await asyncio.gather(
            messenger.send_message(
                chat_id=update["message"]["chat"]["id"],
                text="🍕 Welcome to the Pizza Shop! \nLet's create your perfect pizza! 😋",
                reply_markup=json.dumps({"remove_keyboard": True}),
            ),
            messenger.send_message(
                chat_id=update["message"]["chat"]["id"],
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
                    },
                ),
            ),
        )
        return HandlerStatus.STOP
