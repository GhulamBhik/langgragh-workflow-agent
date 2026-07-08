from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import AgentState
from config import MODEL_NAME

# --------------------------------------------------------
# Base Model
# --------------------------------------------------------

model = ChatGroq(
    model=MODEL_NAME,
    temperature=0,
)


# --------------------------------------------------------
# Classifier Node
# --------------------------------------------------------

def classifier_node(state: AgentState) -> AgentState:
    print(f"\n[classifier_node] query: {state['query']}")

    prompt = SystemMessage(
        content="""
You are an intent classification system.

Classify the user's request into EXACTLY ONE of the following labels:

- summary_request
- factual_question
- code_help
- comparison_request
- opinion_request
- howto_request
- other

Rules:
- Return ONLY the label.
- No explanation.
- No punctuation.
- No extra words.

Examples:

User: Summarize this article.
summary_request

User: What is the capital of France?
factual_question

User: Write Python code to reverse a string.
code_help

User: Compare Python and Java.
comparison_request

User: Should students use AI?
opinion_request

User: How do I deploy FastAPI?
howto_request

User: Tell me something interesting.
other
"""
    )

    response = model.invoke(
        [
            prompt,
            HumanMessage(content=state["query"]),
        ]
    )

    intent = response.content.strip().lower()

    print(f"[classifier_node] intent: {intent}")

    return {
        "intent": intent,
        "revision_count": 0,
    }


# --------------------------------------------------------
# Shared Handler
# --------------------------------------------------------

def _run_handler(
    state: AgentState,
    system_text: str,
    route_name: str,
) -> AgentState:

    print(f"\n[{route_name}] answering query")

    feedback_note = ""

    if state.get("review_feedback") and state.get("revision_count", 0) > 0:
        feedback_note = f"""

IMPORTANT:

Your previous answer did not pass review.

Feedback:
{state['review_feedback']}

Revise the answer by fixing every issue mentioned above.

Do not mention this is a revision.

Return only the improved answer.
"""

    prompt = SystemMessage(
        content=system_text + feedback_note
    )

    messages = [
        prompt,
        HumanMessage(content=state["query"]),
    ]

    response = model.invoke(messages)

    return {
        "route": route_name,
        "answer": response.content.strip(),
        "messages": [response],
    }


# --------------------------------------------------------
# Summary Handler
# --------------------------------------------------------

def summary_handler(state: AgentState):
    return _run_handler(
        state,
        """
You are an expert summarization assistant.

Provide concise and accurate summaries.

Guidelines:
- Focus on the important information.
- Remove unnecessary details.
- Use bullet points when appropriate.
- Never invent facts.
- Keep responses concise unless the user requests more detail.
""",
        "summary_handler",
    )


# --------------------------------------------------------
# Code Handler
# --------------------------------------------------------

def code_handler(state: AgentState):
    return _run_handler(
        state,
        """
You are an expert Python software engineer.

Provide:

1. Correct code.
2. A brief explanation.
3. Time complexity when appropriate.
4. Space complexity when appropriate.

Guidelines:

- Follow Python best practices.
- Write clean, readable code.
- Use meaningful variable names.
- Add comments only when useful.
- Return code inside Markdown code blocks.
- Never execute code.
""",
        "code_handler",
    )


# --------------------------------------------------------
# General Handler
# --------------------------------------------------------

def general_handler(state: AgentState):
    return _run_handler(
        state,
        """
You are a knowledgeable AI assistant.

Provide accurate, complete and well-structured answers.

Guidelines:

- Answer directly.
- Use bullet points when helpful.
- Never invent information.
- If uncertain, clearly say so.
- Keep answers easy to read.
""",
        "general_handler",
    )


# --------------------------------------------------------
# Reviewer Node
# --------------------------------------------------------

def reviewer_node(state: AgentState):
    print(f"\n[reviewer_node] reviewing answer from: {state['route']}")

    prompt = SystemMessage(
        content="""
You are an expert response reviewer.

Evaluate the answer using these criteria:

- Accuracy
- Completeness
- Relevance
- Clarity
- Whether it fully answers the user's question
- Don't review simple Greetings
- Review only those that you think are unclear and unrelated and not clear.
Respond in EXACTLY this format:

STATUS: PASSED
FEEDBACK: Good answer.

OR

STATUS: WEAK
FEEDBACK: One short sentence describing what should be improved.

Return nothing else.
"""
    )

    content = f"""
Query:
{state['query']}

Answer:
{state['answer']}
"""

    response = model.invoke(
        [
            prompt,
            HumanMessage(content=content),
        ]
    )

    text = response.content.strip()

    status = "passed" if "PASSED" in text.upper() else "weak"

    feedback = ""

    if "FEEDBACK:" in text:
        feedback = text.split("FEEDBACK:")[-1].strip()

    print(f"[reviewer_node] status: {status}")
      
    return {
        "review": status,
        "review_feedback": feedback,
        "revision_count": state.get("revision_count", 0)
        + (1 if status == "weak" else 0),
    }


# --------------------------------------------------------
# Final Response Node
# --------------------------------------------------------

def final_response_node(state: AgentState):
    print("\n[final_response_node] finalizing answer")

    return {
        "final_answer": state["answer"],
    }