from pydantic import BaseModel
from typing import Union

class APILogger(BaseModel):
    msg_id: str
    user_id: str
    turn_id: str
    session_id: str
    status: str

class ChannelLogger(BaseModel):
    id: str
    turn_id: str
    channel_id: str
    channel_name: str
    msg_intent: str
    msg_type: str
    sent_to_service: str
    status: str

class LanguageLogger(BaseModel):
    id : str
    turn_id : str
    msg_id : str
    msg_state : str
    msg_language : str
    msg_type : str
    translated_to_language : str
    translation_type : str
    translation_model : str
    response_time : str
    status : str

class Logger(BaseModel):
    source: str
    logger_obj: Union[APILogger, ChannelLogger, LanguageLogger]