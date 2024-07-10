from unittest.mock import patch, MagicMock
import pytest
from lib.data_models import (
    ChannelInput,
    MessageType,
    ChannelIntent,
)

from app.handlers import handle_callback


@pytest.mark.asyncio
@patch("app.handlers.get_active_channel_by_identifier")
@patch("app.handlers.get_user_by_number")
@patch("app.handlers.create_user")
@patch("app.handlers.create_session")
@patch("app.handlers.get_user_session")
@patch("app.handlers.update_session")
@patch("app.handlers.create_turn")
@patch("app.handlers.create_message")
async def test_text_message(
    mock_create_message,
    mock_create_turn,
    mock_update_session,
    mock_get_user_session,
    mock_create_session,
    mock_create_user,
    mock_get_user_by_number,
    mock_get_active_channel_by_identifier,
):
    mock_get_active_channel_by_identifier.return_value = MagicMock(id="channel123")
    mock_get_user_by_number.return_value = None
    mock_create_user.return_value = MagicMock(id="user123")
    mock_create_session.return_value = MagicMock(id="session123")
    mock_get_user_session.return_value = None
    mock_create_turn.return_value = "turn123"
    mock_create_message.return_value = "msg123"

    callback_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "some_id",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "919876543210",
                                "phone_number_id": "phone_no_id1",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "John Doe"},
                                    "wa_id": "919999999999",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "919999999999",
                                    "id": "whatsapp_msg_id1",
                                    "timestamp": "1714990325",
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
    }
    result = [msg async for msg in handle_callback(callback_data)]

    # Assertions
    assert len(result) == 1
    assert isinstance(result[0], ChannelInput)
    assert result[0].session_id == "session123"
    assert result[0].message_id == "msg123"
    assert result[0].turn_id == "turn123"
    assert result[0].intent == ChannelIntent.BOT_IN
    assert result[0].channel_data.type == MessageType.TEXT
    assert result[0].channel_data.text["body"] == "How are you?"

    mock_get_active_channel_by_identifier.assert_called_once_with(
        "919876543210", "whatsapp"
    )
    mock_get_user_by_number.assert_called_once_with("919999999999", "channel123")
    mock_create_user.assert_called_once_with(
        "channel123", "919999999999", "Dummy", "Dummy"
    )
    mock_create_session.assert_called_once_with("user123", "channel123")
    mock_create_turn.assert_called_once_with(
        session_id="session123", channel_id="channel123", turn_type="text", channel="WA"
    )
    mock_create_message.assert_called_once_with(
        turn_id="turn123",
        message_type="text",
        channel="WA",
        channel_id="whatsapp_msg_id1",
        is_user_sent=True,
    )


@pytest.mark.asyncio
@patch("app.handlers.get_active_channel_by_identifier")
@patch("app.handlers.get_user_by_number")
@patch("app.handlers.create_user")
@patch("app.handlers.create_session")
@patch("app.handlers.get_user_session")
@patch("app.handlers.update_session")
@patch("app.handlers.create_turn")
@patch("app.handlers.create_message")
async def test_audio_message(
    mock_create_message,
    mock_create_turn,
    mock_update_session,
    mock_get_user_session,
    mock_create_session,
    mock_create_user,
    mock_get_user_by_number,
    mock_get_active_channel_by_identifier,
):
    mock_get_active_channel_by_identifier.return_value = MagicMock(id="channel123")
    mock_get_user_by_number.return_value = None
    mock_create_user.return_value = MagicMock(id="user123")
    mock_create_session.return_value = MagicMock(id="session123")
    mock_get_user_session.return_value = None
    mock_create_turn.return_value = "turn123"
    mock_create_message.return_value = "msg123"

    callback_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "some_id_2",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "919876543210",
                                "phone_number_id": "phone_no_id2",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "John Doe"},
                                    "wa_id": "919999999999",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "919999999999",
                                    "id": "whatsapp_msg_id2",
                                    "timestamp": "1714990407",
                                    "type": "audio",
                                    "audio": {
                                        "mime_type": "audio/ogg; codecs=opus",
                                        "sha256": "random_sha256_value",
                                        "id": "audio_id1",
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
    }
    result = [msg async for msg in handle_callback(callback_data)]

    # Assertions
    assert len(result) == 1
    assert isinstance(result[0], ChannelInput)
    assert result[0].session_id == "session123"
    assert result[0].message_id == "msg123"
    assert result[0].turn_id == "turn123"
    assert result[0].intent == ChannelIntent.BOT_IN
    assert result[0].channel_data.type == MessageType.AUDIO
    assert result[0].channel_data.audio["id"] == "audio_id1"

    mock_get_active_channel_by_identifier.assert_called_once_with(
        "919876543210", "whatsapp"
    )
    mock_get_user_by_number.assert_called_once_with("919999999999", "channel123")
    mock_create_user.assert_called_once_with(
        "channel123", "919999999999", "Dummy", "Dummy"
    )
    mock_create_session.assert_called_once_with("user123", "channel123")
    mock_create_turn.assert_called_once_with(
        session_id="session123",
        channel_id="channel123",
        turn_type="audio",
        channel="WA",
    )
    mock_create_message.assert_called_once_with(
        turn_id="turn123",
        message_type="audio",
        channel="WA",
        channel_id="whatsapp_msg_id2",
        is_user_sent=True,
    )


@pytest.mark.asyncio
@patch("app.handlers.get_active_channel_by_identifier")
@patch("app.handlers.get_user_by_number")
@patch("app.handlers.create_user")
@patch("app.handlers.create_session")
@patch("app.handlers.get_user_session")
@patch("app.handlers.update_session")
@patch("app.handlers.create_turn")
@patch("app.handlers.create_message")
async def test_button_reply_message(
    mock_create_message,
    mock_create_turn,
    mock_update_session,
    mock_get_user_session,
    mock_create_session,
    mock_create_user,
    mock_get_user_by_number,
    mock_get_active_channel_by_identifier,
):
    mock_get_active_channel_by_identifier.return_value = MagicMock(id="channel123")
    mock_get_user_by_number.return_value = None
    mock_create_user.return_value = MagicMock(id="user123")
    mock_create_session.return_value = MagicMock(id="session123")
    mock_get_user_session.return_value = None
    mock_create_turn.return_value = "turn123"
    mock_create_message.return_value = "msg123"

    callback_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "some_id3",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "919876543210",
                                "phone_number_id": "phone_no_id3",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "John Doe"},
                                    "wa_id": "919999999999",
                                }
                            ],
                            "messages": [
                                {
                                    "context": {
                                        "from": "919876543210",
                                        "id": "whatsapp_user_id1",
                                    },
                                    "from": "919999999999",
                                    "id": "whatsapp_msg_id2",
                                    "timestamp": "1714990452",
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
    }
    result = [msg async for msg in handle_callback(callback_data)]

    # Assertions
    assert len(result) == 1
    assert isinstance(result[0], ChannelInput)
    assert result[0].session_id == "session123"
    assert result[0].message_id == "msg123"
    assert result[0].turn_id == "turn123"
    assert result[0].intent == ChannelIntent.BOT_IN
    assert result[0].channel_data.type == MessageType.INTERACTIVE
    assert result[0].channel_data.interactive["type"] == "button_reply"
    assert result[0].channel_data.interactive["button_reply"]["id"] == "0"
    assert result[0].channel_data.interactive["button_reply"]["title"] == "Yes"

    mock_get_active_channel_by_identifier.assert_called_once_with(
        "919876543210", "whatsapp"
    )
    mock_get_user_by_number.assert_called_once_with("919999999999", "channel123")
    mock_create_user.assert_called_once_with(
        "channel123", "919999999999", "Dummy", "Dummy"
    )
    mock_create_session.assert_called_once_with("user123", "channel123")
    mock_create_turn.assert_called_once_with(
        session_id="session123",
        channel_id="channel123",
        turn_type="interactive",
        channel="WA",
    )
    mock_create_message.assert_called_once_with(
        turn_id="turn123",
        message_type="interactive",
        channel="WA",
        channel_id="whatsapp_msg_id2",
        is_user_sent=True,
    )


@pytest.mark.asyncio
@patch("app.handlers.get_active_channel_by_identifier")
@patch("app.handlers.get_user_by_number")
@patch("app.handlers.create_user")
@patch("app.handlers.create_session")
@patch("app.handlers.get_user_session")
@patch("app.handlers.update_session")
@patch("app.handlers.create_turn")
@patch("app.handlers.create_message")
async def test_list_reply_message(
    mock_create_message,
    mock_create_turn,
    mock_update_session,
    mock_get_user_session,
    mock_create_session,
    mock_create_user,
    mock_get_user_by_number,
    mock_get_active_channel_by_identifier,
):
    mock_get_active_channel_by_identifier.return_value = MagicMock(id="channel123")
    mock_get_user_by_number.return_value = None
    mock_create_user.return_value = MagicMock(id="user123")
    mock_create_session.return_value = MagicMock(id="session123")
    mock_get_user_session.return_value = None
    mock_create_turn.return_value = "turn123"
    mock_create_message.return_value = "msg123"

    callback_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "some_id4",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "919876543210",
                                "phone_number_id": "phone_no_id4",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "John Doe"},
                                    "wa_id": "919999999999",
                                }
                            ],
                            "messages": [
                                {
                                    "context": {
                                        "from": "919876543210",
                                        "id": "whatsapp_user_id1",
                                    },
                                    "from": "919999999999",
                                    "id": "whatsapp_msg_id3",
                                    "timestamp": "1714990499",
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
    }
    result = [msg async for msg in handle_callback(callback_data)]

    # Assertions
    assert len(result) == 1
    assert isinstance(result[0], ChannelInput)
    assert result[0].session_id == "session123"
    assert result[0].message_id == "msg123"
    assert result[0].turn_id == "turn123"
    assert result[0].intent == ChannelIntent.BOT_IN
    assert result[0].channel_data.type == MessageType.INTERACTIVE
    assert result[0].channel_data.interactive["type"] == "list_reply"
    assert result[0].channel_data.interactive["list_reply"]["id"] == "lang_english"
    assert result[0].channel_data.interactive["list_reply"]["title"] == "English"

    mock_get_active_channel_by_identifier.assert_called_once_with(
        "919876543210", "whatsapp"
    )
    mock_get_user_by_number.assert_called_once_with("919999999999", "channel123")
    mock_create_user.assert_called_once_with(
        "channel123", "919999999999", "Dummy", "Dummy"
    )
    mock_create_session.assert_called_once_with("user123", "channel123")
    mock_create_turn.assert_called_once_with(
        session_id="session123",
        channel_id="channel123",
        turn_type="interactive",
        channel="WA",
    )
    mock_create_message.assert_called_once_with(
        turn_id="turn123",
        message_type="interactive",
        channel="WA",
        channel_id="whatsapp_msg_id3",
        is_user_sent=True,
    )
