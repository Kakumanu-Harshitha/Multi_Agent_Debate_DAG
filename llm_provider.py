# llm_provider.py
import os
import requests
from dotenv import load_dotenv
from logger import setup_logger

load_dotenv()
logger = setup_logger("llm")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

def call_groq(prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("Groq API key not configured (set GROQ_API_KEY in .env).")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    resp = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()

def generate(role: str, topic: str, memory_summary: str, last_opponent: str, round_no: int, temperature: float = 0.7) -> str:
    """
    role: "Scientist" or "Philosopher" or "Judge"
    """
    prompt = (
        f"You are participating as the {role} in a structured debate.\n"
        f"Topic: {topic}\n\n"
        f"Your memory summary (your own previous points only):\n{memory_summary or '(none)'}\n\n"
        f"Last opponent line:\n{last_opponent or '(none)'}\n\n"
        f"Round {round_no}: Respond with a clear and concise argument (max 120 words) "
        f"that directly addresses the opponent and advances your position.\n"
        f"Do not repeat yourself. Return only your argument."
    )

    try:
        return call_groq(prompt, max_tokens=300, temperature=temperature)
    except Exception as e:
        logger.error(f"Groq API Error: {e}")
        raise
