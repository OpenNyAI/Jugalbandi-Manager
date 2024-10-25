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

class Logger(BaseModel):
    source: str
    logger_obj: Union[APILogger, ChannelLogger]