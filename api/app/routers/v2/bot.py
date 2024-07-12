import logging
from fastapi import APIRouter, HTTPException, Request
from ...extensions import flow_topic, produce_message, channel_map
from ...handlers.v2.bot import install, delete, add_credentials, list_bots, add_channel
from ...jb_schema import JBBotCode, JBChannelContent

logger = logging.getLogger("jb-manager-api")
router = APIRouter(
    prefix="/bot",
)


@router.get("/")
async def get_all_bots():
    bots = await list_bots()
    return bots


@router.post("/install")
async def install_bot(install_content: JBBotCode):
    flow_input = await install(install_content)
    try:
        produce_message(flow_input.model_dump_json(), topic=flow_topic)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error producing message: {e}"
        ) from e
    return {"status": "success"}


@router.delete("/{bot_id}")
async def delete_bot(bot_id: str):
    delete_response = await delete(bot_id)
    if delete_response["status"] == "error":
        raise HTTPException(status_code=404, detail=delete_response["message"])
    return {"status": "success"}


@router.post("/{bot_id}/credentials")
async def add_bot_credentials(bot_id: str, request: Request):
    request_body = await request.json()
    credentials = request_body.get("credentials")
    if credentials is None:
        raise HTTPException(status_code=400, detail="No credentials provided")
    add_credentials_response = await add_credentials(bot_id, credentials)
    if add_credentials_response["status"] == "error":
        raise HTTPException(status_code=404, detail=add_credentials_response["message"])
    return {"status": "success"}


@router.post("/{bot_id}/channel")
async def add_bot_channel(bot_id: str, channel_content: JBChannelContent):
    if channel_content.type not in channel_map:
        raise HTTPException(
            status_code=400, detail="Channel not supported by this manager"
        )
    add_channel_response = await add_channel(bot_id, channel_content)
    if add_channel_response["status"] == "error":
        raise HTTPException(status_code=404, detail=add_channel_response["message"])
    return {"status": "success"}
