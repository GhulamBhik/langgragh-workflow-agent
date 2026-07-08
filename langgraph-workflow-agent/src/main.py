from fastapi import FastAPI
from pydantic import BaseModel

from graph.build_graph import app as workflow_app


app = FastAPI(
    title="LangGraph Workflow Agent"
)


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
def run_query(request: QueryRequest):

    result_state = workflow_app.invoke(
        {
            "query": request.query,
            "intent": "",
            "route": "",
            "answer": "",
            "review": "",
            "review_feedback": "",
            "revision_count": 0,
            "final_answer": "",
            "messages": [],
        }
    )

    print("\nFINAL STATE:")
    print(result_state)

    return {
        "intent": result_state.get("intent", ""),
        "route": result_state.get("route", ""),
        "review": result_state.get("review", ""),
        "final_answer": result_state.get("final_answer", ""),
        "revision_count": result_state.get("revision_count", 0),

    }


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "LangGraph Workflow Agent is running"
    }