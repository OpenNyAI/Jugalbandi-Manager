import base64
from unittest import mock
from unittest.mock import patch, AsyncMock, MagicMock, Mock
import pytest

from lib.data_models import (
    Channel,
    MessageType,
    ChannelIntent,
    RestBotInput,
    Language,
    Flow,
    FlowIntent,
    LanguageIntent,
    DialogOption,
)

# Patch StorageHandler.get_async_instance before importing the module
mock_async_storage_instance = MagicMock()
mock_async_write_file = AsyncMock()
mock_async_public_url = AsyncMock(return_value="https://storage.url/test_audio.ogg")

mock_async_storage_instance.write_file = mock_async_write_file
mock_async_storage_instance.public_url = mock_async_public_url

mock_sync_storage_instance = MagicMock()
mock_sync_write_file = MagicMock()
mock_sync_public_url = MagicMock(return_value="https://storage.url/test_audio.ogg")

mock_sync_storage_instance.write_file = mock_sync_write_file
mock_sync_storage_instance.public_url = mock_sync_public_url

mock_encryption_handler = MagicMock()
mock_encryption_handler.decrypt_dict = Mock(
    side_effect=lambda x: {
        k: v.replace("encrypted_", "decrypted_") for k, v in x.items()
    }
)
mock_encryption_handler.decrypt_text = Mock(
    side_effect=lambda x: x.replace("encrypted_", "decrypted_")
)

with patch(
    "lib.file_storage.StorageHandler.get_async_instance",
    return_value=mock_async_storage_instance,
):
    with patch(
        "lib.file_storage.StorageHandler.get_sync_instance",
        return_value=mock_sync_storage_instance,
    ):
        with patch("lib.encryption_handler.EncryptionHandler", mock_encryption_handler):
            import src.handlers.incoming

            process_incoming_messages = src.handlers.incoming.process_incoming_messages


@pytest.mark.asyncio
async def test_process_incoming_text_message():
    mock_get_channel_by_turn_id = AsyncMock(
        return_value=MagicMock(channel_id="test_channel_id")
    )
    with patch(
        "src.handlers.incoming.get_channel_by_turn_id", mock_get_channel_by_turn_id
    ):
        bot_input = RestBotInput(
            channel_name="pinnacle_whatsapp",
            headers={},
            query_params={},
            data={
                "timestamp": "1714990325",
                "text": {"body": "How are you?"},
                "type": "text",
            },
        )
        message = Channel(
            source="api",
            turn_id="test_turn_id",
            intent=ChannelIntent.CHANNEL_IN,
            bot_input=bot_input,
        )
        result = await process_incoming_messages(
            turn_id=message.turn_id, bot_input=bot_input
        )
        mock_get_channel_by_turn_id.assert_called_once_with("test_turn_id")
        assert result is not None
        assert isinstance(result, Language)
        assert result.turn_id == "test_turn_id"
        assert result.intent == LanguageIntent.LANGUAGE_IN
        assert result.message is not None
        assert result.message.message_type == MessageType.TEXT
        assert result.message.text is not None
        assert result.message.text.body == "How are you?"


@pytest.mark.asyncio
async def test_process_incoming_audio_message():
    mock_get_channel_by_turn_id = AsyncMock(
        return_value=MagicMock(channel_id="test_channel_id")
    )
    mock_wa_get_user_audio = MagicMock(return_value=base64.b64encode(b"audio_bytes"))

    with patch(
        "src.handlers.incoming.get_channel_by_turn_id", mock_get_channel_by_turn_id
    ):
        with patch(
            "lib.channel_handler.pinnacle_whatsapp_handler.PinnacleWhatsappHandler.wa_download_audio",
            mock_wa_get_user_audio,
        ):
            bot_input = RestBotInput(
                channel_name="pinnacle_whatsapp",
                headers={},
                query_params={},
                data={
                    "timestamp": "1714990325",
                    "audio": {
                        "mime_type": "audio/ogg; codecs=opus",
                        "sha256": "random_sha256_value",
                        "id": "audio_id1",
                        "voice": True,
                    },
                    "type": "audio",
                },
            )
            message = Channel(
                source="api",
                turn_id="test_turn_id",
                intent=ChannelIntent.CHANNEL_IN,
                bot_input=bot_input,
            )
            result = await process_incoming_messages(
                turn_id=message.turn_id, bot_input=bot_input
            )
        mock_sync_write_file.assert_called_once_with(
            "test_turn_id.ogg", b"audio_bytes", "audio/ogg"
        )
        mock_sync_public_url.assert_called_once_with("test_turn_id.ogg")
        assert result is not None
        assert isinstance(result, Language)
        assert result.intent == LanguageIntent.LANGUAGE_IN
        assert result.message is not None
        assert result.message.message_type == MessageType.AUDIO
        assert result.message.audio is not None
        assert result.message.audio.media_url == "https://storage.url/test_audio.ogg"


@pytest.mark.asyncio
async def test_process_incoming_interactive_message():
    bot_input = RestBotInput(
        channel_name="pinnacle_whatsapp",
        headers={},
        query_params={},
        data={
            "timestamp": "1714990452",
            "type": "interactive",
            "interactive": {
                "type": "button_reply",
                "button_reply": {"id": "0", "title": "Yes"},
            },
        },
    )
    message = Channel(
        source="api",
        turn_id="test_turn_id",
        intent=ChannelIntent.CHANNEL_IN,
        bot_input=bot_input,
    )
    mock_get_channel_by_turn_id = AsyncMock(
        return_value=MagicMock(channel_id="test_channel_id")
    )
    with patch(
        "src.handlers.incoming.get_channel_by_turn_id", mock_get_channel_by_turn_id
    ):
        result = await process_incoming_messages(
            turn_id=message.turn_id, bot_input=bot_input
        )
    assert result is not None
    assert isinstance(result, Flow)
    assert result.intent == FlowIntent.USER_INPUT
    assert result.user_input is not None
    assert result.user_input.turn_id == "test_turn_id"
    assert result.user_input.message is not None
    assert result.user_input.message.message_type == MessageType.INTERACTIVE_REPLY
    assert result.user_input.message.interactive_reply is not None
    assert result.user_input.message.interactive_reply.options is not None
    assert len(result.user_input.message.interactive_reply.options) == 1
    assert result.user_input.message.interactive_reply.options[0].option_id == "0"
    assert result.user_input.message.interactive_reply.options[0].option_text == "Yes"


@pytest.mark.asyncio
async def test_process_incoming_language_selection_message():
    bot_input = RestBotInput(
        channel_name="pinnacle_whatsapp",
        headers={},
        query_params={},
        data={
            "timestamp": "1714990499",
            "type": "interactive",
            "interactive": {
                "type": "list_reply",
                "list_reply": {
                    "id": "lang_english",
                    "title": "English",
                },
            },
        },
    )
    message = Channel(
        source="api",
        turn_id="test_turn_id",
        intent=ChannelIntent.CHANNEL_IN,
        bot_input=bot_input,
    )
    mock_get_channel_by_turn_id = AsyncMock(
        return_value=MagicMock(channel_id="test_channel_id")
    )
    with patch(
        "src.handlers.incoming.get_channel_by_turn_id", mock_get_channel_by_turn_id
    ):
        result = await process_incoming_messages(
            turn_id=message.turn_id, bot_input=bot_input
        )

    print(result)

    assert result is not None
    assert isinstance(result, Flow)
    assert result.intent == FlowIntent.DIALOG
    assert result.dialog is not None
    assert result.dialog.turn_id == "test_turn_id"
    assert result.dialog.message is not None
    assert result.dialog.message.message_type == MessageType.DIALOG
    assert result.dialog.message.dialog is not None
    assert result.dialog.message.dialog.dialog_id == DialogOption.LANGUAGE_SELECTED
    assert result.dialog.message.dialog.dialog_input == "en"


@pytest.mark.asyncio
async def test_process_incoming_form_message():
    bot_input = RestBotInput(
        channel_name="pinnacle_whatsapp",
        headers={},
        query_params={},
        data={
            "timestamp": "1714990325",
            "type": "interactive",
            "interactive": {
                "type": "nfm_reply",
                "nfm_reply": {
                    "response_json": {"field": "value"},
                },
            },
        },
    )
    message = Channel(
        source="api",
        turn_id="test_turn_id",
        intent=ChannelIntent.CHANNEL_IN,
        bot_input=bot_input,
    )
    mock_get_channel_by_turn_id = AsyncMock(
        return_value=MagicMock(channel_id="test_channel_id")
    )
    with patch(
        "src.handlers.incoming.get_channel_by_turn_id", mock_get_channel_by_turn_id
    ):
        result = await process_incoming_messages(
            turn_id=message.turn_id, bot_input=bot_input
        )
    assert result is not None
    assert isinstance(result, Flow)
    assert result.intent == FlowIntent.USER_INPUT
    assert result.user_input is not None
    assert result.user_input.turn_id == "test_turn_id"
    assert result.user_input.message is not None
    assert result.user_input.message.message_type == MessageType.FORM_REPLY
    assert result.user_input.message.form_reply is not None
    assert result.user_input.message.form_reply.form_data == {"field": "value"}
