from langgraph.graph import StateGraph, START, END

from graph.state import AgentState

from graph.nodes import (
    classifier_node,
    summary_handler,
    code_handler,
    general_handler,
    reviewer_node,
    final_response_node,
)

from graph.routers import (
    route_by_intent,
    should_revise,
)


# Create graph
graph = StateGraph(AgentState)


# Add nodes
graph.add_node("classifier", classifier_node)

graph.add_node("summary_handler", summary_handler)
graph.add_node("code_handler", code_handler)
graph.add_node("general_handler", general_handler)

graph.add_node("reviewer", reviewer_node)
graph.add_node("final_response", final_response_node)


# Entry point
graph.add_edge(
    START,
    "classifier"
)


# Classifier routing
graph.add_conditional_edges(
    "classifier",
    route_by_intent,
    {
        "summary_handler": "summary_handler",
        "code_handler": "code_handler",
        "general_handler": "general_handler",
    },
)


# All handlers go to reviewer
graph.add_edge(
    "summary_handler",
    "reviewer"
)

graph.add_edge(
    "code_handler",
    "reviewer"
)

graph.add_edge(
    "general_handler",
    "reviewer"
)


# Reviewer routing
graph.add_conditional_edges("reviewer", should_revise, {
    "summary_handler": "summary_handler",
    "code_handler": "code_handler",
    "general_handler": "general_handler",
    "proceed": "final_response",
})


# Final node
graph.add_edge(
    "final_response",
    END
)


# Compile application
app = graph.compile()