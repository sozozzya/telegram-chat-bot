from bot.dispatcher import Dispatcher
from bot.handlers.restart_order import RestartOrder
from tests.mocks import Mock
import json


def test_restart_order_handler():
    test_update = {
        "update_id": 202020202,
        "message": {
            "message_id": 40,
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
            "text": "/restart",
        },
    }

    clear_user_order_json_called = False
    update_user_state_called = False
    send_message_calls = []

    def clear_user_order_json(telegram_id: int) -> None:
        assert telegram_id == 12345
        nonlocal clear_user_order_json_called
        clear_user_order_json_called = True

    def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "WAIT_FOR_PIZZA_NAME"
        nonlocal update_user_state_called
        update_user_state_called = True

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {"state": "WAIT_FOR_PIZZA_NAME", "order_json": json.dumps({})}

    def send_message(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    mock_storage = Mock(
        {
            "get_user": get_user,
            "clear_user_order_json": clear_user_order_json,
            "update_user_state": update_user_state,
        }
    )
    mock_messenger = Mock({"send_message": send_message})

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handler(RestartOrder())

    dispatcher.dispatch(test_update)

    assert clear_user_order_json_called, "Ожидался вызов clear_user_order_json"
    assert update_user_state_called, "Ожидался вызов update_user_state"
    assert len(send_message_calls) == 1
    assert "Please choose your pizza" in send_message_calls[0]["text"]

    reply_markup = json.loads(send_message_calls[0]["kwargs"]["reply_markup"])
    assert "inline_keyboard" in reply_markup

    callback_values = [
        btn["callback_data"] for row in reply_markup["inline_keyboard"] for btn in row
    ]
    expected_pizzas = [
        "pizza_margherita",
        "pizza_pepperoni",
        "pizza_quatro_stagioni",
        "pizza_diavola",
        "pizza_prosciutto",
    ]
    for val in expected_pizzas:
        assert val in callback_values, f"Ожидалась кнопка с callback_data={val}"
