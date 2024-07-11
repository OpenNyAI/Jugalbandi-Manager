from unittest.mock import patch, AsyncMock, MagicMock
import pytest

from lib.data_models import (
    ChannelInput,
    BotOutput,
    MessageType,
    ChannelIntent,
    MessageData,
    OptionsListType,
)

mock_storage_instance = MagicMock()
mock_write_file = AsyncMock()
mock_public_url = AsyncMock(return_value="https://storage.url/test_audio.ogg")

mock_storage_instance.write_file = mock_write_file
mock_storage_instance.public_url = mock_public_url

mock_encryption_handler = MagicMock()
mock_encryption_handler.decrypt_dict = MagicMock(return_value={"whatsapp": "api_key"})
mock_encryption_handler.decrypt_text = MagicMock(return_value="api_key")

with patch(
    "lib.file_storage.StorageHandler.get_async_instance",
    return_value=mock_storage_instance,
):
    with patch("lib.encryption_handler.EncryptionHandler", mock_encryption_handler):
        import src.handlers.outgoing

        send_message_to_user = src.handlers.outgoing.send_message_to_user


@pytest.mark.asyncio
async def test_send_text_message():
    mock_get_user_by_session_id = AsyncMock(
        return_value=MagicMock(identifier="1234567890")
    )
    mock_get_channel_by_session_id = AsyncMock(
        return_value=MagicMock(app_id="test_number", key="encrypted_credentials")
    )
    mock_wa_send_text_message = MagicMock(return_value="test_channel_id")
    mock_create_message = AsyncMock()

    with patch(
        "src.handlers.outgoing.get_user_by_session_id", mock_get_user_by_session_id
    ):
        with patch(
            "src.handlers.outgoing.get_channel_by_session_id",
            mock_get_channel_by_session_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_text_message",
                mock_wa_send_text_message,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    message = ChannelInput(
                        source="language",
                        message_id="test_msg_id",
                        turn_id="test_turn_id",
                        session_id="test_session_id",
                        intent=ChannelIntent.BOT_OUT,
                        data=BotOutput(
                            message_data=MessageData(message_text="Hello"),
                            message_type=MessageType.TEXT,
                        ),
                    )
                    await send_message_to_user(message)
                    mock_wa_send_text_message.assert_called_once_with(
                        wa_bnumber="test_number",
                        wa_api_key="api_key",
                        user_tele="1234567890",
                        text="Hello",
                    )
                    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_audio_message():
    mock_get_user_by_session_id = AsyncMock(
        return_value=MagicMock(identifier="1234567890")
    )
    mock_get_channel_by_session_id = AsyncMock(
        return_value=MagicMock(app_id="test_number", key="encrypted_credentials")
    )
    mock_wa_send_audio_message = MagicMock(return_value="test_channel_id")
    mock_create_message = AsyncMock()

    with patch(
        "src.handlers.outgoing.get_user_by_session_id", mock_get_user_by_session_id
    ):
        with patch(
            "src.handlers.outgoing.get_channel_by_session_id",
            mock_get_channel_by_session_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_audio_message",
                mock_wa_send_audio_message,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    message = ChannelInput(
                        source="language",
                        message_id="test_msg_id",
                        turn_id="test_turn_id",
                        session_id="test_session_id",
                        intent=ChannelIntent.BOT_OUT,
                        data=BotOutput(
                            message_data=MessageData(
                                media_url="https://example.com/audio.ogg"
                            ),
                            message_type=MessageType.AUDIO,
                        ),
                    )
                    await send_message_to_user(message)
                    mock_wa_send_audio_message.assert_called_once_with(
                        wa_bnumber="test_number",
                        wa_api_key="api_key",
                        user_tele="1234567890",
                        audio_url="https://example.com/audio.ogg",
                    )
                    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_interactive_message():
    mock_get_user_by_session_id = AsyncMock(
        return_value=MagicMock(identifier="1234567890")
    )
    mock_get_channel_by_session_id = AsyncMock(
        return_value=MagicMock(app_id="test_number", key="encrypted_credentials")
    )
    mock_wa_send_interactive_message = MagicMock(return_value="test_channel_id")
    mock_create_message = AsyncMock()

    with patch(
        "src.handlers.outgoing.get_user_by_session_id", mock_get_user_by_session_id
    ):
        with patch(
            "src.handlers.outgoing.get_channel_by_session_id",
            mock_get_channel_by_session_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_interactive_message",
                mock_wa_send_interactive_message,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    message = ChannelInput(
                        source="language",
                        message_id="test_msg_id",
                        turn_id="test_turn_id",
                        session_id="test_session_id",
                        intent=ChannelIntent.BOT_OUT,
                        data=BotOutput(
                            message_data=MessageData(message_text="Choose a language"),
                            message_type=MessageType.INTERACTIVE,
                            header="Header",
                            footer="Footer",
                            menu_selector="Selector",
                            menu_title="Title",
                            options_list=[
                                OptionsListType(id="1", title="Option 1"),
                                OptionsListType(id="2", title="Option 2"),
                            ],
                        ),
                    )
                    await send_message_to_user(message)
                    mock_wa_send_interactive_message.assert_called_once()
                    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_image_message():
    mock_get_user_by_session_id = AsyncMock(
        return_value=MagicMock(identifier="1234567890")
    )
    mock_get_channel_by_session_id = AsyncMock(
        return_value=MagicMock(app_id="test_number", key="encrypted_credentials")
    )
    mock_wa_send_image = MagicMock(return_value="test_channel_id")
    mock_create_message = AsyncMock()

    with patch(
        "src.handlers.outgoing.get_user_by_session_id", mock_get_user_by_session_id
    ):
        with patch(
            "src.handlers.outgoing.get_channel_by_session_id",
            mock_get_channel_by_session_id,
        ):
            with patch("lib.whatsapp.WhatsappHelper.wa_send_image", mock_wa_send_image):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    message = ChannelInput(
                        source="language",
                        message_id="test_msg_id",
                        turn_id="test_turn_id",
                        session_id="test_session_id",
                        intent=ChannelIntent.BOT_OUT,
                        data=BotOutput(
                            message_data=MessageData(
                                message_text="Image caption",
                                media_url="https://example.com/image.jpg",
                            ),
                            message_type=MessageType.IMAGE,
                            header="Header",
                            footer="Footer",
                            menu_selector="Selector",
                            menu_title="Title",
                            options_list=None,
                        ),
                    )
                    await send_message_to_user(message)
                    mock_wa_send_image.assert_called_once_with(
                        wa_bnumber="test_number",
                        wa_api_key="api_key",
                        user_tele="1234567890",
                        message="Image caption",
                        header="Header",
                        body="Image caption",
                        footer="Footer",
                        menu_selector="Selector",
                        menu_title="Title",
                        options=None,
                        media_url="https://example.com/image.jpg",
                    )
                    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_document_message():
    mock_get_user_by_session_id = AsyncMock(
        return_value=MagicMock(identifier="1234567890")
    )
    mock_get_channel_by_session_id = AsyncMock(
        return_value=MagicMock(app_id="test_number", key="encrypted_credentials")
    )
    mock_wa_send_document = MagicMock(return_value="test_channel_id")
    mock_create_message = AsyncMock()

    with patch(
        "src.handlers.outgoing.get_user_by_session_id", mock_get_user_by_session_id
    ):
        with patch(
            "src.handlers.outgoing.get_channel_by_session_id",
            mock_get_channel_by_session_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_document",
                mock_wa_send_document,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    message = ChannelInput(
                        source="language",
                        message_id="test_msg_id",
                        turn_id="test_turn_id",
                        session_id="test_session_id",
                        intent=ChannelIntent.BOT_OUT,
                        data=BotOutput(
                            message_data=MessageData(
                                message_text="Document title",
                                media_url="https://example.com/document.pdf",
                            ),
                            message_type=MessageType.DOCUMENT,
                        ),
                        dialog="",
                    )
                    await send_message_to_user(message)
                    mock_wa_send_document.assert_called_once_with(
                        wa_bnumber="test_number",
                        wa_api_key="api_key",
                        user_tele="1234567890",
                        document_url="https://example.com/document.pdf",
                        document_name="Document title",
                    )
                    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_form_message():
    mock_get_user_by_session_id = AsyncMock(
        return_value=MagicMock(identifier="1234567890")
    )
    mock_get_channel_by_session_id = AsyncMock(
        return_value=MagicMock(app_id="test_number", key="encrypted_credentials")
    )
    mock_get_form_parameters = AsyncMock(
        return_value={
            "form_token": "form_token",
            "screen_id": "screen_id",
            "flow_id": "flow_id",
        }
    )
    mock_wa_send_form = MagicMock(return_value="test_channel_id")
    mock_create_message = AsyncMock()

    with patch(
        "src.handlers.outgoing.get_user_by_session_id", mock_get_user_by_session_id
    ):
        with patch(
            "src.handlers.outgoing.get_channel_by_session_id",
            mock_get_channel_by_session_id,
        ):
            with patch(
                "src.handlers.outgoing.WhatsappHelper.wa_send_form", mock_wa_send_form
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    with patch(
                        "src.handlers.outgoing.get_form_parameters",
                        mock_get_form_parameters,
                    ):
                        message = ChannelInput(
                            source="language",
                            message_id="test_msg_id",
                            turn_id="test_turn_id",
                            session_id="test_session_id",
                            intent=ChannelIntent.BOT_OUT,
                            data=BotOutput(
                                message_data=MessageData(message_text="Form body"),
                                message_type=MessageType.FORM,
                                footer="Form footer",
                                form_id="form_id",
                            ),
                            dialog="",
                        )
                        await send_message_to_user(message)
                    mock_wa_send_form.assert_called_once_with(
                        wa_bnumber="test_number",
                        wa_api_key="api_key",
                        user_tele="1234567890",
                        body="Form body",
                        footer="Form footer",
                        form_parameters={
                            "form_token": "form_token",
                            "screen_id": "screen_id",
                            "flow_id": "flow_id",
                        },
                    )
                    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_language_message():
    mock_get_user_by_session_id = AsyncMock(
        return_value=MagicMock(identifier="1234567890")
    )
    mock_get_channel_by_session_id = AsyncMock(
        return_value=MagicMock(app_id="test_number", key="encrypted_credentials")
    )
    mock_wa_send_text_message = MagicMock(return_value="test_channel_id")
    mock_wa_send_interactive_message = MagicMock(return_value="test_channel_id")
    mock_create_message = AsyncMock()

    with patch(
        "src.handlers.outgoing.get_user_by_session_id", mock_get_user_by_session_id
    ):
        with patch(
            "src.handlers.outgoing.get_channel_by_session_id",
            mock_get_channel_by_session_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_text_message",
                mock_wa_send_text_message,
            ):
                with patch(
                    "lib.whatsapp.WhatsappHelper.wa_send_interactive_message",
                    mock_wa_send_interactive_message,
                ):
                    with patch(
                        "src.handlers.outgoing.create_message", mock_create_message
                    ):
                        message = ChannelInput(
                            source="language",
                            message_id="test_msg_id",
                            turn_id="test_turn_id",
                            session_id="test_session_id",
                            intent=ChannelIntent.BOT_OUT,
                            data=BotOutput(
                                message_data=MessageData(message_text="Hello"),
                                message_type=MessageType.TEXT,
                            ),
                            dialog="language",
                        )
                        await send_message_to_user(message)
                        mock_wa_send_text_message.assert_called_once()
                        mock_wa_send_interactive_message.assert_called_once()
                        assert mock_create_message.call_count == 2
