
from llm_config import llm


def analyze_sources(
    sources: list[dict],
    topic: str,
    previous_analysis: str = "",
    review_feedback: str = ""
) -> str:
    """
    Analyze research sources or revise an existing analysis.

    Revisions must use the same supplied source material.
    No unsupported facts or references should be introduced.
    """

    is_revision = bool(previous_analysis.strip())

    if is_revision:
        print("\n[Analyst Agent] Revising existing research analysis...")
    else:
        print("\n[Analyst Agent] Starting research analysis...")

    if not sources:
        raise ValueError("No research sources available for analysis.")

    # Prepare source information
    source_sections = []

    for index, source in enumerate(sources, 1):
        title = source.get("title", "Unknown Title")
        url = source.get("url", "")
        content = source.get("content", "")

        if not isinstance(content, str) or not content.strip():
            continue

        source_text = f"""
[Source {index}]

Title: {title}
URL: {url}

Extracted Content:
{content[:5000]}
"""
        source_sections.append(source_text)

    if not source_sections:
        raise ValueError("No readable source content found.")

    research_material = "\n".join(source_sections)

    print(
        f"[Analyst Agent] Using {len(source_sections)} sources..."
    )

    # Revision prompt
    if is_revision:
        task_instructions = f"""
You previously generated the following research analysis:

PREVIOUS ANALYSIS:

{previous_analysis[:10000]}

FACT CHECKER FEEDBACK:

{review_feedback[:4000]}

YOUR REVISION TASK:

Revise the previous analysis by addressing the Fact Checker's
specific feedback.

Important:
- Focus on the issues identified in the feedback.
- Use only the supplied research source material.
- Do not invent facts, statistics, limitations or references.
- If the source explicitly discusses study heterogeneity,
  meta-analysis limitations, or other limitations, accurately
  include those points.
- If the feedback requests information that is NOT supported
  by the supplied sources, clearly disclose that limitation
  instead of inventing an answer.
- Preserve claims that are already supported.
- Keep source citations accurate.
- Do not claim that the research has been independently verified.

Return the complete revised analysis, not just the changes.
"""
    else:
        task_instructions = """
Prepare a structured preliminary research analysis.

Include these sections:

1. Executive Summary
2. Main Research Findings
3. Important Concepts and Techniques
4. Applications in Healthcare
5. Challenges and Limitations
6. Research Gaps
7. Conclusion
8. Sources Used

If only one source is supplied, clearly mention that this is
a single-source preliminary analysis. Do not claim cross-source
agreement.
"""

    prompt = f"""
You are an academic research analyst.

RESEARCH TOPIC:
{topic}

RESEARCH MATERIAL:

{research_material}

IMPORTANT RULES:

1. Use only the supplied research material.
2. Do not invent facts, statistics or references.
3. Cite claims using labels such as [Source 1].
4. Do not cite information unsupported by the corresponding source.
5. Clearly identify missing information.
6. Distinguish source findings from your interpretation.
7. Do not pretend that one source represents the entire
   scientific literature.
8. Clearly disclose research limitations where the source
   material supports them.

{task_instructions}

Keep the report clear, technical and readable.
"""

    # Ask Groq to analyze or revise
    response = llm.invoke(prompt)

    analysis = response.content

    if not isinstance(analysis, str) or not analysis.strip():
        raise ValueError("Analyst returned an empty response.")

    if is_revision:
        print("[Analyst Agent] Revised analysis completed successfully!")
    else:
        print("[Analyst Agent] Analysis completed successfully!")

    return analysis
