from typing import Dict
from fastapi import APIRouter, HTTPException, Request
from lib.data_models import FlowInput, BotConfig
from lib.models import JBBot
from lib.jb_logging import Logger
from ..crud import get_bot_by_id, update_bot, create_bot, get_bot_list, get_bot_by_phone_number
from ..jb_schema import JBBotActivate, JBBotCode, JBBotUpdate
from ..extensions import produce_message, flow_topic
from ..utils import encrypt_dict

logger = Logger("jb-manager-api")
router = APIRouter(
    prefix="",
)

@router.get("/bots")
async def get_bots():
    bots = await get_bot_list()
    return bots


@router.patch("/bot/{bot_id}")
async def update_bot_data(bot_id: str, update_fields: JBBotUpdate):
    bot = await get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    data = update_fields.dict(exclude_unset=True)

    # encrypt config_env
    if "config_env" in data:
        data["config_env"] = encrypt_dict(data["config_env"])

    await update_bot(bot_id, data)
    return bot


@router.post("/bot/install")
async def install_bot(install_content: JBBotCode):
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
    produce_message(flow_input.model_dump_json(), topic=flow_topic)
    return {"status": "success"}


# endpoint to activate bot and link it with a phone number
@router.post("/bot/{bot_id}/activate")
async def activate_bot(bot_id:str, request_body: JBBotActivate):
    phone_number: str = request_body.phone_number
    if not phone_number:
        raise HTTPException(status_code=400, detail="No phone number provided")
    channels: Dict[str, str] = request_body.channels.model_dump()
    if not channels:
        raise HTTPException(status_code=400, detail="No channels provided")
    if not 'whatsapp' in channels:
        raise HTTPException(status_code=400, detail="Bot must have a whatsapp channel")
    bot: JBBot = await get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bot.status == "active":
        raise HTTPException(status_code=400, detail="Bot already active")
    existing_bot = await get_bot_by_phone_number(phone_number)
    if existing_bot and existing_bot.id != bot_id:
        raise HTTPException(
            status_code=400,
            detail=f"Phone number {phone_number} already in use by bot {existing_bot.name}",
        )
    required_credentials = bot.required_credentials
    current_credentials = bot.credentials if bot.credentials else {}
    missing_credentials = [name for name in required_credentials if name not in current_credentials]
    if missing_credentials:
        raise HTTPException(
            status_code=400,
            detail=f"Bot missing required credentials: {', '.join(missing_credentials)}",
        )
    channels = encrypt_dict(channels)
    bot_data = {}
    bot_data["phone_number"] = phone_number
    bot_data["channels"] = channels
    bot_data["status"] = "active"
    await update_bot(bot_id, bot_data)
    return {"status": "success"}

@router.get("/bot/{bot_id}/deactivate")
async def get_bot(bot_id: str):
    bot = await get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot_data = {
        "status": "inactive",
        "phone_number": None,
        "channels": None
    }
    await update_bot(bot_id, bot_data)
    return bot

@router.delete("/bot/{bot_id}")
async def delete_bot(bot_id: str):
    bot = await get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot_data = {
        "status": "deleted",
        "phone_number": None,
        "channels": None
    }
    await update_bot(bot_id, bot_data)
    return {"status": "success"}

# endpoint to add (config)credentials for a bot to connect to things
@router.post("/bot/{bot_id}/configure")
async def add_bot_configuraton(bot_id:str, request: Request):
    request_body = await request.json()
    bot: JBBot = await get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    credentials = request_body.get("credentials")
    config_env = request_body.get("config_env")
    if credentials is None and config_env is None:
        raise HTTPException(
            status_code=400, detail="No credentials or config_env provided"
        )
    bot_data = {}
    if credentials is not None:
        encrypted_credentials = encrypt_dict(credentials)
        bot_data["credentials"] = encrypted_credentials
    if config_env is not None:
        bot_data["config_env"] = config_env
    await update_bot(bot_id, bot_data)
    return {"status": "success"}
