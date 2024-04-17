from abc import ABC, abstractmethod

from lib.data_models import BotOutput, ChannelData
from lib.models import JBChannel, JBUser


class ChannelHandler(ABC):

    @classmethod
    @abstractmethod
    def is_valid_channel(cls, data: dict):
        pass

    @classmethod
    @abstractmethod
    def to_bot_input(cls, channel: JBChannel, msg_id: str, bot_input: ChannelData):
        pass

    @classmethod
    @abstractmethod
    def parse_bot_output(cls, bot_output: BotOutput, user: JBUser):
        pass

    @classmethod
    @abstractmethod
    def extract_app_id(cls, data: dict):
        pass

    @classmethod
    @abstractmethod
    def get_channel_name(cls):
        pass


class RestChannelHandler(ChannelHandler):

    @classmethod
    @abstractmethod
    def generate_header(cls, channel: JBChannel):
        pass

    @classmethod
    @abstractmethod
    def generate_url(cls, channel: JBChannel, user: JBUser, bot_ouput: BotOutput):
        pass

    @classmethod
    @abstractmethod
    def send_message(cls, channel: JBChannel, user: JBUser, bot_ouput: BotOutput, **kwargs):
        pass
