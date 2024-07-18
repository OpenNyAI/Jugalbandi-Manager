from fastapi import APIRouter, HTTPException, Request, UploadFile
from typing import List
from ...crud import get_chat_history, get_bot_list, get_bot_chat_sessions
from ...handlers.v1 import handle_callback, handle_webhook
from ...handlers.v1.bot_handlers import (
    handle_activate_bot,
    handle_deactivate_bot,
    handle_delete_bot,
    handle_update_bot,
    handle_install_bot,
)
from ...jb_schema import JBBotCode, JBBotActivate
from ...extensions import produce_message, storage
from lib.data_models.indexer import Indexer

router = APIRouter(
    prefix="/v1",
    tags=["v1"],
)


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


@router.post("/bot/install")
async def install_bot(install_content: JBBotCode):
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


@router.post("/callback")
async def callback(request: Request):
    data = await request.json()

    async for channel_input in handle_callback(data, headers={}, query_params={}):
        produce_message(channel_input)

    return 200


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
async def index_data(request: Request, collection_name: str, files: List[UploadFile]):
    file_name_list = [file.filename for file in files]
    for file in files:
        content = await file.read()
        await storage.write_file(file_path=file.filename, file_content=content, mime_type=file.content_type)

    indexer_input = Indexer(
        collection_name=collection_name,
        files=file_name_list,
    )
    
    # write to indexer
    produce_message(indexer_input.model_dump_json(), topic="indexer")

    return {"message": "Files indexed successfully", "collection_name": collection_name, "files": file_name_list}