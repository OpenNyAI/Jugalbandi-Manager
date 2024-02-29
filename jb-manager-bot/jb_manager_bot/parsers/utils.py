import json
from openai import OpenAI

class LLMManager:
    """Language Model Manager for OpenAI's GPT."""

    client: OpenAI = None

    @classmethod
    def get_client(cls, api_key):
        """Return the OpenAI client."""
        if cls.client is None:
            cls.client = OpenAI(api_key=api_key)
        return cls.client

    @classmethod
    def llm(cls, api_key, messages, **kwargs):
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

        client = cls.get_client(api_key)
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


    @classmethod
    def sm(cls, prompt):
        """System message"""
        return {"role": "system", "content": prompt}


    @classmethod
    def um(cls, prompt):
        """User message"""
        return {"role": "user", "content": prompt}


    @classmethod
    def am(cls, prompt):
        """Assistant message"""
        return {"role": "assistant", "content": prompt}


    @classmethod
    def fn(cls, name, description, params, required):
        """Function message"""
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": required,
                },
            },
        }
