# utils.py
import re
from typing import List

def normalize_text(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z0-9\s]", "", s)
    return s

def is_repeat(new_text: str, past_texts: List[str], threshold: float = 0.85) -> bool:
    """
    Simple token-overlap heuristic for near-duplicates.
    """
    nset = set(normalize_text(new_text).split())
    if not nset:
        return True
    for p in past_texts:
        pset = set(normalize_text(p).split())
        if not pset:
            continue
        overlap = len(nset & pset) / max(len(nset), len(pset))
        if overlap >= threshold:
            return True
    return False

def format_round_line(agent_label: str, round_no: int, text: str) -> str:
    return f"[Round {round_no}] {agent_label}: {text}"