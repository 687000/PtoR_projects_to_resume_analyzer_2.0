import json
from openai import OpenAI

_client: OpenAI | None = None

MODEL = "gpt-4o"


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def complete(prompt: str, max_tokens: int = 4096) -> str:
    response = get_client().chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def complete_json(prompt: str, max_tokens: int = 4096) -> dict:
    full_prompt = prompt + "\n\nRespond with valid JSON only. No markdown fences, no explanation."
    text = complete(full_prompt, max_tokens).strip()

    # Strip markdown code fences if the model includes them anyway
    if text.startswith("```"):
        text = text[text.index("\n") + 1 :]
        if "```" in text:
            text = text[: text.rindex("```")]

    return json.loads(text)
