from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class Status(Enum):
    """
    Enum class to define the status of the FSM."""

    WAIT_FOR_ME = 0
    WAIT_FOR_USER_INPUT = 1
    MOVE_FORWARD = 2
    WAIT_FOR_CALLBACK = 3
    WAIT_FOR_PLUGIN = 4
    END = 5


class MessageType(Enum):
    """
    Enum class to define the type of message."""

    INTERACTIVE = "interactive"
    TEXT = "text"
    AUDIO = "audio"
    DOCUMENT = "document"
    FORM = "form"
    IMAGE = "image"
    DIALOG = "dialog"


class OptionsListType(BaseModel):
    id: str
    title: str


class MessageData(BaseModel):
    header: Optional[str] = None
    body: str
    footer: Optional[str] = None


class UploadFile(BaseModel):
    path: str
    mime_type: str
    filename: str

class FSMOutput(BaseModel):
    """
    Model class to define the FSM output."""

    dest: str = "out"
    type: MessageType = MessageType.TEXT
    message_data: MessageData
    options_list: Optional[List[OptionsListType]] = None
    media_url: Optional[str] = None
    file: Optional[UploadFile] = None
    whatsapp_flow_id: Optional[str] = None
    whatsapp_screen_id: Optional[str] = None
    dialog: Optional[str] = None
    menu_selector: Optional[str] = None
    menu_title: Optional[str] = None
    form_token: Optional[str] = None
    plugin_uuid: Optional[str] = None