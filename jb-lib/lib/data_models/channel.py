from abc import ABC
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, model_validator
from .message import Message


class BotInput(BaseModel, ABC):
    channel_name: str


class RestBotInput(BotInput):
    headers: Dict[str, str]
    data: Dict[str, Any]
    query_params: Dict[str, str]


class ChannelIntent(Enum):
    CHANNEL_IN = "channel_in"
    CHANNEL_OUT = "channel_out"


class Channel(BaseModel):
    source: str
    turn_id: str
    intent: ChannelIntent
    bot_input: Optional[RestBotInput] = None
    bot_output: Optional[Message] = None

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: Dict):
        """Validates data field"""
        intent = values.get("intent")
        bot_input = values.get("bot_input")
        bot_output = values.get("bot_output")

        if intent == ChannelIntent.CHANNEL_IN and bot_input is None:
            raise ValueError("Bot input is required for channel in")
        elif intent == ChannelIntent.CHANNEL_OUT and bot_output is None:
            raise ValueError("Bot output is required for channel out")
        return values
