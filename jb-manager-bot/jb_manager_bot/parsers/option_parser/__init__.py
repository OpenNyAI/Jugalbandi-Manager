import os
import json
from pathlib import Path

from jb_manager_bot.parsers.utils import LLMManager

class OptionParser:
    """Parse the user input and return the most appropriate option ID based on the user's response."""

    with open(os.path.join(Path(__file__).parent, "prompt.txt"), "r", encoding="utf-8") as f:
        system_prompt = f.read()

    @classmethod
    def parse(cls, api_key, user_task, options, user_input):
        """Parse the user input and return the most appropriate option ID based on the user's response."""
        for option in options:
            if "id" not in option and not hasattr(option, "id"):
                raise ValueError("Option ID is required")

        result = LLMManager.llm(
            api_key=api_key,
            messages=[
                LLMManager.sm(cls.system_prompt),
                LLMManager.am(
                    f"""User Task- {user_task}
    Options:
    - {options}"""
                ),
                LLMManager.um(user_input),
            ],
            response_format={"type": "json_object"},
            model="gpt-3.5-turbo",
        )
        result = json.loads(result)
        print(result)
        return result["id"]
