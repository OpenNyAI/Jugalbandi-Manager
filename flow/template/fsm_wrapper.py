import sys
import os
import json
from cryptography.fernet import Fernet
import bot
from jb_manager_bot import FSMOutput, AbstractFSM


def decrypt_credentials(credentials: dict) -> dict:
    decrypted_credentials = {}
    for key in credentials:
        decrypted_credentials[key] = (
            Fernet(os.getenv("ENCRYPTION_KEY"))
            .decrypt(credentials[key].encode())
            .decode()
        )
    return decrypted_credentials


def callback_function(fsm_output: FSMOutput):
    output = json.loads(fsm_output.model_dump_json())
    print(json.dumps({"fsm_output": output}))


runner_input = json.loads(sys.argv[1])
message_text = runner_input.get("message_text")
callback_input = runner_input.get("callback_input")
fsm_state_dict = runner_input.get("state")
bot_name = runner_input.get("bot_name")
credentials = runner_input.get("credentials")
config_env = runner_input.get("config_env")

jb_bot: AbstractFSM = getattr(bot, bot_name)

new_state = jb_bot.run_machine(
    send_message=callback_function,
    user_input=message_text,
    callback_input=callback_input,
    state=fsm_state_dict,
    credentials=decrypt_credentials(credentials),
)

print(json.dumps({"new_state": new_state}))
