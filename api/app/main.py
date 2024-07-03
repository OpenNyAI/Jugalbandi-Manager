"""
"""

import os
import logging
from typing import Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from confluent_kafka import KafkaException
from lib.kafka_utils import KafkaProducer

from lib.models import JBBot
from lib.encryption_handler import EncryptionHandler
from .jb_schema import JBBotUpdate, JBBotCode, JBBotActivate
from .handlers import handle_callback, handle_webhook
from .bot_handlers import handle_install_bot, handle_activate_bot, handle_update_bot

from .crud import (
    get_bot_by_id,
    get_bot_by_phone_number,
    get_chat_history,
    get_bot_list,
    get_bot_chat_sessions,
    update_bot,
    create_bot,
)

load_dotenv()

app = FastAPI()
logger = logging.getLogger("jb-manager-api")

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


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/bots")
async def get_bots():
    bots = await get_bot_list()
    return bots


@app.patch("/bot/{bot_id}")
async def update_bot_data(bot_id: str, update_fields: JBBotUpdate):
    bot_data = update_fields.model_dump(exclude_unset=True)
    updated_info = await handle_update_bot(bot_id, bot_data)
    if not updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
    updated_bot = updated_info["bot"]
    return updated_bot


@app.post("/bot/install")
async def install_bot(install_content: JBBotCode):
    flow_input = await handle_install_bot(install_content)
    produce_message(flow_input.model_dump_json(), topic=flow_topic)
    return {"status": "success"}


# endpoint to activate bot and link it with a phone number
@app.post("/bot/{bot_id}/activate")
async def activate_bot(bot_id: str, request_body: JBBotActivate):
    activate_bot_response = await handle_activate_bot(
        bot_id=bot_id, request_body=request_body
    )
    if activate_bot_response["status"] == "error":
        raise HTTPException(status_code=400, detail=activate_bot_response["message"])
    return {"status": "success"}


@app.get("/bot/{bot_id}/deactivate")
async def get_bot(bot_id: str):
    bot_data = {"status": "inactive", "phone_number": None, "channels": None}
    updated_info = await handle_update_bot(bot_id, bot_data)
    if updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
    updated_bot = updated_info["bot"]
    return updated_bot


@app.delete("/bot/{bot_id}")
async def delete_bot(bot_id: str):
    bot_data = {"status": "deleted", "phone_number": None, "channels": None}
    updated_info = await handle_update_bot(bot_id, bot_data)
    if updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
    return {"status": "success"}


# endpoint to add (config)credentials for a bot to connect to things
@app.post("/bot/{bot_id}/configure")
async def add_bot_configuraton(bot_id: str, request: Request):
    request_body = await request.json()
    credentials = request_body.get("credentials")
    config_env = request_body.get("config_env")
    if credentials is None and config_env is None:
        raise HTTPException(
            status_code=400, detail="No credentials or config_env provided"
        )
    bot_data = {}
    if credentials is not None:
        bot_data["credentials"] = credentials
    if config_env is not None:
        bot_data["config_env"] = config_env
    updated_info = await handle_update_bot(bot_id, bot_data)
    if not updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
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
    data = await request.json()

    async for channel_input in handle_callback(data):
        produce_message(channel_input.model_dump_json())

    return 200


@app.post("/webhook")
async def plugin_webhook(request: Request):
    webhook_data = await request.body()
    webhook_data = webhook_data.decode("utf-8")
    try:
        async for flow_input in handle_webhook(webhook_data):
            produce_message(flow_input.model_dump_json(), topic=flow_topic)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return 200
