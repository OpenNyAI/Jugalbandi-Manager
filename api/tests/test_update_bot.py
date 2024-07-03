from unittest.mock import MagicMock, patch, Mock
import pytest
from app.bot_handlers import handle_update_bot

mock_encryption_handler = MagicMock()
mock_encrypt_dict = Mock(
    side_effect=lambda x: {k: f"encrypted_{v}" for k, v in x.items()}
)
mock_encryption_handler.encrypt_dict = mock_encrypt_dict


@pytest.mark.asyncio
@patch(
    "app.bot_handlers.get_bot_by_id",
    return_value={"id": "test_bot_id", "name": "Test Bot"},
)
@patch("app.bot_handlers.update_bot", return_value=True)
@patch("app.bot_handlers.EncryptionHandler", mock_encryption_handler)
async def test_handle_update_bot_with_config_env(mock_update_bot, mock_get_bot_by_id):
    mock_encryption_handler.reset_mock()
    bot_id = "test_bot_id"
    credentials = {"key": "value"}
    bot_data = {
        "name": "Test Bot",
        "credentials": credentials,
    }

    response = await handle_update_bot(bot_id, bot_data)

    mock_encrypt_dict.assert_called_once_with(credentials)
    mock_get_bot_by_id.assert_called_once_with(bot_id)
    mock_update_bot.assert_called_once_with(bot_id, bot_data)

    assert response == {
        "status": "success",
        "message": "Bot updated",
        "bot": mock_get_bot_by_id.return_value,
    }


@pytest.mark.asyncio
@patch(
    "app.bot_handlers.get_bot_by_id",
    return_value={"id": "test_bot_id", "name": "Test Bot"},
)
@patch("app.bot_handlers.update_bot", return_value=True)
async def test_handle_update_bot_without_config_env(
    mock_update_bot, mock_get_bot_by_id
):
    bot_id = "test_bot_id"
    bot_data = {
        "name": "Test Bot",
    }

    response = await handle_update_bot(bot_id, bot_data)

    mock_get_bot_by_id.assert_called_once_with(bot_id)
    mock_update_bot.assert_called_once_with(bot_id, bot_data)

    assert response == {
        "status": "success",
        "message": "Bot updated",
        "bot": mock_get_bot_by_id.return_value,
    }


@pytest.mark.asyncio
@patch("app.bot_handlers.get_bot_by_id", return_value=None)
async def test_handle_update_bot_bot_not_found(mock_get_bot_by_id):
    bot_id = "test_bot_id"
    bot_data = {
        "name": "Test Bot",
    }
    response = await handle_update_bot(bot_id, bot_data)

    mock_get_bot_by_id.assert_called_once_with(bot_id)

    assert response == {"status": "error", "message": "Bot not found"}
