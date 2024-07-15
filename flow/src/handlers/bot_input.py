import logging
import json
import subprocess
from pathlib import Path
from lib.data_models import (
    FSMOutput,
    LanguageInput,
    RAGInput,
    ChannelInput,
    BotOutput,
    MessageData,
    LanguageIntent,
    ChannelIntent,
)
from ..crud import (
    get_bot_by_session_id,
    get_state_by_pid,
    insert_state,
    update_state_and_variables,
)
from ..extensions import produce_message

logger = logging.getLogger("flow")


def handle_bot_output(
    fsm_output: FSMOutput, session_id: str, turn_id: str, message_id: str
):
    media_url = None
    if fsm_output.media_url is not None:
        media_url = fsm_output.media_url

    # if fsm_output.file is not None:
    #     upload_file = fsm_output.file

    #     with open(upload_file.path, "rb") as f:
    #         file_content = f.read()
    #     media_url = save_file(
    #         upload_file.filename, file_content, upload_file.mime_type
    #     )
    logger.info("FSM Output: %s", fsm_output)

    if fsm_output.dest == "out":
        if fsm_output.options_list is not None:
            options_list = [
                {"id": option.id, "title": option.title}
                for option in fsm_output.options_list
            ]
        kafka_out_msg = LanguageInput(
            source="flow",
            session_id=session_id,
            turn_id=turn_id,
            intent=LanguageIntent.LANGUAGE_OUT,
            data=BotOutput(
                message_type=fsm_output.type,
                message_data=MessageData(
                    message_text=fsm_output.text,
                    media_url=media_url if media_url else None,
                ),
                header=fsm_output.header,
                footer=fsm_output.footer,
                menu_selector=fsm_output.menu_selector,
                menu_title=fsm_output.menu_title,
                options_list=(options_list if fsm_output.options_list else None),
            ),
        )
        return kafka_out_msg
    elif fsm_output.dest == "rag":
        rag_input = RAGInput(
            source="flow",
            session_id=session_id,
            turn_id=turn_id,
            collection_name="KB_Law_Files",
            query=fsm_output.text,
            top_chunk_k_value=5,
        )
        return rag_input
    elif fsm_output.dest == "channel":
        channel_input = ChannelInput(
            source="flow",
            session_id=session_id,
            message_id=message_id,
            turn_id=turn_id,
            intent=ChannelIntent.BOT_OUT,
            dialog=fsm_output.dialog,
            data=BotOutput(
                message_type=fsm_output.type,
                message_data=MessageData(
                    message_text=fsm_output.text,
                    media_url=media_url if media_url else None,
                ),
                footer=fsm_output.footer,
                header=fsm_output.header,
                menu_selector=fsm_output.menu_selector,
                menu_title=fsm_output.menu_title,
                options_list=fsm_output.options_list,
                form_id=fsm_output.form_id,
            ),
        )
        return channel_input
    return NotImplemented


async def handle_bot_input(
    session_id: str, turn_id: str, message_id: str, msg_text: str, callback_input: str
):
    state = await get_state_by_pid(session_id)
    logger.info("State: %s", state)

    if state is None:
        # logging.info(f"pid {pid} not found in db, inserting")
        state = await insert_state(session_id, "zero")

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
        "message_text": msg_text,
        "callback_input": callback_input,
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
        print(line)
        if not line:
            continue
        # logger.error("Output from fsm: %s", line)
        fsm_op = json.loads(line)
        if "callback_message" in fsm_op:
            logger.info("Callback message: %s", fsm_op["callback_message"])
            # execute callback
            output = handle_bot_output(
                FSMOutput(**fsm_op["callback_message"]),
                session_id=session_id,
                turn_id=turn_id,
                message_id=message_id,
            )
            logger.info("Output from callback: %s", output)
            produce_message(output)
        else:
            # save new state to db
            new_state_variables = fsm_op["new_state"]
            await update_state_and_variables(session_id, "zerotwo", new_state_variables)
