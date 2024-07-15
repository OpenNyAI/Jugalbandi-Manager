from typing import Dict
from .channel_handler import ChannelHandler, ChannelData, User
from .pinnacle_whatsapp_handler import PinnacleWhatsappHandler
from .telegram_handler import TelegramHandler

channel_map: Dict[str, type[ChannelHandler]] = {
    PinnacleWhatsappHandler.get_channel_name(): PinnacleWhatsappHandler,
    TelegramHandler.get_channel_name(): TelegramHandler,
}
