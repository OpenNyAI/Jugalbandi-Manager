from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, model_validator


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
    TEXT = "text"
    AUDIO = "audio"
    BUTTON = "button"
    OPTION_LIST = "option_list"
    INTERACTIVE_REPLY = "interactive_reply"
    FORM = "form"
    FORM_REPLY = "form_reply"
    DOCUMENT = "document"
    IMAGE = "image"
    DIALOG = "dialog"


class TextMessage(BaseModel):
    header: Optional[str] = None
    body: str
    footer: Optional[str] = None


class AudioMessage(BaseModel):
    media_url: str


class Option(BaseModel):
    option_id: str
    option_text: str


class InteractiveMessage(BaseModel):
    header: str
    body: str
    footer: str


class ButtonMessage(InteractiveMessage):
    options: List[Option]


class ListMessage(InteractiveMessage):
    button_text: str
    list_title: str
    options: List[Option]


class FormMessage(BaseModel):
    header: str
    body: str
    footer: str
    form_id: str


class ImageMessage(BaseModel):
    url: str
    caption: str


class DocumentMessage(BaseModel):
    url: str
    name: str
    caption: str


class InteractiveReplyMessage(BaseModel):
    options: List[Option]


class FormReplyMessage(BaseModel):
    form_data: Dict[str, str]


class DialogOption(Enum):
    CONVERSATION_RESET = "CONVERSATION_RESET"
    LANGUAGE_CHANGE = "LANGUAGE_CHANGE"
    LANGUAGE_SELECTED = "LANGUAGE_SELECTED"


class DialogMessage(BaseModel):
    dialog_id: DialogOption
    dialog_input: Optional[str] = None


class Message(BaseModel):
    message_type: MessageType
    text: Optional[TextMessage] = None
    audio: Optional[AudioMessage] = None
    button: Optional[ButtonMessage] = None
    option_list: Optional[ListMessage] = None
    interactive_reply: Optional[InteractiveReplyMessage] = None
    form: Optional[FormMessage] = None
    form_reply: Optional[FormReplyMessage] = None
    image: Optional[ImageMessage] = None
    document: Optional[DocumentMessage] = None
    dialog: Optional[DialogMessage] = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: Dict):
        """Validates data field"""
        message_type = values.get("message_type")
        text = values.get("text")
        audio = values.get("audio")
        button = values.get("button")
        option_list = values.get("option_list")
        form = values.get("form")
        image = values.get("image")
        document = values.get("document")
        interactive_reply = values.get("interactive_reply")
        form_reply = values.get("form_reply")
        dialog = values.get("dialog")

        if message_type == MessageType.TEXT and text is None:
            raise ValueError(
                f"text cannot be None for message type: {message_type.name}"
            )
        elif message_type == MessageType.AUDIO and audio is None:
            raise ValueError(
                f"audio cannot be None for message type: {message_type.name}"
            )
        elif message_type == MessageType.BUTTON and button is None:
            raise ValueError(
                f"button cannot be None for message type : {message_type.name}"
            )
        elif message_type == MessageType.OPTION_LIST and option_list is None:
            raise ValueError(
                f"option_list cannot be None for message type: {message_type.name}"
            )
        elif message_type == MessageType.FORM and form is None:
            raise ValueError(
                f"form cannot be None for message type: {message_type.name}"
            )
        elif message_type == MessageType.IMAGE and image is None:
            raise ValueError(
                f"image cannot be None for message type: {message_type.name}"
            )
        elif message_type == MessageType.DOCUMENT and document is None:
            raise ValueError(
                f"document cannot be None for message type: {message_type.name}"
            )
        elif (
            message_type == MessageType.INTERACTIVE_REPLY and interactive_reply is None
        ):
            raise ValueError(
                f"interactive_reply cannot be None for message type: {message_type.name}"
            )
        elif message_type == MessageType.FORM_REPLY and form_reply is None:
            raise ValueError(
                f"form_reply cannot be None for message type: {message_type.name}"
            )
        elif message_type == MessageType.DIALOG and dialog is None:
            raise ValueError(
                f"dialog cannot be None for message type: {message_type.name}"
            )

        return values


class FSMIntent(Enum):
    CONVERSATION_RESET = "CONVERSATION_RESET"
    LANGUAGE_CHANGE = "LANGUAGE_CHANGE"
    SEND_MESSAGE = "SEND_MESSAGE"
    RAG_CALL = "RAG_CALL"


class RAGQuery(BaseModel):
    collection_name: str
    query: str
    top_chunk_k_value: int


class FSMInput(BaseModel):
    user_input: Optional[str] = None
    callback_input: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: Dict):
        """Validates data field"""
        user_input = values.get("user_input")
        callback_input = values.get("callback_input")
        if user_input is None and callback_input is None:
            raise ValueError("user_input or callback_input is required")
        elif user_input is not None and callback_input is not None:
            raise ValueError(
                "user_input and callback_input cannot be provided together"
            )
        return values


class FSMOutput(BaseModel):
    intent: FSMIntent
    message: Optional[Message] = None
    rag_query: Optional[RAGQuery] = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: Dict):
        """Validates data field"""
        intent = values.get("intent")
        message = values.get("message")
        rag_query = values.get("rag_query")

        if intent == FSMIntent.SEND_MESSAGE and message is None:
            raise ValueError(f"message cannot be None for intent: {intent.name}")
        elif intent == FSMIntent.RAG_CALL and rag_query is None:
            raise ValueError(f"rag_query cannot be None for intent: {intent.name}")
        return values
