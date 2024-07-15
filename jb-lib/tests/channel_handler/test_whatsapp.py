# import pytest
# import base64
# import json
# from typing import Dict, Generator
# from unittest.mock import patch, MagicMock, AsyncMock
# from lib.data_models import (
#     Message,
#     MessageType,
#     TextMessage,
#     AudioMessage,
#     InteractiveReplyMessage,
#     DialogOption,
#     DialogMessage,
#     Option,
#     RestBotInput,
# )

# mock_storage_instance = MagicMock()
# mock_write_file = AsyncMock()
# mock_public_url = AsyncMock(return_value="https://storage.url/test_audio.ogg")

# mock_storage_instance.write_file = mock_write_file
# mock_storage_instance.public_url = mock_public_url

# with patch("lib.channel_handler.pinnacle_whatsapp_handler", mock_storage_instance):
#     from lib.channel_handler.pinnacle_whatsapp_handler import (
#         PinnacleWhatsappHandler,
#         ChannelData,
#         User,
#         JBChannel,
#         JBUser,
#     )


# @pytest.fixture
# def valid_data():
#     return {
#         "object": "whatsapp_business_account",
#         "entry": [
#             {
#                 "changes": [
#                     {
#                         "value": {
#                             "metadata": {"display_phone_number": "1234567890"},
#                             "messages": [
#                                 {
#                                     "from": "user1",
#                                     "type": "text",
#                                     "text": {"body": "hello"},
#                                 }
#                             ],
#                         }
#                     }
#                 ]
#             }
#         ],
#     }


# @pytest.fixture
# def invalid_data():
#     return {"object": "not_whatsapp_business_account"}


# @pytest.fixture
# def jb_channel():
#     return JBChannel(
#         app_id="app_id", key="encrypted_key", url="https://api.whatsapp.com"
#     )


# @pytest.fixture
# def jb_user():
#     return JBUser(identifier="user1")


# @pytest.fixture
# def text_message():
#     return Message(message_type=MessageType.TEXT, text=TextMessage(body="hello"))


# def test_is_valid_data(valid_data, invalid_data):
#     assert PinnacleWhatsappHandler.is_valid_data(valid_data) == True
#     assert PinnacleWhatsappHandler.is_valid_data(invalid_data) == False


# def test_process_message(valid_data):
#     generator = PinnacleWhatsappHandler.process_message(valid_data)
#     result = next(generator)
#     assert isinstance(result, ChannelData)
#     assert result.bot_identifier == "1234567890"
#     assert result.user.user_identifier == "user1"
#     assert result.message_data == {"type": "text", "text": {"body": "hello"}}


# def test_get_channel_name():
#     assert PinnacleWhatsappHandler.get_channel_name() == "pinnacle_whatsapp"


# def test_to_message_text(jb_channel):
#     bot_input = RestBotInput(data={"type": "text", "text": {"body": "hello"}})
#     result = PinnacleWhatsappHandler.to_message("turn_id", jb_channel, bot_input)
#     assert result.message_type == MessageType.TEXT
#     assert result.text.body == "hello"


# @patch("pinnacle_whatsapp_handler.PinnacleWhatsappHandler.wa_download_audio")
# @patch("pinnacle_whatsapp_handler.storage.write_file")
# def test_to_message_audio(mock_write_file, mock_download_audio, jb_channel):
#     mock_download_audio.return_value = base64.b64encode(b"audio_content").decode(
#         "utf-8"
#     )
#     bot_input = RestBotInput(data={"type": "audio", "audio": {"id": "audio_id"}})
#     result = PinnacleWhatsappHandler.to_message("turn_id", jb_channel, bot_input)
#     assert result.message_type == MessageType.AUDIO
#     assert mock_write_file.called_once()


# def test_parse_bot_output_text(jb_channel, jb_user, text_message):
#     result = PinnacleWhatsappHandler.parse_bot_output(text_message, jb_user, jb_channel)
#     assert result["type"] == "text"
#     assert result["text"]["body"] == "hello"


# def test_parse_text_message(jb_channel, jb_user):
#     text_message = TextMessage(body="hello")
#     result = PinnacleWhatsappHandler.parse_text_message(
#         jb_channel, jb_user, text_message
#     )
#     assert result["type"] == "text"
#     assert result["text"]["body"] == "hello"


# @patch("requests.post")
# def test_send_message(mock_post, jb_channel, jb_user, text_message):
#     mock_post.return_value = MagicMock(
#         status_code=200, json=lambda: {"messages": [{"id": "message_id"}]}
#     )
#     result = PinnacleWhatsappHandler.send_message(jb_channel, jb_user, text_message)
#     assert result == "message_id"
#     assert mock_post.called_once()
