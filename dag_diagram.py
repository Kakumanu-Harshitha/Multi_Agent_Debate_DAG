# dag_diagram.py
import networkx as nx
import matplotlib.pyplot as plt

def generate_dag(filename: str = "debate_graph.png"):
    G = nx.DiGraph()
    nodes = [
        "UserInput",
        "Scientist",
        "Philosopher",
        "Summary",
        "Judge"
    ]
    G.add_nodes_from(nodes)
    edges = [
        ("UserInput", "Scientist"),
        ("Scientist", "Philosopher"),
        ("Philosopher", "Scientist"),
        ("Scientist", "Judge"),
        ("Philosopher", "Judge"),
        ("Summary", "Judge")
    ]
    G.add_edges_from(edges)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 6))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color="#A1C3FF",
        node_size=2400,
        font_size=9,
        font_weight="bold",
        arrowsize=20
    )
    plt.title("Multi-Agent Debate DAG")
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Debate DAG saved to {filename}")
