import streamlit as st
from langgraph.graph import StateGraph, END
from agents.hr_agent_confiq import AgentState, planner_router, action
from agents.hr_agent_llm import llm_planner
from data_base_connection import get_all_names
import json

# Page configuration
st.set_page_config(
    page_title="Organization Agent Chat",
    page_icon="🤖",
    layout="wide"
)

# Streamlit-compatible versions of agent functions
def streamlit_planner(state: AgentState):
    """Planner function adapted for Streamlit"""
    if state.get("needs_input", True):
        # Check if we have pending input from Streamlit
        if st.session_state.pending_user_input:
            state["user_query"] = st.session_state.pending_user_input
            st.session_state.pending_user_input = None
            st.session_state.waiting_for_input = False
        else:
            # Need to wait for user input
            st.session_state.waiting_for_input = True
            st.session_state.input_type = "query"
            return state
    
    # Add selected employee name to query if not already present
    if st.session_state.selected_employee and st.session_state.selected_employee not in state["user_query"]:
        state["user_query"] = f"My name is {st.session_state.selected_employee}. {state['user_query']}"
    
    # Continue with normal planner logic
    try:
        # Add step for planning
        planning_msg = "Planning: Analyzing the request..."
        state["steps"].append(f"🧠 {planning_msg}")
        st.session_state.agent_status = "🧠 Planning..."
        add_system_message(f"🧠 {planning_msg}", "🧠", display_now=True)
        st.session_state.pending_messages.append(("🧠", planning_msg))
        # Write directly to status container (will appear in real-time)
        if st.session_state.get("status_container"):
            st.write(f"🧠 {planning_msg}")
        
        llm_planner_response = llm_planner(user_query=state["user_query"], chat_history=state["chat_history"])
        
        # Add step for reasoning
        reasoning_msg = "Reasoning: Processing the response..."
        state["steps"].append(f"💭 {reasoning_msg}")
        st.session_state.agent_status = "💭 Reasoning..."
        add_system_message(f"💭 {reasoning_msg}", "💭", display_now=True)
        st.session_state.pending_messages.append(("💭", reasoning_msg))
        # Write directly to status container (will appear in real-time)
        if st.session_state.get("status_container"):
            st.write(f"💭 {reasoning_msg}")
        
        json_response = json.loads(llm_planner_response)
        
        # Update chat history
        state["chat_history"].append({"role": "user", "content": state["user_query"]})
        state["chat_history"].append({"role": "assistant", "content": json.dumps(json_response)})
        
        # Extract values
        task = json_response.get("Task", "Unknown task")
        task_type = json_response.get("Task_Type", "Unknown task")
        possible = json_response.get("Possible", "No")
        reason = json_response.get("Reason", "No reason provided")
        action_in_sheet = json_response.get("Action", {})
        answer = json_response.get("Answer", "")
        
        # Store answer for display (use reason if answer is empty)
        if answer:
            state["last_answer"] = answer
        elif reason:
            state["last_answer"] = f"Reason: {reason}"
        
        # Use selected employee name from dropdown (always available since dropdown is required)
        employee_name = st.session_state.selected_employee if st.session_state.selected_employee else json_response.get("Name", "")
        if employee_name:
            state["employee_name"] = employee_name
        
        if employee_name:
            state["needs_input"] = False
            state["task"] = task
            state["steps"].append(f"👤 {employee_name} requested a query")
            state["steps"].append(f"📋 Task: {task}")
            state["steps"].append(f"🔍 Task Type: {task_type}")
            
            # Add task info to chat
            task_msg = f"Task Identified: {task}"
            add_system_message(f"📋 {task_msg}", "📋", display_now=True)
            st.session_state.pending_messages.append(("📋", task_msg))
            if st.session_state.get("status_container"):
                st.write(f"📋 {task_msg}")
            
            task_type_msg = f"Task Type: {task_type}"
            add_system_message(f"🔍 {task_type_msg}", "🔍", display_now=True)
            st.session_state.pending_messages.append(("🔍", task_type_msg))
            if st.session_state.get("status_container"):
                st.write(f"🔍 {task_type_msg}")
            
            if possible == "Yes":
                state["task_type"] = task_type
                state["action_required"] = action_in_sheet
                approval_msg = "Planner approved the action"
                state["steps"].append(f"✅ {approval_msg}")
                state["steps"].append(f"💡 Reason: {reason}")
                add_system_message(f"✅ {approval_msg}", "✅", display_now=True)
                st.session_state.pending_messages.append(("✅", approval_msg))
                if st.session_state.get("status_container"):
                    st.write(f"✅ {approval_msg}")
                
                reason_msg = f"Reasoning: {reason}"
                add_system_message(f"💡 {reason_msg}", "💡", display_now=True)
                st.session_state.pending_messages.append(("💡", reason_msg))
                if st.session_state.get("status_container"):
                    st.write(f"💡 {reason_msg}")
            else:
                denial_msg = "Planner denied the action"
                state["steps"].append(f"❌ {denial_msg}")
                state["steps"].append(f"💡 Reason: {reason}")
                add_system_message(f"❌ {denial_msg}", "❌", display_now=True)
                st.session_state.pending_messages.append(("❌", denial_msg))
                if st.session_state.get("status_container"):
                    st.write(f"❌ {denial_msg}")
                
                reason_msg = f"Reasoning: {reason}"
                add_system_message(f"💡 {reason_msg}", "💡", display_now=True)
                st.session_state.pending_messages.append(("💡", reason_msg))
                if st.session_state.get("status_container"):
                    st.write(f"💡 {reason_msg}")
        else:
            state["needs_input"] = True
            state["steps"].append(f"⚠️ Employee name not provided for task: {task}")
            state["steps"].append(f"❌ Action cannot be performed. Reason: {reason}")
    except Exception as e:
        state["steps"].append(f"❌ Error in planner: {str(e)}")
        st.error(f"Error in planner: {str(e)}")
    
    return state


def streamlit_input_node(state: AgentState):
    """Input node adapted for Streamlit - not needed since we use dropdown"""
    # Since we're using dropdown for employee selection, this node is mostly bypassed
    # But we keep it for compatibility with the graph structure
    if state.get("needs_input", True):
        # If we have selected employee, use it
        if st.session_state.selected_employee:
            state["needs_input"] = False
            state["employee_name"] = st.session_state.selected_employee
        elif st.session_state.pending_user_input:
            state["user_query"] = state.get("user_query", "") + " My name is " + st.session_state.pending_user_input
            state["needs_input"] = False
            st.session_state.pending_user_input = None
            st.session_state.waiting_for_input = False
        else:
            st.session_state.waiting_for_input = True
            st.session_state.input_type = "name"
    return state


def streamlit_decide(state: AgentState):
    """Decide function adapted for Streamlit"""
    # Don't add deciding message to pending_messages (user doesn't need to see this)
    # Only update status for internal tracking
    st.session_state.agent_status = "🤔 Deciding..."
    
    if st.session_state.pending_continue_decision is not None:
        user_input = st.session_state.pending_continue_decision
        st.session_state.pending_continue_decision = None
        if user_input.lower() == "yes":
            state["needs_input"] = True
            state["steps"].append("✅ User chose to continue")
        else:
            state["needs_input"] = False
            state["steps"].append("❌ User chose to end chat")
        st.session_state.waiting_for_continue = False
        st.session_state.agent_status = "Ready"
    else:
        st.session_state.waiting_for_continue = True
    return state


# Initialize agent graph
if "agent_graph" not in st.session_state:
    graph = StateGraph(AgentState)
    graph.add_node("input", streamlit_input_node)
    graph.add_node("planner", streamlit_planner)
    graph.add_node("decide", streamlit_decide)
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
    
    graph.add_edge("action", "decide")
    
    graph.add_conditional_edges(
        "decide",
        planner_router,
        {
            "input": "planner",
            "action": END
        }
    )
    
    st.session_state.agent_graph = graph.compile()

# Initialize session state
if "current_state" not in st.session_state:
    st.session_state.current_state = {
        "user_query": "",
        "task": "",
        "employee_name": "",
        "chat_history": [],
        "steps": [],
        "needs_input": False,
        "task_type": "",
        "action_required": {}
    }

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "waiting_for_input" not in st.session_state:
    st.session_state.waiting_for_input = False

if "waiting_for_continue" not in st.session_state:
    st.session_state.waiting_for_continue = False

if "input_type" not in st.session_state:
    st.session_state.input_type = None

if "execution_steps" not in st.session_state:
    st.session_state.execution_steps = []

if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None

if "pending_continue_decision" not in st.session_state:
    st.session_state.pending_continue_decision = None

if "last_displayed_answer" not in st.session_state:
    st.session_state.last_displayed_answer = None

if "selected_employee" not in st.session_state:
    st.session_state.selected_employee = None

if "agent_status" not in st.session_state:
    st.session_state.agent_status = "Ready"

if "display_mode" not in st.session_state:
    st.session_state.display_mode = False

if "pending_messages" not in st.session_state:
    st.session_state.pending_messages = []

if "status_container" not in st.session_state:
    st.session_state.status_container = None


def add_assistant_message(content):
    """Add assistant message to chat if it's new"""
    if content and content != st.session_state.last_displayed_answer:
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": content
        })
        st.session_state.last_displayed_answer = content

def add_system_message(content, icon="ℹ️", display_now=False):
    """Add system/agent step message to chat"""
    # Don't add to chat_messages if we're using pending_messages for display
    # This prevents duplicate icons when displaying
    # We only add to chat_messages for messages that won't be in pending_messages
    pass

def display_step_in_realtime(icon, msg):
    """Display a step message in real-time if status container is available"""
    # Messages will be written directly to the status container during execution
    # The status container context is handled in the main execution flow
    pass


def execute_agent(state, max_iterations=10):
    """Execute the agent graph step by step, handling the full loop"""
    try:
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            # Start with planner
            state = streamlit_planner(state)
            
            # If waiting for input, return early
            if st.session_state.waiting_for_input:
                return state
            
            # Check router decision
            router_decision = planner_router(state)
            
            if router_decision == "action":
                # Run action
                action_msg = "Executing action..."
                state["steps"].append(f"⚙️ {action_msg}")
                st.session_state.agent_status = "⚙️ Executing..."
                add_system_message(f"⚙️ {action_msg}", "⚙️", display_now=True)
                st.session_state.pending_messages.append(("⚙️", action_msg))
                if st.session_state.get("status_container"):
                    st.write(f"⚙️ {action_msg}")
                
                # Add action execution details to chat before execution
                if state.get("task_type") == "Write" and state.get("action_required"):
                    action_details = f"Updating Sheet: {len(state['action_required'])} cell(s) will be updated"
                    add_system_message(f"📝 {action_details}", "📝", display_now=True)
                    st.session_state.pending_messages.append(("📝", action_details))
                    if st.session_state.get("status_container"):
                        st.write(f"📝 {action_details}")
                elif state.get("task_type") == "Read":
                    read_msg = "Reading Data: Retrieving information from the database"
                    add_system_message(f"📖 {read_msg}", "📖", display_now=True)
                    st.session_state.pending_messages.append(("📖", read_msg))
                    if st.session_state.get("status_container"):
                        st.write(f"📖 {read_msg}")
                
                state = action(state)
                
                # Add success message after action
                if state.get("task_type") == "Write":
                    success_msg = f"Action Completed: Successfully updated {len(state.get('action_required', {}))} cell(s) in the sheet"
                    add_system_message(f"✅ {success_msg}", "✅", display_now=True)
                    st.session_state.pending_messages.append(("✅", success_msg))
                    if st.session_state.get("status_container"):
                        st.write(f"✅ {success_msg}")
                elif state.get("task_type") == "Read":
                    success_msg = "Data Retrieved: Information successfully retrieved"
                    add_system_message(f"✅ {success_msg}", "✅", display_now=True)
                    st.session_state.pending_messages.append(("✅", success_msg))
                    if st.session_state.get("status_container"):
                        st.write(f"✅ {success_msg}")
                
                # Update execution steps
                if state.get("steps"):
                    st.session_state.execution_steps = state["steps"]
                
                # Run decide
                state = streamlit_decide(state)
                
                # If waiting for continue, return early
                if st.session_state.waiting_for_continue:
                    return state
                
                # Check router decision after decide
                router_decision = planner_router(state)
                if router_decision == "action":
                    # End of conversation
                    break
                elif router_decision == "input":
                    # Loop back to planner - continue the loop
                    continue
            
            elif router_decision == "input":
                # Run input node
                state = streamlit_input_node(state)
                
                # If waiting for input, return early
                if st.session_state.waiting_for_input:
                    return state
                
                # After input, continue loop to go back to planner
                continue
            
            # If we reach here, we're done
            break
        
        return state
        
    except Exception as e:
        st.error(f"Error executing agent: {str(e)}")
        import traceback
        with st.expander("Error Details"):
            st.code(traceback.format_exc())
        return state


# Custom CSS for better UI/UX
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .employee-selector {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    /* Remove white backgrounds and borders from chat messages */
    .stChatMessage {
        background-color: transparent !important;
        padding: 0.5rem 0 !important;
    }
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main UI
st.markdown('<div class="main-header"><h1>🤖 Organizational Agent Chat</h1><p>Intelligent HR Management Assistant</p></div>', unsafe_allow_html=True)

# Employee Selection Dropdown at the top
try:
    employee_names = get_all_names()
    if not employee_names:
        st.warning("⚠️ No employees found in the database. Please check your Google Sheet connection.")
        employee_names = []
except Exception as e:
    st.error(f"Error loading employee names: {str(e)}")
    employee_names = []

# Employee selection dropdown with improved UI
st.markdown('<div class="employee-selector">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    # Prepare options with empty string as first option
    dropdown_options = [""] + employee_names if employee_names else [""]
    
    # Calculate index based on current selection
    if st.session_state.selected_employee and st.session_state.selected_employee in employee_names:
        dropdown_index = employee_names.index(st.session_state.selected_employee) + 1
    else:
        dropdown_index = 0
    
    selected_employee = st.selectbox(
        "👤 **Select Your Name:**",
        options=dropdown_options,
        index=dropdown_index,
        key="employee_dropdown",
        help="Select your name from the dropdown to start chatting with the agent"
    )
    
    if selected_employee:
        st.session_state.selected_employee = selected_employee
        # Update current state with selected employee
        if st.session_state.current_state:
            st.session_state.current_state["employee_name"] = selected_employee
    else:
        st.session_state.selected_employee = None

with col2:
    if st.session_state.selected_employee:
        st.success(f"✅ **{st.session_state.selected_employee}**")
    else:
        st.warning("⚠️ Select Employee")

with col3:
    if st.session_state.selected_employee:
        st.metric("Status", "Ready")
    else:
        st.metric("Status", "Waiting")
        
st.markdown('</div>', unsafe_allow_html=True)

# Removed the expander - steps now show in chat

# Sidebar with improved UI
with st.sidebar:
    st.markdown("### 📊 Agent Status")
    st.markdown("---")
    
    # Show current agent status with better visual
    status_color = {
        "Ready": "🟢",
        "🧠 Planning...": "🔵",
        "💭 Reasoning...": "🟣",
        "⚙️ Executing...": "🟠",
        "🤔 Deciding...": "🟡",
        "🤔 Thinking...": "🟡"
    }
    status_icon = status_color.get(st.session_state.agent_status, "⚪")
    st.markdown(f"**Status:** {status_icon} {st.session_state.agent_status}")
    
    st.markdown("---")
    
    if st.session_state.selected_employee:
        st.markdown(f"**✅ Active User:**")
        st.success(f"{st.session_state.selected_employee}")
    elif st.session_state.current_state.get("employee_name"):
        st.markdown(f"**✅ Active User:**")
        st.success(f"{st.session_state.current_state['employee_name']}")
    else:
        st.info("👤 No active user")
    
    if st.button("🔄 Reset Chat", type="secondary"):
        st.session_state.current_state = {
            "user_query": "",
            "task": "",
            "employee_name": "",
            "chat_history": [],
            "steps": [],
            "needs_input": False,
            "task_type": "",
            "action_required": {}
        }
        st.session_state.chat_messages = []
        st.session_state.waiting_for_input = False
        st.session_state.waiting_for_continue = False
        st.session_state.input_type = None
        st.session_state.execution_steps = []
        st.session_state.pending_user_input = None
        st.session_state.pending_continue_decision = None
        st.session_state.last_displayed_answer = None
        st.session_state.selected_employee = None
        st.session_state.agent_status = "Ready"
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 Recent Steps")
    if st.session_state.execution_steps:
        # Show last 5 steps in sidebar
        with st.container():
            for step in st.session_state.execution_steps[-5:]:
                # Compact display for sidebar
                if "🧠" in step or "💭" in step or "⚙️" in step or "🤔" in step:
                    st.caption(step)
                elif "✅" in step:
                    st.caption(f"✅ {step.split('✅')[-1] if '✅' in step else step}")
                elif "❌" in step:
                    st.caption(f"❌ {step.split('❌')[-1] if '❌' in step else step}")
                else:
                    st.caption(step)
    else:
        st.caption("No steps executed yet")

# Main chat interface
st.markdown("### 💬 Chat with HR Agent")
st.markdown("---")

# Show persistent status container if we have status messages from previous query
if st.session_state.get("status_messages"):
    with st.status("✅ Last Query Processing Steps", expanded=True):
        for icon, msg in st.session_state.status_messages:
            st.write(f"{icon} {msg}")

# Display chat history - simple formatting without white bars
# Skip system messages here since they're displayed via pending_messages
for message in st.session_state.chat_messages:
    role = message.get("role", "assistant")
    content = message.get("content", "")
    
    # Skip system messages - they're handled by pending_messages
    if role == "system":
        continue
    
    # Regular user/assistant messages
    with st.chat_message(role):
        st.write(content)

# Handle waiting for input
if st.session_state.waiting_for_input:
    if st.session_state.input_type == "name":
        st.info("❓ Agent: Please provide your name")
    elif st.session_state.input_type == "query":
        st.info("❓ Agent: Please provide your query for this time")
    
    # Don't show input if employee is already selected (shouldn't happen, but safety check)
    if st.session_state.selected_employee and st.session_state.input_type == "name":
        st.session_state.pending_user_input = st.session_state.selected_employee
        st.session_state.waiting_for_input = False
        st.rerun()
    
    user_input = st.text_input("Your response:", key="waiting_input", label_visibility="collapsed")
    
    if st.button("Submit", key="submit_input"):
        if user_input:
            st.session_state.pending_user_input = user_input
            
            # Continue agent execution
            state = st.session_state.current_state.copy()
            state = execute_agent(state)
            st.session_state.current_state = state
            
            # Display answer if available
            if state.get("last_answer"):
                add_assistant_message(state["last_answer"])
            
            # Update execution steps
            if state.get("steps"):
                st.session_state.execution_steps = state["steps"]
            
            st.rerun()

# Handle waiting for continue decision
elif st.session_state.waiting_for_continue:
    with st.chat_message("assistant"):
        st.info("❓ **Do you want to continue with another query?**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✅ Yes, Continue", key="continue_yes", type="primary", use_container_width=True):
            # User wants to continue - reset the continue state and allow new query
            st.session_state.pending_continue_decision = "yes"
            st.session_state.waiting_for_continue = False
            
            # Process the continue decision through decide function
            state = st.session_state.current_state.copy()
            state = streamlit_decide(state)
            st.session_state.current_state = state
            
            # Reset state for new query - clear old query data but keep employee
            st.session_state.current_state["user_query"] = ""
            st.session_state.current_state["needs_input"] = False  # Ready for new input
            st.session_state.current_state["task"] = ""
            st.session_state.current_state["task_type"] = ""
            st.session_state.current_state["action_required"] = {}
            st.session_state.current_state["last_answer"] = ""
            
            # Clear status messages for new query
            st.session_state.status_messages = []
            st.session_state.pending_messages = []
            st.session_state.status_container = None
            
            # Add system message to chat
            with st.chat_message("assistant"):
                st.caption("✅ Ready for your next query!")
            
            st.rerun()
    
    with col2:
        if st.button("❌ No, End Chat", key="continue_no", use_container_width=True):
            # User wants to end chat
            st.session_state.pending_continue_decision = "no"
            st.session_state.waiting_for_continue = False
            
            # Update the state to reflect the end decision
            state = st.session_state.current_state.copy()
            state["needs_input"] = False
            
            # Process the end decision through decide function
            state = streamlit_decide(state)
            st.session_state.current_state = state
            
            with st.chat_message("assistant"):
                st.success("✅ **Chat ended. Thank you!**")
            st.rerun()

# Main input area
else:
    # Only allow chat if employee is selected
    if not st.session_state.selected_employee:
        st.warning("⚠️ **Please select an employee from the dropdown above to start chatting.**")
        user_query = None
    else:
        user_query = st.chat_input(f"💬 Ask {st.session_state.selected_employee} anything...")
    
    if user_query and st.session_state.selected_employee:
        # Add user message to chat
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
        
        # Update state with user query and selected employee
        state = st.session_state.current_state.copy()
        state["user_query"] = user_query
        state["needs_input"] = False
        state["employee_name"] = st.session_state.selected_employee
        st.session_state.current_state = state
        
        # Clear pending messages before execution
        st.session_state.pending_messages = []
        st.session_state.display_mode = True
        
        # Clean up old system messages from chat_messages to prevent duplicates
        st.session_state.chat_messages = [
            msg for msg in st.session_state.chat_messages 
            if msg.get("role") != "system"
        ]
        
        # Create a persistent status container for real-time updates
        # Store status messages in session state to persist across reruns
        if "status_messages" not in st.session_state:
            st.session_state.status_messages = []
        
        # Clear status messages for new query (will be repopulated during execution)
        st.session_state.status_messages = []
        st.session_state.status_container = True  # Flag to indicate we're in status mode
        
        # Run the agent with real-time status display
        with st.status("🤔 Agent is processing...", expanded=True) as status:
            st.session_state.agent_status = "🤔 Thinking..."
            
            # Display messages as they're created during execution
            state = execute_agent(state)
            
            # Collect all messages for persistence
            for icon, msg in st.session_state.pending_messages:
                st.session_state.status_messages.append((icon, msg))
            
            # Display all collected messages in status
            for icon, msg in st.session_state.status_messages:
                st.write(f"{icon} {msg}")
            
            st.session_state.current_state = state
            st.session_state.agent_status = "Ready"
            # Keep status visible and expanded, just update the label
            status.update(label="✅ Processing complete", state="complete")
        
        # Status container will remain visible after this block
        # status_messages are stored in session state for persistence
        
        # Now display all messages in chat format for persistence
        for icon, msg in st.session_state.pending_messages:
            with st.chat_message("assistant"):
                st.caption(f"{icon} {msg}")
        
        # Clear pending messages after display
        st.session_state.pending_messages = []
        st.session_state.display_mode = False
        
        # Display answer if available with better formatting
        if state.get("last_answer"):
            add_assistant_message(state["last_answer"])
            with st.chat_message("assistant"):
                # Format the answer nicely
                answer = state["last_answer"]
                if answer.startswith("Reason:"):
                    st.info(f"**{answer}**")
                else:
                    st.markdown(f"**{answer}**")
        
        # Update execution steps
        if state.get("steps"):
            st.session_state.execution_steps = state["steps"]
        
        # Check if we need to wait for input or continue
        if not st.session_state.waiting_for_input and not st.session_state.waiting_for_continue:
            # Check if task was completed
            router_decision = planner_router(state)
            if router_decision == "action" and not state.get("needs_input"):
                completion_msg = "✅ Task completed successfully!"
                add_system_message(completion_msg, "✅")
                with st.chat_message("assistant"):
                    st.caption(f"✅ {completion_msg}")
        else:
            st.rerun()

# Debug info (collapsible) - moved to sidebar
with st.sidebar:
    st.markdown("---")
    with st.expander("🔍 Debug Info"):
        st.json(st.session_state.current_state)
