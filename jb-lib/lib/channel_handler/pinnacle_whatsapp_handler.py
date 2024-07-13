import base64
import json
import os
from typing import Any, Dict, Generator
import requests

from sqlalchemy import select

from lib.db_session_handler import DBSessionHandler
from ..file_storage.handler import StorageHandler
from ..channel_handler.channel_handler import ChannelData, RestChannelHandler, User
from ..channel_handler.language import LanguageMapping, LanguageCodes
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
    FormReplyMessage
)
from ..models import JBChannel, JBUser, JBForm
from lib.encryption_handler import EncryptionHandler

storage = StorageHandler.get_sync_instance()

class PinnacleWhatsappHandler(RestChannelHandler):

    @classmethod
    def is_valid_data(cls, data: Dict) -> bool:
        return "object" in data and data["object"] == "whatsapp_business_account"

    @classmethod
    def process_message(cls, data: Dict) -> Generator[ChannelData, None, None]:
        if cls.is_valid_data(data):
            for entry in data["entry"]:
                for change in entry["changes"]:
                    if "value" in change:
                        if "metadata" in change["value"]:
                            metadata = change["value"]["metadata"]
                            whatsapp_number = metadata.get("display_phone_number")
                        if "messages" in change["value"]:
                            for message in change["value"]["messages"]:
                                user_identifier = message.pop("from")
                                yield ChannelData(
                                    bot_identifier=whatsapp_number,
                                    user=User(
                                        user_identifier=user_identifier,
                                        user_name="Dummy",
                                        user_phone=user_identifier,
                                    ),
                                    message_data=message,
                                )

    @classmethod
    def get_channel_name(cls) -> str:
        return "pinnacle_whatsapp"

    @classmethod
    def to_message(
        cls, turn_id: str, channel: JBChannel, bot_input: RestBotInput
    ) -> Message:
        data = bot_input.data
        message_type = data["type"]
        message_data = data[message_type]
        if message_type == "text":
            text = message_data["body"]
            return Message(
                message_type=MessageType.TEXT,
                text=TextMessage(body=text),
            )
        elif message_type == "audio":
            audio_id = message_data["id"]
            audio_content = cls.wa_download_audio(channel=channel, file_id=audio_id)
            audio_bytes = base64.b64decode(audio_content)
            audio_file_name = f"{turn_id}.ogg"
            storage.write_file(audio_file_name, audio_bytes, "audio/ogg")
            storage_url = storage.public_url(audio_file_name)

            return Message(
                message_type=MessageType.AUDIO,
                audio=AudioMessage(media_url=storage_url),
            )
        elif message_type == "interactive":
            interactive_type = message_data["type"]
            interactive_message_data = message_data[interactive_type]
            if interactive_type == "button_reply":
                options = [
                    Option(
                        option_id=interactive_message_data["id"],
                        option_text=interactive_message_data["title"],
                    )
                ]
                return Message(
                    message_type=MessageType.INTERACTIVE_REPLY,
                    interactive_reply=InteractiveReplyMessage(options=options),
                )
            elif interactive_type == "list_reply":
                if (selected_language:=interactive_message_data["id"]).startswith("lang_"):
                    selected_language = selected_language.replace("lang_", "").upper()
                    return Message(
                        message_type=MessageType.DIALOG,
                        dialog=DialogMessage(
                            dialog_id=DialogOption.LANGUAGE_SELECTED,
                            dialog_input=LanguageCodes[selected_language].value.lower()
                        ),
                    )
                options = [
                    Option(
                        option_id=interactive_message_data["id"],
                        option_text=interactive_message_data["title"],
                    )
                ]
                return Message(
                    message_type=MessageType.INTERACTIVE_REPLY,
                    interactive_reply=InteractiveReplyMessage(options=options),
                )
            elif interactive_type == "nfm_reply":
                return Message(
                    message_type=MessageType.FORM_REPLY,
                    form_reply=FormReplyMessage(form_data=interactive_message_data["response_json"])
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
                channel=channel,
                user=user,
                message=message.option_list
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
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.identifier),
            "type": "text",
            "text": {"body": str(message.body)},
        }
        return data

    @classmethod
    def parse_audio_message(
        cls, channel: JBChannel, user: JBUser, message: AudioMessage
    ) -> Dict[str, Any]:
        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.identifier),
            "type": "audio",
            "audio": {"link": message.media_url},
        }
        return data

    @classmethod
    def parse_list_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: ListMessage,
    ) -> Dict[str, Any]:
        list_message_data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.identifier),
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": message.header[:59] if message.header else None,
                },
                "body": {"text": message.body},
                "footer": {"text": message.footer},
                "action": {
                    "button": message.button_text,
                    "sections": [
                        {
                            "title": message.list_title,
                            "rows": [
                                {
                                    "id": option.option_id,
                                    "title": option.option_text[:20],
                                }
                                for option in message.options
                            ],
                        }
                    ],
                },
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
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.identifier),
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": message.header[:59] if message.header else None,
                },
                "body": {"text": message.body},
                "footer": {"text": message.footer},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": x.option_id, "title": x.option_text[:20]},
                        }
                        for x in message.options
                    ],
                },
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
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.identifier),
            "type": "image",
            "image": {"link": message.url, "caption": message.caption},
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
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.identifier),
            "type": "document",
            "document": {
                "link": message.url,
                "filename": message.name,
                "caption": message.caption,
            },
        }
        return data

    @classmethod
    def get_form_parameters(cls, form_id: str):
        # Create a query to insert a new row into JBPluginMapping
        with DBSessionHandler() as session:
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
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.identifier),
            "type": "interactive",
            "interactive": {
                "type": "flow",
                "body": {"text": message.body},
                "footer": {"text": message.footer},
                "action": {
                    "name": "flow",
                    "parameters": form_parameters,
                },
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
                Option(option_id=f"lang_{language.lower()}", option_text=representation.value)
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
        encryption_key: str = str(channel.key)
        decrypted_key = EncryptionHandler.decrypt_text(encryption_key)
        headers = {
            "Content-type": "application/json",
            "wanumber": channel.app_id,
            "apikey": decrypted_key,
        }
        return headers

    @classmethod
    def send_message(cls, channel: JBChannel, user: JBUser, message: Message):
        url = f'{channel.url}/v1/messages'
        headers = cls.generate_header(channel=channel)
        data = cls.parse_bot_output(message=message, channel=channel, user=user)
        import logging
        r = requests.post(url, data=json.dumps(data), headers=headers)
        json_output = r.json()
        logging.error(json_output)
        if json_output and json_output["messages"]:
            return json_output["messages"][0]["id"]
        return None

    @classmethod
    def wa_download_audio(cls, channel: JBChannel, file_id: str):
        url = f"{channel.url}/v1/downloadmedia/{file_id}"
        headers = cls.generate_header(channel=channel)
        r = requests.get(url, headers=headers)
        file_content = base64.b64encode(r.content)
        return file_content