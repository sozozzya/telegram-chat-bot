import json

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class SuccessfulPaymentHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "message" not in update:
            return False

        return "successful_payment" in update["message"]

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        # Update user state to ORDER_FINISHED
        storage.update_user_state(telegram_id, OrderState.ORDER_FINISHED)

        messenger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="🎉 Thank you! Your order has been confirmed and is being prepared! \n"
            "Thank you for your payment! Your pizza will be ready soon. Send /start to place another order.",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        return HandlerStatus.STOP
