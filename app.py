import streamlit as st
from database import init_db, execute_query, DB_SCHEMA
from agent import SQLReflectionAgent

st.set_page_config(page_title="Module 2: Grounded SQL Reflection Agent", page_icon="🔍", layout="wide")

st.title("🔍 Module 2: Grounded SQL Reflection Agent")
st.markdown("Demonstrates **Grounded Reflection** with execution feedback and **External Human Input**.")

if "db_conn" not in st.session_state:
    st.session_state.db_conn = init_db()

conn = st.session_state.db_conn

# Initialize Session State Variables
defaults = {
    "current_sql": "",
    "user_query": "Find total spending for each customer in the USA with completed orders over $100 total.",
    "execution_result": None,
    "critique": ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

with st.sidebar:
    st.header("🗄️ Database Schema")
    st.code(DB_SCHEMA, language="sql")

# Natural Language Request Input
user_query = st.text_input("Enter Natural Language Request:", value=st.session_state.user_query)

col_gen, col_reset = st.columns([2, 1])
with col_gen:
    if st.button("1️⃣ Generate Initial SQL Query", type="primary"):
        agent = SQLReflectionAgent()
        st.session_state.user_query = user_query
        st.session_state.current_sql = agent.generate_sql(user_query)
        st.session_state.execution_result = execute_query(conn, st.session_state.current_sql)
        st.session_state.critique = agent.reflect_on_execution(
            user_query, st.session_state.current_sql, st.session_state.execution_result
        )

# Display Current Query & Database Execution State
if st.session_state.current_sql:
    st.divider()
    res_col1, res_col2 = st.columns([1, 1])

    with res_col1:
        st.subheader("📄 Current SQL Draft")
        st.code(st.session_state.current_sql, language="sql")

        exec_res = st.session_state.execution_result
        if exec_res["success"]:
            if len(exec_res["data"]) == 0:
                st.warning("⚠️ Query Executed Successfully, but returned 0 rows.")
            else:
                st.success(f"✅ Execution Successful! ({len(exec_res['data'])} rows returned)")
                st.dataframe(exec_res["data"])
        else:
            st.error(f"❌ Runtime Error: {exec_res['error']}")

    with res_col2:
        st.subheader("🤖 Automated Reflection Critique")
        st.info(st.session_state.critique)

    # --- EXTERNAL INPUT / REFLECTION CONTROL SECTION ---
    st.divider()
    st.subheader("🛠️ External Input & Manual Refinement")
    st.caption("Provide human feedback or instructions to modify the query based on real results.")

    with st.form("external_feedback_form"):
        human_input = st.text_input(
            "Enter External Instructions / Feedback:",
            placeholder="e.g., The status column requires uppercase 'COMPLETED' instead of lowercase 'completed'."
        )
        apply_refinement = st.form_submit_button("2️⃣ Apply Reflection & Refine SQL", type="primary")

    if apply_refinement:
        agent = SQLReflectionAgent()
        with st.spinner("Refining SQL using automated critique and external input..."):
            # Refine SQL using feedback
            new_sql = agent.refine_sql(
                st.session_state.user_query,
                st.session_state.current_sql,
                st.session_state.critique,
                human_input
            )
            # Re-execute and reflect
            st.session_state.current_sql = new_sql
            st.session_state.execution_result = execute_query(conn, new_sql)
            st.session_state.critique = agent.reflect_on_execution(
                st.session_state.user_query, new_sql, st.session_state.execution_result
            )
            st.rerun()