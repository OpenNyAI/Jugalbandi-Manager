import base64
import json
from typing import Any, Dict, Generator
import requests

from sqlalchemy import select
from lib.encryption_handler import EncryptionHandler

from ..db_session_handler import DBSessionHandler
from ..file_storage.handler import StorageHandler
from .channel_handler import ChannelData, RestChannelHandler, User
from .language import LanguageMapping
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
    RestBotInput,
    ListMessage,
    ButtonMessage,
    DialogMessage,
    DialogOption,
)
from ..models import JBChannel, JBUser, JBForm


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
            bot_identifier = from_details["id"]
            yield ChannelData(
                bot_identifier=str(bot_identifier),
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
    def to_message(
        cls, turn_id: str, channel: JBChannel, bot_input: RestBotInput
    ) -> Message:
        data = bot_input.data
        message_data = data
        if "text" in message_data:
            text = message_data["text"]
            return Message(
                message_type=MessageType.TEXT,
                text=TextMessage(body=text),
            )
        elif "audio" in message_data or "voice" in message_data:
            audio_type = "audio" if "audio" in message_data else "voice"
            audio_id = message_data[audio_type]["file_id"]
            audio_content = cls.telegram_download_audio(
                channel=channel, file_id=audio_id
            )
            audio_bytes = base64.b64decode(audio_content)
            audio_file_name = f"{turn_id}.ogg"
            storage = StorageHandler.get_sync_instance()
            storage.write_file(audio_file_name, audio_bytes, "audio/ogg")
            storage_url = storage.public_url(audio_file_name)

            return Message(
                message_type=MessageType.AUDIO,
                audio=AudioMessage(media_url=storage_url),
            )
        elif "document" in message_data:
            file_id = message_data["document"]["file_id"]
            file_content = cls.telegram_download_document(
                channel=channel, file_id=file_id
            )
            file_bytes = base64.b64decode(file_content)
            file_name = message_data["file_name"]
            storage = StorageHandler.get_sync_instance()
            storage.write_file(file_name, file_bytes, "application/octet-stream")
            storage_url = storage.public_url(file_name)

            return Message(
                message_type=MessageType.DOCUMENT,
                document=DocumentMessage(
                    url=storage_url, name=file_name, caption=message_data.get("caption")
                ),
            )
        elif "photo" in message_data:
            file_id = message_data["photo"][0]["file_id"]
            file_content = cls.telegram_download_photo(channel=channel, file_id=file_id)
            file_bytes = base64.b64decode(file_content)
            file_name = f"{turn_id}.jpg"
            storage = StorageHandler.get_sync_instance()
            storage.write_file(file_name, file_bytes, "image/jpeg")
            storage_url = storage.public_url(file_name)

            return Message(
                message_type=MessageType.IMAGE,
                image=ImageMessage(
                    url=storage_url, caption=message_data.get("caption")
                ),
            )
        elif "data" in message_data:
            options = [
                Option(
                    option_id=message_data["data"],
                    option_text=message_data["data"],
                )
            ]
            return Message(
                message_type=MessageType.INTERACTIVE_REPLY,
                interactive_reply=InteractiveReplyMessage(options=options),
            )
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
    def get_form_parameters(cls, form_id: str):
        with DBSessionHandler.get_sync_session() as session:
            with session.begin():
                result = session.execute(select(JBForm).where(JBForm.id == form_id))
                s = result.scalars().first()
                return s

    @classmethod
    def parse_form_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: FormMessage,
    ) -> Dict[str, Any]:
        form_id = message.form_id

        form_parameters = cls.get_form_parameters(form_id)
        data = {
            "chat_id": str(user.identifier),
            "text": message.body,
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": param["text"], "callback_data": param["data"]}]
                    for param in form_parameters
                ]
            },
        }
        return data

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
        encrypted_key: str = str(channel.key)
        decrypted_key = EncryptionHandler.decrypt_text(encrypted_key)
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
