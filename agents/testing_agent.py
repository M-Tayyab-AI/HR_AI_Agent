from typing import TypedDict, List
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    task: str
    steps: List[str]

def planner(state: AgentState):
    print("🧠 Planner running...")
    state["steps"].append("Planner decided to perform action")
    return state

def action(state: AgentState):
    print("⚙️ Action running...")
    state["steps"].append("Action executed task")
    return state

def decide(state: AgentState):
    print("🤔 Deciding...")
    return state

def route(state: AgentState):
    if len(state["steps"]) < 5:
        return "continue"
    return "end"


graph = StateGraph(AgentState)

graph.add_node("planner", planner)
graph.add_node("action", action)
graph.add_node("decide", decide)

graph.set_entry_point("planner")

graph.add_edge("planner", "action")
graph.add_edge("action", "decide")

graph.add_conditional_edges(
    "decide",
    route,
    {
        "continue": "planner",
        "end": END
    }
)
app = graph.compile()

initial_state = {
    "task": "learn langgraph",
    "steps": []
}

final_state = app.invoke(initial_state)
print("\nFinal State:", final_state)
