from enum import Enum
from pydantic import BaseModel
from .message import Message


class LanguageIntent(Enum):
    LANGUAGE_IN = "language_in"
    LANGUAGE_OUT = "language_out"


class Language(BaseModel):
    source: str
    turn_id: str
    intent: LanguageIntent
    message: Message
