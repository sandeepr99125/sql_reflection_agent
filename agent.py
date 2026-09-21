import os
from google import genai
from openai import OpenAI
from config import Config
from database import DB_SCHEMA

class SQLReflectionAgent:
    def __init__(self):
        Config.validate()
        
        # Primary: Gemini Client
        self.gemini_client = genai.Client(api_key=Config.GEMINI_API_KEY) if Config.GEMINI_API_KEY else None
        
        # Fallback: OpenRouter Client
        self.openrouter_client = None
        if Config.OPENROUTER_API_KEY:
            self.openrouter_client = OpenAI(
                base_url=Config.OPENROUTER_BASE_URL,
                api_key=Config.OPENROUTER_API_KEY
            )

    def _call_llm(self, prompt: str) -> str:
        """Calls Gemini first; falls back to OpenRouter on failure."""
        
        # 1. Primary Attempt (Gemini)
        if self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model=Config.PRIMARY_MODEL,
                    contents=prompt
                )
                return response.text.strip().replace("```sql", "").replace("```", "").strip()
            except Exception as e:
                print(f"[Gemini Error]: {e}")

        # 2. Fallback Attempt (OpenRouter)
        if self.openrouter_client:
            try:
                response = self.openrouter_client.chat.completions.create(
                    model=Config.OPENROUTER_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                output = response.choices[0].message.content
                return output.strip().replace("```sql", "").replace("```", "").strip()
            except Exception as e:
                print(f"[OpenRouter Error]: {e}")

        raise RuntimeError("Both primary (Gemini) and fallback (OpenRouter) models failed to respond. Check terminal logs for details.")

    def generate_sql(self, user_prompt: str) -> str:
        """Generates initial SQL draft."""
        prompt = f"""
        You are an expert SQL Developer. Write an SQLite query for this request:
        User Request: "{user_prompt}"

        Database Schema:
        {DB_SCHEMA}

        Note: String values in status are UPPERCASE ('COMPLETED', 'PENDING', 'REFUNDED').
        Return ONLY the raw SQL query without markdown or explanations.
        """
        return self._call_llm(prompt)

    def reflect_on_execution(self, user_prompt: str, current_sql: str, exec_result: dict) -> str:
        """Critiques SQL draft using database execution feedback."""
        if not exec_result["success"]:
            feedback_context = f"EXECUTION ERROR: {exec_result['error']}"
        elif len(exec_result["data"]) == 0:
            feedback_context = (
                "EXECUTION SUCCESSFUL, BUT RETURNED 0 ROWS.\n"
                "Warning: Check if string casing matched (e.g. 'completed' vs 'COMPLETED') or if conditions were too restrictive."
            )
        else:
            feedback_context = f"EXECUTION SUCCESS: Returned {len(exec_result['data'])} rows.\nResults: {exec_result['data']}"

        prompt = f"""
        You are a Senior Database Administrator. Critique this SQLite query.

        User Request: "{user_prompt}"
        Database Schema:
        {DB_SCHEMA}

        Generated Query:
        {current_sql}

        Execution Output:
        {feedback_context}

        Checklist:
        1. If 0 rows were returned, is there a case-sensitivity issue or wrong filter?
        2. Are joins, column names, or aggregations correct?

        If the query is 100% correct and returns valid records, reply with ONLY "VALID".
        Otherwise, explain why it failed and provide fix instructions.
        """
        return self._call_llm(prompt)

    def refine_sql(self, user_prompt: str, current_sql: str, critique: str, human_feedback: str = None) -> str:
        """Fixes SQL query using combined automated critique and external human feedback."""
        extra_feedback = f"\nExternal User Feedback: {human_feedback}" if human_feedback else ""
        
        prompt = f"""
        Fix the SQLite query based on the feedback provided.

        User Request: "{user_prompt}"
        Database Schema:
        {DB_SCHEMA}

        Current SQL Draft:
        {current_sql}

        Automated Critique:
        {critique}
        {extra_feedback}

        Return ONLY the corrected raw SQL statement.
        """
        return self._call_llm(prompt)