from pydantic import BaseModel

class APILogger(BaseModel):
    msg_id: str
    user_id: str
    turn_id: str
    session_id: str
    status: str

class Logger(BaseModel):
    source: str
    api_logger: APILogger