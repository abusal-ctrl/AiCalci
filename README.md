# 🧮 AI MathLab

An AI-powered mathematical computing web app built with **Flask + LangChain + LangGraph + SymPy**.

## Architecture

```
User Question
     ↓
LangGraph Workflow
     ↓
Analyzer → Router → Solver → Verifier → Explainer
     ↓
LangChain-style Tools
     ↓
SymPy / NumPy (deterministic math)
     ↓
Answer + Steps
```

## Features

- 🤖 Natural-language math solver ("Solve x² + 5x + 6 = 0")
- 🧮 Scientific calculator endpoint
- 📐 Algebra, calculus, statistics tools
- ✅ Verification layer
- 📝 Step-by-step explanations

## Setup

```bash
git clone <your-repo>
cd AI-MathLab
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # optional: add LLM API key
python app.py
```

Open http://localhost:5000

## Try these

- `Solve x squared plus 5x plus 6 equals zero`
- `What is 25 percent of 840`
- `Find the derivative of x cubed plus 4x`
- `Integrate x squared plus 1`

## Why LangChain + LangGraph?

- **LangGraph** = orchestration (state machine, node routing)
- **LangChain** = tool abstraction (SymPy wrappers callable by the workflow)
- **LLM** = only used for NL→intent translation (optional; regex fallback works offline)

This separation means the math is always correct (SymPy), and the AI layer only handles language understanding — a best practice for AI/ML engineering.