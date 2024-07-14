import asyncio
import json
import traceback
import logging
from dotenv import load_dotenv

from lib.data_models import (
    Flow,
)
from .extensions import consumer, flow_topic
from .crud import (
    get_all_bots,
)
from .handlers.bot_install import install_or_update_bot
from .handlers.flow_input import handle_flow_input

load_dotenv()

logger = logging.getLogger("flow")


async def flow_init():
    # fetch all bots from db and install them
    bots = await get_all_bots()
    for bot in bots:
        try:
            await install_or_update_bot(
                bot_id=bot.id,
                bot_fsm_code=bot.code,
                bot_requirements_txt=bot.requirements,
                index_urls=bot.index_urls,
            )
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
            flow_input = Flow(**msg)

            await handle_flow_input(flow_input=flow_input)

        except Exception as e:
            logger.error("Error in flow loop: %s :: %s", e, traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(flow_loop())
