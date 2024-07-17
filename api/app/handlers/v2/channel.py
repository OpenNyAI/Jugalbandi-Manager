from typing import Dict
from lib.encryption_handler import EncryptionHandler
from ...crud import get_channel_by_id, update_channel
from ...extensions import channel_map


async def list_available_channels():
    return list(channel_map.keys())


async def update(channel_id: str, channel_data: Dict[str, str]):
    channel = await get_channel_by_id(channel_id)
    if not channel:
        return {"status": "error", "message": "Channel not found"}
    channel_data = {
        k: v
        for k, v in channel_data.items()
        if v is not None and k in ["key", "app_id", "name", "type", "url"]
    }
    if "type" in channel_data and channel_data["type"] not in channel_map:
        return {"status": "error", "message": "Channel not supported by this manager"}
    if "key" in channel_data:
        channel_data["key"] = EncryptionHandler.encrypt_text(channel_data["key"])
    await update_channel(channel_id, channel_data)
    return {"status": "success"}


async def activate(channel_id: str):
    channel = await get_channel_by_id(channel_id)
    if not channel:
        return {"status": "error", "message": "Channel not found"}
    channel_data = {"status": "active"}
    await update_channel(channel_id, channel_data)
    return {"status": "success"}


async def deactivate(channel_id: str):
    channel = await get_channel_by_id(channel_id)
    if not channel:
        return {"status": "error", "message": "Channel not found"}
    channel_data = {"status": "inactive"}
    await update_channel(channel_id, channel_data)
    return {"status": "success"}


async def delete(channel_id: str):
    channel = await get_channel_by_id(channel_id)
    if not channel:
        return {"status": "error", "message": "Channel not found"}
    channel_data = {"status": "deleted"}
    await update_channel(channel_id, channel_data)
    return {"status": "success"}
