# graph_nodes.py
from typing import Dict, Any
from logger import setup_logger
from utils import is_repeat, format_round_line
from llm_provider import generate
from state import DebateStateFactory

logger = setup_logger("nodes")

def _summary_from_list(lines, last_n=4):
    return " | ".join(lines[-last_n:]) if lines else ""

def user_input_node(state):
    # Ask the user for topic
    print("\n--------------------------------------")
    print("Enter the debate topic (or press Enter to use default).")
    topic = input("Topic: ").strip()
    print("--------------------------------------\n")

    # If user presses Enter → use default topic
    if not topic:
        topic = "Should AI be regulated like medicine?"
        print(f"Using default topic: {topic}\n")

    state["topic"] = topic

    # Ensure messages list exists
    if "messages" not in state:
        state["messages"] = []

    print(f"✅ Debate topic set to: {state['topic']}\n")
    return state


def scientist_node(state: Dict[str, Any]) -> Dict[str, Any]:
    next_round = state.get("round_number", 0) + 1
    # enforce allowed rounds for scientist
    if next_round not in (1, 3, 5, 7):
        msg = f"Scientist attempted to speak at invalid round {next_round}"
        logger.error(msg)
        state.setdefault("validation_log", []).append(msg)
        raise RuntimeError(msg)

    topic = state["topic"]
    mem_frag = state.get("memory_summary_scientist", "")
    last_opponent = state.get("full_transcript", [])[-1] if state.get("full_transcript") else ""

    arg = generate("Scientist", topic, mem_frag, last_opponent, next_round).strip()

    past = state.get("past_scientist_args", [])
    if is_repeat(arg, past, threshold=0.85):
        logger.warning("Scientist near-duplicate detected; adding nuance.")
        arg = f"{arg} (clarified in round {next_round})."
        if is_repeat(arg, past, threshold=0.85):
            raise RuntimeError("Scientist could not avoid repetition.")

    line = format_round_line("Scientist", next_round, arg)
    print(line)
    logger.info(line)

    state["full_transcript"] = state.get("full_transcript", []) + [line]
    state["memory_scientist"] = state.get("memory_scientist", []) + [arg]
    state["memory_summary_scientist"] = _summary_from_list(state["memory_scientist"])
    state["past_scientist_args"] = state.get("past_scientist_args", []) + [arg]
    state["round_number"] = next_round
    # also keep human-readable history for summary_node
    state.setdefault("history", []).append(line)

    return state

def philosopher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    next_round = state.get("round_number", 0) + 1
    if next_round not in (2, 4, 6, 8):
        msg = f"Philosopher attempted to speak at invalid round {next_round}"
        logger.error(msg)
        state.setdefault("validation_log", []).append(msg)
        raise RuntimeError(msg)

    topic = state["topic"]
    mem_frag = state.get("memory_summary_philosopher", "")
    last_opponent = state.get("full_transcript", [])[-1] if state.get("full_transcript") else ""

    arg = generate("Philosopher", topic, mem_frag, last_opponent, next_round).strip()

    past = state.get("past_philosopher_args", [])
    if is_repeat(arg, past, threshold=0.85):
        logger.warning("Philosopher near-duplicate detected; adding nuance.")
        arg = f"{arg} (clarified in round {next_round})."
        if is_repeat(arg, past, threshold=0.85):
            raise RuntimeError("Philosopher could not avoid repetition.")

    line = format_round_line("Philosopher", next_round, arg)
    print(line)
    logger.info(line)

    state["full_transcript"] = state.get("full_transcript", []) + [line]
    state["memory_philosopher"] = state.get("memory_philosopher", []) + [arg]
    state["memory_summary_philosopher"] = _summary_from_list(state["memory_philosopher"])
    state["past_philosopher_args"] = state.get("past_philosopher_args", []) + [arg]
    state["round_number"] = next_round
    state.setdefault("history", []).append(line)

    return state

def summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state.get("topic", "Unknown Topic")
    history = state.get("history", [])
    # friendly short summary
    if history:
        summary_text = f"Debate Summary on '{topic}':\n" + "\n".join(history[-4:])
    else:
        summary_text = f"Debate Summary on '{topic}': No arguments yet."
    state["memory_summary_scientist"] = state.get("memory_summary_scientist", "")
    state["memory_summary_philosopher"] = state.get("memory_summary_philosopher", "")
    # append to transcript & history
    state["full_transcript"] = state.get("full_transcript", []) + [f"[Summary]: {summary_text}"]
    state.setdefault("history", []).append(f"[Summary]: {summary_text}")
    print(f"[Summary] {summary_text}")
    logger.info("[Summary] %s", summary_text)
    return state

def judge_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("JudgeNode: reviewing debate...")
    print("\n--- Judge is reviewing the debate ---\n")

    ft = state.get("full_transcript", [])
    sum_sci = state.get("memory_summary_scientist", "")
    sum_phi = state.get("memory_summary_philosopher", "")

    transcript_snippet = "\n".join(ft[-8:])
    # small judge prompt but we will reuse generate() for judge behavior
    judge_output = generate("Judge", state.get("topic", ""), "", transcript_snippet, state.get("round_number", 8)).strip()

    # parse best-effort
    summary = ""
    winner = ""
    justification = ""
    for line in judge_output.splitlines():
        low = line.lower()
        if low.startswith("summary:"):
            summary = line.split(":", 1)[1].strip()
        elif low.startswith("winner:"):
            winner = line.split(":", 1)[1].strip()
        elif low.startswith("justification:"):
            justification = line.split(":", 1)[1].strip()

    # fallback heuristics
    if not winner:
        low = judge_output.lower()
        if "scientist" in low and "philosopher" in low:
            if "winner:" in low:
                winner_line = [l for l in judge_output.splitlines() if "winner" in l.lower()]
                if winner_line:
                    winner = winner_line[0].split(":", 1)[1].strip()
            else:
                winner = "Scientist"
        elif "scientist" in low:
            winner = "Scientist"
        elif "philosopher" in low:
            winner = "Philosopher"
        else:
            winner = "Scientist"

    state["winner"] = winner
    state["reason"] = justification or judge_output
    state["full_transcript"] = state.get("full_transcript", []) + [f"[Judge] Summary: {summary} | Winner: {winner} | Reason: {state['reason']}"]
    state.setdefault("history", []).append(f"[Judge] Winner: {winner}")
    print(f"\n[Judge] Summary: {summary}\n[Judge] Winner: {winner}\n[Judge] Justification: {state['reason']}\n")
    logger.info("[Judge] Winner: %s", winner)
    logger.info("[Judge] Justification: %s", state['reason'])
    return state

def route_to_agent(state: Dict[str, Any]) -> str:
    r = state.get("round_number", 0) or 0
    if r >= 8:
        logger.info("Router: reached 8 rounds -> judge")
        return "judge"
    next_round = r + 1
    if next_round % 2 == 1:
        logger.info("Router: route to scientist (round %d)", next_round)
        return "scientist"
    else:
        logger.info("Router: route to philosopher (round %d)", next_round)
        return "philosopher"