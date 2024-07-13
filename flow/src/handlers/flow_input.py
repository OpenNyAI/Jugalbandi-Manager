import json
from lib.data_models import FlowInput
from .bot_install import handle_bot_installation_or_update
from .bot_input import handle_bot_input


async def handle_flow_input(flow_input: FlowInput):
    if flow_input.source == "api" and flow_input.bot_config is not None:
        await handle_bot_installation_or_update(flow_input.bot_config)
    elif flow_input.source in ["language", "api", "retriever", "channel"]:
        session_id: str = flow_input.session_id
        message_id: str = flow_input.message_id
        turn_id: str = flow_input.turn_id
        callback_input = None
        msg_text = None
        if flow_input.source == "language":
            msg_text = flow_input.message_text
        elif flow_input.source == "api":
            callback_input = json.dumps(flow_input.plugin_input)
        elif flow_input.source == "retriever":
            rag_response = flow_input.rag_response
            msg_text = json.dumps(
                {"chunks": [response.model_dump() for response in rag_response]}
            )
        elif flow_input.source == "channel":
            if flow_input.form_response is not None:
                msg_text = json.dumps(flow_input.form_response)
            elif flow_input.dialog is not None:
                msg_text = flow_input.dialog
            else:
                msg_text = flow_input.message_text

        await handle_bot_input(
            session_id=session_id,
            turn_id=turn_id,
            message_id=message_id,
            msg_text=msg_text,
            callback_input=callback_input,
        )
    else:
        raise ValueError("Invalid source in flow input")
