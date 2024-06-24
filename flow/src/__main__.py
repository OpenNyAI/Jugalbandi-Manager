import asyncio
import json
import traceback
import os
import logging
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv


from . import crud
# from .extensions import save_file
from lib.kafka_utils import KafkaConsumer, KafkaProducer
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

load_dotenv()

logging.basicConfig()
logger = logging.getLogger("flow")
logger.setLevel(logging.INFO)


logger.info("Starting Listening")

kafka_broker = os.getenv("KAFKA_BROKER")
flow_topic = os.getenv("KAFKA_FLOW_TOPIC")
rag_topic = os.getenv("KAFKA_RAG_TOPIC")
language_topic = os.getenv("KAFKA_LANGUAGE_TOPIC")
channel_topic = os.getenv("KAFKA_CHANNEL_TOPIC")

logger.info("Connecting to topic %s", language_topic)

consumer = KafkaConsumer.from_env_vars(
    group_id="cooler_group_id", auto_offset_reset="latest"
)
producer = KafkaProducer.from_env_vars()

logger.info("Connected to topic %s", language_topic)

cache = {}


async def install_or_update_bot(bot_config: BotConfig):
    bot_id = bot_config.bot_id
    bot_name = bot_config.bot_name
    fsm_code = bot_config.bot_fsm_code
    requirements_txt = (
        "openai\ncryptography\njb-manager-bot\n" + bot_config.bot_requirements_txt
    )
    index_urls = bot_config.index_urls if bot_config.index_urls else []

    bots_parent_directory = Path(__file__).parent.parent
    bots_root_directory = Path(os.path.join(bots_parent_directory, "bots"))
    bot_dir = Path(os.path.join(bots_root_directory, bot_id))

    # remove directory if it already exists
    if bot_dir.exists():
        shutil.rmtree(bot_dir)

    bot_dir.mkdir(exist_ok=True, parents=True)

    # copy the contents of Path(__file__).parent/template into the bot's directory
    template_dir = Path(os.path.join(bots_parent_directory, "template"))
    for item in template_dir.iterdir():
        if item.is_dir():
            shutil.copytree(item, bot_dir / item.name)
        else:
            shutil.copy2(item, bot_dir)

    bot_code_file = Path(os.path.join(bot_dir, "bot.py"))
    bot_code_file.write_text(fsm_code)

    # create a requirements.txt file in the bot's directory
    requirements_file = Path(os.path.join(bot_dir, "requirements.txt"))
    requirements_file.write_text(requirements_txt)

    # create a venv inside the bot's directory
    venv_dir = Path(os.path.join(bot_dir, ".venv"))
    subprocess.run(["python3", "-m", "venv", venv_dir])
    install_command = [str(venv_dir / "bin" / "pip"), "install"]
    for index_url in index_urls:
        install_command.extend(["--extra-index-url", index_url])
    install_command.extend(["-r", requirements_file])
    subprocess.run(install_command)
    logger.info("Installed bot %s", bot_id)


async def flow_init():
    # install()
    # fetch all bots from db and install them
    bots = await crud.get_all_bots()
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
            await install_or_update_bot(real_bot_config)
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

            session_id = flow_input.session_id
            message_id = flow_input.message_id
            path = ""
            session_details = await crud.get_session_with_bot(flow_input.session_id)
            callback_input = None
            msg_text = None
            if session_details is None:
                bot_id = flow_input.bot_config.bot_id
            else:
                bot_id = session_details.bot_id
            if flow_input.source == "language":
                msg_text = flow_input.message_text
            elif flow_input.source == "api":
                if flow_input.bot_config is not None:
                    # TODO: install bot here
                    # currently we are assuming the bot is already added to the JB_Bot table in api
                    # in the future the bot data would ideally be passed via kafka message and
                    # we would need to add the bot to the JB_Bot table from here
                    jb_bot = await crud.get_bot_by_id(flow_input.bot_config.bot_id)

                    real_bot_config = BotConfig(
                        bot_id=jb_bot.id,
                        bot_name=jb_bot.name,
                        bot_fsm_code=jb_bot.code,
                        bot_requirements_txt=jb_bot.requirements,
                        index_urls=jb_bot.index_urls,
                    )

                    await install_or_update_bot(real_bot_config)
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

            state = await crud.get_state_by_pid(session_id)
            logger.info("State: %s", state)

            if state is None:
                # logging.info(f"pid {pid} not found in db, inserting")
                state = await crud.insert_state(session_id, "zero")

            def generate_reference_id():
                result = crud.insert_jb_plugin_uuid(
                    flow_input.session_id, flow_input.turn_id
                )
                return result

            def cb(fsm_output: FSMOutput):
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
                logger.info("FSM Output Destination: %s", fsm_output.dest)
                if fsm_output.dest == "out":
                    if fsm_output.options_list is not None:
                        options_list = [
                            {"id": option.id, "title": option.title}
                            for option in fsm_output.options_list
                        ]
                    kafka_out_msg = LanguageInput(
                        source="flow",
                        session_id=session_id,
                        turn_id=flow_input.turn_id,
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
                            options_list=(
                                options_list if fsm_output.options_list else None
                            ),
                        ),
                    )
                    logger.info("FLOW -- %s --> %s", language_topic, kafka_out_msg)

                    logger.info("FLOW -- %s --> %s", language_topic, kafka_out_msg)
                    producer.send_message(
                        language_topic, kafka_out_msg.model_dump_json()
                    )
                elif fsm_output.dest == "rag":
                    rag_input = RAGInput(
                        source="flow",
                        session_id=session_id,
                        turn_id=flow_input.turn_id,
                        collection_name="KB_Law_Files",
                        query=msg_text,
                        top_chunk_k_value=5,
                    )
                    logger.info("FLOW -- %s --> %s", rag_topic, rag_input)
                    producer.send_message(rag_topic, rag_input.model_dump_json())
                elif fsm_output.dest == "channel":
                    channel_input = ChannelInput(
                        source="flow",
                        session_id=session_id,
                        message_id=message_id,
                        turn_id=flow_input.turn_id,
                        intent=ChannelIntent.BOT_OUT,
                        dialog=fsm_output.dialog,
                        data=BotOutput(
                            message_type=fsm_output.type,
                            wa_flow_id=fsm_output.whatsapp_flow_id,
                            wa_screen_id=fsm_output.whatsapp_screen_id,
                            message_data=MessageData(
                                message_text=fsm_output.text,
                                media_url=media_url if media_url else None,
                            ),
                            footer=fsm_output.footer,
                            header=fsm_output.header,
                            menu_selector=fsm_output.menu_selector,
                            menu_title=fsm_output.menu_title,
                            options_list=fsm_output.options_list,
                            form_token=fsm_output.form_token,
                        ),
                    )
                    logger.info("FLOW -- %s --> %s", channel_topic, channel_input)

                    producer.send_message(
                        channel_topic, channel_input.model_dump_json()
                    )

            # get name from bot id
            bot_details = await crud.get_bot_by_id(bot_id)
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
                logger.info("Output from fsm: %s", line)
                fsm_op = json.loads(line)
                if "callback_message" in fsm_op:
                    logger.info("Callback message: %s", fsm_op["callback_message"])
                    # execute callback
                    cb(FSMOutput(**fsm_op["callback_message"]))
                else:
                    # save new state to db
                    new_state_variables = fsm_op["new_state"]
                    saved_state = await crud.update_state_and_variables(
                        session_id, "zerotwo", new_state_variables
                    )
                    logger.info("Saved state: %s", saved_state)
        except Exception as e:
            logger.error("Error in flow loop: %s :: %s", e, traceback.format_exc())
        logger.info("Finished processing message")


if __name__ == "__main__":
    asyncio.run(flow_loop())
