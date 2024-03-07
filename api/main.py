"""
"""

import json
import os
from typing import List
import uuid
from fastapi import FastAPI, HTTPException, Request, APIRouter, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.models import APIKey
from fastapi.middleware.cors import CORSMiddleware
from utils import extract_reference_id
from confluent_kafka import KafkaException
from lib.kafka_utils import KafkaProducer
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from lib.whatsapp import WhatsappHelper
from jb_schema import (
    JBBotUpdate,
    JBBotCode,
    GithubAuth,
    JBAdminUser
)

from lib.data_models import (
    BotInput,
    ChannelData,
    ChannelInput,
    ChannelIntent,
    FlowInput,
    MessageType,
    MessageData,
    BotConfig
)
from lib.jb_logging import Logger
from lib.models import JBBot

import httpx
import jwt
from datetime import datetime, timedelta
import secrets

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
    get_admin_user,
    create_admin_user
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

public_keys = {}
MS_ISSUER = None
MS_JWKS_URI = None
last_updated = datetime.min

MS_CLIENT_ID = os.environ.get("MS_CLIENT_ID")
MS_TENANT_ID = os.environ.get("MS_TENANT_ID")
GOOGLE_TOKEN_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

async def fetch_ms_public_keys():
    global MS_ISSUER, MS_JWKS_URI, public_keys, last_updated
    if datetime.now() - last_updated > timedelta(hours=1):
        url = f"https://login.microsoftonline.com/{MS_TENANT_ID}/.well-known/openid-configuration"
        async with httpx.AsyncClient() as client:
            config = await client.get(url)
            if config.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Error fetching token config: {config.text}")
            data = config.json()
            MS_ISSUER = data["issuer"]
            MS_JWKS_URI = data["jwks_uri"]
            ms_jwks = await client.get(MS_JWKS_URI)
            if ms_jwks.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Error fetching token config: {ms_jwks.text}")
            for jwk in ms_jwks.json()["keys"]:
                public_keys[f'ms_{jwk["kid"]}'] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
            last_updated = datetime.now()


api_key_header_auth = APIKeyHeader(name="Authorization", scheme_name="JWT Auth Bearer Token", auto_error=False)
login_method_header = APIKeyHeader(name="Loginmethod", scheme_name="Login Method", auto_error=False)

async def verify_jwt(token: str = Security(api_key_header_auth), login_method: str = Security(login_method_header)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    if login_method == "ms":
        await fetch_ms_public_keys()
        unverified_header = jwt.get_unverified_header(token.replace('Bearer ', ''))
        kid = unverified_header['kid']
        key = public_keys[f"ms_{kid}"]
        try:
            jwt_payload = jwt.decode(
                token.replace('Bearer ', ''),
                issuer=MS_ISSUER,
                audience=MS_CLIENT_ID,
                key=key,
                algorithms=[unverified_header['alg']],
                options={"verify_signature": True}
                )
            return jwt_payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token Expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid Token")
    elif login_method == "google":
        async with httpx.AsyncClient() as client:
            token_info = await client.get(f"{GOOGLE_TOKEN_INFO_URL}", headers={"Authorization": token})
            if token_info.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Token")
            token_info = token_info.json()
            return token_info
    elif login_method == "github":
        async with httpx.AsyncClient() as client:
            token_info = await client.get(f"https://api.github.com/user", headers={"Authorization": token})
            if token_info.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Token")
            token_info = token_info.json()
            return token_info
    else:
        raise HTTPException(status_code=401, detail="Invalid Login Method")

router = APIRouter(
    dependencies=[Depends(verify_jwt)],
)



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

@app.post("/github-auth")
async def github_auth(data:GithubAuth):
    if not data.code:
        raise HTTPException(status_code=400, detail="No code provided")
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    client_secret = os.environ.get("GITHUB_CLIENT_SECRET")
    redirect_uri = os.environ.get("REDIRECT_URI")
    async with httpx.AsyncClient() as client:
        token = await client.post(TOKEN_URL, data={"client_id": client_id, "client_secret": client_secret, "code": data.code, "redirect_uri": redirect_uri}, headers={"Accept": "application/json"})
        if token.status_code != 200:
            raise HTTPException(status_code=401, detail="Error fetching token")
        return token.json()

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
@router.post("/bot/{bot_id}/activate")
async def activate_bot(bot_id:str, request: Request):
    request_body = await request.json()
    phone_number: str = request_body.get("phone_number")
    channels: List[str] = request_body.get("channels")
    if channels is None:
        channels = ["whatsapp"]
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
        "status": "inactive"
    }
    await update_bot(bot_id, bot_data)
    return bot

@router.delete("/bot/{bot_id}")
async def delete_bot(bot_id: str):
    bot = await get_bot_by_id(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    await update_bot(bot_id, {"status": "deleted"})
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

@router.get('/github-user')
async def get_github_user(request: Request):
    token = request.headers.get("Authorization")
    async with httpx.AsyncClient() as client:
        user_info = await client.get("https://api.github.com/user", headers={"Authorization": token})
        if user_info.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Token")
        user_info = user_info.json()
        return  {
            "id": user_info["node_id"],
            "name": user_info["name"],
            "email": user_info["email"] or user_info["login"]
        }

@router.post("/admin_user")
async def save_user_if_not_found(admin_user: JBAdminUser):
    user = await get_admin_user(id=admin_user.id)
    if user is None:
        admin_user.jb_secret = secrets.token_urlsafe(32)
        user = await create_admin_user(admin_user.model_dump())
    return user


# get all messages related to a session
@router.get("/chats/{bot_id}/sessions/{session_id}")
async def get_session(bot_id: str, session_id: str):
    sessions = await get_bot_chat_sessions(bot_id, session_id)
    return sessions


# get all chats related to a bot
@router.get("/chats/{bot_id}")
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

app.include_router(router)