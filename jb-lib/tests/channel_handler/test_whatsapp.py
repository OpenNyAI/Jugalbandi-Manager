import unittest
from unittest.mock import patch, MagicMock
from lib.channel_handler.pinnacle_whatsapp_handler import PinnacleWhatsappHandler, ChannelData, User, JBChannel, JBUser, Message, TextMessage, AudioMessage, InteractiveReplyMessage, ButtonMessage, ListMessage, ImageMessage, DocumentMessage, FormMessage, DialogMessage, DialogOption

class TestPinnacleWhatsappHandler(unittest.TestCase):

    @patch('PinnacleWhatsappHandler.is_valid_data')
    def test_is_valid_data(self, mock_is_valid_data):
        data = {"object": "whatsapp_business_account"}
        mock_is_valid_data.return_value = True
        self.assertTrue(PinnacleWhatsappHandler.is_valid_data(data))

    @patch('PinnacleWhatsappHandler.is_valid_data')
    def test_process_message(self, mock_is_valid_data):
        mock_is_valid_data.return_value = True
        data = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "display_phone_number": "1234567890"
                                },
                                "messages": [
                                    {
                                        "from": "user1",
                                        "id": "message1",
                                        "type": "text",
                                        "text": {"body": "Hello"}
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        messages = list(PinnacleWhatsappHandler.process_message(data))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].user.user_identifier, "user1")

    def test_get_channel_name(self):
        self.assertEqual(PinnacleWhatsappHandler.get_channel_name(), "pinnacle_whatsapp")

    def test_to_message_text(self):
        turn_id = "turn1"
        channel = JBChannel(key="key", app_id="app_id", url="url")
        bot_input = MagicMock()
        bot_input.data = {"type": "text", "text": {"body": "Hello"}}
        message = PinnacleWhatsappHandler.to_message(turn_id, channel, bot_input)
        self.assertEqual(message.text.body, "Hello")

    @patch('PinnacleWhatsappHandler.wa_download_audio')
    @patch('storage.write_file')
    def test_to_message_audio(self, mock_write_file, mock_wa_download_audio):
        mock_wa_download_audio.return_value = base64.b64encode(b"audio_content").decode('utf-8')
        turn_id = "turn1"
        channel = JBChannel(key="key", app_id="app_id", url="url")
        bot_input = MagicMock()
        bot_input.data = {"type": "audio", "audio": {"id": "audio1"}}
        message = PinnacleWhatsappHandler.to_message(turn_id, channel, bot_input)
        self.assertEqual(message.audio.media_url, mock_write_file.return_value)

    def test_parse_bot_output_text(self):
        message = Message(message_type="text", text=TextMessage(body="Hello"))
        user = JBUser(identifier="user1")
        channel = JBChannel(key="key", app_id="app_id", url="url")
        data = PinnacleWhatsappHandler.parse_bot_output(message, user, channel)
        self.assertEqual(data["text"]["body"], "Hello")

    def test_parse_text_message(self):
        message = TextMessage(body="Hello")
        user = JBUser(identifier="user1")
        channel = JBChannel(key="key", app_id="app_id", url="url")
        data = PinnacleWhatsappHandler.parse_text_message(channel, user, message)
        self.assertEqual(data["text"]["body"], "Hello")

    def test_parse_audio_message(self):
        message = AudioMessage(media_url="http://example.com/audio.ogg")
        user = JBUser(identifier="user1")
        channel = JBChannel(key="key", app_id="app_id", url="url")
        data = PinnacleWhatsappHandler.parse_audio_message(channel, user, message)
        self.assertEqual(data["audio"]["link"], "http://example.com/audio.ogg")

    def test_parse_list_message(self):
        options = [Option(option_id="option1", option_text="Option 1")]
        message = ListMessage(header="Header", body="Body", footer="Footer", button_text="Button", list_title="Title", options=options)
        user = JBUser(identifier="user1")
        channel = JBChannel(key="key", app_id="app_id", url="url")
        data = PinnacleWhatsappHandler.parse_list_message(channel, user, message)
        self.assertEqual(data["interactive"]["action"]["sections"][0]["rows"][0]["title"], "Option 1")

    def test_parse_button_message(self):
        options = [Option(option_id="option1", option_text="Option 1")]
        message = ButtonMessage(header="Header", body="Body", footer="Footer", options=options)
        user = JBUser(identifier="user1")
        channel = JBChannel(key="key", app_id="app_id", url="url")
        data = PinnacleWhatsappHandler.parse_button_message(channel, user, message)
        self.assertEqual(data["interactive"]["action"]["buttons"][0]["reply"]["title"], "Option 1")

    def test_parse_image_message(self):
        message = ImageMessage(url="http://example.com/image.jpg", caption="Image")
        user = JBUser(identifier="user1")
        channel = JBChannel(key="key", app_id="app_id", url="url")
        data = PinnacleWhatsappHandler.parse_image_message(channel, user, message)
        self.assertEqual(data["image"]["link"], "http://example.com/image.jpg")

    def test_parse_document_message(self):
        message = DocumentMessage(url="http://example.com/doc.pdf", name="Document", caption="Document")
        user = JBUser(identifier="user1")
        channel = JBChannel(key="key", app_id="app_id", url="url")
        data = PinnacleWhatsappHandler.parse_document_message(channel, user, message)
        self.assertEqual(data["document"]["link"], "http://example.com/doc.pdf")

    @patch('PinnacleWhatsappHandler.get_form_parameters')
    def test_parse_form_message(self, mock_get_form_parameters):
        mock_get_form_parameters.return_value = {"param": "value"}
        message = FormMessage(form_id="form1", body="Body", footer="Footer")
        user = JBUser(identifier="user1")
        channel = JBChannel(key="key", app_id="app_id", url="url")
        data = PinnacleWhatsappHandler.parse_form_message(channel, user, message)
        self.assertEqual(data["interactive"]["action"]["parameters"], {"param": "value"})

    def test_parse_dialog_message_language_change(self):
        message = DialogMessage(dialog_id=DialogOption.LANGUAGE_CHANGE)
        user = JBUser(identifier="user1")
        channel = JBChannel(key="key", app_id="app_id", url="url")
        data = PinnacleWhatsappHandler.parse_dialog_message(channel, user, message)
        self.assertEqual(data["interactive"]["type"], "list")

    @patch('EncryptionHandler.decrypt_text')
    def test_generate_header(self, mock_decrypt_text):
        mock_decrypt_text.return_value = "decrypted_key"
        channel = JBChannel(key="key", app_id="app_id", url="url")
        headers = PinnacleWhatsappHandler.generate_header(channel)
        self.assertEqual(headers["apikey"], "decrypted_key")

    @patch('PinnacleWhatsappHandler.parse_bot_output')
    @patch('PinnacleWhatsappHandler.generate_header')
    @patch('requests.post')
    def test_send_message(self, mock_post, mock_generate_header, mock_parse_bot_output):
        mock_parse_bot_output.return_value = {"data": "value"}
        mock_generate_header.return_value = {"header": "value"}
        mock_post.return_value.json.return_value = {"messages": [{"id": "message1"}]}
        channel = JBChannel(key="key", app_id="app_id", url="url")
        user = JBUser(identifier="user1")
        message = Message(message_type="text", text=TextMessage(body="Hello"))
        message_id = PinnacleWhatsappHandler.send_message(channel, user, message)
        self.assertEqual(message_id, "message1")

    @patch('requests.get')
    def test_wa_download_audio(self, mock_get):
        mock_get.return_value.content = b"audio_content"
        channel = JBChannel(key="key", app_id="app_id", url="url")
        file_id = "file1"
        file_content = PinnacleWhatsappHandler.wa_download_audio(channel, file_id)
        self.assertEqual(base64.b64decode(file_content), b"audio_content")


if __name__ == "__main__":
    unittest.main()
