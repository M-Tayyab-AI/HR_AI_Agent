from typing import TypedDict, List
from agents.hr_agent_llm import llm_planner
import json
from data_base_connection import update_sheet_by_cell

class AgentState(TypedDict):
    user_query: str
    task: str
    task_type: str
    chat_history: list
    employee_name: str
    steps: List[str]
    needs_input: bool
    action_required: dict

def planner(state: AgentState):
    print("🧠 Planner running...")
    if state.get("needs_input",True):
        user_input = input("❓ Agent: Please provide your query for this time: ")
        state["user_query"]=user_input
    print(state["user_query"])
    llm_planner_response=llm_planner(user_query=state["user_query"],chat_history=state["chat_history"])
    print(llm_planner_response)
    print("-"*100)
    json_response=json.loads(llm_planner_response)
    print(json_response)
    print("-"*100)
    # Update chat history (conversation memory)
    state["chat_history"].append(
        {"role": "user", "content": state["user_query"]}
    )
    state["chat_history"].append(
        {"role": "assistant", "content": json.dumps(json_response)}
    )
    # Extract values with safe defaults
    employee_name = json_response.get("Name", "")
    task = json_response.get("Task", "Unknown task")
    task_type = json_response.get("Task_Type", "Unknown task")
    possible = json_response.get("Possible", "No")
    reason = json_response.get("Reason", "No reason provided")
    action_in_sheet = json_response.get("Action",{})
    if employee_name:
        state["needs_input"] = False
        state['employee_name'] = employee_name
        state["steps"].append(f"{employee_name} requested a query")
        if possible == "Yes":
            state["task_type"] = task_type
            state["action_required"] = action_in_sheet
            state["steps"].append("✅ Planner approved the action")
        else:
            state["steps"].append(f"❌ Planner denied the action. Reason: {reason}")
    else:
        state["needs_input"] = True
        state["steps"].append(f"⚠️ Employee name not provided for task: {task}")
        state["steps"].append(f"❌ Action cannot be performed. Reason: {reason}")
    return state

def planner_router(state: AgentState):
    if state.get("needs_input", True):
        return "input"
    return "action"


def input_node(state: AgentState):
    if state.get("needs_input", True):
        user_input = input("❓ Agent: Please provide your name: ")
        state["user_query"] = state["user_query"]+ " My names is " +user_input
        state["needs_input"] = False
    return state

def action(state: AgentState):
    print("⚙️ Action running...")
    if state["task_type"]=="Read":
        print("LLM gives answer just base on read")
        state["steps"].append(
            f"🚀 Executing action: {state['task']} for {state['employee_name']}"
        )
    elif state["task_type"]=="Write":
        print("Updating Excel sheet or DB")
        state["steps"].append(
            f"🚀 Executing action: {state['task']} for {state['employee_name']}"
        )
        print("-"*100)
        print(state["action_required"])
        print("-"*100)
        update_sheet_by_cell(cell_data=state["action_required"])
        state["steps"].append(
            f"✅ Action Executed Successfully: {state['task']} for {state['employee_name']}"
        )
    else:
        state["steps"].append(
            f"❌ Action cannot be performed. Reason wrong Task Type : {state["task_type"]}"
        )
    return state

def decide(state: AgentState):
    user_input = input("❓ Agent: Do you wanna continue? yes or no ")
    if user_input=="yes":
        state["needs_input"] = True
        return state
    else:
        state["needs_input"] = False
        return state