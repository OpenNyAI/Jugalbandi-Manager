import sys
import os
import json
from cryptography.fernet import Fernet
import bot
from jb_manager_bot import AbstractFSM
from jb_manager_bot.data_models import FSMOutput, FSMInput, FSMIntent


def decrypt_credentials(credentials: dict) -> dict:
    fernet_client = Fernet(os.getenv("ENCRYPTION_KEY"))
    decrypted_credentials = {}
    for key in credentials:
        decrypted_credentials[key] = fernet_client.decrypt(
            credentials[key].encode()
        ).decode()
    return decrypted_credentials


def callback_function(fsm_output: FSMOutput):
    output = json.loads(fsm_output.model_dump_json())
    print(json.dumps({"fsm_output": output}))


runner_input = json.loads(sys.argv[1])
fsm_state_dict = runner_input.get("state")
bot_name = runner_input.get("bot_name")
credentials = runner_input.get("credentials")
config_env = runner_input.get("config_env")

fsm_input = runner_input.get("fsm_input")
fsm_input = FSMInput.model_validate(fsm_input)
jb_bot: AbstractFSM = getattr(bot, bot_name)

if fsm_input.user_input and fsm_input.user_input.lower() == "hi":
    callback_function(FSMOutput(intent=FSMIntent.CONVERSATION_RESET))
else:
    new_state = jb_bot.run_machine(
        send_message=callback_function,
        user_input=fsm_input.user_input,
        callback_input=fsm_input.callback_input,
        state=fsm_state_dict,
        credentials=decrypt_credentials(credentials),
    )
    print(json.dumps({"new_state": new_state}))
