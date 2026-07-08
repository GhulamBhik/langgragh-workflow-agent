# LangGraph Workflow Agent

A workflow-based AI assistant built using **LangGraph**, **FastAPI**, **Streamlit**, and **Groq**.

The application processes a user query through a structured workflow:

1. Classify the user's intent.
2. Route the request to the appropriate handler.
3. Generate a response.
4. Review the generated response.
5. Return the final response.

---

## Project Structure

```text
langgraph-workflow-agent/
├── .github/
│   └── workflows/
│       └── ci.yml
├── Execution_Video/
│   └── Execution_Video.mp4
├── screenshots/
│   ├── Answer.png
│   ├── Graph Flow.png
│   ├── Json_Answer.png
│   └── UserInterface.png
├── src/
│   ├── __pycache__/
│   ├── graph/
│   │   ├── __pycache__/
│   │   ├── build_graph.py
│   │   ├── nodes.py
│   │   ├── routers.py
│   │   └── state.py
│   ├── config.py
│   └── main.py
├── streamlit_app/
│   └── app.py
├── tests/
│   ├── data/
│   │   ├── sample_inputs/
│   │   │   └── prompts.json
│   │   └── sample_outputs/
│   │       └── results.json
│   └── test_basic.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Prerequisites

- Python 3.11 or later
- Groq API Key

Create a `.env` file inside the project and add your API key:

```env
GROQ_API_KEY=your_api_key_here
```

---

## Installation

### Clone the repository

```bash
git clone <repository-url>
cd langgraph-workflow-agent
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### macOS/Linux

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Backend (FastAPI)

Open a terminal.

Navigate to the project directory:

```bash
cd langgraph-workflow-agent
```

Go inside the `src` folder:

```bash
cd src
```

Run the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend will start at:

```
http://localhost:8000
```

Swagger API documentation:

```
http://localhost:8000/docs
```

---

# Running the Frontend (Streamlit)

Open a **new terminal**.

Navigate to the project root:

```bash
cd langgraph-workflow-agent
```

Run Streamlit:

```bash
streamlit run streamlit_app/app.py
```

The application will automatically open in your browser.

---

# Running Tests

From the project root:

```bash
python tests/test_basic.py
```

Test outputs will be saved in:

```text
tests/data/sample_outputs/
```

---

# Workflow

```text
                User Query
                    │
                    ▼
          Intent Classification
                    │
                    ▼
          Route to Appropriate Handler
                    │
                    ▼
          Generate Response
                    │
                    ▼
           Review Response
                    │
                    ▼
            Final Response
```


---

# Supported Routes

- `summary_handler`
- `code_handler`
- `general_handler`

---

