import logging
from typing import Dict, AsyncGenerator, Tuple, Optional
from lib.channel_handler import ChannelHandler
from lib.data_models import (
    Channel,
    ChannelIntent,
    RestBotInput,
    Flow,
    FlowIntent,
    Callback,
    CallbackType,
)
from ...crud import (
    get_active_channel_by_identifier,
    get_user_by_number,
    create_user,
    create_turn,
    get_plugin_reference,
)
from ...utils import extract_reference_id

logger = logging.getLogger("jb-manager-api")


async def handle_webhook(webhook_data: str) -> AsyncGenerator[Flow, None]:
    plugin_uuid = extract_reference_id(webhook_data)
    if not plugin_uuid:
        # Ignoring callbacks without plugin_uuid
        return
    logger.info("Plugin UUID: %s", plugin_uuid)
    plugin_reference = await get_plugin_reference(plugin_uuid)
    if plugin_reference is None:
        raise ValueError("Plugin reference not found")
    turn_id: str = plugin_reference.turn_id
    logger.info("Webhook Data: %s", webhook_data)
    flow_input = Flow(
        source="api",
        intent=FlowIntent.CALLBACK,
        callback=Callback(
            turn_id=turn_id,
            callback_type=CallbackType.EXTERNAL,
            external=webhook_data,
        ),
    )
    yield flow_input


async def handle_callback(
    callback_data: Dict,
    headers: Dict,
    query_params: Dict,
    chosen_channel: type[ChannelHandler],
) -> AsyncGenerator[Tuple[Optional[ValueError], Optional[Channel]], None]:
    for channel_data in chosen_channel.process_message(callback_data):
        bot_identifier = channel_data.bot_identifier
        user = channel_data.user
        message_data = channel_data.message_data

        jb_channel = await get_active_channel_by_identifier(
            bot_identifier, chosen_channel.get_channel_name()
        )
        if jb_channel is None:
            logger.error("Active channel not found for identifier %s", bot_identifier)
            yield ValueError("Active channel not found"), None

        bot_id: str = jb_channel.bot_id
        channel_id: str = jb_channel.id

        jb_user = await get_user_by_number(user.user_identifier, channel_id=channel_id)
        if jb_user is None:
            # register user
            logger.info("Registering user")
            jb_user = await create_user(
                channel_id, user.user_identifier, user.user_name, user.user_name
            )

        user_id: str = jb_user.id
        turn_id = await create_turn(
            bot_id=bot_id, channel_id=channel_id, user_id=user_id
        )
        channel_input = Channel(
            source="api",
            turn_id=turn_id,
            intent=ChannelIntent.CHANNEL_IN,
            bot_input=RestBotInput(
                channel_name=chosen_channel.get_channel_name(),
                headers=headers,
                data=message_data,
                query_params=query_params,
            ),
        )
        yield None, channel_input
