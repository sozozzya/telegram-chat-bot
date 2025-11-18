from bot.dispatcher import Dispatcher
from bot.handlers.pizza_size import PizzaSize
from bot.domain.order_state import OrderState
from tests.mocks import Mock
import json


def test_pizza_size_handler():
    test_update = {
        "update_id": 111222333,
        "callback_query": {
            "id": "xyz789",
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "message": {
                "message_id": 15,
                "chat": {
                    "id": 12345,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private",
                },
            },
            "data": "size_medium",
        },
    }

    update_user_order_json_called = False
    update_user_state_called = False
    answer_callback_query_called = False
    delete_message_called = False
    send_message_calls = []

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {
            "state": "WAIT_FOR_PIZZA_SIZE",
            "order_json": '{"pizza_name": "Margherita"}',
        }

    def update_user_order_json(telegram_id: int, order_data: dict) -> None:
        assert telegram_id == 12345
        assert order_data["pizza_size"] == "Medium (30cm)"
        assert order_data["pizza_name"] == "Margherita"
        nonlocal update_user_order_json_called
        update_user_order_json_called = True

    def update_user_state(telegram_id: int, state: OrderState) -> None:
        assert telegram_id == 12345
        assert state == OrderState.WAIT_FOR_DRINKS
        nonlocal update_user_state_called
        update_user_state_called = True

    def answer_callback_query(callback_query_id: str) -> dict:
        assert callback_query_id == "xyz789"
        nonlocal answer_callback_query_called
        answer_callback_query_called = True
        return {"ok": True}

    def delete_message(chat_id: int, message_id: int) -> dict:
        assert chat_id == 12345
        assert message_id == 15
        nonlocal delete_message_called
        delete_message_called = True
        return {"ok": True}

    def send_message(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    mock_storage = Mock(
        {
            "get_user": get_user,
            "update_user_order_json": update_user_order_json,
            "update_user_state": update_user_state,
        }
    )
    mock_messenger = Mock(
        {
            "answer_callback_query": answer_callback_query,
            "delete_message": delete_message,
            "send_message": send_message,
        }
    )

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handler(PizzaSize())

    dispatcher.dispatch(test_update)

    assert update_user_order_json_called, "Ожидался вызов update_user_order_json"
    assert update_user_state_called, "Ожидался вызов update_user_state"
    assert answer_callback_query_called, "Ожидался вызов answer_callback_query"
    assert delete_message_called, "Ожидался вызов delete_message"

    assert len(send_message_calls) == 1, "Ожидался один вызов send_message"
    text = send_message_calls[0]["text"]
    assert "Perfect! 🎯" in text
    assert "Medium (30cm)" in text
    assert "Would you like a drink?" in text

    reply_markup = json.loads(send_message_calls[0]["kwargs"]["reply_markup"])
    assert "inline_keyboard" in reply_markup

    callback_values = [
        btn["callback_data"] for row in reply_markup["inline_keyboard"] for btn in row
    ]
    expected_values = [
        "drink_coca_cola",
        "drink_pepsi",
        "drink_orange_juice",
        "drink_apple_juice",
        "drink_water",
        "drink_iced_tea",
        "drink_no_drinks",
    ]
    for val in expected_values:
        assert val in callback_values, f"Ожидалась кнопка с callback_data={val}"
