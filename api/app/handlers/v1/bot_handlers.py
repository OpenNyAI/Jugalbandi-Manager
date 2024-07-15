import os
import uuid
from typing import Dict
from lib.models import JBBot
from lib.data_models import Flow, BotConfig, FlowIntent, BotIntent, Bot
from lib.encryption_handler import EncryptionHandler
from ...jb_schema import JBBotActivate, JBBotCode
from ...crud import (
    create_channel,
    get_bot_by_id,
    update_channel,
    update_bot,
    get_channels_by_identifier,
    get_channel_by_id,
)


async def handle_install_bot(install_content: JBBotCode) -> Flow:
    bot_id = str(uuid.uuid4())
    flow_input = Flow(
        source="api",
        intent=FlowIntent.BOT,
        bot_config=BotConfig(
            bot_id=bot_id,
            intent=BotIntent.INSTALL,
            bot=Bot(
                name=install_content.name,
                fsm_code=install_content.code,
                requirements_txt=install_content.requirements,
                index_urls=install_content.index_urls,
                required_credentials=install_content.required_credentials,
                version=install_content.version,
            ),
        ),
    )
    return flow_input


async def handle_activate_bot(bot_id: str, request_body: JBBotActivate):
    phone_number: str = request_body.phone_number
    if not phone_number:
        return {"status": "error", "message": "No phone number provided"}
    channels: Dict[str, str] = request_body.channels.model_dump()
    if not channels:
        return {"status": "error", "message": "No channels provided"}
    if not "whatsapp" in channels:
        return {"status": "error", "message": "Bot must have a whatsapp channel"}
    bot: JBBot = await get_bot_by_id(bot_id)
    if not bot:
        return {"status": "error", "message": "Bot not found"}
    existing_channels = await get_channels_by_identifier(
        identifier=phone_number, channel_type="whatsapp"
    )
    print(existing_channels)
    if existing_channels:
        for channel in existing_channels:
            if channel.status == "active" and channel.bot_id != bot_id:
                return {
                    "status": "error",
                    "message": f"Phone number {phone_number} already in use by bot {channel.bot.name}",
                }
            elif channel.status == "active" and channel.bot_id == bot_id:
                return {"status": "error", "message": "Bot already active"}
            elif channel.status == "inactive" and channel.bot_id == bot_id:
                channel_key = EncryptionHandler.encrypt_text(channels["whatsapp"])
                channel_data = {"status": "active", "key": channel_key}
                await update_channel(channel.id, channel_data)
                return {"status": "success"}
    required_credentials = bot.required_credentials
    current_credentials = bot.credentials if bot.credentials else {}
    missing_credentials = [
        name for name in required_credentials if name not in current_credentials
    ]
    if missing_credentials:
        return {
            "status": "error",
            "message": f"Bot missing required credentials: {', '.join(missing_credentials)}",
        }
    channel_key = EncryptionHandler.encrypt_text(channels["whatsapp"])
    channel_data = {
        "name": "whatsapp",
        "type": "whatsapp",
        "key": channel_key,
        "app_id": phone_number,
        "url": os.getenv("WA_API_HOST"),
        "status": "active",
    }
    await create_channel(bot_id, channel_data)
    return {"status": "success"}


async def handle_update_bot(bot_id: str, bot_data: Dict):
    if "credentials" in bot_data:
        bot_data["credentials"] = EncryptionHandler.encrypt_dict(
            bot_data["credentials"]
        )
    bot = await get_bot_by_id(bot_id)
    if not bot:
        return {"status": "error", "message": "Bot not found"}
    await update_bot(bot_id, bot_data)
    return {"status": "success", "message": "Bot updated", "bot": bot}


async def handle_update_channel(channel_id: str, channel_data: Dict):
    if "key" in channel_data:
        channel_data["key"] = EncryptionHandler.encrypt_text(channel_data["key"])
    channel = await get_channel_by_id(channel_id)
    if not channel:
        return {"status": "error", "message": "Channel not found"}
    await update_channel(channel_id, channel_data)
    return {"status": "success", "message": "Channel updated", "channel": channel}


async def handle_delete_bot(bot_id: str):
    bot_data = {"status": "deleted"}
    updated_info = await handle_update_bot(bot_id, bot_data)
    if updated_info["status"] == "error":
        return updated_info
    updated_bot = updated_info["bot"]
    for channel in updated_bot.channels:
        channel_data = {"status": "deleted"}
        await update_channel(channel.id, channel_data)
    return {"status": "success", "message": "Bot deleted"}


async def handle_deactivate_bot(bot_id: str):
    bot = await get_bot_by_id(bot_id)
    if not bot:
        return {"status": "error", "message": "Bot not found"}
    for channel in bot.channels:
        channel_data = {"status": "inactive"}
        await update_channel(channel.id, channel_data)
    return {"status": "success", "message": "Bot deactivated"}
