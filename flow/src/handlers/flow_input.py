import logging
from lib.data_models import Flow, FlowIntent
from .bot_install import handle_bot
from .bot_input import handle_user_input, handle_callback_input, handle_dialog_input

logger = logging.getLogger("flow")


async def handle_flow_input(flow_input: Flow):
    flow_intent = flow_input.intent
    if flow_intent == FlowIntent.BOT:
        if not flow_input.bot_config:
            logger.error("Bot config not found in flow input")
            return
        await handle_bot(flow_input.bot_config)
    elif flow_intent == FlowIntent.DIALOG:
        if not flow_input.dialog:
            logger.error("Dialog not found in flow input")
            return
        await handle_dialog_input(flow_input.dialog)
    elif flow_intent == FlowIntent.CALLBACK:
        if not flow_input.callback:
            logger.error("Callback not found in flow input")
            return
        await handle_callback_input(flow_input.callback)
    elif flow_intent == FlowIntent.USER_INPUT:
        if not flow_input.user_input:
            logger.error("User input not found in flow input")
            return
        await handle_user_input(flow_input.user_input)
    else:
        logger.error("Invalid flow intent: %s", flow_intent)
