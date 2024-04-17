import base64
import json
import os
from typing import List, Optional

import requests
from dotenv import load_dotenv

from lib.azure_storage import AzureStorage
from lib.channel_handler import RestChannelHandler
from lib.data_models import BotOutput, ChannelData, MessageType
from lib.models import JBChannel, JBUser
from lib.utils import decrypt_credentials

load_dotenv()

azure_creds = {
    "account_url": os.getenv("STORAGE_ACCOUNT_URL"),
    "account_key": os.getenv("STORAGE_ACCOUNT_KEY"),
    "container_name": os.getenv("STORAGE_AUDIOFILES_CONTAINER"),
    "base_path": "input/",
}
storage = AzureStorage(**azure_creds)


class MsgInfo(object):
    def __init__(self, msgtype: MessageType, time: str, content: str):
        self.msgtype = msgtype
        self.time = time
        self.content = content

    def __repr__(self) -> str:
        return f"Custom MsgInfo: {self.msgtype} :: {self.time} :: {self.content}"


class CustomChannelHelper(RestChannelHandler):
    @classmethod
    def extract_app_id(cls, data):
        if "object" in data and data["object"] == "custom":
            for entry in data["entry"]:
                for change in entry["changes"]:
                    if "value" in change and "metadata" in change["value"]:
                        metadata = change["value"]["metadata"]
                        app_id = metadata.get("bot_id", None)
                        if app_id:
                            return app_id
        return None

    @classmethod
    def process_messsage(cls, data: dict):
        if "object" in data and data["object"] == "custom":
            for entries in data["entry"]:
                for change in entries["changes"]:
                    if "messages" in change["value"]:
                        for msg_obj in change["value"]["messages"]:
                            data = {"name": "Dummy"}
                            for key in ["from", "id", "timestamp", "type"]:
                                data[key] = msg_obj[key]
                            t = msg_obj["type"]
                            data[t] = msg_obj[t]
                            yield data

    @classmethod
    def get_channel_name(cls):
        return "custom"

    @classmethod
    def is_valid_channel(cls, data: dict):
        return "object" in data and data["object"] == "custom"

    @classmethod
    def generate_header(cls, channel: JBChannel):
        decrypted_key = decrypt_credentials(channel.key)
        headers = {
            "Content-type": "application/json",
            "Authentication": f"Bearer {decrypted_key}",
        }
        return headers

    @classmethod
    def generate_url(cls, channel: JBChannel, user: JBUser, bot_output: BotOutput):
        return channel.url + "/v1/messages"

    @classmethod
    def send_message(
        cls, channel: JBChannel, user: JBUser, bot_ouput: BotOutput, **kwargs
    ):
        url = cls.generate_url(bot_output=bot_ouput, channel=channel, user=user)
        data = cls.parse_bot_output(bot_output=bot_ouput, channel=channel, user=user)
        headers = cls.generate_header(bot_output=bot_ouput, channel=channel, user=user)
        try:
            r = requests.post(url, data=json.dumps(data), headers=headers)
            json_output = r.json()
            if json_output and json_output["messages"]:
                return json_output["messages"][0]["id"]
            return None
        except Exception:
            return None

    @classmethod
    async def to_bot_input(cls, channel: JBChannel, msg_id: str, msg_obj: ChannelData):
        message_type = msg_obj.type
        if message_type == MessageType.TEXT:
            recieved_message = CustomChannelHelper.get_user_text(msg_obj)
        if message_type == MessageType.AUDIO:
            recieved_message = CustomChannelHelper.get_user_audio(
                channel=channel, msg_obj=msg_obj
            )
            audio_bytes = base64.b64decode(recieved_message.content)
            audio_file_name = f"{msg_id}.ogg"
            await storage.write_file(audio_file_name, audio_bytes, "audio/ogg")
            storage_url = await storage.make_public(audio_file_name)
            recieved_message.content = storage_url
        if message_type == MessageType.INTERACTIVE:
            recieved_message = CustomChannelHelper.get_interactive_reply(msg_obj)
        if message_type == MessageType.FORM:
            recieved_message = CustomChannelHelper.get_form_reply(msg_obj)
        return recieved_message

    @classmethod
    def parse_bot_output(cls, bot_output: BotOutput, channel: JBChannel, user: JBUser):
        message_text = bot_output.message_data.message_text
        message_type = bot_output.message_type
        if message_type == MessageType.TEXT:
            data = cls.parse_text_message(
                channel=channel, user=user, message=message_text
            )
        elif message_type == MessageType.AUDIO:
            media_url = bot_output.message_data.media_url
            data = cls.parse_audio_message(
                channel=channel, user=user, audio_url=media_url
            )
        elif message_type == MessageType.INTERACTIVE:
            data = cls.parse_interactive_message(
                channel=channel,
                user=user,
                message=message_text,
                header=bot_output.header,
                body=message_text,
                footer=bot_output.footer,
                menu_selector=bot_output.menu_selector,
                menu_title=bot_output.menu_title,
                options=(
                    [option.model_dump() for option in bot_output.options_list]
                    if bot_output.options_list
                    else None
                ),
                media_url=bot_output.message_data.media_url,
            )
        elif message_type == MessageType.IMAGE:
            data = cls.parse_image_message(
                channel=channel,
                user=user,
                message=message_text,
                header=bot_output.header,
                body=message_text,
                footer=bot_output.footer,
                menu_selector=bot_output.menu_selector,
                menu_title=bot_output.menu_title,
                options=(
                    [option.model_dump() for option in bot_output.options_list]
                    if bot_output.options_list
                    else None
                ),
                media_url=bot_output.message_data.media_url,
            )
        elif message_type == MessageType.DOCUMENT:
            data = cls.parse_document_message(
                channel=channel,
                user=user,
                document_url=bot_output.message_data.media_url,
                document_name=bot_output.message_data.message_text,
            )
        elif message_type == MessageType.FORM:
            data = cls.parse_form_message(
                channel=channel,
                user=user,
                flow_id=bot_output.wa_flow_id,
                screen_id=bot_output.wa_screen_id,
                body=bot_output.message_data.message_text,
                footer=bot_output.footer,
                token=bot_output.form_token,
            )
        return data

    @classmethod
    def parse_text_message(cls, channel: JBChannel, user: JBUser, text: str) -> str:
        data = {
            "messaging_product": channel.type,
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.phone_number),
            "type": "text",
            "text": {"body": str(text)},
        }
        return data

    @classmethod
    def parse_audio_message(
        cls, channel: JBChannel, user: JBUser, audio_url: str
    ) -> str:
        data = {
            "messaging_product": channel.type,
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.phone_number),
            "type": "audio",
            "audio": {"link": audio_url},
        }
        return data

    @classmethod
    def parse_interactive_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: str,
        header: str,
        body: str,
        footer: str,
        menu_selector: str | None,
        menu_title: str,
        options: List[dict],
        media_url: Optional[str] = None,
    ) -> str:

        header_dict = dict()
        if media_url:
            header_dict = {"type": "image", "image": {"link": media_url}}
        else:
            header_dict = {"type": "text", "text": header[:59] if header else None}

        # force options title to be <= 20 chars
        for x in options:
            x["title"] = x["title"][:20]

        if len(options) > 3:
            # send list
            data = {
                "messaging_product": channel.type,
                "preview_url": False,
                "recipient_type": "individual",
                "to": str(user.phone_number),
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {"text": body},
                    "footer": {"text": footer},
                    "action": {
                        "button": menu_selector,
                        "sections": [{"title": menu_title, "rows": options}],
                    },
                },
            }
        else:
            # send reply buttons
            data = {
                "messaging_product": channel.type,
                "preview_url": False,
                "recipient_type": "individual",
                "to": str(user.phone_number),
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": body},
                    "footer": {"text": footer},
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {"id": x["id"], "title": x["title"]},
                            }
                            for x in options
                        ],
                    },
                },
            }
        if header_dict and header_dict[header_dict["type"]]:
            data["interactive"]["header"] = header_dict
        return data

    @classmethod
    def parse_image_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        message: str,
        header: str,
        body: str,
        footer: str,
        menu_selector: str | None,
        menu_title: str,
        options: Optional[List[dict]],
        media_url: Optional[str] = None,
    ) -> str:
        if options:
            data = cls.parse_interactive_message(
                channel=channel,
                user=user,
                message=message,
                header=header,
                body=body,
                footer=footer,
                menu_selector=menu_selector,
                menu_title=menu_title,
                options=options,
                media_url=media_url,
            )
        else:
            data = {
                "messaging_product": channel.type,
                "preview_url": False,
                "recipient_type": "individual",
                "to": str(user.phone_number),
                "type": "image",
                "image": {"link": media_url, "caption": message},
            }
        return data

    @classmethod
    def parse_document_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        document_url: str,
        document_name: str,
        caption: str | None = None,
    ) -> str:
        data = {
            "messaging_product": channel.type,
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.phone_number),
            "type": "document",
            "document": {
                "link": document_url,
                "filename": document_name,
                "caption": caption,
            },
        }
        return data

    @classmethod
    def parse_form_message(
        cls,
        channel: JBChannel,
        user: JBUser,
        body: str,
        footer: str,
        token: str,
        flow_id: str,
        screen_id: str,
    ) -> str:
        data = {
            "messaging_product": channel.type,
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user.phone_number),
            "type": "interactive",
            "interactive": {
                "type": "flow",
                "body": {"text": body},
                "footer": {"text": footer},
                "action": {
                    "name": "flow",
                    "parameters": {
                        "flow_message_version": "3",
                        "flow_token": token,
                        "flow_id": flow_id,
                        "flow_cta": "Fill Form",
                        "flow_action": "navigate",
                        "flow_action_payload": {"screen": screen_id},
                    },
                },
            },
        }
        return data

    @classmethod
    def get_user_text(cls, msg_obj: ChannelData):
        if msg_obj.type == MessageType.TEXT:
            time_stp = msg_obj.timestamp
            data = msg_obj.text["body"]
            return MsgInfo(MessageType.TEXT, time_stp, data)
        return {}

    @classmethod
    def get_user_audio(cls, channel: JBChannel, msg_obj: ChannelData):
        if msg_obj.type == MessageType.AUDIO:
            time_stp = msg_obj.timestamp
            data = msg_obj.audio["id"]
            b64audio = CustomChannelHelper.download_audio(channel=channel, fileid=data)
            return MsgInfo(MessageType.AUDIO, time_stp, b64audio)
        return {}

    @classmethod
    def get_interactive_reply(cls, msg_obj: ChannelData):
        if msg_obj.type == MessageType.INTERACTIVE:
            time_stp = msg_obj.timestamp
            interaction_type = msg_obj.interactive["type"]
            data = msg_obj.interactive[interaction_type]["id"]
            return MsgInfo(MessageType.INTERACTIVE, time_stp, data)
        return {}

    @classmethod
    def get_form_reply(cls, msg_obj: ChannelData):
        if msg_obj.type == MessageType.FORM:
            time_stp = msg_obj.timestamp
            interaction_type = msg_obj.form["type"]
            data = msg_obj.form[interaction_type]["response_json"]
            return MsgInfo(MessageType.INTERACTIVE, time_stp, data)
        return {}

    @classmethod
    def download_audio(cls, channel: JBChannel, fileid: dict):
        url = channel.url + "/v1/downloadmedia/" + fileid
        headers = CustomChannelHelper.generate_header(channel=channel)
        try:
            r = requests.get(url, headers=headers)
            file_content = base64.b64encode(r.content)
            return file_content
        except Exception:
            return None
