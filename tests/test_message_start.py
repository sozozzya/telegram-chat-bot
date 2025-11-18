from bot.dispatcher import Dispatcher
from bot.handlers.message_start import MessageStart
from bot.domain.order_state import OrderState
from tests.mocks import Mock
import json


def test_message_start_handler():
    test_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "chat": {
                "id": 12345,
                "first_name": "Test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1640995200,
            "text": "/start",
        },
    }

    clear_user_data_called = False
    update_user_state_called = False
    send_message_calls = []

    def clear_user_order_json(telegram_id: int) -> None:
        assert telegram_id == 12345
        nonlocal clear_user_data_called
        clear_user_data_called = True

    def update_user_state(telegram_id: int, state: OrderState) -> None:
        assert telegram_id == 12345
        assert state == OrderState.WAIT_FOR_PIZZA_NAME
        nonlocal update_user_state_called
        update_user_state_called = True

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {"state": None, "order_json": "{}"}

    def send_message(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    mock_storage = Mock(
        {
            "clear_user_order_json": clear_user_order_json,
            "update_user_state": update_user_state,
            "get_user": get_user,
        }
    )
    mock_messenger = Mock({"send_message": send_message})

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handler(MessageStart())

    dispatcher.dispatch(test_update)

    assert clear_user_data_called, "Ожидался вызов clear_user_order_json"
    assert update_user_state_called, "Ожидался вызов update_user_state"

    assert len(send_message_calls) == 2, "Ожидалось 2 вызова send_message"

    assert (
        send_message_calls[0]["text"]
        == "🍕 Welcome to the Pizza Shop! \nLet's create your perfect pizza! 😋"
    )
    assert send_message_calls[1]["text"] == "Please choose your pizza 🍽️"

    first_reply = json.loads(send_message_calls[0]["kwargs"]["reply_markup"])
    assert "remove_keyboard" in first_reply

    second_reply = json.loads(send_message_calls[1]["kwargs"]["reply_markup"])
    assert "inline_keyboard" in second_reply
    assert any(
        btn["callback_data"] == "pizza_margherita"
        for row in second_reply["inline_keyboard"]
        for btn in row
    )
    assert any(
        btn["callback_data"] == "pizza_pepperoni"
        for row in second_reply["inline_keyboard"]
        for btn in row
    )
