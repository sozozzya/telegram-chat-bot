import json
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class OrderApprove(Handler):
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

        if state != "WAIT_FOR_ORDER_APPROVE":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data in ["approve_yes", "approve_restart"]

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

        messenger.answer_callback_query(update["callback_query"]["id"])

        if callback_data == "approve_yes":
            storage.update_user_state(telegram_id, "ORDER_FINISHED")
            messenger.delete_message(chat_id=chat_id, message_id=message_id)
            messenger.send_message(
                chat_id=chat_id,
                text="🎉 Thank you! Your order has been confirmed and is being prepared!",
                reply_markup=json.dumps({"remove_keyboard": True}),
            )
            return HandlerStatus.STOP

        if callback_data == "approve_restart":
            try:
                messenger.delete_message(chat_id=chat_id, message_id=message_id - 1)
            except Exception:
                pass

            storage.clear_user_order_json(telegram_id)
            storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

            messenger.delete_message(chat_id=chat_id, message_id=message_id)

            messenger.send_message(
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
