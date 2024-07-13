import os
import json
import requests
import base64
import logging
import traceback
from enum import Enum

from dotenv import load_dotenv
from typing import List, Optional, Dict

from lib.data_models import (
    MessageType,
    Message,
    TextMessage,
    AudioMessage,
    Option,
    InteractiveReplyMessage,
    DialogMessage,
    DialogOption,
    FormReplyMessage,
    RestBotInput,
)
from lib.file_storage import StorageHandler
from lib.models import JBChannel

load_dotenv()

wa_api_host = os.getenv("WA_API_HOST")

logger = logging.getLogger(__name__)


class WAMsgType(int, Enum):
    text = 0
    audio = 1
    interactive = 2


class WAMsgInfo(object):
    def __init__(self, msgtype: WAMsgType, time: str, content: str):
        self.msgtype = msgtype
        self.time = time
        self.content = content

    def __repr__(self) -> str:
        return f"WAMsgInfo: {self.msgtype} :: {self.time} :: {self.content}"


class WAMsgList(object):
    def __init__(self, mobile: str):
        self.mobile = mobile
        self.time_msg_dict = {}

    def add_msg(self, time: str, text: str, msgtype: WAMsgType):
        self.time_msg_dict[time] = WAMsgInfo(msgtype, time, text)

    def get_msg_list(self):
        return list(self.time_msg_dict.values())


# get inputs from user


class WhatsappHelper:
    @staticmethod
    def extract_whatsapp_business_number(data):
        if "object" in data and data["object"] == "whatsapp_business_account":
            for entry in data["entry"]:
                for change in entry["changes"]:
                    if "value" in change and "metadata" in change["value"]:
                        metadata = change["value"]["metadata"]
                        # Extracting the WhatsApp business number
                        whatsapp_number = metadata.get("display_phone_number", None)
                        if whatsapp_number:
                            return whatsapp_number
        return None

    @staticmethod
    def process_messsage(data: dict):
        if "object" in data and data["object"] == "whatsapp_business_account":
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

    # get audio message from user
    @staticmethod
    def wa_get_user_audio(wa_bnumber: str, wa_api_key: str, audio_id: str):
        b64audio = WhatsappHelper.wa_download_audio(
            wa_bnumber=wa_bnumber, wa_api_key=wa_api_key, fileid=audio_id
        )
        return b64audio

    @staticmethod
    def wa_download_audio(wa_bnumber: str, wa_api_key: str, fileid: dict):
        url = wa_api_host + "/v1/downloadmedia/" + fileid
        headers = {
            "Content-type": "application/json",
            "wanumber": wa_bnumber,
            "apikey": wa_api_key,
        }

        try:
            r = requests.get(url, headers=headers)
            file_content = base64.b64encode(r.content)
            return file_content
        except:
            return None

    # get message status
    @staticmethod
    def wa_get_msg_status(data: dict):
        try:
            msg_status = {}
            if "object" in data and data["object"] == "whatsapp_business_account":
                for entries in data["entry"]:
                    for change in entries["changes"]:
                        if "statuses" in change["value"]:
                            for stat_obj in change["value"]["statuses"]:
                                tele = stat_obj["recipient_id"]
                                msg_id = stat_obj["id"]
                                status = stat_obj["status"]

                                if tele not in msg_status:
                                    msg_status[tele] = {}

                                msg_status[tele][msg_id] = status

            return msg_status
        except:
            return {}

    # send text message
    @staticmethod
    def wa_send_text_message(
        wa_bnumber: str, wa_api_key: str, user_tele: str, text: str
    ) -> str:
        url = wa_api_host + "/v1/messages"
        headers = {
            "Content-type": "application/json",
            "wanumber": wa_bnumber,
            "apikey": wa_api_key,
        }

        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user_tele),
            "type": "text",
            "text": {"body": str(text)},
        }

        try:
            r = requests.post(url, data=json.dumps(data), headers=headers)
            json_output = r.json()
            if json_output and json_output["messages"]:
                return json_output["messages"][0]["id"]

            return None
        except:
            return None

    # send audio message
    @staticmethod
    def wa_send_audio_message(
        wa_bnumber: str, wa_api_key: str, user_tele: str, audio_url: str
    ) -> str:
        url = wa_api_host + "/v1/messages"
        headers = {
            "Content-type": "application/json",
            "wanumber": wa_bnumber,
            "apikey": wa_api_key,
        }

        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user_tele),
            "type": "audio",
            "audio": {"link": audio_url},
        }

        try:
            r = requests.post(url, data=json.dumps(data), headers=headers)
            json_output = r.json()
            if json_output and json_output["messages"]:
                return json_output["messages"][0]["id"]

            return None
        except Exception as e:
            logger.error(
                "Error in sending audio message: %s %s", e, traceback.format_exc()
            )
            return None

    # handle list
    # send list

    @staticmethod
    def wa_send_image(
        wa_bnumber: str,
        wa_api_key: str,
        user_tele: str,
        message: str,
        media_url: str,
    ) -> str:
        url = wa_api_host + "/v1/messages"
        headers = {
            "Content-type": "application/json",
            "wanumber": wa_bnumber,
            "apikey": wa_api_key,
        }

        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user_tele),
            "type": "image",
            "image": {"link": media_url, "caption": message},
        }

        try:
            r = requests.post(url, data=json.dumps(data), headers=headers)
            json_output = r.json()
            if json_output and json_output["messages"]:
                return json_output["messages"][0]["id"]

            else:
                logger.error("Status Code: %s :: %s", r.status_code, json_output)
            return None
        except Exception as e:
            logger.error(
                "Error in sending interactive message: %s, %s",
                e,
                traceback.format_exc(),
            )
            return None

    # handle interactive
    # send interactive
    @staticmethod
    def wa_send_interactive_message(
        wa_bnumber: str,
        wa_api_key: str,
        user_tele: str,
        message: str,
        header: str,
        body: str,
        footer: str,
        menu_selector: str | None,
        menu_title: str,
        options: List[dict],
        media_url: Optional[str] = None,
    ) -> str:
        """Button Title should be <=20"""
        url = wa_api_host + "/v1/messages"
        headers = {
            "Content-type": "application/json",
            "wanumber": wa_bnumber,
            "apikey": wa_api_key,
        }

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
                "messaging_product": "whatsapp",
                "preview_url": False,
                "recipient_type": "individual",
                "to": str(user_tele),
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
                "messaging_product": "whatsapp",
                "preview_url": False,
                "recipient_type": "individual",
                "to": str(user_tele),
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

        try:
            r = requests.post(url, data=json.dumps(data), headers=headers)
            json_output = r.json()
            if json_output and json_output["messages"]:
                return json_output["messages"][0]["id"]
            else:
                logger.error("Status Code: %s :: %s", r.status_code, json_output)
            return None
        except Exception as e:
            logger.error(
                "Error in sending interactive message: %s, %s",
                e,
                traceback.format_exc(),
            )
            return None

    @staticmethod
    def wa_send_document(
        wa_bnumber: str,
        wa_api_key: str,
        user_tele: str,
        document_url: str,
        document_name: str,
        caption: str | None = None,
    ) -> str:
        url = wa_api_host + "/v1/messages"
        headers = {
            "Content-type": "application/json",
            "wanumber": wa_bnumber,
            "apikey": wa_api_key,
        }

        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user_tele),
            "type": "document",
            "document": {
                "link": document_url,
                "filename": document_name,
                "caption": caption,
            },
        }

        try:
            r = requests.post(url, data=json.dumps(data), headers=headers)
            json_output = r.json()
            if json_output and json_output["messages"]:
                return json_output["messages"][0]["id"]

            return None
        except:
            return None

    @staticmethod
    def wa_send_form(
        wa_bnumber: str,
        wa_api_key: str,
        user_tele: str,
        body: str,
        footer: str,
        form_parameters: Dict,
    ) -> str:
        flow_id = form_parameters["flow_id"]
        screen_id = form_parameters["screen_id"]
        token = form_parameters["token"]
        url = wa_api_host + "/alpha/whatsappflows"
        headers = {
            "Content-type": "application/json",
            "wanumber": wa_bnumber,
            "apikey": wa_api_key,
        }

        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": str(user_tele),
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

        try:
            r = requests.post(url, data=json.dumps(data), headers=headers)
            json_output = r.json()
            if json_output and json_output["messages"]:
                return json_output["messages"][0]["id"]

            return None
        except:
            return None

    # higher level method will return the right object based on the message type
