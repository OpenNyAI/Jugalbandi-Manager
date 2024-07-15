import pytest
import base64
import json
from unittest.mock import patch, MagicMock
from typing import Dict
from lib.channel_handler import ChannelData, User
from lib.data_models import (
    MessageType,
    TextMessage,
    AudioMessage,
    InteractiveReplyMessage,
    DocumentMessage,
    Option,
    ImageMessage,
    ListMessage,
    ButtonMessage,
    Message
)
from lib.models import JBChannel, JBUser
from lib.channel_handler.telegram_handler import TelegramHandler
from lib.encryption_handler import EncryptionHandler


@pytest.fixture
def sample_channel():
    return JBChannel(
        id="sample_channel_id",
        app_id="sample_app_id",
        key=EncryptionHandler.encrypt_text("sample_key"),
        url="https://api.telegram.org/bot<bot_token>/sendMessage"
    )

@pytest.fixture
def sample_user():
    return JBUser(id="sample_user_id", identifier="12345")

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
        audio=AudioMessage(media_url="http://example.com/audio.ogg")
    )

@pytest.fixture
def sample_message_document():
    return Message(
        message_type=MessageType.DOCUMENT,
        document=DocumentMessage(url="http://example.com/doc.pdf", name="document.pdf")
    )

@pytest.fixture
def sample_message_image():
    return Message(
        message_type=MessageType.IMAGE,
        image=ImageMessage(url="http://example.com/image.jpg", caption="Sample Image")
    )

@pytest.fixture
def sample_message_list():
    return Message(
        message_type=MessageType.OPTION_LIST,
        option_list=ListMessage(
            body="Choose an option:",
            options=[Option(option_id="1", option_text="Option 1"), Option(option_id="2", option_text="Option 2")]
        )
    )

@pytest.fixture
def sample_message_button():
    return Message(
        message_type=MessageType.BUTTON,
        button=ButtonMessage(
            body="Press a button:",
            options=[Option(option_id="1", option_text="Button 1"), Option(option_id="2", option_text="Button 2")]
        )
    )


def test_is_valid_data():
    valid_data = {"update_id": 12345, "message": {"text": "Hello"}}
    invalid_data = {"update_id": 12345}

    assert TelegramHandler.is_valid_data(valid_data) is True
    assert TelegramHandler.is_valid_data(invalid_data) is False


def test_process_message():
    data = {
        "update_id": 12345,
        "message": {
            "from": {"id": 67890, "username": "test_user"},
            "text": "Hello"
        }
    }
    messages = list(TelegramHandler.process_message(data))
    assert len(messages) == 1
    assert messages[0].user.user_identifier == "67890"


def test_get_channel_name():
    assert TelegramHandler.get_channel_name() == "telegram"


@patch('requests.get')
def test_telegram_download_audio(mock_get, sample_channel):
    mock_response = MagicMock()
    mock_response.content = base64.b64encode(b"audio content")
    mock_get.return_value = mock_response

    file_content = TelegramHandler.telegram_download_audio(sample_channel, "file_id")
    assert file_content == base64.b64encode(b"audio content")


def test_parse_text_message(sample_channel, sample_user, sample_message_text):
    data = TelegramHandler.parse_bot_output(sample_message_text, sample_user, sample_channel)
    assert data["chat_id"] == "12345"
    assert data["text"] == "Hello"


def test_parse_audio_message(sample_channel, sample_user, sample_message_audio):
    data = TelegramHandler.parse_bot_output(sample_message_audio, sample_user, sample_channel)
    assert data["chat_id"] == "12345"
    assert data["audio"] == "http://example.com/audio.ogg"


def test_parse_document_message(sample_channel, sample_user, sample_message_document):
    data = TelegramHandler.parse_bot_output(sample_message_document, sample_user, sample_channel)
    assert data["chat_id"] == "12345"
    assert data["document"] == "http://example.com/doc.pdf"


def test_parse_image_message(sample_channel, sample_user, sample_message_image):
    data = TelegramHandler.parse_bot_output(sample_message_image, sample_user, sample_channel)
    assert data["chat_id"] == "12345"
    assert data["photo"] == "http://example.com/image.jpg"
    assert data["caption"] == "Sample Image"


def test_parse_list_message(sample_channel, sample_user, sample_message_list):
    data = TelegramHandler.parse_bot_output(sample_message_list, sample_user, sample_channel)
    assert data["chat_id"] == "12345"
    assert data["text"] == "Choose an option:"
    assert len(data["reply_markup"]["inline_keyboard"]) == 2


def test_parse_button_message(sample_channel, sample_user, sample_message_button):
    data = TelegramHandler.parse_bot_output(sample_message_button, sample_user, sample_channel)
    assert data["chat_id"] == "12345"
    assert data["text"] == "Press a button:"
    assert len(data["reply_markup"]["inline_keyboard"]) == 2
