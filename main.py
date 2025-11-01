# main.py
from dotenv import load_dotenv
from logger import setup_logger
from state import DebateState, DebateStateFactory
from graph_nodes import (
    user_input_node,
    scientist_node,
    philosopher_node,
    summary_node,
    judge_node,
    route_to_agent,
)
from dag_diagram import generate_dag
from langgraph.graph import StateGraph, END

load_dotenv()
logger = setup_logger("main")

def build_and_run():
    workflow = StateGraph(DebateState)

    # --- Nodes ---
    workflow.add_node("user_input", user_input_node)
    workflow.add_node("scientist", scientist_node)
    workflow.add_node("philosopher", philosopher_node)
    workflow.add_node("summary", summary_node)
    workflow.add_node("judge", judge_node)

    # --- ENTRY POINT MUST BE USER INPUT FIRST ---
    workflow.set_entry_point("user_input")

    # After user input → send to router to choose scientist first
    workflow.add_conditional_edges("user_input", route_to_agent, {
        "scientist": "scientist",
        "philosopher": "philosopher",
        "judge": "judge",   # failsafe
    })

    # Debate turn logic
    workflow.add_conditional_edges("scientist", route_to_agent, {
        "scientist": "scientist",
        "philosopher": "philosopher",
        "judge": "judge"
    })
    workflow.add_conditional_edges("philosopher", route_to_agent, {
        "scientist": "scientist",
        "philosopher": "philosopher",
        "judge": "judge"
    })

    # Judge ends the debate
    workflow.add_edge("judge", END)

    app = workflow.compile()

    # Generate DAG image
    try:
        generate_dag()
    except Exception as e:
        logger.warning("DAG generation failed: %s", e)

    state = DebateStateFactory()

    print("\nStarting Debate...\n")

    # Run Graph
    try:
        last_state = None
        for event in app.stream(state):
            if isinstance(event, dict):
                last_state = event.get("new_state") or last_state
        final = last_state or state
    except:
        final = app.invoke(state)

    # Show transcript
    print("\n========= FULL DEBATE TRANSCRIPT =========\n")
    for line in final.get("full_transcript", []):
        print(line)

    # Show judgment
    print("\n=========== JUDGE RESULT ===========\n")
    print(f"Winner: {final['winner']}")
    print(f"Reason: {final['reason']}")

    print("\nLogs: debate_log.txt  |  DAG: debate_graph.png")


if __name__ == "__main__":
    build_and_run()
