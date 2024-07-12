import logging
from fastapi import APIRouter, HTTPException, Request
from ...handlers.v2.channel import (
    delete,
    deactivate,
    activate,
    update,
    list_available_channels,
)

logger = logging.getLogger("jb-manager-api")
router = APIRouter(
    prefix="/channel",
)


@router.get("/")
async def get_all_channels():
    channels = await list_available_channels()
    return channels


@router.post("/{channel_id}")
async def update_channel(channel_id: str, request: Request):
    request_body = await request.json()
    updated_info = await update(channel_id, request_body)
    if updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
    return updated_info


@router.get("/{channel_id}/activate")
async def activate_channel(channel_id: str):
    updated_info = await activate(channel_id)
    if updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
    return {"status": "success"}


@router.get("/{channel_id}/deactivate")
async def deactivate_channel(channel_id: str):
    updated_info = await deactivate(channel_id)
    if updated_info["status"] == "error":
        raise HTTPException(status_code=404, detail=updated_info["message"])
    return {"status": "success"}


@router.delete("/{channel_id}")
async def add_channel(channel_id: str):
    delete_response = await delete(channel_id)
    if delete_response["status"] == "error":
        raise HTTPException(status_code=404, detail=delete_response["message"])
    return {"status": "success"}
