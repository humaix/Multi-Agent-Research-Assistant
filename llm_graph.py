
from typing import TypedDict
import re

from langgraph.graph import StateGraph, START, END
from llm_config import llm


# 1. Define shared state
class ResearchState(TypedDict):
    topic: str
    research_plan: list[str]
    final_summary: str


# 2. LLM-powered Planner Agent
def planner_node(state: ResearchState):

    print("\n[Planner Agent] Asking Groq to create research plan...")

    topic = state["topic"]

    prompt = f"""
    You are an expert research planner.

    Create exactly 4 important research areas
    for the following topic:

    {topic}

    Requirements:
    - Make each research area specific.
    - Cover different aspects of the topic.
    - Return only a numbered list.
    - Do not add an introduction or conclusion.
    """

    response = llm.invoke(prompt)

    # Convert LLM response into a Python list
    raw_output = response.content

    plan = []

    for line in raw_output.splitlines():

        item = re.sub(
            r"^\s*(?:[-*•]|\d+[.)])\s*",
            "",
            line
        ).strip()

        if item:
            plan.append(item)

    if not plan:
        raise ValueError("Planner did not generate a valid research plan.")

    print("\n[Planner Agent] Research plan generated!")

    return {
        "research_plan": plan
    }


# 3. LLM-powered Summary Agent
def summary_node(state: ResearchState):

    print("\n[Summary Agent] Generating research overview...")

    topic = state["topic"]

    research_areas = "\n".join(
        f"- {item}" for item in state["research_plan"]
    )

    prompt = f"""
    You are a professional research report writer.

    Topic:
    {topic}

    Research areas:
    {research_areas}

    Write a concise preliminary research overview.

    Requirements:
    - Explain the topic in simple technical language.
    - Discuss the importance of the research areas.
    - Organize the response with clear headings.
    - Do not invent references or claim that sources were verified.
    - Clearly state that this is a preliminary overview.
    - Keep the report within 400-500 words.
    - Use proper spacing and readable formatting.
    - Complete every section and table.
    - Never end the report in the middle of a sentence.
    """

    response = llm.invoke(prompt)

    print("\n[Summary Agent] Overview generated!")

    return {
        "final_summary": response.content
    }


# 4. Build LangGraph
workflow = StateGraph(ResearchState)

workflow.add_node("planner", planner_node)
workflow.add_node("summary", summary_node)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "summary")
workflow.add_edge("summary", END)


# 5. Compile graph
app = workflow.compile()


# 6. Initial state
initial_state = {
    "topic": "Artificial Intelligence in Healthcare",
    "research_plan": [],
    "final_summary": ""
}


# 7. Execute
result = app.invoke(initial_state)


# 8. Display results
print("\n========== AI RESEARCH PLAN ==========\n")

for index, item in enumerate(result["research_plan"], 1):
    print(f"{index}. {item}")

print("\n========== FINAL RESEARCH OVERVIEW ==========\n")

print(result["final_summary"])
