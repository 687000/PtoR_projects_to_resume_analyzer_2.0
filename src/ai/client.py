import json
import os

import anthropic

_client: anthropic.Anthropic | None = None

MODEL = "claude-sonnet-4-6"


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def complete(prompt: str, max_tokens: int = 4096) -> str:
    response = get_client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def complete_json(prompt: str, max_tokens: int = 4096) -> dict:
    full_prompt = prompt + "\n\nRespond with valid JSON only. No markdown fences, no explanation."
    text = complete(full_prompt, max_tokens).strip()

    # Strip markdown code fences if the model includes them anyway
    if text.startswith("```"):
        text = text[text.index("\n") + 1:]
        if "```" in text:
            text = text[:text.rindex("```")]

    return json.loads(text)
