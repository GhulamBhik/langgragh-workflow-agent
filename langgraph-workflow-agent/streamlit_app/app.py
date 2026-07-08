import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/query")

st.set_page_config(
    page_title="LangGraph Workflow Agent",
    page_icon=":compass:",
    layout="wide",
)

# ------------------ CSS ------------------

st.markdown("""
<style>

.main{
    padding-top:2rem;
}

.block-container{
    padding-top:2rem;
    padding-bottom:3rem;
    max-width:1100px;
}

.big-title{
    font-size:36px;
    font-weight:700;
    color:#f5f5f7;
    letter-spacing:-0.5px;
}

@media (prefers-color-scheme: light) {
    .big-title{
        color:#000000;
    }
}

.subtitle{
    color:#8b8d98;
    font-size:15px;
    margin-bottom:28px;
}

.metric-card{
    background:#15171d;
    padding:18px;
    border-radius:12px;
    border:1px solid #262a34;
    text-align:center;
    transition:0.2s;
}

.metric-card:hover{
    border-color:#4f7cff;
}

.metric-label{
    font-size:11px;
    color:#8b8d98;
    text-transform:uppercase;
    letter-spacing:1px;
}

.metric-value{
    font-size:18px;
    font-weight:600;
    margin-top:8px;
    color:#f5f5f7;
}

.answer-box{
    background:#15171d;
    border-radius:14px;
    padding:24px;
    border-left:4px solid #4f7cff;
    border-top:1px solid #262a34;
    border-right:1px solid #262a34;
    border-bottom:1px solid #262a34;
    color:#e4e5ea;
    line-height:1.6;
}

.answer-title{
    color:#8b8d98;
    font-size:12px;
    margin-bottom:14px;
    text-transform:uppercase;
    letter-spacing:1px;
}

.tool-badge{
    display:inline-block;
    background:#1d2029;
    color:#e4e5ea;
    padding:5px 12px;
    border-radius:6px;
    margin-right:8px;
    margin-bottom:8px;
    font-size:12px;
    border:1px solid #333744;
}

.section-title{
    color:#f5f5f7;
    font-size:14px;
    font-weight:600;
    text-transform:uppercase;
    letter-spacing:1px;
    margin:28px 0 14px 0;
}

.graph-box{
    background:#15171d;
    border-radius:14px;
    padding:20px;
    border:1px solid #262a34;
}

.footer{
    text-align:center;
    color:#5a5c66;
    margin-top:40px;
    font-size:13px;
}

</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------

st.markdown(
    """
<div class='big-title'>LangGraph Workflow Agent</div>
<div class='subtitle'>
Query &rarr; Intent Classification &rarr; Routing &rarr; Generation &rarr; Review &rarr; Final Response
</div>
""",
    unsafe_allow_html=True,
)

# ------------------ SIDEBAR ------------------

with st.sidebar:

    st.subheader("Workflow")

    st.markdown("""
1. Classify Intent
2. Route Request
3. Generate Response
4. Review Quality
5. Final Answer
""")

    st.divider()

    st.caption("LangGraph Workflow Demo")

# ------------------ INPUT ------------------

query = st.text_area(
    "Enter your query",
    height=140,
    placeholder="Example: Compare Python and Java",
)

submit = st.button(
    "Run Workflow",
    use_container_width=True,
)


# ------------------ GRAPH RENDERING ------------------

def _edge_style(active: bool, revise: bool = False) -> str:
    if revise:
        return "stroke:#e0a740;stroke-width:3;filter:url(#glow-amber);" if active else "stroke:#333744;stroke-width:2;"
    if active:
        return "stroke:#4f7cff;stroke-width:3;filter:url(#glow-blue);"
    return "stroke:#333744;stroke-width:2;"


def _node_style(active: bool) -> str:
    if active:
        return "fill:#1b2436;stroke:#4f7cff;stroke-width:2;filter:url(#glow-blue);"
    return "fill:#1b1d24;stroke:#333744;stroke-width:1.5;"

def render_workflow_graph(result: dict) -> str:
    route = result.get("route", "")
    review = str(result.get("review", "")).lower()
    revision_count = result.get("revision_count", 0) or 0
    final_answer = result.get("final_answer", "")
    
    # Robust check: Active if review passed OR if we have a valid final answer generated
    passed = (review == "passed") or (bool(final_answer) and final_answer != "-")

    revised = revision_count >= 1

    is_summary = route == "summary_handler"
    is_code = route == "code_handler"
    is_general = route == "general_handler"

    marker_summary = "arrow-active" if is_summary else "arrow-idle"
    marker_code = "arrow-active" if is_code else "arrow-idle"
    marker_general = "arrow-active" if is_general else "arrow-idle"
    marker_final = "arrow-active" if passed else "arrow-idle"

    # Specific markers for revision loops so only the active revised path glows amber
    marker_revise_summary = "arrow-amber" if (revised and is_summary) else "arrow-idle"
    marker_revise_code = "arrow-amber" if (revised and is_code) else "arrow-idle"
    marker_revise_general = "arrow-amber" if (revised and is_general) else "arrow-idle"

    lines = []
    
    # SVG Container
    lines.append('<svg viewBox="0 0 1050 360" width="100%" height="360" xmlns="http://www.w3.org/2000/svg">')
    
    # Definitions (Markers & Global Filters to prevent clipping)
    lines.append('<defs>')
    lines.append('<marker id="arrow-active" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#4f7cff" /></marker>')
    lines.append('<marker id="arrow-idle" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#333744" /></marker>')
    lines.append('<marker id="arrow-amber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#e0a740" /></marker>')
    lines.append('<filter id="glow-blue" x="0" y="0" width="1050" height="360" filterUnits="userSpaceOnUse"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    lines.append('<filter id="glow-amber" x="0" y="0" width="1050" height="360" filterUnits="userSpaceOnUse"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    lines.append('</defs>')

    # ---- Edges ----
    
    # 1. Start -> Classifier
    lines.append(f'<path d="M 56 155 L 85 155.1" style="{_edge_style(True)}" marker-end="url(#arrow-active)" />')
    
    # Classifier -> Handlers
    lines.append(f'<path d="M 230 140 L 325 45" style="{_edge_style(is_summary)}" marker-end="url(#{marker_summary})" />')
    lines.append(f'<path d="M 230 155 L 325 155.1" style="{_edge_style(is_code)}" marker-end="url(#{marker_code})" />')
    lines.append(f'<path d="M 230 170 L 325 270" style="{_edge_style(is_general)}" marker-end="url(#{marker_general})" />')
    
    # Handlers -> Reviewer
    lines.append(f'<path d="M 500 45 L 575 140" style="{_edge_style(is_summary)}" marker-end="url(#{marker_summary})" />')
    lines.append(f'<path d="M 500 155 L 575 155.1" style="{_edge_style(is_code)}" marker-end="url(#{marker_code})" />')
    lines.append(f'<path d="M 500 270 L 575 170" style="{_edge_style(is_general)}" marker-end="url(#{marker_general})" />')
    
    # 2. Reviewer -> Final Response
    lines.append(f'<path d="M 720 155 L 795 155.1" style="{_edge_style(passed)}" marker-end="url(#{marker_final})" />')
    
    # 3. Final Response -> End Node
    lines.append(f'<path d="M 940 155 L 975 155.1" style="{_edge_style(passed)}" marker-end="url(#{marker_final})" />')

    # 4. Revision Loops (Perfected Bézier Arcs)
    lines.append(f'<path d="M 650 130 C 650 -20, 415 -20, 415 12" fill="none" style="{_edge_style(revised and is_summary, revise=True)}" marker-end="url(#{marker_revise_summary})" />')
    lines.append(f'<path d="M 600 130 C 600 70, 415 70, 415 127" fill="none" style="{_edge_style(revised and is_code, revise=True)}" marker-end="url(#{marker_revise_code})" />')
    lines.append(f'<path d="M 650 180 C 650 340, 415 340, 415 298" fill="none" style="{_edge_style(revised and is_general, revise=True)}" marker-end="url(#{marker_revise_general})" />')

    # ---- Nodes ----
    lines.append(f'<circle cx="40" cy="155" r="16" style="{_node_style(True)}" />')
    lines.append('<text x="40" y="159" text-anchor="middle" font-size="10" fill="#e4e5ea">Start</text>')
    
    lines.append(f'<rect x="90" y="130" width="140" height="50" rx="10" style="{_node_style(True)}" />')
    lines.append('<text x="160" y="160" text-anchor="middle" font-size="13" fill="#e4e5ea">Classifier</text>')
    
    lines.append(f'<rect x="330" y="15" width="170" height="50" rx="10" style="{_node_style(is_summary)}" />')
    lines.append('<text x="415" y="45" text-anchor="middle" font-size="12" fill="#e4e5ea">Summary Handler</text>')
    
    lines.append(f'<rect x="330" y="130" width="170" height="50" rx="10" style="{_node_style(is_code)}" />')
    lines.append('<text x="415" y="160" text-anchor="middle" font-size="12" fill="#e4e5ea">Code Handler</text>')
    
    lines.append(f'<rect x="330" y="245" width="170" height="50" rx="10" style="{_node_style(is_general)}" />')
    lines.append('<text x="415" y="275" text-anchor="middle" font-size="12" fill="#e4e5ea">General Handler</text>')
    
    lines.append(f'<rect x="580" y="130" width="140" height="50" rx="10" style="{_node_style(True)}" />')
    lines.append('<text x="650" y="160" text-anchor="middle" font-size="13" fill="#e4e5ea">Reviewer</text>')
    
    lines.append(f'<rect x="800" y="130" width="140" height="50" rx="10" style="{_node_style(passed)}" />')
    lines.append('<text x="870" y="160" text-anchor="middle" font-size="12" fill="#e4e5ea">Final Response</text>')

    lines.append(f'<circle cx="995" cy="155" r="16" style="{_node_style(passed)}" />')
    lines.append('<text x="995" y="159" text-anchor="middle" font-size="10" fill="#e4e5ea">End</text>')

    lines.append('</svg>')

    return "".join(lines)
# ------------------ RUN ------------------

if submit:

    if not query.strip():
        st.warning("Please enter a query.")
        st.stop()

    with st.spinner("Running LangGraph workflow..."):

        try:

            response = requests.post(
                API_URL,
                json={"query": query},
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to FastAPI.\n\nMake sure your backend is running."
            )
            st.stop()

    if response.status_code != 200:

        st.error(response.text)
        st.stop()

    result = response.json()

    intent = result.get("intent", "-")
    route = result.get("route", "-")
    review = result.get("review", "-")
    tools = result.get("tools_used", [])
    answer = result.get("final_answer", "-")
    revision_count = result.get("revision_count", 0)

    review_label = "Passed" if str(review).lower() == "passed" else "Weak"

    # ---------------- Metrics ----------------

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
<div class='metric-card'>
<div class='metric-label'>Intent</div>
<div class='metric-value'>{intent}</div>
</div>
""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
<div class='metric-card'>
<div class='metric-label'>Route</div>
<div class='metric-value'>{route}</div>
</div>
""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
<div class='metric-card'>
<div class='metric-label'>Review</div>
<div class='metric-value'>{review_label}</div>
</div>
""", unsafe_allow_html=True)


    st.markdown("")

    tab1, tab2 = st.tabs(
        [
            "Final Answer",
            "Raw Response",
        ]
    )

    with tab1:

       

        st.markdown(
            f"""
<div class='answer-box'>
<div class='answer-title'>
Final Response
</div>

{answer}

</div>
""",
            unsafe_allow_html=True,
        )

    with tab2:

        st.json(result)

    # ---------------- Workflow Graph ----------------

    st.markdown("<div class='section-title'>Workflow Path</div>", unsafe_allow_html=True)

    graph_svg = render_workflow_graph(result)

    st.markdown(
        f"<div class='graph-box'>{graph_svg}</div>",
        unsafe_allow_html=True,
    )

# ---------------- Footer ----------------

st.markdown(
    """
<div class='footer'>
Built using Streamlit, FastAPI and LangGraph
</div>
""",
    unsafe_allow_html=True,
)