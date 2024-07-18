import json
import base64
from unittest.mock import patch, MagicMock, Mock
import pytest
from lib.data_models import (
    MessageType,
    TextMessage,
    AudioMessage,
    DocumentMessage,
    Option,
    ImageMessage,
    ListMessage,
    ButtonMessage,
    Message,
    DialogMessage,
    DialogOption,
)
from lib.models import JBChannel, JBUser

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
    from lib.channel_handler import TelegramHandler


@pytest.fixture
def sample_channel():
    return JBChannel(
        id="sample_channel_id",
        app_id="test_telegram_bot_id",
        key="encrypted_test_channel_key",
        url="https://api.telegram.org",
    )


@pytest.fixture
def sample_user():
    return JBUser(id="sample_user_id", identifier="test_telegram_identifier")


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
                "chat_id": "test_telegram_identifier",
                "text": "Hello",
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
                "chat_id": "test_telegram_identifier",
                "voice": "https://example.com/test-audio.mp3",
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
                "chat_id": "test_telegram_identifier",
                "text": "This is a button message",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "Option 1", "callback_data": "1"}],
                        [{"text": "Option 2", "callback_data": "2"}],
                    ]
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
                "chat_id": "test_telegram_identifier",
                "text": "This is a list message",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "Option 1", "callback_data": "1"}],
                        [{"text": "Option 2", "callback_data": "2"}],
                    ]
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
                "chat_id": "test_telegram_identifier",
                "photo": "https://example.com/test-image.jpg",
                "caption": "This is an image",
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
                "chat_id": "test_telegram_identifier",
                "document": "https://example.com/test-document.pdf",
                "caption": "This is a document",
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
                "chat_id": "test_telegram_identifier",
                "text": "Please select your preferred language",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "English", "callback_data": "lang_english"}],
                        [
                            {
                                "text": "\u0939\u093f\u0902\u0926\u0940",
                                "callback_data": "lang_hindi",
                            }
                        ],
                        [
                            {
                                "text": "\u09ac\u09be\u0982\u09b2\u09be",
                                "callback_data": "lang_bengali",
                            }
                        ],
                        [
                            {
                                "text": "\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0",
                                "callback_data": "lang_gujarati",
                            }
                        ],
                        [
                            {
                                "text": "\u092e\u0930\u093e\u0920\u0940",
                                "callback_data": "lang_marathi",
                            }
                        ],
                        [
                            {
                                "text": "\u0b13\u0b21\u0b3f\u0b06",
                                "callback_data": "lang_oriya",
                            }
                        ],
                        [
                            {
                                "text": "\u0a2a\u0a70\u0a1c\u0a3e\u0a2c\u0a40",
                                "callback_data": "lang_punjabi",
                            }
                        ],
                        [
                            {
                                "text": "\u0c95\u0ca8\u0ccd\u0ca8\u0ca1",
                                "callback_data": "lang_kannada",
                            }
                        ],
                        [
                            {
                                "text": "\u0d2e\u0d32\u0d2f\u0d3e\u0d33\u0d02",
                                "callback_data": "lang_malayalam",
                            }
                        ],
                        [
                            {
                                "text": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd",
                                "callback_data": "lang_tamil",
                            }
                        ],
                    ]
                },
            }
        ),
    ),
}

test_input_messages = {
    "text_message": (
        {
            "update_id": 654987321,
            "message": {
                "message_id": 1234,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "test_telegram_first_name",
                    "last_name": "test_telegram_last_name",
                    "username": "test_telegram_username",
                    "language_code": "en",
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "test_telegram_first_name",
                    "last_name": "test_telegram_last_name",
                    "username": "test_telegram_username",
                    "type": "private",
                },
                "date": 1721213755,
                "text": "Hi",
            },
        },
        {
            "data": {"message_id": 1234, "date": 1721213755, "text": "Hi"},
            "user_identifier": "123456789",
            "user_name": "test_telegram_username",
        },
    ),
    "audio_message": (
        {
            "update_id": 654987321,
            "message": {
                "message_id": 1235,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "test_telegram_first_name",
                    "last_name": "test_telegram_last_name",
                    "username": "test_telegram_username",
                    "language_code": "en",
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "test_telegram_first_name",
                    "last_name": "test_telegram_last_name",
                    "username": "test_telegram_username",
                    "type": "private",
                },
                "date": 1721213963,
                "voice": {
                    "duration": 2,
                    "mime_type": "audio/ogg",
                    "file_id": "test_file_id",
                    "file_unique_id": "test_file_unique_id",
                    "file_size": 45368,
                },
            },
        },
        {
            "data": {
                "message_id": 1235,
                "date": 1721213963,
                "voice": {
                    "duration": 2,
                    "mime_type": "audio/ogg",
                    "file_id": "test_file_id",
                    "file_unique_id": "test_file_unique_id",
                    "file_size": 45368,
                },
            },
            "user_identifier": "123456789",
            "user_name": "test_telegram_username",
        },
    ),
    "interactive_reply_message": (
        {
            "update_id": 654987321,
            "callback_query": {
                "id": "test_callback_id",
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "test_telegram_first_name",
                    "last_name": "test_telegram_last_name",
                    "username": "test_telegram_username",
                    "language_code": "en",
                },
                "message": {
                    "message_id": 1236,
                    "from": {
                        "id": 9876543210,
                        "is_bot": True,
                        "first_name": "test_bot_name",
                        "username": "test_bot_username",
                    },
                    "chat": {
                        "id": 123456789,
                        "first_name": "test_telegram_first_name",
                        "last_name": "test_telegram_last_name",
                        "username": "test_telegram_username",
                        "type": "private",
                    },
                    "date": 1721213761,
                    "text": "Please select your preferred option",
                    "reply_markup": {
                        "inline_keyboard": [
                            [{"text": "Option 1", "callback_data": "option_1"}],
                            [{"text": "Option 2", "callback_data": "option_2"}],
                        ]
                    },
                },
                "chat_instance": "-3027013130390797136",
                "data": "option_1",
            },
        },
        {
            "data": {
                "id": "test_callback_id",
                "chat_instance": "-3027013130390797136",
                "data": "option_1",
            },
            "user_identifier": "123456789",
            "user_name": "test_telegram_username",
        },
    ),
}


@pytest.mark.parametrize(
    "message",
    list(test_input_messages.values()),
    ids=list(test_input_messages.keys()),
)
def test_is_valid_data(message):
    assert TelegramHandler.is_valid_data(message[0]) is True


def test_get_channel_name():
    assert TelegramHandler.get_channel_name() == "telegram"


@pytest.mark.parametrize(
    "message",
    list(test_input_messages.values()),
    ids=list(test_input_messages.keys()),
)
def test_process_message(message):
    channel_data = [msg for msg in TelegramHandler.process_message(message[0])]
    assert len(channel_data) == 1
    assert channel_data[0].message_data == message[1]["data"]
    assert channel_data[0].user.user_identifier == message[1]["user_identifier"]
    assert channel_data[0].user.user_name == message[1]["user_name"]


@patch("requests.get")
def test_telegram_download_audio(mock_get, sample_channel):
    mock_response = MagicMock()
    mock_response.content = b"audio content"
    mock_get.return_value = mock_response

    print(mock_response.content)
    print(base64.b64encode(b"audio content"))
    with patch("lib.channel_handler.telegram_handler.requests.get", mock_get):
        file_content = TelegramHandler.telegram_download_audio(
            sample_channel, "file_id"
        )

    assert file_content == base64.b64encode(b"audio content")


def test_parse_text_message(sample_channel, sample_user, sample_message_text):
    data = TelegramHandler.parse_bot_output(
        sample_message_text, sample_user, sample_channel
    )
    assert data["chat_id"] == "test_telegram_identifier"
    assert data["text"] == "Hello"


def test_parse_audio_message(sample_channel, sample_user, sample_message_audio):
    data = TelegramHandler.parse_bot_output(
        sample_message_audio, sample_user, sample_channel
    )
    assert data["chat_id"] == "test_telegram_identifier"
    assert data["voice"] == "https://example.com/test-audio.mp3"


def test_parse_document_message(sample_channel, sample_user, sample_message_document):
    data = TelegramHandler.parse_bot_output(
        sample_message_document, sample_user, sample_channel
    )
    assert data["chat_id"] == "test_telegram_identifier"
    assert data["document"] == "https://example.com/test-document.pdf"


def test_parse_image_message(sample_channel, sample_user, sample_message_image):
    data = TelegramHandler.parse_bot_output(
        sample_message_image, sample_user, sample_channel
    )
    assert data["chat_id"] == "test_telegram_identifier"
    assert data["photo"] == "https://example.com/test-image.jpg"
    assert data["caption"] == "This is an image"


def test_parse_list_message(sample_channel, sample_user, sample_message_list):
    data = TelegramHandler.parse_bot_output(
        sample_message_list, sample_user, sample_channel
    )
    assert data["chat_id"] == "test_telegram_identifier"
    assert data["text"] == "This is a list message"
    assert len(data["reply_markup"]["inline_keyboard"]) == 2


def test_parse_button_message(sample_channel, sample_user, sample_message_button):
    data = TelegramHandler.parse_bot_output(
        sample_message_button, sample_user, sample_channel
    )
    assert data["chat_id"] == "test_telegram_identifier"
    assert data["text"] == "This is a button message"
    assert len(data["reply_markup"]["inline_keyboard"]) == 2


@pytest.mark.parametrize(
    "message",
    list(test_output_messages.values()),
    ids=list(test_output_messages.keys()),
)
def test_send_message(message, sample_channel, sample_user):
    mock_post = MagicMock()
    with patch("lib.channel_handler.telegram_handler.requests.post") as mock_post:
        TelegramHandler.send_message(sample_channel, sample_user, message[0])
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/botdecrypted_test_channel_key/{message[1]}",
            data=message[2],
            headers={"Content-type": "application/json"},
        )
