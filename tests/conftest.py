import pytest
from tests.mocks import Mock


@pytest.fixture
def mock_storage():
    return Mock(
        {
            "clear_user_order_json": lambda telegram_id: None,
            "update_user_state": lambda telegram_id, state: None,
            "update_user_order_json": lambda telegram_id, order: None,
            "get_user": lambda telegram_id: {"state": None, "order_json": "{}"},
        }
    )


@pytest.fixture
def mock_messenger():
    return Mock(
        {
            "send_message": lambda chat_id, text, **kwargs: {"ok": True},
            "answer_callback_query": lambda callback_id: None,
            "delete_message": lambda chat_id, message_id: None,
        }
    )
