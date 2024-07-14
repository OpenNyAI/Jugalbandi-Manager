import logging
import json
import subprocess
from datetime import datetime
from pathlib import Path
from lib.data_models import (
    FSMOutput,
    Language,
    LanguageIntent,
    Channel,
    ChannelIntent,
    FSMInput,
    FSMIntent,
    Message,
    MessageType,
    Flow,
    FlowIntent,
    DialogMessage,
    DialogOption,
    Dialog,
    RAG,
    UserInput,
    Callback,
    CallbackType,
)
from ..crud import (
    get_bot_by_session_id,
    get_session_by_turn_id,
    get_state_by_session_id,
    insert_state,
    update_state_and_variables,
    create_message,
    create_session,
    update_session,
    update_user_language,
)
from ..extensions import produce_message

logger = logging.getLogger("flow")


def handle_bot_output(fsm_output: FSMOutput, turn_id: str):
    intent = fsm_output.intent
    if intent == FSMIntent.SEND_MESSAGE:
        message = fsm_output.message
        if not message:
            logger.error("Message not found in fsm output")
            return
        message_type = message.message_type
        if message_type == MessageType.FORM:
            destination = "channel"
            flow_output = Channel(
                source="flow",
                turn_id=turn_id,
                intent=ChannelIntent.CHANNEL_OUT,
                bot_output=message,
            )
        else:
            destination = "language"
            flow_output = Language(
                source="flow",
                turn_id=turn_id,
                intent=LanguageIntent.LANGUAGE_OUT,
                message=message,
            )
    elif intent == FSMIntent.CONVERSATION_RESET:
        destination = "flow"
        flow_output = Flow(
            source="flow",
            intent=FlowIntent.DIALOG,
            dialog=Dialog(
                turn_id=turn_id,
                message=Message(
                    message_type=MessageType.DIALOG,
                    dialog=DialogMessage(dialog_id=DialogOption.CONVERSATION_RESET),
                ),
            ),
        )
    elif intent == FSMIntent.LANGUAGE_CHANGE:
        destination = "channel"
        flow_output = Channel(
            source="flow",
            turn_id=turn_id,
            intent=ChannelIntent.CHANNEL_OUT,
            bot_output=Message(
                message_type=MessageType.DIALOG,
                dialog=DialogMessage(dialog_id=DialogOption.LANGUAGE_CHANGE),
            ),
        )
    elif intent == FSMIntent.RAG_CALL:
        destination = "rag"
        rag_query = fsm_output.rag_query
        if not rag_query:
            logger.error("RAG query not found in fsm output")
            return
        flow_output = RAG(
            source="flow",
            turn_id=turn_id,
            collection_name=rag_query.collection_name,
            query=rag_query.query,
            top_chunk_k_value=rag_query.top_chunk_k_value,
        )
    else:
        logger.error("Invalid intent in fsm output")
        return NotImplemented
    logger.info("Output to %s: %s", destination, flow_output)
    return flow_output


async def manage_session(turn_id: str, new_session: bool = False):
    if new_session:
        session = await create_session(turn_id)
    else:
        session = await get_session_by_turn_id(turn_id)
        timeout = 60 * 60 * 24 * 1000  # 24 hours
        if not session:
            session = await create_session(turn_id)
        elif session.updated_at.timestamp() + timeout < datetime.now().timestamp():
            session = await create_session(turn_id)
        else:
            await update_session(session.id)
    return session


async def handle_bot_input(fsm_input: FSMInput, session_id: str):
    state = await get_state_by_session_id(session_id)
    if state is None:
        state = await insert_state(session_id, "zero")
    logger.info("State: %s", state)

    # get name from bot id
    bot_details = await get_bot_by_session_id(session_id)
    if not bot_details:
        logger.error("Bot not found for session_id: %s", session_id)
        return
    bot_id: str = bot_details.id
    bot_name: str = bot_details.name
    config_env = bot_details.config_env
    config_env = {} if config_env is None else config_env
    credentials = bot_details.credentials
    credentials = {} if credentials is None else credentials

    path = Path(__file__).parent.parent.parent / "bots" / bot_id

    ## need to pass state json and msg_text to the bot
    fsm_runner_input = {
        "fsm_input": fsm_input.model_dump(exclude_none=True),
        "state": state.variables,
        "bot_name": bot_name,
        "credentials": credentials,
        "config_env": config_env,
    }
    completed_process = subprocess.run(
        [
            str(path / ".venv" / "bin" / "python"),
            str(path / "fsm_wrapper.py"),
            json.dumps(fsm_runner_input),
        ],
        capture_output=True,
        text=True,
    )

    if completed_process.stderr:
        logger.error("Error while running fsm: %s", completed_process.stderr)
        return

    # logger.error("Output from fsm: %s", completed_process.stdout)
    for line in completed_process.stdout.split("\n"):
        if not line:
            continue
        logger.error("Output from fsm: %s", line)
        fsm_runner_output = json.loads(line)
        if "fsm_output" in fsm_runner_output:
            fsm_output = fsm_runner_output["fsm_output"]
            logger.info("Callback message: %s", fsm_output)
            fsm_output = FSMOutput.model_validate(fsm_output)
            # execute callback
            yield fsm_output
        else:
            # save new state to db
            new_state_variables = fsm_runner_output["new_state"]
            logger.info("FSM Runner message: %s", fsm_runner_output)
            await update_state_and_variables(session_id, "zerotwo", new_state_variables)


async def handle_user_input(user_input: UserInput):
    message = user_input.message
    message_type = message.message_type
    if message_type == MessageType.TEXT:
        if not message.text:
            logger.error("Text not found in user input")
            return
        # TODO: content filter
        fsm_input = FSMInput(user_input=message.text.body)
    elif message_type == MessageType.INTERACTIVE_REPLY:
        if not message.interactive_reply:
            logger.error("Interactive reply not found in user input")
            return
        selected_options = json.dumps(
            [
                option.model_dump(exclude_none=True)
                for option in message.interactive_reply.options
            ]
        )
        fsm_input = FSMInput(user_input=selected_options)
    elif message_type == MessageType.FORM_REPLY:
        if not message.form_reply:
            logger.error("Form reply not found in user input")
            return
        form_response = json.dumps(message.form_reply.form_data)
        fsm_input = FSMInput(user_input=form_response)
    else:
        return NotImplemented

    turn_id = user_input.turn_id
    await create_message(
        turn_id=turn_id,
        message_type=message_type.value,
        is_user_sent=True,
        message=getattr(message, message.message_type.value).model_dump_json(
            exclude_none=True
        ),
    )
    session = await manage_session(turn_id=turn_id)
    session_id: str = session.id
    async for fsm_output in handle_bot_input(fsm_input, session_id=session_id):
        flow_output = handle_bot_output(fsm_output, turn_id=turn_id)
        produce_message(flow_output)


async def handle_callback_input(callback: Callback):
    callback_type = callback.callback_type
    if callback_type == CallbackType.EXTERNAL:
        callback_input = callback.external
        fsm_input = FSMInput(callback_input=callback_input)
    elif callback_type == CallbackType.RAG:
        if not callback.rag_response:
            logger.error("RAG response not found in callback input")
            return
        callback_input = [
            resp.model_dump_json(exclude_none=True) for resp in callback.rag_response
        ]
        callback_input = json.dumps(callback_input)
        fsm_input = FSMInput(callback_input=callback_input)

    turn_id = callback.turn_id
    session = await manage_session(turn_id=turn_id)
    session_id: str = session.id
    async for fsm_output in handle_bot_input(fsm_input, session_id=session_id):
        flow_output = handle_bot_output(fsm_output, turn_id=turn_id)
        produce_message(flow_output)


async def handle_dialog_input(dialog: Dialog):
    turn_id = dialog.turn_id
    if not dialog.message.dialog:
        logger.error("Message not found in dialog input")
        return
    dialog_id = dialog.message.dialog.dialog_id
    if dialog_id == DialogOption.CONVERSATION_RESET:
        fsm_input = FSMInput(user_input="reset")
        new_session = True
    elif dialog_id == DialogOption.LANGUAGE_SELECTED:
        selected_language: str = dialog.message.dialog.dialog_input
        await update_user_language(turn_id=turn_id, selected_language=selected_language)
        fsm_input = FSMInput(user_input="language_selected")
        new_session = False
    else:
        return NotImplemented

    session = await manage_session(turn_id=turn_id, new_session=new_session)
    session_id: str = session.id
    async for fsm_output in handle_bot_input(fsm_input, session_id=session_id):
        flow_output = handle_bot_output(fsm_output, turn_id=turn_id)
        produce_message(flow_output)
