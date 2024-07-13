import logging
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

logger = logging.getLogger("flow")


def handle_bot_output(
    fsm_output: FSMOutput, session_id: str, turn_id: str, message_id: str, msg_text: str
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
            query=msg_text,
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
