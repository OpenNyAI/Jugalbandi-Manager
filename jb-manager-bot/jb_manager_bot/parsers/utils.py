import json
from typing import List
from openai import OpenAI, AzureOpenAI


class LLMManager:
    """Language Model Manager for OpenAI's GPT."""

    client: OpenAI = None

    @classmethod
    def get_client(
        cls,
        openai_api_key=None,
        azure_openai_api_key=None,
        azure_openai_api_version=None,
        azure_endpoint=None,
    ):
        """Return the OpenAI client."""
        if cls.client is None:
            if azure_openai_api_key is not None:
                cls.client = AzureOpenAI(
                    api_key=azure_openai_api_key,
                    api_version=azure_openai_api_version,
                    azure_endpoint=azure_endpoint,
                )
            else:
                cls.client = OpenAI(api_key=openai_api_key)
        return cls.client

    @classmethod
    def llm(
        cls,
        messages,
        openai_api_key=None,
        azure_openai_api_key=None,
        azure_openai_api_version=None,
        azure_endpoint=None,
        **kwargs
    ):
        """Use the OpenAI Language Model API to generate a response based on the given messages."""

        kwargs["model"] = kwargs.get("model")
        kwargs["messages"] = messages
        args = {
            k: v
            for k, v in kwargs.items()
            if k
            in [
                "model",
                "messages",
                "temperature",
                "tools",
                "stream",
                "response_format",
            ]
        }

        if args.get("temperature", None) is None:
            args["temperature"] = 1e-6

        client = cls.get_client(
            openai_api_key=openai_api_key,
            azure_openai_api_key=azure_openai_api_key,
            azure_openai_api_version=azure_openai_api_version,
            azure_endpoint=azure_endpoint,
        )
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
                return {
                    "function": None,
                    "message": completions.choices[0].message.content,
                }
            function = completions.choices[0].message.tool_calls[0].function
            return {
                "function": function.name,
                "arguments": json.loads(function.arguments),
            }

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

    @classmethod
    def generate_embeddings(
        cls,
        inputs: List[str],
        model: str,
        openai_api_key=None,
        azure_openai_api_key=None,
        azure_openai_api_version=None,
        azure_endpoint=None,
        **kwargs
    ):
        """Use the OpenAI Embeddings API to generate embeddings for the given inputs."""
        client = cls.get_client(
            openai_api_key=openai_api_key,
            azure_openai_api_key=azure_openai_api_key,
            azure_openai_api_version=azure_openai_api_version,
            azure_endpoint=azure_endpoint,
        )
        args = {
            k: v
            for k, v in kwargs.items()
            if k
            in [
                "encoding_format",
                "dimensions",
            ]
        }
        response = client.embeddings.create(model=model, input=inputs, **args)
        embeddings = [emb.embedding for emb in response.data]

        return embeddings
