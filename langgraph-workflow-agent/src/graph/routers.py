from graph.state import AgentState
from config import MAX_REVISIONS


def route_by_intent(state: AgentState) -> str:
    intent = state["intent"]
    if intent in ("summary_request", "factual_question"):
        return "summary_handler"
    elif intent == "code_help":
        return "code_handler"
    else:
        return "general_handler"


def should_use_tool(state: AgentState) -> str:
    messages = state.get("messages", [])
    if not messages:
        return "no_tool"
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "use_tool"
    return "no_tool"


def should_revise(state: AgentState) -> str:
    if state["review"] == "passed":
        return "proceed"
    if state["revision_count"] < MAX_REVISIONS:
        return state["route"]  # go back to whichever handler produced this answer
    return "proceed"