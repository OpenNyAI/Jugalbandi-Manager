from abc import abstractmethod
from typing import Dict
from lib.models import JBChannel, JBUser
from lib.data_models import Message
from .channel_handler import ChannelHandler


class RestChannelHandler(ChannelHandler):

    @classmethod
    @abstractmethod
    def generate_header(cls, channel: JBChannel) -> Dict:
        pass

    @classmethod
    @abstractmethod
    def generate_url(cls, channel: JBChannel, user: JBUser, message: Message) -> str:
        pass
