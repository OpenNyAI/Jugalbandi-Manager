import json
from fastapi import APIRouter, Request, HTTPException
from lib.data_models import FlowInput
from lib.jb_logging import Logger
from ..crud import get_plugin_reference
from ..utils import extract_reference_id
from ..extensions import produce_message, flow_topic

logger = Logger("jb-manager-api")
router = APIRouter(
    prefix="",
)

@router.post("/webhook")
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