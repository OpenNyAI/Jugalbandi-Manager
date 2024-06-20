import os
import json
from pathlib import Path

from jb_manager_bot.parsers.utils import LLMManager


class OptionParser:
    """Parse the user input and return the most appropriate option ID based on the user's response."""

    with open(
        os.path.join(Path(__file__).parent, "prompt.txt"), "r", encoding="utf-8"
    ) as f:
        system_prompt = f.read()

    @classmethod
    def parse(
        cls,
        user_task,
        options,
        user_input,
        openai_api_key=None,
        azure_openai_api_key=None,
        azure_openai_api_version=None,
        azure_endpoint=None,
        model="gpt-3.5-turbo"
    ):
        """Parse the user input and return the most appropriate option ID based on the user's response."""

        if azure_openai_api_key is not None:
            model = model.replace(".", "")

        for option in options:
            if "id" not in option and not hasattr(option, "id"):
                raise ValueError("Option ID is required")

        result = LLMManager.llm(
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
            model=model,
            openai_api_key=openai_api_key,
            azure_openai_api_key=azure_openai_api_key,
            azure_openai_api_version=azure_openai_api_version,
            azure_endpoint=azure_endpoint,
        )
        result = json.loads(result)
        return result["id"]
