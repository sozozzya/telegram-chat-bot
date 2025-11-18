from bot.handlers.handler import Handler
from bot.handlers.database_logger import DatabaseLogger
from bot.handlers.ensure_user_exists import EnsureUserExists
from bot.handlers.message_start import MessageStart
from bot.handlers.pizza_selection import PizzaSelection
from bot.handlers.pizza_size import PizzaSize
from bot.handlers.drink_selection import DrinkSelection
from bot.handlers.approve_order import ApproveOrder
from bot.handlers.restart_order import RestartOrder
from bot.handlers.pre_checkout_query import PreCheckoutQueryHandler
from bot.handlers.successful_payment import SuccessfulPaymentHandler


def get_handlers() -> list[Handler]:
    return [
        DatabaseLogger(),
        EnsureUserExists(),
        MessageStart(),
        PizzaSelection(),
        PizzaSize(),
        DrinkSelection(),
        ApproveOrder(),
        RestartOrder(),
        PreCheckoutQueryHandler(),
        SuccessfulPaymentHandler(),
    ]
