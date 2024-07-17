from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.jb_schema import JBBotActivate, JBBotChannels
from lib.models import JBBot, JBChannel

from app.handlers.v1.bot_handlers import handle_activate_bot


mock_encryption_handler = MagicMock()
mock_encrypt_dict = MagicMock()
mock_encrypt_text = MagicMock()
mock_encryption_handler.encrypt_dict = mock_encrypt_dict
mock_encryption_handler.encrypt_text = mock_encrypt_text


@pytest.mark.asyncio
async def test_handle_activate_bot_no_phone_number():
    request_body = JBBotActivate(
        phone_number="", channels=JBBotChannels(**{"whatsapp": "12345"})
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {"status": "error", "message": "No phone number provided"}


@pytest.mark.asyncio
@patch("app.handlers.v1.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
async def test_handle_activate_bot_bot_not_found(mock_get_bot_by_id):
    mock_get_bot_by_id.return_value = None
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {"status": "error", "message": "Bot not found"}


@pytest.mark.asyncio
@patch("app.handlers.v1.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
@patch(
    "app.handlers.v1.bot_handlers.get_channels_by_identifier", new_callable=AsyncMock
)
async def test_handle_activate_bot_bot_already_active(
    mock_get_channels_by_identifier, mock_get_bot_by_id
):
    mock_get_bot_by_id.return_value = JBBot(
        id="bot_id", status="active", required_credentials=[], credentials={}
    )
    mock_get_channels_by_identifier.return_value = [
        JBChannel(
            id="channel_id",
            bot_id="bot_id",
            name="SomeChannel",
            status="active",
            key="encrypted_key",
            app_id="1234567890",
            url="http://some.url",
            type="whatsapp",
            bot=JBBot(id="bot_id", name="OtherBot", status="active"),
        )
    ]
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {"status": "error", "message": "Bot already active"}


@pytest.mark.asyncio
@patch("app.handlers.v1.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
@patch(
    "app.handlers.v1.bot_handlers.get_channels_by_identifier", new_callable=AsyncMock
)
@patch("app.handlers.v1.bot_handlers.update_channel", new_callable=AsyncMock)
@patch("app.handlers.v1.bot_handlers.EncryptionHandler", mock_encryption_handler)
async def test_handle_activate_bot_existing_channel(
    mock_update_channel, mock_get_channels_by_identifier, mock_get_bot_by_id
):
    mock_get_bot_by_id.return_value = JBBot(
        id="bot_id", status="active", required_credentials=[], credentials={}
    )
    mock_get_channels_by_identifier.return_value = [
        JBChannel(
            id="channel_id",
            bot_id="bot_id",
            name="SomeChannel",
            status="inactive",
            key="encrypted_key",
            app_id="1234567890",
            url="http://some.url",
            type="whatsapp",
            bot=JBBot(id="bot_id", name="OtherBot", status="active"),
        )
    ]
    mock_encrypt_text.return_value = "encrypted_value"
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )
    response = await handle_activate_bot("bot_id", request_body)
    mock_update_channel.assert_called_once_with(
        "channel_id", {"status": "active", "key": "encrypted_value"}
    )
    assert response == {"status": "success"}


@pytest.mark.asyncio
@patch("app.handlers.v1.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
@patch(
    "app.handlers.v1.bot_handlers.get_channels_by_identifier", new_callable=AsyncMock
)
@patch("app.handlers.v1.bot_handlers.update_bot", new_callable=AsyncMock)
async def test_handle_activate_bot_phone_number_in_use(
    mock_get_bot_by_id, mock_get_channels_by_identifier, mock_
):
    mock_get_bot_by_id.return_value = JBBot(
        id="bot_id", status="inactive", required_credentials=[], credentials={}
    )
    mock_get_channels_by_identifier.return_value = [
        JBChannel(
            id="channel_id",
            bot_id="other_bot_id",
            name="SomeChannel",
            status="active",
            key="encrypted_key",
            app_id="1234567890",
            url="http://some.url",
            type="whatsapp",
            bot=JBBot(id="other_bot_id", name="OtherBot", status="active"),
        )
    ]
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {
        "status": "error",
        "message": "Phone number 1234567890 already in use by bot OtherBot",
    }


@pytest.mark.asyncio
@patch("app.handlers.v1.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
@patch(
    "app.handlers.v1.bot_handlers.get_channels_by_identifier", new_callable=AsyncMock
)
async def test_handle_activate_bot_missing_credentials(
    mock_get_channels_by_identifier, mock_get_bot_by_id
):
    mock_get_bot_by_id.return_value = JBBot(
        id="bot_id", status="active", required_credentials=["api_key"], credentials={}
    )
    mock_get_channels_by_identifier.return_value = None
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )
    response = await handle_activate_bot("bot_id", request_body)
    assert response == {
        "status": "error",
        "message": "Bot missing required credentials: api_key",
    }


@pytest.mark.asyncio
@patch("app.handlers.v1.bot_handlers.create_channel", new_callable=AsyncMock)
@patch("app.handlers.v1.bot_handlers.get_bot_by_id", new_callable=AsyncMock)
@patch(
    "app.handlers.v1.bot_handlers.get_channels_by_identifier", new_callable=AsyncMock
)
@patch("app.handlers.v1.bot_handlers.EncryptionHandler", mock_encryption_handler)
@patch("app.handlers.v1.bot_handlers.os.getenv", return_value="http://some.url")
async def test_handle_activate_bot_success(
    mock_os_getenv,
    mock_get_channels_by_identifier,
    mock_get_bot_by_id,
    mock_create_channel,
):
    mock_get_bot_by_id.return_value = JBBot(
        id="bot_id", status="inactive", required_credentials=[], credentials={}
    )
    mock_get_channels_by_identifier.return_value = None
    mock_encrypt_dict.return_value = {"whatsapp": "encrypted_value"}
    mock_encrypt_text.return_value = "encrypted_value"
    request_body = JBBotActivate(
        phone_number="1234567890", channels={"whatsapp": "12345"}
    )

    response = await handle_activate_bot("bot_id", request_body)

    mock_create_channel.assert_called_once_with(
        "bot_id",
        {
            "name": "whatsapp",
            "type": "pinnacle_whatsapp",
            "key": "encrypted_value",
            "app_id": "1234567890",
            "url": "http://some.url",
            "status": "active",
        },
    )
    assert response == {"status": "success"}
