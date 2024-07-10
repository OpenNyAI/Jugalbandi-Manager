from abc import ABC, abstractmethod
from typing import Dict, Generator, Optional
from pydantic import BaseModel
from lib.models import JBChannel, JBUser
from lib.data_models import Message, BotInput


class User(BaseModel):
    user_identifier: str
    user_name: str
    user_email: Optional[str] = None
    user_phone: Optional[str] = None


class ChannelData(BaseModel):
    bot_identifier: str
    user: User
    message_data: Dict


class ChannelHandler(ABC):

    @classmethod
    @abstractmethod
    def is_valid_data(cls, data: Dict) -> bool:
        pass

    @classmethod
    @abstractmethod
    def get_channel_name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def to_message(cls, turn_id: str, channel: JBChannel, bot_input: BotInput) -> Message:
        pass

    @classmethod
    @abstractmethod
    def parse_bot_output(cls, message: Message, user: JBUser, channel: JBChannel) -> Dict:
        pass

    @classmethod
    @abstractmethod
    def process_message(cls, data: Dict) -> Generator[ChannelData, None, None]:
        pass

    @classmethod
    @abstractmethod
    def send_message(cls, channel: JBChannel, user: JBUser, message: Message):
        pass


class RestChannelHandler(ChannelHandler):

    @classmethod
    @abstractmethod
    def generate_header(cls, channel: JBChannel) -> Dict:
        pass

    @classmethod
    @abstractmethod
    def generate_url(cls, channel: JBChannel, user: JBUser, message: Message) -> str:
        pass