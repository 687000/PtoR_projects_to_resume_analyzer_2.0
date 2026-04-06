import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def complete(prompt: str, system: str = "", max_tokens: int = 4096) -> str:
    client = get_client()
    messages = [{"role": "user", "content": prompt}]
    kwargs = {"model": "claude-opus-4-6", "max_tokens": max_tokens, "messages": messages}
    if system:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    return response.content[0].text


def complete_json(prompt: str, system: str = "", max_tokens: int = 4096) -> dict:
    text = complete(prompt, system=system, max_tokens=max_tokens)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        start = text.find("[")
        end = text.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON found in response: {text[:200]}")
    return json.loads(text[start:end])
