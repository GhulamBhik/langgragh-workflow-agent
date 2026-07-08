from typing_extensions import TypedDict
from typing import Optional


class AgentState(TypedDict):
    query: str
    intent: str
    route: str
    answer: str
    review: str
    review_feedback: Optional[str]
    revision_count: int
    final_answer: str