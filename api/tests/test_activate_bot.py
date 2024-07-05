from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.jb_schema import JBBotActivate, JBBotChannels
from lib.models import JBBot
from app.bot_handlers import handle_activate_bot


mock_encryption_handler = MagicMock()
mock_encrypt_dict = MagicMock()
mock_encryption_handler.encrypt_dict = mock_encrypt_dict


@pytest.mark.asyncio
async def test_handle_activate_bot_no_phone_number():
    request_body = JBBotActivate(
        phone_number="", channels=JBBotChannels(**{"whatsapp": "12345"})
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {"status": "error", "message": "No phone number provided"}


@pytest.mark.asyncio
@patch("app.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
async def test_handle_activate_bot_bot_not_found(mock_get_bot_by_id):
    mock_get_bot_by_id.return_value = None
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {"status": "error", "message": "Bot not found"}


@pytest.mark.asyncio
@patch("app.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
async def test_handle_activate_bot_bot_already_active(mock_get_bot_by_id):
    mock_get_bot_by_id.return_value = JBBot(
        id="bot_id", status="active", required_credentials=[], credentials={}
    )
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {"status": "error", "message": "Bot already active"}


@pytest.mark.asyncio
@patch("app.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
@patch("app.bot_handlers.get_bot_by_phone_number", new_callable=AsyncMock)
@patch("app.bot_handlers.update_bot", new_callable=AsyncMock)
async def test_handle_activate_bot_phone_number_in_use(
    mock_get_bot_by_id, mock_get_bot_by_phone_number, mock_
):
    mock_get_bot_by_id.return_value = JBBot(
        id="bot_id", status="inactive", required_credentials=[], credentials={}
    )
    mock_get_bot_by_phone_number.return_value = JBBot(
        id="other_bot_id",
        name="OtherBot",
        status="inactive",
        required_credentials=[],
        credentials={},
    )
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {
        "status": "error",
        "message": "Phone number 1234567890 already in use by bot OtherBot",
    }


@pytest.mark.asyncio
@patch("app.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
@patch("app.bot_handlers.get_bot_by_phone_number", new_callable=AsyncMock)
async def test_handle_activate_bot_missing_credentials(
    mock_get_bot_by_phone_number, mock_get_bot_by_id
):
    mock_get_bot_by_id.return_value = JBBot(
        id="bot_id", status="inactive", required_credentials=["api_key"], credentials={}
    )
    mock_get_bot_by_phone_number.return_value = None
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {
        "status": "error",
        "message": "Bot missing required credentials: api_key",
    }


@pytest.mark.asyncio
@patch("app.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
@patch("app.bot_handlers.get_bot_by_phone_number", new_callable=AsyncMock)
@patch("app.bot_handlers.update_bot", new_callable=AsyncMock)
@patch("app.bot_handlers.EncryptionHandler", mock_encryption_handler)
async def test_handle_activate_bot_success(
    mock_update_bot, mock_get_bot_by_phone_number, mock_get_bot_by_id
):
    mock_get_bot_by_id.return_value = JBBot(
        id="bot_id", status="inactive", required_credentials=[], credentials={}
    )
    mock_get_bot_by_phone_number.return_value = None
    mock_encrypt_dict.return_value = {"whatsapp": "encrypted_value"}
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )

    response = await handle_activate_bot("bot_id", request_body)

    mock_update_bot.assert_called_once_with(
        "bot_id",
        {
            "phone_number": "1234567890",
            "channels": {"whatsapp": "encrypted_value"},
            "status": "active",
        },
    )
    assert response == {"status": "success"}
