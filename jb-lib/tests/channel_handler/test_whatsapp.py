import json
import base64
from unittest.mock import patch, MagicMock, AsyncMock, Mock
import pytest
from lib.data_models import (
    MessageType,
    Message,
    TextMessage,
    AudioMessage,
    InteractiveReplyMessage,
    Option,
    ImageMessage,
    ListMessage,
    ButtonMessage,
    DocumentMessage,
    DialogMessage,
    DialogOption,
)
from lib.models import JBChannel, JBUser
from lib.channel_handler.pinnacle_whatsapp_handler import PinnacleWhatsappHandler as WhatsAppHandler

# Mocks for StorageHandler and EncryptionHandler
mock_storage_instance = MagicMock()
mock_write_file = AsyncMock()
mock_public_url = AsyncMock(return_value="https://storage.url/test_audio.ogg")
mock_storage_instance.write_file = mock_write_file
mock_storage_instance.public_url = mock_public_url

mock_encryption_handler = MagicMock()
mock_encryption_handler.decrypt_dict = Mock(
    side_effect=lambda x: {k: v.replace("encrypted_", "decrypted_") for k, v in x.items()}
)
mock_encryption_handler.decrypt_text = Mock(
    side_effect=lambda x: x.replace("encrypted_", "decrypted_")
)

with patch("lib.file_storage.handler.StorageHandler.get_sync_instance", return_value=mock_storage_instance):
    with patch("lib.encryption_handler.EncryptionHandler", mock_encryption_handler):
        from lib.channel_handler.pinnacle_whatsapp_handler import PinnacleWhatsappHandler as WhatsAppHandler

# Fixtures
@pytest.fixture
def sample_channel():
    return JBChannel(
        id="sample_channel_id",
        app_id="test_whatsapp_bot_id",
        key="encrypted_test_channel_key",
        url="https://api.whatsapp.com"
    )

@pytest.fixture
def sample_user():
    return JBUser(
        user_identifier="test_whatsapp_identifier",
        user_name="Test User"
    )

@pytest.fixture
def sample_message_text():
    return Message(
        message_type=MessageType.TEXT,
        text=TextMessage(body="Hello")
    )

@pytest.fixture
def sample_message_audio():
    return Message(
        message_type=MessageType.AUDIO,
        audio=AudioMessage(media_url="https://storage.url/test_audio.ogg")
    )

@pytest.fixture
def sample_message_image():
    return Message(
        message_type=MessageType.IMAGE,
        image=ImageMessage(url="https://storage.url/test_image.jpg", caption="Test Image")
    )

@pytest.fixture
def sample_message_list():
    options = [Option(option_id="1", option_text="Option 1")]
    return Message(
        message_type=MessageType.OPTION_LIST,
        option_list=ListMessage(header="Header", body="Body", footer="Footer", button_text="Button", options=options, list_title="List Title")
    )

@pytest.fixture
def sample_message_button():
    options = [Option(option_id="1", option_text="Option 1")]
    return Message(
        message_type=MessageType.BUTTON,
        button=ButtonMessage(header="Header", body="Body", footer="Footer", options=options)
    )

@pytest.fixture
def sample_message_document():
    return Message(
        message_type=MessageType.DOCUMENT,
        document=DocumentMessage(url="https://storage.url/test_document.pdf", name="Test Document", caption="Test Caption")
    )

test_output_messages = {
    "text_message": (
        Message(
            message_type=MessageType.TEXT,
            text=TextMessage(body="Hello"),
        ),
        "sendMessage",
        json.dumps(
            {
                "messaging_product": "whatsapp",
                "preview_url": False,
                "recipient_type": "individual",
                "to": "test_whatsapp_identifier",
                "type": "text",
                "text": {"body": "Hello"},
            }
        ),
    ),
}

test_input_messages = {
    "text_message": (
        {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {"display_phone_number": "1234567890"},
                                "messages": [
                                    {
                                        "from": "test_whatsapp_identifier",
                                        "type": "text",
                                        "text": {"body": "Hello"},
                                    }
                                ],
                            }
                        }
                    ]
                }
            ],
        },
        {
            "user_identifier": "test_whatsapp_identifier",
            "user_name": "Dummy",
            "data": {
                "type": "text",
                "text": {"body": "Hello"},
            },
        },
    ),
}

@pytest.mark.parametrize(
    "message",
    list(test_input_messages.values()),
    ids=list(test_input_messages.keys()),
)
def test_is_valid_data(message):
    assert WhatsAppHandler.is_valid_data(message[0]) is True

def test_get_channel_name():
    assert WhatsAppHandler.get_channel_name() == "pinnacle_whatsapp"

@pytest.mark.parametrize(
    "message",
    list(test_input_messages.values()),
    ids=list(test_input_messages.keys()),
)
def test_process_message(message):
    channel_data = [msg for msg in WhatsAppHandler.process_message(message[0])]
    assert len(channel_data) == 1
    assert channel_data[0].message_data == message[1]["data"]
    assert channel_data[0].user.user_identifier == message[1]["user_identifier"]
    assert channel_data[0].user.user_name == message[1]["user_name"]

@patch("requests.get")
def test_whatsapp_download_audio(mock_get, sample_channel):
    mock_response = MagicMock()
    mock_response.content = b"audio content"
    mock_get.return_value = mock_response

    with patch("lib.channel_handler.whatsapp_handler.requests.get", mock_get):
        file_content = WhatsAppHandler.wa_download_audio(
            sample_channel, "file_id"
        )

    assert file_content == base64.b64encode(b"audio content")

def test_parse_text_message(sample_channel, sample_user, sample_message_text):
    data = WhatsAppHandler.parse_bot_output(
        sample_message_text, sample_user, sample_channel
    )
    assert data["to"] == "test_whatsapp_identifier"
    assert data["text"]["body"] == "Hello"


@pytest.mark.parametrize(
    "message",
    list(test_output_messages.values()),
    ids=list(test_output_messages.keys()),
)
def test_send_message(message, sample_channel, sample_user):
    mock_post = MagicMock()
    with patch("lib.channel_handler.whatsapp_handler.requests.post") as mock_post:
        WhatsAppHandler.send_message(sample_channel, sample_user, message[0])
        mock_post.assert_called_once_with(
            f"{sample_channel.url}/v1/messages",
            data=message[2],
            headers={"Content-type": "application/json", "wanumber": sample_channel.app_id, "apikey": "decrypted_test_channel_key"},
        )
