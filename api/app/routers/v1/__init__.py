import logging
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, Request
from fastapi.datastructures import UploadFile
from lib.data_models.indexer import Indexer, IndexType
from lib.file_storage import StorageHandler

from ...crud import get_bot_chat_sessions, get_bot_list, get_chat_history
from ...extensions import produce_message
from ...handlers.v1 import handle_webhook
from ...handlers.v1.bot_handlers import (
    handle_activate_bot,
    handle_deactivate_bot,
    handle_delete_bot,
    handle_install_bot,
    handle_update_bot,
)
from ...jb_schema import JBBotActivate, JBBotCode

logger = logging.getLogger("jb-manager-api")
router = APIRouter(
    prefix="/v1",
    tags=["v1"],
)
JBMANAGER_KEY = str(uuid.uuid4())
KEYS = {"JBMANAGER_KEY": str(uuid.uuid4())}


@router.get("/bots")
async def get_bots():
    bots = await get_bot_list()
    for bot in bots:
        status = "inactive"
        channels = bot.channels
        for channel in channels:
            if channel.status == "active":
                status = "active"
                break
        bot.status = status
    return bots


@router.get("/secret")
async def get_secret_key():
    return {"secret": KEYS["JBMANAGER_KEY"]}


@router.put("/refresh-key")
async def refresh_secret_key():
    KEYS["JBMANAGER_KEY"] = str(uuid.uuid4())
    return {"status": "success"}


@router.post("/bot/install")
async def install_bot(request: Request, install_content: JBBotCode):
    headers = dict(request.headers)
    authorization = headers.get("authorization")
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header not provided")
    if authorization != f"Bearer {KEYS['JBMANAGER_KEY']}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    flow_input = await handle_install_bot(install_content)
    try:
        produce_message(flow_input)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error producing message: {e}"
        ) from e
    return {"status": "success"}


# endpoint to activate bot and link it with a phone number
@router.post("/bot/{bot_id}/activate")
async def activate_bot(bot_id: str, request_body: JBBotActivate):
    activate_bot_response = await handle_activate_bot(
        bot_id=bot_id, request_body=request_body
    )
    if activate_bot_response["status"] == "error":
        raise HTTPException(status_code=400, detail=activate_bot_response["message"])
    return {"status": "success"}


@router.get("/bot/{bot_id}/deactivate")
async def get_bot(bot_id: str):
    updated_info = await handle_deactivate_bot(bot_id)
    if updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
    return {"status": "success"}


@router.delete("/bot/{bot_id}")
async def delete_bot(bot_id: str):
    updated_info = await handle_delete_bot(bot_id)
    if updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
    return {"status": "success"}


# endpoint to add (config)credentials for a bot to connect to things
@router.post("/bot/{bot_id}/configure")
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
    if updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
    return {"status": "success"}


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


@router.get("/chats")
async def get_chats(bot_id: str) -> list:
    chats = await get_chat_history(bot_id)
    return chats


@router.post("/webhook")
async def plugin_webhook(request: Request):
    webhook_data = await request.body()
    webhook_data = webhook_data.decode("utf-8")
    try:
        async for flow_input in handle_webhook(webhook_data):
            produce_message(flow_input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return 200


@router.post("/index-data")
async def index_data(
    indexer_type: IndexType,
    collection_name: str,
    files: List[UploadFile],
):
    storage = StorageHandler.get_async_instance()
    files_list = []
    for file in files:
        await storage.write_file(
            file_path=file.filename,
            file_content=file.file.read(),
            mime_type=file.content_type,
        )
        files_list.append(file.filename)
    indexer_input = Indexer(
        type=indexer_type.value,
        collection_name=collection_name,
        files=files_list,
    )
    # write to indexer
    produce_message(indexer_input)

    return {"message": f"Indexing started for the files in {collection_name}"}
