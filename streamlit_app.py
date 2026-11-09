
import os
import uuid
import streamlit as st

from langgraph.types import Command
from integrated_graph import app


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Multi-Agent AI Research Assistant")
st.caption("Powered by LangGraph and Groq")

st.markdown(
    "Generate research reports using multiple AI agents, "
    "source-grounded analysis, fact checking, and human approval."
)


# ==========================================
# SESSION STATE
# ==========================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "result" not in st.session_state:
    st.session_state.result = None

if "interrupt_data" not in st.session_state:
    st.session_state.interrupt_data = None

if "completed" not in st.session_state:
    st.session_state.completed = False


# ==========================================
# GRAPH CONFIGURATION
# ==========================================

def get_config():
    return {
        "recursion_limit": 10,
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }


# ==========================================
# WORKFLOW EXECUTION
# ==========================================

def start_research(topic):

    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.result = None
    st.session_state.interrupt_data = None
    st.session_state.completed = False

    initial_state = {
        "topic": topic,
        "research_plan": [],
        "sources": [],
        "failed_sources": [],
        "research_attempts": 0,
        "new_sources_count": 0,
        "analysis": "",
        "revision_attempts": 0,
        "review_status": "",
        "review_feedback": "",
        "human_decision": "",
        "final_report": ""
    }

    return app.invoke(
        initial_state,
        config=get_config()
    )


# ==========================================
# RESUME AFTER HUMAN REVIEW
# ==========================================

def resume_research(decision, feedback):

    return app.invoke(
        Command(
            resume={
                "decision": decision,
                "feedback": feedback
            }
        ),
        config=get_config()
    )


# ==========================================
# HANDLE GRAPH RESULT
# ==========================================

def handle_result(result):

    st.session_state.result = result

    if "__interrupt__" in result:

        interrupt_data = result["__interrupt__"][0].value

        st.session_state.interrupt_data = interrupt_data
        st.session_state.completed = False

    else:

        st.session_state.interrupt_data = None
        st.session_state.completed = True


# ==========================================
# RESEARCH INPUT
# ==========================================

st.subheader("Start New Research")

topic = st.text_input(
    "Enter your research topic",
    placeholder="e.g. Explainable AI in Healthcare"
)

if st.button("🚀 Start Research", type="primary"):

    if not topic.strip():

        st.warning("Please enter a research topic.")

    else:

        try:
            with st.spinner(
                "AI agents are researching and analyzing your topic..."
            ):
                result = start_research(topic.strip())

                handle_result(result)

            st.rerun()

        except Exception as error:

            st.error(f"Workflow error: {error}")


# ==========================================
# HUMAN REVIEW
# ==========================================

if st.session_state.interrupt_data:

    data = st.session_state.interrupt_data

    st.divider()
    st.subheader("👤 Human Review Required")

    st.info(data["message"])

    st.markdown(f"**Research Topic:** {data['topic']}")

    st.markdown(
        f"**Fact Checker Status:** {data['fact_checker_status']}"
    )

    with st.expander("Fact Checker Feedback", expanded=True):

        st.write(data["fact_checker_feedback"])

    with st.expander("Research Analysis", expanded=True):

        st.markdown(data["analysis"])

    human_feedback = st.text_area(
        "Your feedback (optional)",
        placeholder="Enter your review comments..."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("✅ Approve Research", type="primary"):

            try:
                with st.spinner("Generating final research report..."):

                    result = resume_research(
                        "approve",
                        human_feedback
                    )

                    handle_result(result)

                st.rerun()

            except Exception as error:

                st.error(f"Resume error: {error}")

    with col2:

        if st.button("❌ Reject Research"):

            try:
                with st.spinner("Processing your decision..."):

                    result = resume_research(
                        "reject",
                        human_feedback
                    )

                    handle_result(result)

                st.rerun()

            except Exception as error:

                st.error(f"Resume error: {error}")


# ==========================================
# FINAL REPORT
# ==========================================

if st.session_state.completed:

    result = st.session_state.result

    st.divider()
    st.subheader("📄 Research Results")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Research Attempts",
        result["research_attempts"]
    )

    col2.metric(
        "Sources Retrieved",
        len(result["sources"])
    )

    col3.metric(
        "Analysis Revisions",
        result["revision_attempts"]
    )

    st.markdown(
        f"**Fact Checker:** {result['review_status']}"
    )

    st.markdown(
        f"**Human Decision:** {result['human_decision']}"
    )

    if result["human_decision"] == "approve":

        st.success("Research approved by human reviewer.")

    else:

        st.warning(
            "Research was rejected. Review the report carefully "
            "before using its findings."
        )

    report = result["final_report"]

    st.markdown("---")
    st.markdown(report)

    st.download_button(
        label="⬇️ Download Research Report",
        data=report,
        file_name="final_research_report.md",
        mime="text/markdown"
    )
