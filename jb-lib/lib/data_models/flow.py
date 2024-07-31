from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, model_validator, Field
from .message import Message, MessageType
from .retriever import RAGResponse


class FlowIntent(Enum):
    BOT = "bot"
    CALLBACK = "callback"
    USER_INPUT = "user_input"
    DIALOG = "dialog"


class BotIntent(Enum):
    INSTALL = "install"
    DELETE = "delete"


class Bot(BaseModel):
    name: str
    fsm_code: str
    requirements_txt: str
    index_urls: Optional[List[str]] = Field(default_factory=list)
    required_credentials: Optional[List[str]] = Field(default_factory=list)
    version: str


class BotConfig(BaseModel):
    bot_id: str
    intent: BotIntent
    bot: Optional[Bot] = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: Dict):
        """Validates data field"""
        intent = values.get("intent")
        bot = values.get("bot")

        if intent == BotIntent.INSTALL and bot is None:
            raise ValueError("Bot cannot be None for intent: INSTALL")
        return values


class UserInput(BaseModel):
    turn_id: str
    message: Message


class CallbackType(Enum):
    EXTERNAL = "external"
    RAG = "rag"


class Callback(BaseModel):
    turn_id: str
    callback_type: CallbackType
    external: Optional[str] = None
    rag_response: Optional[List[RAGResponse]] = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: Dict):
        """Validates data field"""
        callback_type = values.get("callback_type")
        external = values.get("external")
        rag_response = values.get("rag_response")

        if callback_type == CallbackType.EXTERNAL and external is None:
            raise ValueError("external cannot be None for CallbackType: EXTERNAL")
        elif callback_type == CallbackType.RAG and rag_response is None:
            raise ValueError("rag_response cannot be None for CallbackType: RAG")
        return values


class Dialog(BaseModel):
    turn_id: str
    message: Message

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: Dict):
        """Validates data field"""
        message = values.get("message")

        if isinstance(message, Dict):
            message = Message(**message)

        if message.message_type != MessageType.DIALOG:
            raise ValueError("Only dialog message type is allowed for dialog intent")
        return values


class Flow(BaseModel):
    source: str
    intent: FlowIntent
    bot_config: Optional[BotConfig] = None
    dialog: Optional[Dialog] = None
    callback: Optional[Callback] = None
    user_input: Optional[UserInput] = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: Dict):
        """Validates data field"""
        intent = values.get("intent")
        bot_config = values.get("bot_config")
        dialog = values.get("dialog")
        callback = values.get("callback")
        user_input = values.get("user_input")

        if intent == FlowIntent.BOT and bot_config is None:
            raise ValueError(f"bot_config cannot be None for intent: {intent.name}")
        elif intent == FlowIntent.DIALOG and dialog is None:
            raise ValueError(f"dialog cannot be None for intent: {intent.name}")
        elif intent == FlowIntent.CALLBACK and callback is None:
            raise ValueError(f"callback cannot be None for intent: {intent.name}")
        elif intent == FlowIntent.USER_INPUT and user_input is None:
            raise ValueError(f"user_input cannot be None for intent: {intent.name}")
        return values


class FSMIntent(Enum):
    CONVERSATION_RESET = "CONVERSATION_RESET"
    LANGUAGE_CHANGE = "LANGUAGE_CHANGE"
    SEND_MESSAGE = "SEND_MESSAGE"
    RAG_CALL = "RAG_CALL"
    WEBHOOK = "WEBHOOK"


class Webhook(BaseModel):
    reference_id: str


class RAGQuery(BaseModel):
    collection_name: str
    query: str
    top_chunk_k_value: int


class FSMOutput(BaseModel):
    intent: FSMIntent
    message: Optional[Message] = None
    rag_query: Optional[RAGQuery] = None
    webhook: Optional[Webhook] = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: Dict):
        """Validates data field"""
        intent = values.get("intent")
        message = values.get("message")
        rag_query = values.get("rag_query")
        webhook = values.get("webhook")

        if intent == FSMIntent.SEND_MESSAGE and message is None:
            raise ValueError(f"message cannot be None for intent: {intent.name}")
        elif intent == FSMIntent.RAG_CALL and rag_query is None:
            raise ValueError(f"rag_query cannot be None for intent: {intent.name}")
        elif intent == FSMIntent.WEBHOOK and webhook is None:
            raise ValueError(f"webhook cannot be None for intent: {intent.name}")
        return values


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
