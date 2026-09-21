# 🔍 Module 2: Grounded SQL Reflection Agent

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sqlreflectionagentgit-fghghxggdm3nvmtye6j22h.streamlit.app/)

An implementation of the **Reflection Design Pattern** based on DeepLearning.AI's *Agentic AI* course taught by Andrew Ng.

This project demonstrates **Grounded Self-Reflection** by taking database execution feedback (e.g., SQLite runtime errors, case-mismatch, 0-row results) and feeding it back into the LLM self-correction loop along with optional human-in-the-loop input.

## 🌟 Key Features
- **Grounded Reflection Loop:** LLM generates SQL, executes it against an in-memory SQLite database, inspects real runtime feedback, and self-corrects.
- **Resilient Model Fallback:** Tries Gemini primary model first, with automatic fallback to OpenRouter free models on API outage or rate limit errors.
- **Human-in-the-Loop Integration:** Allows external user intervention to guide refinement.

## 🛠️ Tech Stack
- **Framework:** Python, Streamlit
- **LLM Providers:** Google Gemini (`google-genai`), OpenRouter (`openai`)
- **Database Engine:** SQLite3 (In-Memory)

## 🚀 Quickstart (Local Run)

1. **Clone Repository:**
   ```bash
   git clone [https://github.com/your-username/sql_reflection_agent.git](https://github.com/your-username/sql_reflection_agent.git)
   cd sql_reflection_agent