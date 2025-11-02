
# Multi-Agent Debate System

This project is a command-line multi-agent debate system built using LangGraph. It simulates a debate between a "Scientist" agent and a "Philosopher" agent on a user-provided topic. A "Judge" agent reviews the debate and declares a winner after a set number of rounds.

This system is built with a stateful graph that manages the flow of the conversation, logs the debate, and visualizes its own structure.
# Demo video
[click on this for explnation](https://1drv.ms/v/c/695d4659be40ade4/EX4LwljQR55Okx3GB_ojtUMBB8V5FQ_t0ygNJW5vMkxvCA?e=x3kekA)


## Features

* **Multi-Agent:** Includes Scientist, Philosopher, and Judge agents.
* **Stateful Graph:** Uses `StateGraph` from LangGraph to manage the debate state (topic, rounds, arguments).
* **Dynamic Routing:** Automatically routes between the Scientist and Philosopher for 4 rounds each, then proceeds to the Judge.
* **LLM Integration:** Connects to the Groq API for fast LLM responses.
* **Logging:** Logs the summary of each debate round to `debate_log.txt`.
* **Graph Visualization:** Automatically generates a PNG diagram (`debate_graph.png`) of the agent workflow using NetworkX and Matplotlib.

## Project Structure

debate/

│

├── main.py # Starts and manages the debate workflow

├── graph_nodes.py # Logic for Scientist, Philosopher, Judge, and User input nodes

├── state.py # Maintains shared debate state across rounds

├── logger.py # Logging setup for saving debate logs

├── dag_diagram.py # Generates DAG visualization of the debate flow

├── requirements.txt # Python dependencies


├── debate_log.txt # Debate transcript logs (auto-generated)

└── debate_graph.png # DAG flow diagram (auto-generated)
## Outputs
After the script runs, you will find two new files in your directory:

debate_log.txt: A log file containing the arguments from each round.

debate_graph.png: A visual diagram of the agent workflow.
## 🌟 Features
Multi-agent debate workflow

Logical reasoning and argument generation

Automatic judgment and explanation

Full transcript saved

Workflow DAG visualization

## Setup and Installation

Follow these steps to set up and run the project.

### 1. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.


# Create a new virtual environment (e.g., named .venv)
```bash
python -m venv .venv

# Activate the virtual environment

# On Windows
.\.venv\Scripts\activate

# On macOS/Linux:

source .venv/bin/activate
````
2. Install Dependencies
```bash
# Install all the required Python packages using the requirements.txt file.


pip install -r requirements.txt
````

3. Set Up Environment Variables
```bash
# This project requires a Groq API key to function.
#Create a file named .env in the main debate/ directory.
#Open the .env file and add your Groq API key:

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
````
Replace your_groq_api_key_here with your actual key.

4.How to Run


```bash
#Once your virtual environment is active and your .env file is set up, run the main script from your terminal:
pip install -r requirements.txt
python main.py
```

The application will start and prompt you to enter a debate topic. The debate will run for 4 rounds, after which the Judge's verdict will be printed to the console.

