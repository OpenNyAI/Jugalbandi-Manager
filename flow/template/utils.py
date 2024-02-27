import json

import openai


def parse_options(user_input, user_task, options):
    """Parse the user input and return the most appropriate option ID based on the user's response."""
    result = llm(
        [
            sm(
                """Given a user's response and a list of options, determine the most appropriate option that the user's response corresponds to. The options are provided in a structured format, each with a unique ID and a title that represents the action or response. The user's response is a statement expressing their preference among the provided options.
Options:
- List each option with its ID and title.

User Response:
- Include the user's response here.

Task:
Analyze the user's response and select the option ID that best matches the intent of their response. Consider the sentiment, keywords, and overall meaning of the user's statement. If the user's response clearly aligns with one of the options, provide the corresponding option ID. If the user's response is ambiguous or does not clearly align with any of the options, indicate that the response is inconclusive.

Output: {id:"{selected_id}"}
You need to return the `id` corresponding to the selected option from the list in json format and nothing else.

Determine the most appropriate option ID based on the user's response."""
            ),
            am(
                f"""User Task- {user_task}
Options:
- {options}"""
            ),
            um(user_input),
        ],
        response_format={"type": "json_object"},
        model="gpt-3.5-turbo",
    )
    result = json.loads(result)
    return result["id"]


def llm(messages, **kwargs):
    """Use the OpenAI Language Model API to generate a response based on the given messages."""
    client = openai.Client(api_key=kwargs.get("OPENAI_API_KEY", None))

    kwargs["model"] = kwargs.get("model")
    kwargs["messages"] = messages
    args = {
        k: v
        for k, v in kwargs.items()
        if k
        in ["model", "messages", "temperature", "tools", "stream", "response_format"]
    }

    if args.get("temperature", None) is None:
        args["temperature"] = 1e-6

    completions = client.chat.completions.create(**args)

    if args.get("stream", False):
        full_response = ""
        for chunk in completions:
            for choice in chunk.choices:
                if choice.finish_reason == "stop":
                    break
                if choice.delta.content is not None:
                    kwargs["callback"](choice.delta.content)
                    full_response += choice.delta.content
        return full_response
    elif args.get("tools", None) is None:
        return completions.choices[0].message.content
    else:
        if completions.choices[0].message.tool_calls is None:
            return {"function": None, "message": completions.choices[0].message.content}
        function = completions.choices[0].message.tool_calls[0].function
        return {"function": function.name, "arguments": json.loads(function.arguments)}


def sm(prompt):
    """System message"""
    return {"role": "system", "content": prompt}


def um(prompt):
    """User message"""
    return {"role": "user", "content": prompt}


def am(prompt):
    """Assistant message"""
    return {"role": "assistant", "content": prompt}


def fn(name, description, params, required):
    """Function message"""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {k: v for k, v in params.items()},
                "required": required,
            },
        },
    }
