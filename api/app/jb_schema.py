from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class JBBotUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    status: Optional[str] = None
    config_env: Optional[Dict] = {}
    version: Optional[str] = None
    channels: Optional[List[str]] = None

    model_config = {"from_attributes": True}


# add credentials endpoint
class JBBotConfig(BaseModel):
    bot_id: str
    credentials: Dict = {}
    config_env: Dict = {}

    model_config = {"from_attributes": True}


class JBBotChannels(BaseModel):
    whatsapp: str


# add activate bot endpoint
class JBBotActivate(BaseModel):
    phone_number: str
    channels: JBBotChannels

    model_config = {"from_attributes": True}


class JBBotCode(BaseModel):
    name: str
    status: str = "inactive"
    dsl: str
    code: str
    requirements: str
    index_urls: List[str]
    version: Optional[str] = "v0.1"
    required_credentials: Optional[List[str]] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class JBChannelContent(BaseModel):
    name: str
    type: str
    url: str
    app_id: str
    key: str
    status: str = "inactive"

    model_config = {"from_attributes": True}
