from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class JBBotUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[str] = None
    config_env: Optional[Dict] = {}
    version: Optional[str] = None
    channels: Optional[List[str]] = None

    class Config:
        from_attributes = True


# add credentials endpoint
class JBBotConfig(BaseModel):
    bot_id: str
    credentials: Dict = {}
    config_env: Dict = {}

    class Config:
        from_attributes = True


# add activate bot endpoint
class JBBotActivate(BaseModel):
    bot_id: str
    phone_number: str
    channels: Optional[List[str]] = ["whatsapp"]

    class Config:
        from_attributes = True


class JBBotCode(BaseModel):
    name: str
    status: str = "inactive"
    dsl: str
    code: str
    requirements: str
    index_urls: List[str]
    version: Optional[str] = "v0.1"
    required_credentials: Optional[List[str]] = Field(default_factory=list)

    class Config:
        from_attributes = True
