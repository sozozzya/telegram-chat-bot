from bot.dispatcher import Dispatcher
from bot.handlers.order_approve import OrderApprove
from tests.mocks import Mock
import json


def test_order_approve_handler():
    test_update = {
        "update_id": 101010101,
        "callback_query": {
            "id": "approve1",
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "message": {
                "message_id": 30,
                "chat": {
                    "id": 12345,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private",
                },
            },
            "data": "approve_yes",
        },
    }

    update_user_state_called = False
    answer_callback_query_called = False
    delete_message_called = False
    send_message_calls = []

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {
            "state": "WAIT_FOR_ORDER_APPROVE",
            "order_json": json.dumps(
                {
                    "pizza_name": "Margherita",
                    "pizza_size": "Medium (30cm)",
                    "drink": "Coca Cola",
                }
            ),
        }

    def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "ORDER_FINISHED"
        nonlocal update_user_state_called
        update_user_state_called = True

    def answer_callback_query(callback_query_id: str) -> dict:
        assert callback_query_id == "approve1"
        nonlocal answer_callback_query_called
        answer_callback_query_called = True
        return {"ok": True}

    def delete_message(chat_id: int, message_id: int) -> dict:
        assert chat_id == 12345
        assert message_id == 30
        nonlocal delete_message_called
        delete_message_called = True
        return {"ok": True}

    def send_message(chat_id: int, text: str, **kwargs) -> dict:
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    mock_storage = Mock({"get_user": get_user, "update_user_state": update_user_state})
    mock_messenger = Mock(
        {
            "answer_callback_query": answer_callback_query,
            "delete_message": delete_message,
            "send_message": send_message,
        }
    )

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handler(OrderApprove())

    dispatcher.dispatch(test_update)

    assert answer_callback_query_called
    assert update_user_state_called
    assert delete_message_called
    assert len(send_message_calls) == 1
    assert "Thank you" in send_message_calls[0]["text"]
    reply_markup = json.loads(send_message_calls[0]["kwargs"]["reply_markup"])
    assert "remove_keyboard" in reply_markup


def test_order_approve_restart_handler():
    test_update = {
        "update_id": 101010102,
        "callback_query": {
            "id": "approve2",
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "message": {
                "message_id": 31,
                "chat": {
                    "id": 12345,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private",
                },
            },
            "data": "approve_restart",
        },
    }

    clear_user_order_json_called = False
    update_user_state_called = False
    answer_callback_query_called = False
    delete_message_calls = []
    send_message_calls = []

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {
            "state": "WAIT_FOR_ORDER_APPROVE",
            "order_json": json.dumps(
                {
                    "pizza_name": "Margherita",
                    "pizza_size": "Medium (30cm)",
                    "drink": "Coca Cola",
                }
            ),
        }

    def clear_user_order_json(telegram_id: int) -> None:
        assert telegram_id == 12345
        nonlocal clear_user_order_json_called
        clear_user_order_json_called = True

    def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "WAIT_FOR_PIZZA_NAME"
        nonlocal update_user_state_called
        update_user_state_called = True

    def answer_callback_query(callback_query_id: str) -> dict:
        assert callback_query_id == "approve2"
        nonlocal answer_callback_query_called
        answer_callback_query_called = True
        return {"ok": True}

    def delete_message(chat_id: int, message_id: int) -> dict:
        delete_message_calls.append(message_id)
        return {"ok": True}

    def send_message(chat_id: int, text: str, **kwargs) -> dict:
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    mock_storage = Mock(
        {
            "get_user": get_user,
            "clear_user_order_json": clear_user_order_json,
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
    dispatcher.add_handler(OrderApprove())

    dispatcher.dispatch(test_update)

    assert answer_callback_query_called
    assert clear_user_order_json_called
    assert update_user_state_called

    assert 30 in delete_message_calls
    assert 31 in delete_message_calls
    assert len(send_message_calls) == 1
    assert "Please choose your pizza" in send_message_calls[0]["text"]
    reply_markup = json.loads(send_message_calls[0]["kwargs"]["reply_markup"])

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
        assert val in callback_values
