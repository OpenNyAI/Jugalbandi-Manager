from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, model_validator


class MessageData(BaseModel):
    message_text: Optional[str] = None
    media_url: Optional[str] = None
    # One has to be present


class MessageType(Enum):
    INTERACTIVE = "interactive"
    TEXT = "text"
    AUDIO = "audio"
    DOCUMENT = "document"
    FORM = "form"
    IMAGE = "image"
    DIALOG = "dialog"


class ChannelIntent(Enum):
    BOT_IN = "bot_in"
    BOT_OUT = "bot_out"


class OptionsListType(BaseModel):
    id: str
    title: str


class BotOutput(BaseModel):
    message_type: MessageType
    message_data: MessageData
    options_list: Optional[List[OptionsListType]] = None
    document: Optional[Dict[str, Any]] = None
    wa_screen_id: Optional[str] = None
    wa_flow_id: Optional[str] = None
    header: Optional[str] = None
    footer: Optional[str] = None
    menu_selector: Optional[str] = None
    menu_title: Optional[str] = None
    form_token: Optional[str] = None


class BotInput(BaseModel):
    message_type: MessageType
    message_data: MessageData


class ChannelData(BaseModel):
    type: MessageType
    timestamp: str
    text: Optional[Dict[str, Any]] = None
    audio: Optional[Dict[str, Any]] = None
    interactive: Optional[Dict[str, Any]] = None
    form: Optional[Dict[str, Any]] = None


class ChannelInput(BaseModel):
    source: str
    session_id: str
    message_id: Optional[str] = None
    turn_id: str
    intent: ChannelIntent
    channel_data: Optional[ChannelData] = None
    data: BotInput | BotOutput
    dialog: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values):
        """Validates data field"""
        data = values.get("data")
        if isinstance(data, (BotInput, BotOutput)):
            return values
        intent = values.get("intent")
        if intent == ChannelIntent.BOT_IN.value:
            values["data"] = BotInput(**data)
        elif intent == ChannelIntent.BOT_OUT.value:
            values["data"] = BotOutput(**data)
        else:
            raise ValueError("Invalid type")
        return values


class LanguageIntent(Enum):
    LANGUAGE_IN = "language_in"
    LANGUAGE_OUT = "language_out"


class LanguageInput(BaseModel):
    source: str
    session_id: str
    message_id: Optional[str] = None
    turn_id: str
    intent: LanguageIntent
    # message_type: Optional[MessageType] = None
    # message_data: MessageData
    # options_list: Optional[List[OptionsListType]] = None
    data: BotInput | BotOutput

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values):
        """Validates data field"""
        data = values.get("data")
        if isinstance(data, (BotInput, BotOutput)):
            return values
        intent = values.get("intent")
        if intent == LanguageIntent.LANGUAGE_IN.value:
            values["data"] = BotInput(**data)
        elif intent == LanguageIntent.LANGUAGE_OUT.value:
            values["data"] = BotOutput(**data)
        else:
            raise ValueError("Invalid type")
        return values


class UploadFile(BaseModel):
    path: str
    mime_type: str
    filename: str


class FSMOutput(BaseModel):
    dest: str = "out"
    type: MessageType = MessageType.TEXT
    header: Optional[str] = None
    text: str
    footer: Optional[str] = None
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


class RAGResponse(BaseModel):
    chunk: str
    metadata: Dict[str, Any] = {}


class BotConfig(BaseModel):
    bot_id: str
    bot_name: Optional[str] = None
    bot_fsm_code: Optional[str] = None
    bot_requirements_txt: Optional[str] = None
    bot_version: Optional[str] = None
    bot_config_env: Optional[Dict[str, Any]] = None
    index_urls: Optional[List[str]] = None


class FlowInput(BaseModel):
    source: str
    intent: Optional[LanguageIntent] = None
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    turn_id: Optional[str] = None
    message_text: Optional[str] = None
    rag_response: Optional[List[RAGResponse]] = None
    dialog: Optional[str] = None
    form_response: Optional[dict] = None
    plugin_input: Optional[dict] = None
    bot_config: Optional[BotConfig] = None


class RAGInput(BaseModel):
    source: str
    session_id: str
    turn_id: str
    collection_name: str
    query: str
    top_chunk_k_value: int


class IndexerInput(BaseModel):
    collection_name: str
    files: List[str]
