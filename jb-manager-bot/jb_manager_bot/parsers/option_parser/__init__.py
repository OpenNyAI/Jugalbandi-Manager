import os
import json
from pathlib import Path

from jb_manager_bot.parsers.utils import LLMManager

SYSTEM_PROMPT = """
Given a user's response and a list of options, determine the most appropriate option that the user's response corresponds to. The options are provided in a structured format, each with a unique ID and a title that represents the action or response. The user's response is a statement expressing their preference among the provided options.
Options:
- List each option with its ID and title.

User Response:
- Include the user's response here.

Task:
Analyze the user's response and select the option ID that best matches the intent of their response. Consider the sentiment, keywords, and overall meaning of the user's statement. If the user's response clearly aligns with one of the options, provide the corresponding option ID. If the user's response is ambiguous or does not clearly align with any of the options, indicate that the response is inconclusive.

Output: {id:"{selected_id}"}
You need to return the `id` corresponding to the selected option from the list in json format and nothing else.

Determine the most appropriate option ID based on the user's response.
"""


class OptionParser:
    """Parse the user input and return the most appropriate option ID based on the user's response."""

    system_prompt = SYSTEM_PROMPT

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


class Parser:

    @classmethod
    def parse_user_input(
        cls,
        user_task,
        options,
        user_input,
        openai_api_key=None,
        azure_openai_api_key=None,
        azure_openai_api_version=None,
        azure_endpoint=None,
    ):
        model = "gpt-3.5-turbo"
        if azure_openai_api_key is not None:
            model = model.replace(".", "")

        if options is None:
            result = LLMManager.llm(
                messages=[
                    LLMManager.sm(user_task),
                    LLMManager.um(f"User Input: {user_input}"),
                ],
                response_format={"type": "json_object"},
                model=model,
                openai_api_key=openai_api_key,
                azure_openai_api_key=azure_openai_api_key,
                azure_openai_api_version=azure_openai_api_version,
                azure_endpoint=azure_endpoint,
            )
            result = json.loads(result)
            return result
        else:
            model = "gpt-3.5-turbo"
            if azure_openai_api_key is not None:
                model = model.replace(".", "")

            for option in options:
                if "id" not in option and not hasattr(option, "id"):
                    raise ValueError("Option ID is required")

            result = LLMManager.llm(
                messages=[
                    LLMManager.sm(SYSTEM_PROMPT),
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
            return result
