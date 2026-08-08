"""Shared LLM client — Groq (fast inference, generous free tier)."""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = os.environ["GROQ_API_KEY"]
MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """Single-turn call to Groq. Returns raw text content."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    resp = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """Call Groq and parse the response as JSON. Raises on malformed output."""
    raw = call_llm(system_prompt, user_prompt, json_mode=True)
    return json.loads(raw)