from langgraph.graph import StateGraph, END
from hr_agent_confiq import AgentState, planner, planner_router, action, input_node, decide

employee_query="My name is Tayyab and I want to remove bonus from Admins position and give Arslan and Hadia 10% bonus for their outstanding for past 3 months and Captilize the bonus column name"

graph = StateGraph(AgentState)

graph.add_node("input", input_node)
graph.add_node("planner", planner)
graph.add_node("decide", decide)
graph.add_node("action", action)
graph.set_entry_point("planner")

graph.add_conditional_edges(
    "planner",
    planner_router,
    {
        "input": "planner",
        "action": "action"
    }
)

graph.add_edge("action","decide")

graph.add_conditional_edges(
    "decide",
    planner_router,
    {
        "input":"planner",
        "action":END
    }
)
# graph.add_edge("action", END)

app = graph.compile()

initial_state: AgentState = {
    "user_query": employee_query,
    "task": "",
    "employee_name": "",
    "chat_history": [],
    "steps": [],
    "needs_input": False,
    "task_type": "",
    "action_required":{}
}


final_state = app.invoke(initial_state)
# print("\nFinal State:", final_state)
print(final_state["steps"])
print(final_state["chat_history"])