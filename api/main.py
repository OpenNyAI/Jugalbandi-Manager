"""
"""

import json
import os
from typing import Dict
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from utils import extract_reference_id
from confluent_kafka import KafkaException
from lib.kafka_utils import KafkaProducer
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from lib.whatsapp import WhatsappHelper
from jb_schema import JBBotUpdate, JBBotCode

from lib.data_models import (
    BotInput,
    ChannelData,
    ChannelInput,
    ChannelIntent,
    FlowInput,
    MessageType,
    MessageData,
    BotConfig,
)
from lib.jb_logging import Logger
from lib.models import JBBot

from crud import (
    create_turn,
    create_user,
    get_plugin_reference,
    get_user_by_number,
    get_user_session,
    create_session,
    update_session,
    create_message,
    get_bot_by_id,
    get_bot_phone_number,
    get_chat_history,
    get_bot_list,
    get_bot_chat_sessions,
    update_bot,
    create_bot,
)

load_dotenv()

app = FastAPI()
logger = Logger("jb-manager-api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kafka_channel_topic = os.getenv("KAFKA_CHANNEL_TOPIC")
flow_topic = os.getenv("KAFKA_FLOW_TOPIC")

# Connect Kafka Producer automatically using env variables
# and SASL, if applicable
producer = KafkaProducer.from_env_vars()


def produce_message(message: str, topic: str = kafka_channel_topic):
    try:
        logger.info(f"Sending msg to {topic} topic: {message}")
        producer.send_message(topic=topic, value=message)
    except KafkaException as e:
        raise HTTPException(status_code=500, detail=f"Error producing message: {e}")


def encrypt_text(text: str) -> str:
    # TODO - implement encryption
    encryption_key = os.getenv("FERNET_KEY")
    f = Fernet(encryption_key)
    return f.encrypt(text.encode()).decode()


def encrypt_dict(data: dict) -> dict:
    encrypted_data = {}
    for k, v in data.items():
        encrypted_data[k] = encrypt_text(v)
    return encrypted_data


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/bots")
async def get_bots():
    bots = await get_bot_list()
    return bots


@app.patch("/bot/{bot_id}")
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


@app.post("/bot/install")
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
@app.post("/bot/{bot_id}/activate")
async def activate_bot(bot_id:str, request: Request):
    request_body = await request.json()
    phone_number: str = request_body.get("phone_number")
    if not phone_number:
        raise HTTPException(status_code=400, detail="No phone number provided")
    channels: Dict[str, str] = request_body.get("channels")
    if not channels:
        raise HTTPException(status_code=400, detail="No channels provided")
    if "whatsapp" not in channels:
        raise HTTPException(status_code=400, detail="Bot must have a whatsapp channel")
    bot: JBBot = await get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    if bot.status == "active":
        raise HTTPException(status_code=400, detail="Bot already active")
    existing_bot = await get_bot_phone_number(phone_number)
    if existing_bot:
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

@app.get("/bot/{bot_id}/deactivate")
async def get_bot(bot_id: str):
    bot = await get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot_data = {
        "status": "inactive"
    }
    await update_bot(bot_id, bot_data)
    return bot

@app.delete("/bot/{bot_id}")
async def delete_bot(bot_id: str):
    bot = await get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    await update_bot(bot_id, {"status": "deleted"})
    return {"status": "success"}

# endpoint to add (config)credentials for a bot to connect to things
@app.post("/bot/{bot_id}/configure")
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


# get all messages related to a session
@app.get("/chats/{bot_id}/sessions/{session_id}")
async def get_session(bot_id: str, session_id: str):
    sessions = await get_bot_chat_sessions(bot_id, session_id)
    return sessions


# get all chats related to a bot
@app.get("/chats/{bot_id}")
async def get_chats(bot_id: str, skip: int = 0, limit: int = 100):
    chats = await get_chat_history(bot_id, skip, limit)
    return chats


@app.get("/chats")
async def get_chats(bot_id: str) -> list:
    chats = await get_chat_history(bot_id)
    return chats


@app.post("/callback")
async def callback(request: Request):
    # if whatsapp parse with whatsapp library
    # if telegram parse with telegram library:
    data = await request.json()

    # TODO - write code to differentiate channel and identify helper to use

    bot_number = WhatsappHelper.extract_whatsapp_business_number(data)
    bot_id = await get_bot_phone_number(bot_number)
    if bot_id is None:
        logger.error(f"Bot not found for number {bot_number}")
        return 404

    for message in WhatsappHelper.process_messsage(data):
        contact_number = message["from"]
        contact_name = message["name"]  # Set to Dummy at the moment
        user = await get_user_by_number(contact_number, bot_id)
        turn_id = str(uuid.uuid4())

        if user is None:
            # register user
            logger.info("Registering user")
            user = await create_user(bot_id, contact_number, contact_name, contact_name)

        create_new_session = False
        message_type = message["type"]
        if message_type == "text":
            message_text = message[message_type]["body"]
            if message_text.lower() == "hi":
                create_new_session = True

        if create_new_session:
            # create session
            logger.info("Creating session")
            session = await create_session(user.id, bot_id)
        else:
            session = await get_user_session(bot_id, user.id, 24 * 60 * 60 * 1000)
            if session is None:
                # create session
                logger.info("Creating session")
                session = await create_session(user.id, bot_id)
            else:
                await update_session(session.id)

        message_type = message["type"]
        if message_type == "interactive":
            message_type = (
                "form" if message[message_type]["type"] == "nfm_reply" else message_type
            )
            message["type"] = message_type
            message[message_type] = message.pop("interactive")

        turn_id = await create_turn(
            session_id=session.id,
            bot_id=bot_id,
            turn_type=message_type,
            channel="WA",
        )
        msg_id = await create_message(
            turn_id=turn_id,
            message_type=message_type,
            channel="WA",
            channel_id=message["id"],
            is_user_sent=True,
        )

        # remove mobile number
        message.pop("from")

        channel_input = ChannelInput(
            source="api",
            session_id=session.id,
            message_id=msg_id,
            turn_id=turn_id,
            intent=ChannelIntent.BOT_IN,
            channel_data=ChannelData(**message),
            data=BotInput(
                message_type=MessageType.TEXT,
                message_data=MessageData(message_text="dummy"),
            ),
        )

        # write to channel
        produce_message(channel_input.model_dump_json())

    return 200


@app.post("/webhook")
async def plugin_webhook(request: Request):
    webhook_data = await request.body()
    webhook_data = webhook_data.decode("utf-8")
    plugin_uuid = extract_reference_id(webhook_data)
    if not plugin_uuid:
        raise HTTPException(
            status_code=400, detail="Plugin UUID not found in webhook data"
        )
    logger.info(f"Plugin UUID: {plugin_uuid}")
    plugin_reference = await get_plugin_reference(plugin_uuid)
    logger.info(f"Webhook Data: {webhook_data}")
    flow_input = FlowInput(
        source="api",
        session_id=plugin_reference.session_id,
        turn_id=plugin_reference.turn_id,
        plugin_input=json.loads(webhook_data),
    )
    produce_message(flow_input.model_dump_json(), topic=flow_topic)
    return 200
