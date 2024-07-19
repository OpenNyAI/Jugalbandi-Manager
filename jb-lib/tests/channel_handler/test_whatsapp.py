import json
import base64
from unittest.mock import patch, MagicMock, Mock
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

# Mocks for EncryptionHandler


mock_encryption_handler = MagicMock()
mock_encryption_handler.decrypt_dict = Mock(
    side_effect=lambda x: {
        k: v.replace("encrypted_", "decrypted_") for k, v in x.items()
    }
)
mock_encryption_handler.decrypt_text = Mock(
    side_effect=lambda x: x.replace("encrypted_", "decrypted_")
)

with patch("lib.encryption_handler.EncryptionHandler", mock_encryption_handler):
    from lib.channel_handler.pinnacle_whatsapp_handler import PinnacleWhatsappHandler


# Fixtures
@pytest.fixture
def sample_channel():
    return JBChannel(
        id="sample_channel_id",
        app_id="test_whatsapp_bot_id",
        key="encrypted_test_channel_key",
        url="https://api.whatsapp.com",
    )


@pytest.fixture
def sample_user():
    return JBUser(identifier="test_whatsapp_identifier", id="sample_user_id")


@pytest.fixture
def sample_message_text():
    return test_output_messages["text_message"][0]


@pytest.fixture
def sample_message_audio():
    return test_output_messages["audio_message"][0]


@pytest.fixture
def sample_message_document():
    return test_output_messages["document_message"][0]


@pytest.fixture
def sample_message_image():
    return test_output_messages["image_message"][0]


@pytest.fixture
def sample_message_list():
    return test_output_messages["list_message"][0]


@pytest.fixture
def sample_message_button():
    return test_output_messages["button_message"][0]


test_output_messages = {
    "text_message": (
        Message(
            message_type=MessageType.TEXT,
            text=TextMessage(
                body="Hello",
            ),
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
    "audio_message": (
        Message(
            message_type=MessageType.AUDIO,
            audio=AudioMessage(
                media_url="https://example.com/test-audio.mp3",
            ),
        ),
        "sendVoice",
        json.dumps(
            {
                "messaging_product": "whatsapp",
                "preview_url": False,
                "recipient_type": "individual",
                "to": "test_whatsapp_identifier",
                "type": "audio",
                "audio": {"link": "https://example.com/test-audio.mp3"},
            }
        ),
    ),
    "button_message": (
        Message(
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
        ),
        "sendMessage",
        json.dumps(
            {
                "messaging_product": "whatsapp",
                "preview_url": False,
                "recipient_type": "individual",
                "to": "test_whatsapp_identifier",
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "header": {"type": "text", "text": "Button header"},
                    "body": {"text": "This is a button message"},
                    "footer": {"text": "Button footer"},
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {"id": "1", "title": "Option 1"},
                            },
                            {
                                "type": "reply",
                                "reply": {"id": "2", "title": "Option 2"},
                            },
                        ]
                    },
                },
            }
        ),
    ),
    "list_message": (
        Message(
            message_type=MessageType.OPTION_LIST,
            option_list=ListMessage(
                body="This is a list message",
                header="Button header",
                footer="Button footer",
                button_text="Button text",
                list_title="List title",
                options=[
                    Option(option_id="1", option_text="Option 1"),
                    Option(option_id="2", option_text="Option 2"),
                ],
            ),
        ),
        "sendMessage",
        json.dumps(
            {
                "messaging_product": "whatsapp",
                "preview_url": False,
                "recipient_type": "individual",
                "to": "test_whatsapp_identifier",
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "header": {"type": "text", "text": "Button header"},
                    "body": {"text": "This is a list message"},
                    "footer": {"text": "Button footer"},
                    "action": {
                        "button": "Button text",
                        "sections": [
                            {
                                "title": "List title",
                                "rows": [
                                    {"id": "1", "title": "Option 1"},
                                    {"id": "2", "title": "Option 2"},
                                ],
                            }
                        ],
                    },
                },
            }
        ),
    ),
    "image_message": (
        Message(
            message_type=MessageType.IMAGE,
            image=ImageMessage(
                url="https://example.com/test-image.jpg",
                caption="This is an image",
            ),
        ),
        "sendPhoto",
        json.dumps(
            {
                "messaging_product": "whatsapp",
                "preview_url": False,
                "recipient_type": "individual",
                "to": "test_whatsapp_identifier",
                "type": "image",
                "image": {
                    "link": "https://example.com/test-image.jpg",
                    "caption": "This is an image",
                },
            }
        ),
    ),
    "document_message": (
        Message(
            message_type=MessageType.DOCUMENT,
            document=DocumentMessage(
                url="https://example.com/test-document.pdf",
                name="Document title",
                caption="This is a document",
            ),
        ),
        "sendDocument",
        json.dumps(
            {
                "messaging_product": "whatsapp",
                "preview_url": False,
                "recipient_type": "individual",
                "to": "test_whatsapp_identifier",
                "type": "document",
                "document": {
                    "link": "https://example.com/test-document.pdf",
                    "filename": "Document title",
                    "caption": "This is a document",
                },
            }
        ),
    ),
    "language_message": (
        Message(
            message_type=MessageType.DIALOG,
            dialog=DialogMessage(
                dialog_id=DialogOption.LANGUAGE_CHANGE,
                dialog_input=None,
            ),
        ),
        "sendMessage",
        json.dumps(
            {
                "messaging_product": "whatsapp",
                "preview_url": False,
                "recipient_type": "individual",
                "to": "test_whatsapp_identifier",
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "header": {"type": "text", "text": "Language"},
                    "body": {"text": "Please select your preferred language"},
                    "footer": {
                        "text": "\u092d\u093e\u0937\u093e \u091a\u0941\u0928\u0947\u0902"
                    },
                    "action": {
                        "button": "\u091a\u0941\u0928\u0947\u0902 / Select",
                        "sections": [
                            {
                                "title": "\u092d\u093e\u0937\u093e\u090f\u0901 / Languages",
                                "rows": [
                                    {"id": "lang_english", "title": "English"},
                                    {
                                        "id": "lang_hindi",
                                        "title": "\u0939\u093f\u0902\u0926\u0940",
                                    },
                                    {
                                        "id": "lang_bengali",
                                        "title": "\u09ac\u09be\u0982\u09b2\u09be",
                                    },
                                    {
                                        "id": "lang_gujarati",
                                        "title": "\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0",
                                    },
                                    {
                                        "id": "lang_marathi",
                                        "title": "\u092e\u0930\u093e\u0920\u0940",
                                    },
                                    {
                                        "id": "lang_oriya",
                                        "title": "\u0b13\u0b21\u0b3f\u0b06",
                                    },
                                    {
                                        "id": "lang_punjabi",
                                        "title": "\u0a2a\u0a70\u0a1c\u0a3e\u0a2c\u0a40",
                                    },
                                    {
                                        "id": "lang_kannada",
                                        "title": "\u0c95\u0ca8\u0ccd\u0ca8\u0ca1",
                                    },
                                    {
                                        "id": "lang_malayalam",
                                        "title": "\u0d2e\u0d32\u0d2f\u0d3e\u0d33\u0d02",
                                    },
                                    {
                                        "id": "lang_tamil",
                                        "title": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd",
                                    },
                                ],
                            }
                        ],
                    },
                },
            }
        ),
    ),
}


@pytest.mark.parametrize(
    "message",
    list(test_output_messages.values()),
    ids=list(test_output_messages.keys()),
)
def test_send_message(message, sample_channel, sample_user):
    mock_post = MagicMock()
    with patch(
        "lib.channel_handler.pinnacle_whatsapp_handler.requests.post"
    ) as mock_post:
        PinnacleWhatsappHandler.send_message(sample_channel, sample_user, message[0])
        mock_post.assert_called_once_with(
            f"{sample_channel.url}/v1/messages",
            data=message[2],
            headers={
                "Content-type": "application/json",
                "wanumber": "test_whatsapp_bot_id",
                "apikey": "decrypted_test_channel_key",
            },
        )


test_input_messages = {
    "text_message": (
        {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "test_id_1",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "test_phone_number_1",
                                    "phone_number_id": "test_phone_number_id_1",
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "John Doe"},
                                        "wa_id": "test_wa_id_1",
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "test_wa_id_1",
                                        "id": "test_message_id_1",
                                        "timestamp": "test_timestamp_1",
                                        "text": {"body": "How are you?"},
                                        "type": "text",
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        },
        {
            "user_identifier": "test_wa_id_1",
            "user_name": "Dummy",
            "data": {
                "type": "text",
                "timestamp": "test_timestamp_1",
                "text": {"body": "How are you?"},
            },
        },
    ),
    "audio_message": (
        {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "test_id_2",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "test_phone_number_2",
                                    "phone_number_id": "test_phone_number_id_2",
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "John Doe"},
                                        "wa_id": "test_wa_id_2",
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "test_wa_id_2",
                                        "id": "test_message_id_2",
                                        "timestamp": "test_timestamp_2",
                                        "type": "audio",
                                        "audio": {
                                            "mime_type": "audio/ogg; codecs=opus",
                                            "sha256": "test_sha256_1",
                                            "id": "test_audio_id_1",
                                            "voice": True,
                                        },
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        },
        {
            "user_identifier": "test_wa_id_2",
            "user_name": "Dummy",
            "data": {
                "type": "audio",
                "timestamp": "test_timestamp_2",
                "audio": {
                    "mime_type": "audio/ogg; codecs=opus",
                    "sha256": "test_sha256_1",
                    "id": "test_audio_id_1",
                    "voice": True,
                },
            },
        },
    ),
    "button_reply": (
        {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "test_id_3",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "test_phone_number_3",
                                    "phone_number_id": "test_phone_number_id_3",
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "John Doe"},
                                        "wa_id": "test_wa_id_3",
                                    }
                                ],
                                "messages": [
                                    {
                                        "context": {
                                            "from": "test_phone_number_3",
                                            "id": "test_context_id_1",
                                        },
                                        "from": "test_wa_id_3",
                                        "id": "test_message_id_3",
                                        "timestamp": "test_timestamp_3",
                                        "type": "interactive",
                                        "interactive": {
                                            "type": "button_reply",
                                            "button_reply": {"id": "0", "title": "Yes"},
                                        },
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        },
        {
            "user_identifier": "test_wa_id_3",
            "user_name": "Dummy",
            "data": {
                "type": "interactive",
                "timestamp": "test_timestamp_3",
                "interactive": {
                    "type": "button_reply",
                    "button_reply": {"id": "0", "title": "Yes"},
                },
            },
        },
    ),
    "list_reply": (
        {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "test_id_4",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "test_phone_number_4",
                                    "phone_number_id": "test_phone_number_id_4",
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "John Doe"},
                                        "wa_id": "test_wa_id_4",
                                    }
                                ],
                                "messages": [
                                    {
                                        "context": {
                                            "from": "test_phone_number_4",
                                            "id": "test_context_id_2",
                                        },
                                        "from": "test_wa_id_4",
                                        "id": "test_message_id_4",
                                        "timestamp": "test_timestamp_4",
                                        "type": "interactive",
                                        "interactive": {
                                            "type": "list_reply",
                                            "list_reply": {
                                                "id": "lang_english",
                                                "title": "English",
                                            },
                                        },
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        },
        {
            "user_identifier": "test_wa_id_4",
            "user_name": "Dummy",
            "data": {
                "timestamp": "test_timestamp_4",
                "type": "interactive",
                "interactive": {
                    "type": "list_reply",
                    "list_reply": {
                        "id": "lang_english",
                        "title": "English",
                    },
                },
            },
        },
    ),
}


def test_get_channel_name():
    assert PinnacleWhatsappHandler.get_channel_name() == "pinnacle_whatsapp"


@pytest.mark.parametrize(
    "message",
    list(test_input_messages.values()),
    ids=list(test_input_messages.keys()),
)
def test_is_valid_data(message):
    assert PinnacleWhatsappHandler.is_valid_data(message[0]) is True


@pytest.mark.parametrize(
    "message",
    list(test_input_messages.values()),
    ids=list(test_input_messages.keys()),
)
def test_process_message(message):
    channel_data = [msg for msg in PinnacleWhatsappHandler.process_message(message[0])]
    assert len(channel_data) == 1
    assert channel_data[0].message_data == message[1]["data"]
    assert channel_data[0].user.user_identifier == message[1]["user_identifier"]
    assert channel_data[0].user.user_name == message[1]["user_name"]


@patch("requests.get")
def test_whatsapp_download_audio(mock_get, sample_channel):
    mock_response = MagicMock()
    mock_response.content = b"audio content"
    mock_get.return_value = mock_response

    with patch("lib.channel_handler.pinnacle_whatsapp_handler.requests.get", mock_get):
        file_content = PinnacleWhatsappHandler.wa_download_audio(
            sample_channel, "file_id"
        )

    assert file_content == base64.b64encode(b"audio content")


def test_parse_text_message(sample_channel, sample_user, sample_message_text):
    data = PinnacleWhatsappHandler.parse_bot_output(
        sample_message_text, sample_user, sample_channel
    )
    assert data["to"] == "test_whatsapp_identifier"
    assert data["text"]["body"] == "Hello"
