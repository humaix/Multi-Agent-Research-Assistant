
import os
import re

from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END

from llm_config import llm
from research_pipeline import run_research

from agents.analyst import analyze_sources
from agents.fact_checker import fact_check_analysis


# ==========================================
# CONFIGURATION
# ==========================================

MAX_RESEARCH_ATTEMPTS = 2
MAX_ANALYSIS_REVISIONS = 2

# ==========================================
# 1. SHARED STATE
# ==========================================

class ResearchState(TypedDict):

    topic: str
    research_plan: list[str]

    sources: list[dict]
    failed_sources: list[dict]

    research_attempts: int
    new_sources_count: int

    analysis: str
    revision_attempts: int
    review_status: str
    review_feedback: str
    human_decision: str
    final_report: str


# ==========================================
# 2. PLANNER AGENT
# ==========================================

def planner_node(state: ResearchState):

    print("\n[Planner Agent] Creating research plan...")

    topic = state["topic"]

    prompt = f"""
    You are an expert academic research planner.

    Create exactly 4 research areas for:

    {topic}

    Requirements:
    - Focus on important research directions.
    - Cover different aspects of the topic.
    - Return a numbered list only.
    """

    response = llm.invoke(prompt)

    plan = []

    for line in response.content.splitlines():

        item = re.sub(
            r"^\s*(?:[-*•]|\d+[.)])\s*",
            "",
            line
        ).strip()

        if item:
            plan.append(item)

    if not plan:

        raise ValueError(
            "Planner generated an empty research plan."
        )

    print(
        f"[Planner Agent] Generated {len(plan)} research areas."
    )

    return {
        "research_plan": plan
    }


# ==========================================
# 3. RESEARCH AGENT
# ==========================================

def researcher_node(state: ResearchState):

    attempt = state["research_attempts"] + 1

    print(f"\n[Research Agent] Starting attempt {attempt}...")

    topic = state["topic"]

    query = (
        f"{topic} open access full text "
        "research articles"
    )

    # Use reviewer feedback for another search attempt
    if attempt > 1:

        feedback = state["review_feedback"]

        # Remove status label
        feedback = re.sub(
            r"(?im)^STATUS\s*:.*$",
            "",
            feedback
        )

        # Remove feedback label
        feedback = re.sub(
            r"(?im)^FEEDBACK\s*:\s*",
            "",
            feedback
        )

        feedback = " ".join(feedback.split())

        query = (
            f"{topic} {feedback[:180]} "
            "open access full text research articles"
        )

    # Perform web research
    try:

        research_data = run_research(query)

    except Exception as error:

        print(
            f"[Research Agent] Search failed: {error}"
        )

        return {

            "research_attempts": attempt,

            "failed_sources": state["failed_sources"] + [{
                "title": "Research pipeline error",
                "url": "",
                "error": str(error)
            }],

            "new_sources_count": 0
        }

    # ======================================
    # MERGE SOURCES WITHOUT DUPLICATES
    # ======================================

    existing_sources = state["sources"]

    existing_urls = {
        source.get("url")
        for source in existing_sources
        if source.get("url")
    }

    new_sources = [

        source

        for source in research_data.get("sources", [])

        if (
            source.get("url")
            and source.get("url") not in existing_urls
        )

    ]

    all_sources = existing_sources + new_sources

    all_failed_sources = (
        state["failed_sources"]
        + research_data.get("failed_sources", [])
    )

    print(
        f"[Research Agent] Total usable sources: "
        f"{len(all_sources)}"
    )

    print(
        f"[Research Agent] New sources found: "
        f"{len(new_sources)}"
    )

    return {

        "research_attempts": attempt,

        "sources": all_sources,

        "failed_sources": all_failed_sources,

        "new_sources_count": len(new_sources)
    }


# ==========================================
# 4. ANALYST AGENT
# ==========================================

def analyst_node(state: ResearchState):

    sources = state["sources"]

    if not sources:
        analysis = (
            "Research analysis could not be generated "
            "because no readable source content was retrieved."
        )

        return {
            "analysis": analysis
        }

    # Check whether this is an initial analysis or a revision
    is_revision = (
        state["review_status"] == "REVISION_REQUIRED"
        and bool(state["analysis"].strip())
    )

    if is_revision:

        print(
            "\n[Analyst Agent] Revising analysis using "
            "Fact Checker feedback..."
        )

        revision_attempts = state["revision_attempts"] + 1

        analysis = analyze_sources(
            sources=sources,
            topic=state["topic"],
            previous_analysis=state["analysis"],
            review_feedback=state["review_feedback"]
        )

        return {
            "analysis": analysis,
            "revision_attempts": revision_attempts
        }

    print(
        "\n[Analyst Agent] Analyzing retrieved information..."
    )

    analysis = analyze_sources(
        sources=sources,
        topic=state["topic"]
    )

    return {
        "analysis": analysis
    }


# ==========================================
# 5. FACT CHECKER AGENT
# ==========================================

def fact_checker_node(state: ResearchState):

    print(
        "\n[Fact Checker Agent] Reviewing analysis..."
    )

    # if not state["sources"]:

    #     review = {

    #         "status": "REVISION_REQUIRED",

    #         "feedback": (
    #             "No readable research sources were retrieved."
    #         )

    #     }
    if not state["sources"]:

        review = {

            "status": "NEEDS_HUMAN_REVIEW",

            "feedback": (
                "No readable research sources were retrieved. "
                "The analysis cannot be fact-checked because "
                "no usable source content is available. "
                "Human review is required."
            )

        }

    else:

        review = fact_check_analysis(
            analysis=state["analysis"],
            sources=state["sources"]
        )

    status = review.get(
        "status",
        "NEEDS_HUMAN_REVIEW"
    )

    # Validate returned status
    allowed_statuses = {
        "APPROVED",
        "REVISION_REQUIRED",
        "NEEDS_HUMAN_REVIEW"
    }

    if status not in allowed_statuses:

        status = "NEEDS_HUMAN_REVIEW"

    # # Prevent unlimited retries
    # if (
    #     status == "REVISION_REQUIRED"
    #     and state["research_attempts"] >= MAX_RESEARCH_ATTEMPTS
    # ):

    #     status = "NEEDS_HUMAN_REVIEW"

    print(
        f"[Fact Checker Agent] Final status: {status}"
    )

    return {

        "review_status": status,

        "review_feedback": review["feedback"]
    }


# ==========================================
# 6. ROUTING AFTER RESEARCH
# ==========================================

def route_after_research(state: ResearchState):

    # Stop if maximum attempts reached
    # and no new sources were retrieved

    if (
        state["research_attempts"] >= MAX_RESEARCH_ATTEMPTS
        and state["new_sources_count"] == 0
    ):

        print(
            "\n[Workflow] No new sources found. "
            "Routing to Human Review."
        )

        return "human_review"

    print(
        "\n[Workflow] Sending research to Analyst Agent."
    )

    return "analyst"


# ==========================================
# 7. ROUTING AFTER FACT CHECKER
# ==========================================
def route_after_review(state: ResearchState):

    status = state["review_status"]

    if status == "REVISION_REQUIRED":

        if state["revision_attempts"] >= MAX_ANALYSIS_REVISIONS:

            print(
                "\n[Workflow] Maximum analysis revisions reached. "
                "Routing to Human Review."
            )

            return "human_review"

        print(
            "\n[Workflow] Analysis revision requested. "
            "Sending back to Analyst Agent."
        )

        return "revise"

    elif status == "NEEDS_HUMAN_REVIEW":

        print("\n[Workflow] Manual human review required.")

        return "human_review"

    # else:

    #     print(
    #         "\n[Workflow] Research approved. "
    #         "Moving to final report."
    #     )

    #     return "finish"

    else:

        print(
            "\n[Workflow] Automated review completed. "
            "Sending research for human approval."
        )

        return "human_review"


# ==========================================
# 8. HUMAN REVIEW NODE
# ==========================================

# def human_review_node(state: ResearchState):

#     print("\n[Human Review] Manual review is required.")

#     feedback = state["review_feedback"]

#     feedback += (
#         "\n\nHuman Review Required: "
#         "The automated workflow could not confidently "
#         "approve the research. A human reviewer should "
#         "inspect the available evidence and analysis "
#         "before accepting the findings."
#     )

#     return {
#         "review_status": "NEEDS_HUMAN_REVIEW",
#         "review_feedback": feedback
#     }

def human_review_node(state: ResearchState):

    print("\n[Human Review] Waiting for human approval...")

    human_response = interrupt({
        "message": "Please review the research before finalizing.",
        "topic": state["topic"],
        "analysis": state["analysis"],
        "fact_checker_status": state["review_status"],
        "fact_checker_feedback": state["review_feedback"]
    })

    decision = human_response.get("decision", "").lower()
    human_feedback = human_response.get("feedback", "")

    if decision == "approve":

        print("\n[Human Review] Research approved by human.")

        status = "APPROVED"

    else:

        print("\n[Human Review] Research rejected by human.")

        status = "NEEDS_HUMAN_REVIEW"

    feedback = (
        state["review_feedback"]
        + f"\n\nHuman Decision: {decision.upper()}"
        + f"\nHuman Feedback: {human_feedback}"
    )

    return {
        "review_status": status,
        "review_feedback": feedback,
        "human_decision": decision
    }

# ==========================================
# 9. REPORT WRITER
# ==========================================

def report_writer_node(state: ResearchState):

    print(
        "\n[Report Writer] Preparing final report..."
    )

    report = (
        f"# Research Report: {state['topic']}\n\n"
    )

    report += (
        f"**Review Status:** "
        f"{state['review_status']}\n\n"
    )

    report += (
        f"**Research Attempts:** "
        f"{state['research_attempts']}\n\n"
    )
    report += (
    f"**Analysis Revisions:** "
    f"{state['revision_attempts']}\n\n"
    )
    report += (
        f"**New Sources in Last Attempt:** "
        f"{state['new_sources_count']}\n\n"
    )

    # Research Plan
    report += "## Research Plan\n\n"

    for item in state["research_plan"]:

        report += f"- {item}\n"

    # Research Analysis
    report += "\n## Research Analysis\n\n"

    report += state["analysis"]

    # Fact Checker Review
    report += "\n\n## Fact Checker Review\n\n"

    report += state["review_feedback"]

    # Successful Sources
    report += "\n\n## Sources Used\n\n"

    for index, source in enumerate(
        state["sources"], 1
    ):

        report += (
            f"{index}. "
            f"[{source.get('title', 'Untitled')}]"
            f"({source.get('url', '')})\n"
        )

    if not state["sources"]:

        report += (
            "No readable sources were extracted.\n"
        )

    # Failed Sources
    report += "\n## Inaccessible Sources\n\n"

    if state["failed_sources"]:

        for index, source in enumerate(
            state["failed_sources"], 1
        ):

            report += (
                f"{index}. "
                f"{source.get('title', 'Unknown source')} "
                f"- {source.get('error', 'Unknown error')}\n"
            )

    else:

        report += "No failed sources recorded.\n"

    # Limitations
    report += "\n## Research Limitations\n\n"

    report += (
        f"- Successfully extracted sources: "
        f"{len(state['sources'])}\n"
        f"- Research attempts: "
        f"{state['research_attempts']}\n"
        "- Source-grounding review does not constitute "
        "independent scientific verification.\n"
        "- Findings are limited to the accessible "
        "source material retrieved by this system.\n"
    )

    if state["review_status"] == "NEEDS_HUMAN_REVIEW":

        report += (
            "\n**Human review required:** "
            "The system could not confidently approve "
            "the research analysis.\n"
        )

    print(
        "[Report Writer] Final report prepared."
    )

    return {
        "final_report": report
    }


# ==========================================
# 10. BUILD LANGGRAPH
# ==========================================

workflow = StateGraph(ResearchState)


# Register all nodes
workflow.add_node("planner", planner_node)

workflow.add_node("researcher", researcher_node)

workflow.add_node("analyst", analyst_node)

workflow.add_node("fact_checker", fact_checker_node)

workflow.add_node("human_review", human_review_node)

workflow.add_node("report_writer", report_writer_node)


# ==========================================
# 11. CONNECT GRAPH
# ==========================================

# Starting point
workflow.add_edge(
    START,
    "planner"
)


# Planner -> Researcher
workflow.add_edge(
    "planner",
    "researcher"
)


# Researcher -> Conditional routing
workflow.add_conditional_edges(

    "researcher",

    route_after_research,

    {
        "analyst": "analyst",

        "human_review": "human_review"
    }

)


# Analyst -> Fact Checker
workflow.add_edge(
    "analyst",
    "fact_checker"
)


# Fact Checker -> Conditional routing
workflow.add_conditional_edges(
    "fact_checker",
    route_after_review,
    {
        "revise": "analyst",
        "human_review": "human_review",
        # "finish": "report_writer"
    }
)


# Human Review -> Report Writer
workflow.add_edge(
    "human_review",
    "report_writer"
)


# Report Writer -> END
workflow.add_edge(
    "report_writer",
    END
)


# ==========================================
# 12. COMPILE GRAPH
# ==========================================

# Always compile AFTER registering all nodes and edges

memory = MemorySaver()

app = workflow.compile(
    checkpointer=memory
)


# 13 . main 

if __name__ == "__main__":

    initial_state = {
        "topic": "Explainable AI in Healthcare",
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

    config = {
        "recursion_limit": 10,
        "configurable": {
            "thread_id": "research-session-1"
        }
    }

    print("\n====================================")
    print("MULTI-AGENT AI RESEARCH ASSISTANT")
    print("====================================")

    # Start workflow
    result = app.invoke(initial_state, config=config)

    # Handle Human-in-the-Loop interruptions
    while "__interrupt__" in result:

        interrupt_data = result["__interrupt__"][0].value

        print("\n====================================")
        print("HUMAN REVIEW REQUIRED")
        print("====================================")

        print("\nTopic:", interrupt_data["topic"])

        print(
            "\nFact Checker Status:",
            interrupt_data["fact_checker_status"]
        )

        print("\nFact Checker Feedback:")
        print(interrupt_data["fact_checker_feedback"])

        print("\nResearch Analysis:")
        print(interrupt_data["analysis"])

        while True:

            decision = input(
                "\nEnter decision (approve/reject): "
            ).strip().lower()

            if decision in ["approve", "reject"]:
                break

            print("Please enter approve or reject.")

        human_feedback = input(
            "Enter your feedback (or press Enter to skip): "
        ).strip()

        # Resume workflow
        result = app.invoke(
            Command(
                resume={
                    "decision": decision,
                    "feedback": human_feedback
                }
            ),
            config=config
        )

    # Save final report
    os.makedirs("outputs", exist_ok=True)

    output_file = "outputs/final_research_report.md"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(result["final_report"])

    print("\n====================================")
    print("WORKFLOW COMPLETED")
    print("====================================")

    print("Research attempts:", result["research_attempts"])
    print("Total sources:", len(result["sources"]))
    print("Analysis revisions:", result["revision_attempts"])
    print("Fact Checker Status:", result["review_status"])
    print("Human Decision:", result["human_decision"])

    print("\nFinal report saved to:", output_file)
