import base64
import json
from typing import Any, Dict, Generator
import requests

from lib.encryption_handler import EncryptionHandler
from lib.models import JBChannel, JBUser

from .channel_handler import ChannelData, User
from .rest_channel_handler import RestChannelHandler
from .language import LanguageMapping, LanguageCodes
from ..data_models import (
    MessageType,
    Message,
    TextMessage,
    AudioMessage,
    InteractiveMessage,
    Option,
    FormMessage,
    ImageMessage,
    DocumentMessage,
    InteractiveReplyMessage,
    FormReplyMessage,
    RestBotInput,
    ListMessage,
    ButtonMessage,
    DialogMessage,
    DialogOption,
)


class TelegramHandler(RestChannelHandler):

    @classmethod
    def is_valid_data(cls, data: Dict) -> bool:
        if "update_id" in data and (
            "message" in data
            or "edited_message" in data
            or "channel_post" in data
            or "callback_query" in data
        ):
            return True
        return False

    @classmethod
    def process_message(cls, data: Dict) -> Generator[ChannelData, None, None]:
        if cls.is_valid_data(data):
            if "message" in data:
                message_data = data["message"]
                message_data.pop("chat")
            elif "edited_message" in data:
                message_data = data["edited_message"]
                message_data.pop("chat")
            elif "callback_query" in data:
                message_data = data.get("callback_query")
                message_data.pop("message")
            from_details = message_data.pop("from")
            user_identifier = from_details["id"]
            yield ChannelData(
                user=User(
                    user_identifier=str(user_identifier),
                    user_name=from_details.get("username", "Dummy"),
                    user_phone=str(user_identifier),
                ),
                message_data=message_data,
            )

    @classmethod
    def get_channel_name(cls) -> str:
        return "telegram"

    @classmethod
    def get_message_type(cls, bot_input: RestBotInput) -> MessageType:
        data = bot_input.data
        if "text" in data:
            return MessageType.TEXT
        elif "audio" in data or "voice" in data:
            return MessageType.AUDIO
        elif "document" in data:
            return MessageType.DOCUMENT
        elif "photo" in data:
            return MessageType.IMAGE
        elif "data" in data:
            if data["data"].startswith("lang_"):
                return MessageType.DIALOG
            return MessageType.INTERACTIVE_REPLY
        return NotImplemented

    @classmethod
    def to_text_message(cls, bot_input: RestBotInput) -> TextMessage:
        message_data = bot_input.data
        text = message_data["text"]
        return TextMessage(body=text)

    @classmethod
    def get_audio(cls, channel: JBChannel, bot_input: RestBotInput) -> bytes:
        message_data = bot_input.data
        audio_type = "audio" if "audio" in message_data else "voice"
        audio_id = message_data[audio_type]["file_id"]
        audio_content = cls.telegram_download_audio(channel=channel, file_id=audio_id)
        return audio_content

    @classmethod
    def to_interactive_reply_message(
        cls, bot_input: RestBotInput
    ) -> InteractiveReplyMessage:
        message_data = bot_input.data
        options = [
            Option(
                option_id=message_data["data"],
                option_text=message_data["data"],
            )
        ]
        return InteractiveReplyMessage(options=options)

    @classmethod
    def to_dialog_message(cls, bot_input: RestBotInput) -> DialogMessage:
        message_data = bot_input.data
        selected_language = message_data["data"].replace("lang_", "").upper()
        return DialogMessage(
            dialog_id=DialogOption.LANGUAGE_SELECTED,
            dialog_input=LanguageCodes[selected_language].value.lower(),
        )

    @classmethod
    def to_form_reply_message(cls, bot_input: RestBotInput) -> FormReplyMessage:
        return NotImplemented

    @classmethod
    def parse_bot_output(
        cls, message: Message, user: JBUser, channel: JBChannel
    ) -> Dict:
        message_type = message.message_type
        if message_type == MessageType.TEXT:
            data = cls.parse_text_message(
                channel=channel, user=user, message=message.text
            )
        elif message_type == MessageType.AUDIO:
            data = cls.parse_audio_message(
                channel=channel, user=user, message=message.audio
            )
        elif message_type == MessageType.BUTTON:
            data = cls.parse_button_message(
                channel=channel,
                user=user,
                message=message.button,
            )
        elif message_type == MessageType.OPTION_LIST:
            data = cls.parse_list_message(
                channel=channel, user=user, message=message.option_list
            )
        elif message_type == MessageType.IMAGE:
            data = cls.parse_image_message(
                channel=channel,
                user=user,
                message=message.image,
            )
        elif message_type == MessageType.DOCUMENT:
            data = cls.parse_document_message(
                channel=channel,
                user=user,
                message=message.document,
            )
        elif message_type == MessageType.FORM:
            data = cls.parse_form_message(
                channel=channel,
                user=user,
                message=message.form,
            )
        elif message_type == MessageType.DIALOG:
            data = cls.parse_dialog_message(
                channel=channel,
                user=user,
                message=message.dialog,
            )
        else:
            return NotImplemented
        return data

    @classmethod
    def parse_text_message(
        cls, channel: JBChannel, user: JBUser, message: TextMessage
    ) -> Dict[str, Any]:
        data = {
            "chat_id": str(user.identifier),
            "text": str(message.body),
        }
        return data

    @classmethod
    def parse_audio_message(
        cls, channel: JBChannel, user: JBUser, message: AudioMessage
    ) -> Dict[str, Any]:
        data = {
            "chat_id": str(user.identifier),
            "voice": message.media_url,
        }
        return data

    @classmethod
    def parse_list_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: ListMessage,
    ) -> Dict[str, Any]:
        # Telegram does not have a direct equivalent to list messages
        # Assuming using inline keyboard as a substitute
        list_message_data = {
            "chat_id": str(user.identifier),
            "text": message.body,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": option.option_text[:20],
                            "callback_data": option.option_id,
                        }
                    ]
                    for option in message.options
                ]
            },
        }
        return list_message_data

    @classmethod
    def parse_button_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: ButtonMessage,
    ) -> Dict[str, Any]:
        button_message_data = {
            "chat_id": str(user.identifier),
            "text": message.body,
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": option.option_text[:20],
                            "callback_data": option.option_id,
                        }
                    ]
                    for option in message.options
                ]
            },
        }
        return button_message_data

    @classmethod
    def parse_interactive_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: InteractiveMessage,
    ) -> Dict[str, Any]:
        if isinstance(message, ListMessage):
            data = cls.parse_list_message(channel, user, message)
        elif isinstance(message, ButtonMessage):
            data = cls.parse_button_message(channel, user, message)
        else:
            return NotImplemented
        return data

    @classmethod
    def parse_image_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: ImageMessage,
    ) -> Dict[str, Any]:
        data = {
            "chat_id": str(user.identifier),
            "photo": message.url,
            "caption": message.caption,
        }
        return data

    @classmethod
    def parse_document_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: DocumentMessage,
    ) -> Dict[str, Any]:
        data = {
            "chat_id": str(user.identifier),
            "document": message.url,
            "caption": message.caption,
        }
        return data

    @classmethod
    def parse_form_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: FormMessage,
    ) -> Dict[str, Any]:
        return NotImplemented

    @classmethod
    def parse_dialog_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: DialogMessage,
    ) -> Dict[str, Any]:
        if message.dialog_id == DialogOption.LANGUAGE_CHANGE:
            languages = [
                Option(
                    option_id=f"lang_{language.lower()}",
                    option_text=representation.value,
                )
                for language, representation in LanguageMapping.__members__.items()
            ]
            language_message = ListMessage(
                header="Language",
                body="Please select your preferred language",
                footer="भाषा चुनें",
                options=languages[:10],
                button_text="चुनें / Select",
                list_title="भाषाएँ / Languages",
            )
            return cls.parse_list_message(channel, user, language_message)
        return NotImplemented

    @classmethod
    def generate_header(cls, channel: JBChannel):
        headers = {
            "Content-type": "application/json",
        }
        return headers

    @classmethod
    def generate_url(cls, channel: JBChannel, user: JBUser, message: Message):
        encrypted_key: str = str(channel.key)
        decrypted_key = EncryptionHandler.decrypt_text(encrypted_key)
        if message.message_type == MessageType.AUDIO:
            return f"{channel.url}/bot{decrypted_key}/sendVoice"
        elif message.message_type == MessageType.DOCUMENT:
            return f"{channel.url}/bot{decrypted_key}/sendDocument"
        elif message.message_type == MessageType.IMAGE:
            return f"{channel.url}/bot{decrypted_key}/sendPhoto"
        else:
            return f"{channel.url}/bot{decrypted_key}/sendMessage"

    @classmethod
    def send_message(cls, channel: JBChannel, user: JBUser, message: Message):
        url = f"{cls.generate_url(channel, user, message)}"
        headers = cls.generate_header(channel=channel)
        data = cls.parse_bot_output(message=message, channel=channel, user=user)
        r = requests.post(url, data=json.dumps(data), headers=headers)
        json_output = r.json()
        if json_output and json_output["result"]:
            return json_output["result"]["message_id"]
        return None

    @classmethod
    def download_file(cls, channel: JBChannel, file_id: str):
        encrypted_key: str = str(channel.key)
        decrypted_key = EncryptionHandler.decrypt_text(encrypted_key)
        file_path_url = f"{channel.url}/bot{decrypted_key}/getFile?file_id={file_id}"
        headers = cls.generate_header(channel=channel)
        file_path_response = requests.get(file_path_url, headers=headers).json()
        file_path = file_path_response["result"]["file_path"]
        file_url = f"{channel.url}/file/bot{decrypted_key}/{file_path}"
        file_response = requests.get(file_url)
        file_content = base64.b64encode(file_response.content)
        return file_content

    @classmethod
    def telegram_download_audio(cls, channel: JBChannel, file_id: str):
        return cls.download_file(channel, file_id)

    @classmethod
    def telegram_download_document(cls, channel: JBChannel, file_id: str):
        return cls.download_file(
            channel, file_id
        )  # Same method can be used for documents

    @classmethod
    def telegram_download_photo(cls, channel: JBChannel, file_id: str):
        return cls.download_file(channel, file_id)  # Same method can be used for photos
