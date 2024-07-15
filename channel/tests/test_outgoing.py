from unittest.mock import patch, AsyncMock, MagicMock, Mock
import pytest

from lib.data_models import (
    MessageType,
    Message,
    TextMessage,
    AudioMessage,
    ButtonMessage,
    FormMessage,
    ImageMessage,
    DocumentMessage,
    DialogMessage,
    DialogOption,
    Option,
)

mock_storage_instance = MagicMock()
mock_write_file = AsyncMock()
mock_public_url = AsyncMock(return_value="https://storage.url/test_audio.ogg")

mock_storage_instance.write_file = mock_write_file
mock_storage_instance.public_url = mock_public_url

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
    return_value=mock_storage_instance,
):
    with patch("lib.encryption_handler.EncryptionHandler", mock_encryption_handler):
        import src.handlers.outgoing

        send_message_to_user = src.handlers.outgoing.send_message_to_user


@pytest.mark.asyncio
async def test_send_text_message():
    mock_channel = MagicMock(
        app_id="test_number",
        key="encrypted_credentials",
    )
    mock_user = MagicMock(
        identifier="1234567890",
    )
    mock_get_user_by_turn_id = AsyncMock(return_value=mock_user)
    mock_get_channel_by_turn_id = AsyncMock(return_value=mock_channel)
    mock_wa_send_text_message = MagicMock()
    mock_create_message = AsyncMock()

    message = Message(
        message_type=MessageType.TEXT,
        text=TextMessage(
            body="Hello",
        ),
    )
    turn_id = "test_turn_id"

    with patch("src.handlers.outgoing.get_user_by_turn_id", mock_get_user_by_turn_id):
        with patch(
            "src.handlers.outgoing.get_channel_by_turn_id", mock_get_channel_by_turn_id
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_text_message",
                mock_wa_send_text_message,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    await send_message_to_user(turn_id=turn_id, message=message)

    mock_get_channel_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_get_user_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_wa_send_text_message.assert_called_once_with(
        wa_bnumber="test_number",
        wa_api_key="decrypted_credentials",
        user_tele="1234567890",
        text="Hello",
    )
    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_audio_message():
    mock_channel = MagicMock(
        app_id="test_number",
        key="encrypted_credentials",
    )
    mock_user = MagicMock(
        identifier="1234567890",
    )
    mock_get_user_by_turn_id = AsyncMock(return_value=mock_user)
    mock_get_channel_by_turn_id = AsyncMock(return_value=mock_channel)
    mock_wa_send_audio_message = MagicMock()
    mock_create_message = AsyncMock()

    message = Message(
        message_type=MessageType.AUDIO,
        audio=AudioMessage(
            media_url="https://example.com/audio.ogg",
        ),
    )
    turn_id = "test_turn_id"

    with patch("src.handlers.outgoing.get_user_by_turn_id", mock_get_user_by_turn_id):
        with patch(
            "src.handlers.outgoing.get_channel_by_turn_id",
            mock_get_channel_by_turn_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_audio_message",
                mock_wa_send_audio_message,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    await send_message_to_user(turn_id=turn_id, message=message)
    mock_get_channel_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_get_user_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_wa_send_audio_message.assert_called_once_with(
        wa_bnumber="test_number",
        wa_api_key="decrypted_credentials",
        user_tele="1234567890",
        audio_url="https://example.com/audio.ogg",
    )
    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_interactive_message():
    mock_channel = MagicMock(
        app_id="test_number",
        key="encrypted_credentials",
    )
    mock_user = MagicMock(
        identifier="1234567890",
    )
    mock_get_user_by_turn_id = AsyncMock(return_value=mock_user)
    mock_get_channel_by_turn_id = AsyncMock(return_value=mock_channel)
    mock_wa_send_interactive_message = MagicMock()
    mock_create_message = AsyncMock()

    message = Message(
        message_type=MessageType.BUTTON,
        button=ButtonMessage(
            body="This is a button message",
            header="Button header",
            footer="Button footer",
            options=[
                Option(option_id="1", option_text="Option 1"),
                Option(option_id="2", option_text="Option 2"),
            ],
        ),
    )
    turn_id = "test_turn_id"

    with patch("src.handlers.outgoing.get_user_by_turn_id", mock_get_user_by_turn_id):
        with patch(
            "src.handlers.outgoing.get_channel_by_turn_id",
            mock_get_channel_by_turn_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_interactive_message",
                mock_wa_send_interactive_message,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    await send_message_to_user(turn_id=turn_id, message=message)
    mock_get_channel_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_get_user_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_wa_send_interactive_message.assert_called_once_with(
        wa_bnumber="test_number",
        wa_api_key="decrypted_credentials",
        user_tele="1234567890",
        message="This is a button message",
        header="Button header",
        body="This is a button message",
        footer="Button footer",
        menu_selector=None,
        menu_title="This is a button message",
        options=[
            {"option_id": "1", "option_text": "Option 1"},
            {"option_id": "2", "option_text": "Option 2"},
        ],
    )
    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_image_message():
    mock_channel = MagicMock(
        app_id="test_number",
        key="encrypted_credentials",
    )
    mock_user = MagicMock(
        identifier="1234567890",
    )
    mock_get_user_by_turn_id = AsyncMock(return_value=mock_user)
    mock_get_channel_by_turn_id = AsyncMock(return_value=mock_channel)
    mock_wa_send_image_message = MagicMock()
    mock_create_message = AsyncMock()

    message = Message(
        message_type=MessageType.IMAGE,
        image=ImageMessage(
            url="https://example.com/image.jpg",
            caption="This is an image",
        ),
    )
    turn_id = "test_turn_id"

    with patch("src.handlers.outgoing.get_user_by_turn_id", mock_get_user_by_turn_id):
        with patch(
            "src.handlers.outgoing.get_channel_by_turn_id",
            mock_get_channel_by_turn_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_image",
                mock_wa_send_image_message,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    await send_message_to_user(turn_id=turn_id, message=message)
    mock_get_channel_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_get_user_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_wa_send_image_message.assert_called_once_with(
        wa_bnumber="test_number",
        wa_api_key="decrypted_credentials",
        user_tele="1234567890",
        message="This is an image",
        media_url="https://example.com/image.jpg",
    )
    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_document_message():
    mock_channel = MagicMock(
        app_id="test_number",
        key="encrypted_credentials",
    )
    mock_user = MagicMock(
        identifier="1234567890",
    )
    mock_get_user_by_turn_id = AsyncMock(return_value=mock_user)
    mock_get_channel_by_turn_id = AsyncMock(return_value=mock_channel)
    mock_wa_send_document_message = MagicMock()
    mock_create_message = AsyncMock()

    message = Message(
        message_type=MessageType.DOCUMENT,
        document=DocumentMessage(
            url="https://example.com/document.pdf",
            name="Document title",
            caption="This is a document",
        ),
    )
    turn_id = "test_turn_id"

    with patch("src.handlers.outgoing.get_user_by_turn_id", mock_get_user_by_turn_id):
        with patch(
            "src.handlers.outgoing.get_channel_by_turn_id",
            mock_get_channel_by_turn_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_document",
                mock_wa_send_document_message,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    await send_message_to_user(turn_id=turn_id, message=message)
    mock_get_channel_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_get_user_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_wa_send_document_message.assert_called_once_with(
        wa_bnumber="test_number",
        wa_api_key="decrypted_credentials",
        user_tele="1234567890",
        document_url="https://example.com/document.pdf",
        document_name="Document title",
        caption="This is a document",
    )
    mock_create_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_form_message():
    mock_channel = MagicMock(
        app_id="test_number",
        key="encrypted_credentials",
    )
    mock_user = MagicMock(
        identifier="1234567890",
    )
    mock_get_user_by_turn_id = AsyncMock(return_value=mock_user)
    mock_get_channel_by_turn_id = AsyncMock(return_value=mock_channel)
    mock_wa_send_form = MagicMock()
    mock_create_message = AsyncMock()
    mock_form_parameters = {
        "form_token": "form_token",
        "screen_id": "screen_id",
        "flow_id": "flow_id",
    }
    mock_get_form_parameters = AsyncMock(return_value=mock_form_parameters)

    message = Message(
        message_type=MessageType.FORM,
        form=FormMessage(
            header="Form header",
            body="Form body",
            footer="Form footer",
            form_id="form_id",
        ),
    )
    turn_id = "test_turn_id"

    with patch("src.handlers.outgoing.get_user_by_turn_id", mock_get_user_by_turn_id):
        with patch(
            "src.handlers.outgoing.get_channel_by_turn_id",
            mock_get_channel_by_turn_id,
        ):
            with patch(
                "src.handlers.outgoing.get_form_parameters",
                mock_get_form_parameters,
            ):
                with patch(
                    "lib.whatsapp.WhatsappHelper.wa_send_form",
                    mock_wa_send_form,
                ):
                    with patch(
                        "src.handlers.outgoing.create_message", mock_create_message
                    ):
                        await send_message_to_user(turn_id=turn_id, message=message)
    mock_get_channel_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_get_user_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_wa_send_form.assert_called_once_with(
        wa_bnumber="test_number",
        wa_api_key="decrypted_credentials",
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
    mock_channel = MagicMock(
        app_id="test_number",
        key="encrypted_credentials",
    )
    mock_user = MagicMock(
        identifier="1234567890",
    )
    mock_get_user_by_turn_id = AsyncMock(return_value=mock_user)
    mock_get_channel_by_turn_id = AsyncMock(return_value=mock_channel)
    mock_wa_send_interactive_message = MagicMock()
    mock_create_message = AsyncMock()

    message = Message(
        message_type=MessageType.DIALOG,
        dialog=DialogMessage(
            dialog_id=DialogOption.LANGUAGE_CHANGE,
            dialog_input=None,
        ),
    )

    turn_id = "test_turn_id"

    with patch("src.handlers.outgoing.get_user_by_turn_id", mock_get_user_by_turn_id):
        with patch(
            "src.handlers.outgoing.get_channel_by_turn_id",
            mock_get_channel_by_turn_id,
        ):
            with patch(
                "lib.whatsapp.WhatsappHelper.wa_send_interactive_message",
                mock_wa_send_interactive_message,
            ):
                with patch("src.handlers.outgoing.create_message", mock_create_message):
                    await send_message_to_user(turn_id=turn_id, message=message)
    mock_get_channel_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_get_user_by_turn_id.assert_called_once_with(turn_id=turn_id)
    mock_wa_send_interactive_message.assert_called_once_with(
        wa_bnumber="test_number",
        wa_api_key="decrypted_credentials",
        user_tele="1234567890",
        message="Please select your preferred language",
        header="Language",
        body="Choose a Language",
        footer="भाषा चुनें",
        menu_selector="चुनें / Select",
        menu_title="भाषाएँ / Languages",
        options=[
            {"option_id": "lang_hindi", "option_text": "हिन्दी"},
            {"option_id": "lang_english", "option_text": "English"},
            {"option_id": "lang_bengali", "option_text": "বাংলা"},
            {"option_id": "lang_telugu", "option_text": "తెలుగు"},
            {"option_id": "lang_marathi", "option_text": "मराठी"},
            {"option_id": "lang_tamil", "option_text": "தமிழ்"},
            {"option_id": "lang_gujarati", "option_text": "ગુજરાતી"},
            {"option_id": "lang_urdu", "option_text": "اردو"},
            {"option_id": "lang_kannada", "option_text": "ಕನ್ನಡ"},
            {"option_id": "lang_odia", "option_text": "ଓଡ଼ିଆ"},
        ],
    )
    mock_create_message.assert_called_once()
