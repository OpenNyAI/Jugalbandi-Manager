import json
import os
from typing import Dict, List
from openai import OpenAI, AzureOpenAI
from openai.types import CompletionUsage
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
azure_openai_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
azure_openai_version = os.getenv("AZURE_OPENAI_VERSION")

if azure_openai_key:
    openai_client = AzureOpenAI(
        api_key=azure_openai_key,
        azure_endpoint=azure_openai_endpoint,
        api_version=azure_openai_version,
    )
else:
    openai_client = OpenAI(api_key=openai_key)

openai_pricing_map: Dict[str, Dict[str, float]] = {
    "text-embedding-ada-002": {"prompt_tokens": 0.1},
    "gpt-4-turbo-2024-04-09": {"prompt_tokens": 10, "completion_tokens": 10},
    "gpt-4-turbo-preview": {"prompt_tokens": 10, "completion_tokens": 10},
    "gpt-3.5-turbo-0125": {"prompt_tokens": 0.5, "completion_tokens": 1.5},
    "gpt-3.5-turbo-instruct": {"prompt_tokens": 1.5, "completion_tokens": 2},
    "gpt-35-turbo-0125": {"prompt_tokens": 0.5, "completion_tokens": 1.5},
    "gpt-35-turbo-instruct": {"prompt_tokens": 1.5, "completion_tokens": 2},
}


def calculate_cost(usages: List[CompletionUsage], model: str):
    cost = 0
    pricing = openai_pricing_map[model]

    for usage in usages:
        usage = usage.model_dump(exclude_none=True)
        for key, value in usage.items():
            cost += value * (pricing.get(key, 0)/1_000_000)
    return cost


def generate_embeddings(conversation_summary: List[str]):
    def chunker(seq, size):
        return (seq[pos : pos + size] for pos in range(0, len(seq), size))

    embeddings = []
    usage = []
    model = "text-embedding-ada-002"
    for openai_input in chunker(conversation_summary, 1000):
        response = openai_client.embeddings.create(model=model, input=openai_input)
        embeddings.extend([emb.embedding for emb in response.data])
        usage.append(response.usage)

    cost = calculate_cost(usage, model)
    return embeddings, cost


def llm(messages, **kwargs):
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

    completions = openai_client.chat.completions.create(**args)
    usage: CompletionUsage = completions.usage

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
        return completions.choices[0].message.content, calculate_cost(
            [usage], args["model"]
        )
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
                "properties": params,
                "required": required,
            },
        },
    }
