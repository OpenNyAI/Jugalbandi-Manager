import json
import openai


def llm(client: openai.OpenAI, messages, **kwargs):
    """Use the OpenAI Language Model API to generate a response based on the given messages."""
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
