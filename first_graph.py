
# from typing import TypedDict
# from langgraph.graph import StateGraph, START, END


# # 1. Define shared state
# class ResearchState(TypedDict):
#     topic: str
#     research_plan: list[str]
#     research_focus: str
#     final_summary: str


# # 2. Planner node
# def planner_node(state: ResearchState):

#     print("\n[Planner Agent] Creating research plan...")

#     topic = state["topic"]

#     plan = [
#         f"Understand the fundamentals of {topic}",
#         f"Explore applications of {topic}",
#         f"Identify benefits and challenges of {topic}",
#         f"Analyze future trends in {topic}"
#     ]

#     return {
#         "research_plan": plan
#     }


# # 3. Healthcare research node
# def healthcare_research_node(state: ResearchState):

#     print("\n[Healthcare Research Agent] Healthcare route selected.")

#     return {
#         "research_focus": "Healthcare-focused research"
#     }


# # 4. General research node
# def general_research_node(state: ResearchState):

#     print("\n[General Research Agent] General route selected.")

#     return {
#         "research_focus": "General research"
#     }


# # 5. Routing function
# def route_research(state: ResearchState):

#     topic = state["topic"].lower()

#     healthcare_keywords = [
#         "healthcare",
#         "medical",
#         "hospital",
#         "patient"
#     ]

#     if any(word in topic for word in healthcare_keywords):
#         return "healthcare"

#     return "general"


# # 6. Summary node
# def summary_node(state: ResearchState):

#     print("\n[Summary Agent] Preparing research outline...")

#     summary = f"Research Topic: {state['topic']}\n"
#     summary += f"Research Focus: {state['research_focus']}\n"
#     summary += "\nResearch Areas:\n"

#     for item in state["research_plan"]:
#         summary += f"- {item}\n"

#     return {
#         "final_summary": summary
#     }


# # 7. Build graph
# workflow = StateGraph(ResearchState)

# workflow.add_node("planner", planner_node)
# workflow.add_node("healthcare_research", healthcare_research_node)
# workflow.add_node("general_research", general_research_node)
# workflow.add_node("summary", summary_node)


# # 8. Connect nodes
# workflow.add_edge(START, "planner")

# # Conditional routing
# workflow.add_conditional_edges(
#     "planner",
#     route_research,
#     {
#         "healthcare": "healthcare_research",
#         "general": "general_research"
#     }
# )

# workflow.add_edge("healthcare_research", "summary")
# workflow.add_edge("general_research", "summary")
# workflow.add_edge("summary", END)


# # 9. Compile graph
# app = workflow.compile()


# # 10. Execute graph
# initial_state = {
#     "topic": "Artificial Intelligence in Education",
#     "research_plan": [],
#     "research_focus": "",
#     "final_summary": ""
# }

# result = app.invoke(initial_state)


# # 11. Display result
# print("\n========== FINAL RESULT ==========")
# print(result["final_summary"])






from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# 1. Shared State
class ResearchState(TypedDict):
    topic: str
    research_plan: list[str]
    research_focus: str
    research_attempts: int
    quality_score: int
    research_findings: str
    review_status: str
    final_summary: str


# 2. Planner Node
def planner_node(state: ResearchState):

    print("\n[Planner Agent] Creating research plan...")

    topic = state["topic"]

    plan = [
        f"Understand the fundamentals of {topic}",
        f"Explore applications of {topic}",
        f"Identify benefits and challenges of {topic}",
        f"Analyze future trends in {topic}"
    ]

    return {"research_plan": plan}


# 3. Healthcare Research Node
def healthcare_research_node(state: ResearchState):

    print("\n[Healthcare Research Agent] Healthcare route selected.")

    return {
        "research_focus": "Healthcare-focused research"
    }


# 4. General Research Node
def general_research_node(state: ResearchState):

    print("\n[General Research Agent] General route selected.")

    return {
        "research_focus": "General research"
    }


# 5. Routing Function
def route_research(state: ResearchState):

    topic = state["topic"].lower()

    healthcare_keywords = [
        "healthcare",
        "medical",
        "hospital",
        "patient"
    ]

    if any(word in topic for word in healthcare_keywords):
        return "healthcare"

    return "general"


# 6. Research Node
def research_node(state: ResearchState):

    attempt = state["research_attempts"] + 1

    print(f"\n[Research Agent] Research attempt: {attempt}")

    # Simulated results for learning graph cycles.
    # We will replace this with actual LLM research later.
    if attempt == 1:
        quality = 55
        findings = "Initial research findings. Some information is missing."

    else:
        quality = 85
        findings = "Improved research findings with sufficient information."

    print(f"[Research Agent] Quality score: {quality}")

    return {
        "research_attempts": attempt,
        "quality_score": quality,
        "research_findings": findings
    }


# 7. Review Node
def review_node(state: ResearchState):

    print("\n[Fact Checker Agent] Reviewing research...")

    if state["quality_score"] >= 70:

        print("[Fact Checker] Research approved.")

        status = "approved"

    elif state["research_attempts"] >= 2:

        print("[Fact Checker] Maximum attempts reached.")

        status = "needs_human_review"

    else:

        print("[Fact Checker] Research incomplete. Requesting revision.")

        status = "revision_required"

    return {
        "review_status": status
    }


# 8. Conditional Routing After Review
def route_after_review(state: ResearchState):

    if state["review_status"] == "revision_required":
        return "retry"

    return "summary"


# 9. Summary Node
def summary_node(state: ResearchState):

    print("\n[Summary Agent] Preparing final outline...")

    summary = f"Research Topic: {state['topic']}\n"
    summary += f"Research Focus: {state['research_focus']}\n"
    summary += f"Research Attempts: {state['research_attempts']}\n"
    summary += f"Quality Score: {state['quality_score']}\n"
    summary += f"Review Status: {state['review_status']}\n"
    summary += f"\nFindings: {state['research_findings']}\n"
    summary += "\nResearch Areas:\n"

    for item in state["research_plan"]:
        summary += f"- {item}\n"

    return {
        "final_summary": summary
    }


# 10. Build Graph
workflow = StateGraph(ResearchState)

workflow.add_node("planner", planner_node)
workflow.add_node("healthcare_research", healthcare_research_node)
workflow.add_node("general_research", general_research_node)
workflow.add_node("research", research_node)
workflow.add_node("review", review_node)
workflow.add_node("summary", summary_node)


# 11. Connect Graph
workflow.add_edge(START, "planner")

workflow.add_conditional_edges(
    "planner",
    route_research,
    {
        "healthcare": "healthcare_research",
        "general": "general_research"
    }
)

workflow.add_edge("healthcare_research", "research")
workflow.add_edge("general_research", "research")

workflow.add_edge("research", "review")

# Feedback loop
workflow.add_conditional_edges(
    "review",
    route_after_review,
    {
        "retry": "research",
        "summary": "summary"
    }
)

workflow.add_edge("summary", END)


# 12. Compile
app = workflow.compile()


# 13. Initial State
initial_state = {
    "topic": "Artificial Intelligence in Healthcare",
    "research_plan": [],
    "research_focus": "",
    "research_attempts": 0,
    "quality_score": 0,
    "research_findings": "",
    "review_status": "",
    "final_summary": ""
}


# 14. Execute
result = app.invoke(initial_state)

print("\n========== FINAL RESULT ==========")
print(result["final_summary"])
