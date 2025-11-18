from bot.dispatcher import Dispatcher
from bot.handlers.pizza_selection import PizzaSelection
from bot.domain.order_state import OrderState
from tests.mocks import Mock
import json


def test_pizza_selection_handler():
    test_update = {
        "update_id": 987654321,
        "callback_query": {
            "id": "abc123",
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "message": {
                "message_id": 10,
                "chat": {
                    "id": 12345,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private",
                },
            },
            "data": "pizza_margherita",
        },
    }

    update_user_order_json_called = False
    update_user_state_called = False
    answer_callback_query_called = False
    delete_message_called = False
    send_message_calls = []

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {"state": "WAIT_FOR_PIZZA_NAME", "order_json": "{}"}

    def update_user_order_json(telegram_id: int, order_data: dict) -> None:
        assert telegram_id == 12345
        assert order_data == {"pizza_name": "Margherita"}
        nonlocal update_user_order_json_called
        update_user_order_json_called = True

    def update_user_state(telegram_id: int, state: OrderState) -> None:
        assert telegram_id == 12345
        assert state == OrderState.WAIT_FOR_PIZZA_SIZE
        nonlocal update_user_state_called
        update_user_state_called = True

    def answer_callback_query(callback_query_id: str) -> dict:
        assert callback_query_id == "abc123"
        nonlocal answer_callback_query_called
        answer_callback_query_called = True
        return {"ok": True}

    def delete_message(chat_id: int, message_id: int) -> dict:
        assert chat_id == 12345
        assert message_id == 10
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
    dispatcher.add_handler(PizzaSelection())

    dispatcher.dispatch(test_update)

    assert update_user_order_json_called, "Ожидался вызов update_user_order_json"
    assert update_user_state_called, "Ожидался вызов update_user_state"
    assert answer_callback_query_called, "Ожидался вызов answer_callback_query"
    assert delete_message_called, "Ожидался вызов delete_message"

    assert len(send_message_calls) == 1, "Ожидался один вызов send_message"
    assert "Great choice! 🍕" in send_message_calls[0]["text"]
    assert "Margherita" in send_message_calls[0]["text"]

    reply_markup = json.loads(send_message_calls[0]["kwargs"]["reply_markup"])
    assert "inline_keyboard" in reply_markup

    callback_values = [
        btn["callback_data"] for row in reply_markup["inline_keyboard"] for btn in row
    ]
    expected_values = ["size_small", "size_medium", "size_large", "size_extra_large"]

    for val in expected_values:
        assert val in callback_values, f"Ожидалась кнопка с callback_data={val}"
