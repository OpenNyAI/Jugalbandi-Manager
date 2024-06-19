import os
import sys
import base64
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
print(sys.path)
from lib.data_models import (
    ChannelInput,
    ChannelData,
    MessageType,
    ChannelIntent,
    BotInput,
    MessageData,
    LanguageInput,
    FlowInput,
    LanguageIntent
)
from lib.whatsapp import WAMsgType

# Patch StorageHandler.get_instance before importing the module
mock_storage_instance = MagicMock()
mock_write_file = AsyncMock()
mock_public_url = AsyncMock(return_value="https://storage.url/test_audio.ogg")

mock_storage_instance.write_file = mock_write_file
mock_storage_instance.public_url = mock_public_url

with patch(
    "lib.file_storage.StorageHandler.get_instance", return_value=mock_storage_instance
):
    import src.handlers.incoming  # replace with your actual module path

    process_incoming_messages = src.handlers.incoming.process_incoming_messages


@pytest.mark.asyncio
async def test_process_incoming_text_message():
    mock_update_message = AsyncMock()
    mock_get_bot_by_session_id = AsyncMock(
        return_value=("test_number", "encrypted_credentials")
    )
    with patch("src.handlers.incoming.update_message", mock_update_message):
        message = ChannelInput(
            source="api",
            message_id="test_msg_id",
            turn_id="test_turn_id",
            session_id="test_session_id",
            intent=ChannelIntent.BOT_IN,
            channel_data=ChannelData(
                type=MessageType.TEXT,
                timestamp="2021-09-01T00:00:00Z",
                text={"body": "Hello"},
            ),
            data=BotInput(
                message_type=MessageType.TEXT,
                message_data=MessageData(message_text="Hello"),
            ),
        )
        result = await process_incoming_messages(message)
        mock_update_message.assert_called_once_with("test_msg_id", message_text="Hello")
        assert result is not None
        assert isinstance(result, LanguageInput)
        assert result.intent == LanguageIntent.LANGUAGE_IN
        assert result.data is not None
        assert result.data.message_type == MessageType.TEXT
        assert result.data.message_data is not None
        assert result.data.message_data.message_text is not None
        assert result.data.message_data.message_text == "Hello"


@pytest.mark.asyncio
async def test_process_incoming_audio_message():
    mock_update_message = AsyncMock()
    mock_get_bot_by_session_id = AsyncMock(
        return_value=("test_number", "encrypted_credentials")
    )
    mock_decrypt_credentials = MagicMock(return_value={"whatsapp": "api_key"})
    mock_wa_get_user_audio = MagicMock(
        return_value=MagicMock(content=base64.b64encode(b"audio_bytes").decode("utf-8"))
    )

    with patch("src.handlers.incoming.update_message", mock_update_message):
        with patch(
            "src.handlers.incoming.get_bot_by_session_id", mock_get_bot_by_session_id
        ):
            with patch(
                "src.handlers.incoming.decrypt_credentials", mock_decrypt_credentials
            ):
                with patch(
                    "lib.whatsapp.WhatsappHelper.wa_get_user_audio",
                    mock_wa_get_user_audio,
                ):
                    message = ChannelInput(
                        source="api",
                        message_id="test_msg_id",
                        turn_id="test_turn_id",
                        session_id="test_session_id",
                        intent=ChannelIntent.BOT_IN,
                        channel_data=ChannelData(
                            type=MessageType.AUDIO,
                            timestamp="2021-09-01T00:00:00Z",
                            audio={"url": "https://storage.url/test_audio.ogg"},
                        ),
                        data=BotInput(
                            message_type=MessageType.AUDIO,
                            message_data=MessageData(
                                media_url="https://storage.url/test_audio.ogg"
                            ),
                        ),
                    )
                    result = await process_incoming_messages(message)
                    mock_write_file.assert_called_once_with(
                        "test_msg_id.ogg", b"audio_bytes", "audio/ogg"
                    )
                    mock_public_url.assert_called_once_with("test_msg_id.ogg")
                    mock_update_message.assert_called_once_with(
                        "test_msg_id",
                        media_url="https://storage.url/test_audio.ogg",
                    )
                    assert result is not None
                    assert isinstance(result, LanguageInput)
                    assert result.intent == LanguageIntent.LANGUAGE_IN
                    assert result.data is not None
                    assert result.data.message_type == MessageType.AUDIO
                    assert result.data.message_data is not None
                    assert result.data.message_data.media_url is not None
                    assert result.data.message_data.media_url == "https://storage.url/test_audio.ogg"


@pytest.mark.asyncio
async def test_process_incoming_interactive_message():
    message = ChannelInput(
        source="api",
        message_id="test_msg_id",
        turn_id="test_turn_id",
        session_id="test_session_id",
        intent=ChannelIntent.BOT_IN,
        channel_data=ChannelData(
            type=MessageType.INTERACTIVE,
            timestamp="2021-09-01T00:00:00Z",
            interactive={
                "type": "button",
                "button": {
                    "id": "test_button_id",
                },
            },
        ),
        data=BotInput(
            message_type=MessageType.TEXT,
            message_data=MessageData(message_text="Hello"),
        ),
    )
    result = await process_incoming_messages(message)
    assert result is not None
    assert isinstance(result, LanguageInput)
    assert result.intent == LanguageIntent.LANGUAGE_IN
    assert result.data is not None
    assert result.data.message_type == MessageType.INTERACTIVE
    assert result.data.message_data is not None
    assert result.data.message_data.message_text is not None
    assert result.data.message_data.message_text == "test_button_id"

@pytest.mark.asyncio
async def test_process_incoming_language_selection_message():
    mock_set_user_language = AsyncMock()
    with patch("src.handlers.incoming.set_user_language", mock_set_user_language):
        message = ChannelInput(
            source="api",
            message_id="test_msg_id",
            turn_id="test_turn_id",
            session_id="test_session_id",
            intent=ChannelIntent.BOT_IN,
            channel_data=ChannelData(
                type=MessageType.INTERACTIVE,
                timestamp="2021-09-01T00:00:00Z",
                interactive={
                    "type": "button",
                    "button": {
                        "id": "lang_hindi",
                    },
                },
            ),
            data=BotInput(
                message_type=MessageType.TEXT,
                message_data=MessageData(message_text="Hello"),
            ),
        )
        result = await process_incoming_messages(message)
        assert result is not None
        assert isinstance(result, FlowInput)
        assert result.intent == LanguageIntent.LANGUAGE_IN
        assert result.dialog is not None
        assert result.dialog == "language_selected"

@pytest.mark.asyncio
async def test_process_incoming_form_message():
    message = ChannelInput(
        source="api",
        message_id="test_msg_id",
        turn_id="test_turn_id",
        session_id="test_session_id",
        intent=ChannelIntent.BOT_IN,
        channel_data=ChannelData(
            type=MessageType.FORM,
            timestamp="2021-09-01T00:00:00Z",
            form={"type": "form", "form": {"response_json": '{"field": "value"}'}},
        ),
        data=BotInput(
            message_type=MessageType.TEXT,
            message_data=MessageData(message_text="Hello"),
        ),
    )
    result = await process_incoming_messages(message)
    assert result is not None
    assert isinstance(result, FlowInput)
    assert result.form_response is not None

