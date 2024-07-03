from typing import Dict
from lib.models import JBBot
from lib.data_models import FlowInput, BotConfig
from lib.encryption_handler import EncryptionHandler
from .jb_schema import JBBotActivate, JBBotCode
from .crud import create_bot, get_bot_by_id, get_bot_by_phone_number, update_bot


async def handle_install_bot(install_content: JBBotCode) -> FlowInput:
    bot_data = install_content.model_dump()
    bot = await create_bot(bot_data)
    flow_input = FlowInput(
        source="api",
        bot_config=BotConfig(
            bot_id=bot.id,
            bot_name=install_content.name,
            bot_fsm_code=install_content.code,
            bot_requirements_txt=install_content.requirements,
            index_urls=install_content.index_urls,
            bot_version=install_content.version,
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
    if bot.status == "active":
        return {"status": "error", "message": "Bot already active"}
    existing_bot = await get_bot_by_phone_number(phone_number)
    if existing_bot and existing_bot.id != bot_id:
        return {
            "status": "error",
            "message": f"Phone number {phone_number} already in use by bot {existing_bot.name}",
        }
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
    channels = EncryptionHandler.encrypt_dict(channels)
    bot_data = {}
    bot_data["phone_number"] = phone_number
    bot_data["channels"] = channels
    bot_data["status"] = "active"
    await update_bot(bot_id, bot_data)
    return {"status": "success"}


async def handle_update_bot(bot_id: str, bot_data: Dict):
    print(bot_data)
    if "config_env" in bot_data:
        print("encrypting config env")
        print(EncryptionHandler.encrypt_dict)
        bot_data["config_env"] = EncryptionHandler.encrypt_dict(bot_data["config_env"])
    bot = await get_bot_by_id(bot_id)
    if not bot:
        return {"status": "error", "message": "Bot not found"}
    await update_bot(bot_id, bot_data)
    return {"status": "success", "message": "Bot updated", "bot": bot}
