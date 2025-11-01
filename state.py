# state.py
from typing import TypedDict, List, Dict, Any

class DebateState(TypedDict):
    topic: str
    round_number: int
    full_transcript: List[str]
    memory_scientist: List[str]
    memory_philosopher: List[str]
    memory_summary_scientist: str
    memory_summary_philosopher: str
    past_scientist_args: List[str]
    past_philosopher_args: List[str]
    validation_log: List[str]
    winner: str
    reason: str
    history: List[str]

def DebateStateFactory() -> DebateState:
    return {
        "topic": "",
        "round_number": 0,
        "full_transcript": [],
        "memory_scientist": [],
        "memory_philosopher": [],
        "memory_summary_scientist": "",
        "memory_summary_philosopher": "",
        "past_scientist_args": [],
        "past_philosopher_args": [],
        "validation_log": [],
        "winner": "",
        "reason": "",
        "history": []
    }