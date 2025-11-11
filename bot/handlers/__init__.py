from bot.handlers.handler import Handler
from bot.handlers.database_logger import DatabaseLogger
from bot.handlers.ensure_user_exists import EnsureUserExists
from bot.handlers.message_start import MessageStart
from bot.handlers.pizza_selection import PizzaSelection
from bot.handlers.pizza_size import PizzaSize
from bot.handlers.drink_selection import DrinkSelection
from bot.handlers.order_approve import OrderApprove
from bot.handlers.restart_order import RestartOrder


def get_handlers() -> list[Handler]:
    return [
        DatabaseLogger(),
        EnsureUserExists(),
        MessageStart(),
        PizzaSelection(),
        PizzaSize(),
        DrinkSelection(),
        OrderApprove(),
        RestartOrder(),
    ]
