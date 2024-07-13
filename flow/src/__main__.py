import asyncio
import json
import traceback
import logging
import subprocess
from dotenv import load_dotenv

# from .extensions import save_file
from lib.data_models import (
    BotOutput,
    ChannelInput,
    FSMOutput,
    FlowInput,
    LanguageInput,
    LanguageIntent,
    MessageData,
    RAGInput,
    ChannelIntent,
    BotConfig,
)
from .extensions import consumer, flow_topic, produce_message
from .crud import (
    get_all_bots,
    get_bot_by_session_id,
    get_state_by_pid,
    insert_state,
    update_state_and_variables,
)
from .handlers.bot import handle_bot_installation_or_update, install_or_update_bot
from .handlers.callback import cb

load_dotenv()

logger = logging.getLogger("flow")


async def flow_init():
    # fetch all bots from db and install them
    bots = await get_all_bots()
    for bot in bots:
        try:
            real_bot_config = BotConfig(
                bot_id=bot.id,
                bot_name=bot.name,
                bot_fsm_code=bot.code,
                bot_requirements_txt=bot.requirements,
                bot_config_env=bot.config_env,
                index_urls=bot.index_urls,
            )
            await install_or_update_bot(bot_id=bot.id, bot_config=real_bot_config)
        except Exception as e:
            logger.error(
                "Error while installing bot: %s :: %s", e, traceback.format_exc()
            )


async def flow_loop():
    logger.info("Installing bots")
    try:
        await flow_init()
    except Exception as e:
        logger.error("Error while installing bots: %s :: %s", e, traceback.format_exc())
    logger.info("Finished installing bots, starting flow loop")

    while True:
        try:
            logger.info("Waiting for message")
            msg = consumer.receive_message(flow_topic)
            msg = json.loads(msg)
            logger.info("Message Recieved :: %s", msg)
            flow_input = FlowInput(**msg)
            # logging.info("FlowInput Pydantic:", flow_input)

            session_id: str = flow_input.session_id
            message_id: str = flow_input.message_id
            callback_input = None
            msg_text = None
            if flow_input.source == "language":
                msg_text = flow_input.message_text
            elif flow_input.source == "api":
                if flow_input.bot_config is not None:
                    await handle_bot_installation_or_update(flow_input.bot_config)
                    continue
                if flow_input.plugin_input is not None:
                    callback_input = json.dumps(flow_input.plugin_input)
                    # write code to fetch from db
            elif flow_input.source == "retriever":
                msg_text = json.dumps(
                    {
                        "chunks": [
                            response.model_dump()
                            for response in flow_input.rag_response
                        ]
                    }
                )
            elif flow_input.source == "channel":
                if flow_input.form_response is not None:
                    msg_text = json.dumps(flow_input.form_response)
                elif flow_input.dialog is not None:
                    msg_text = flow_input.dialog
                else:
                    msg_text = flow_input.message_text

            # logging.info(f"Message received from {source}: {msg_text}")

            state = await get_state_by_pid(session_id)
            logger.info("State: %s", state)

            if state is None:
                # logging.info(f"pid {pid} not found in db, inserting")
                state = await insert_state(session_id, "zero")

            # get name from bot id
            bot_details = await get_bot_by_session_id(session_id)
            bot_name = bot_details.name
            config_env = bot_details.config_env
            config_env = {} if config_env is None else config_env
            credentials = bot_details.credentials
            credentials = {} if credentials is None else credentials

            path = Path(__file__).parent.parent / "bots" / bot_id

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
                continue

            # logger.error("Output from fsm: %s", completed_process.stdout)
            for line in completed_process.stdout.split("\n"):
                if not line:
                    continue
                # logger.error("Output from fsm: %s", line)
                fsm_op = json.loads(line)
                if "callback_message" in fsm_op:
                    logger.info("Callback message: %s", fsm_op["callback_message"])
                    # execute callback
                    output = cb(
                        FSMOutput(**fsm_op["callback_message"]),
                        session_id=session_id,
                        turn_id=flow_input.turn_id,
                        message_id=message_id,
                        msg_text=msg_text,
                    )
                    logger.info("Output from callback: %s", output)
                    produce_message(output)
                else:
                    # save new state to db
                    new_state_variables = fsm_op["new_state"]
                    saved_state = await update_state_and_variables(
                        session_id, "zerotwo", new_state_variables
                    )

        except Exception as e:
            logger.error("Error in flow loop: %s :: %s", e, traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(flow_loop())
