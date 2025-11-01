# llm_provider.py
import os
import logging
import requests
from logger import setup_logger
from dotenv import load_dotenv
load_dotenv()
logger = setup_logger("llm")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
FORCE_STUB = os.getenv("FORCE_STUB", "no").lower() in ("1", "yes", "true")

# Deterministic stub responses for offline/demo mode
_scientist_templates = [
    "Empirical risk assessment shows high-impact AI needs structured oversight.",
    "Clinical-style testing and certification reduce catastrophic failures in high-risk systems.",
    "Case studies from medicine and aviation show regulation reduces systemic risk.",
    "A risk-based adaptive framework balances innovation and public safety."
]
_philosopher_templates = [
    "Regulation can stifle philosophical inquiry and autonomy — caution is needed.",
    "Premature regulation may ossify values and slow moral progress.",
    "What counts as 'harm' is contested; we must protect freedom of thought.",
    "Ethical reflection and debate should guide policy rather than blunt rules."
]

def stub_generate(role: str, topic: str, memory_frag: str, last_opponent: str, round_no: int) -> str:
    idx = (round_no - 1) // 2
    if role.lower().startswith("scientist"):
        base = _scientist_templates[idx % len(_scientist_templates)]
    elif role.lower().startswith("philosopher"):
        base = _philosopher_templates[idx % len(_philosopher_templates)]
    else:
        base = "I summarize: " + (memory_frag or topic)
    if last_opponent:
        return f"{base} (Ref: {last_opponent[:120]})"
    return base

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
        "temperature": temperature
    }
    resp = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Parse typical OpenAI-style response
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        # fallback shapes
        if isinstance(data, dict):
            if "text" in data:
                return data["text"].strip()
            if "generated_text" in data:
                return data["generated_text"].strip()
        logger.debug("Groq response unexpected shape: %s", data)
        return str(data)[:1000]

def generate(role: str, topic: str, memory_frag: str, last_opponent: str, round_no: int, temperature: float = 0.7) -> str:
    """
    role: "Scientist" or "Philosopher" or "Judge"
    """
    prompt = (
        f"You are a {role} in a structured debate.\n"
        f"Topic: {topic}\n\n"
        f"Your memory summary (only your memory):\n{memory_frag or '(none)'}\n\n"
        f"Last opponent line:\n{last_opponent or '(none)'}\n\n"
        f"Round {round_no}: Provide a concise (<=120 words) argument that advances your position and directly addresses the last opponent line. "
        f"Avoid repeating earlier points verbatim. Return only the argument."
    )

    if FORCE_STUB:
        logger.info("FORCE_STUB enabled — using deterministic stub LLM.")
        return stub_generate(role, topic, memory_frag, last_opponent, round_no)

    try:
        return call_groq(prompt, max_tokens=300, temperature=temperature)
    except Exception as e:
        logger.warning("Groq call failed: %s — falling back to stub.", e)
        return stub_generate(role, topic, memory_frag, last_opponent, round_no)
