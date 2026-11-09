
import re
from llm_config import fact_checker_llm


# ==========================================
# FACT CHECKER AGENT
# ==========================================

def fact_check_analysis(
    analysis: str,
    sources: list[dict]
) -> dict:

    print("\n[Fact Checker Agent] Reviewing research analysis...")

    # ======================================
    # 1. VALIDATE INPUTS
    # ======================================

    if not analysis or not analysis.strip():

        return {
            "status": "NEEDS_HUMAN_REVIEW",
            "feedback": (
                "Research analysis is empty. "
                "Automated fact checking cannot proceed."
            )
        }

    if not sources:

        return {
            "status": "REVISION_REQUIRED",
            "feedback": "No readable research sources are available."
        }

    # ======================================
    # 2. VALIDATE SOURCE QUALITY
    # ======================================

    usable_sources = [
        source
        for source in sources
        if (
            isinstance(source, dict)
            and len(source.get("content", "").strip()) >= 1000
        )
    ]

    if not usable_sources:

        return {
            "status": "REVISION_REQUIRED",
            "feedback": (
                "Available sources do not contain enough readable "
                "content for a reliable source-grounding review. "
                "Minimum required content is 1000 characters per source."
            )
        }

    print(
        f"[Fact Checker Agent] Valid sources: {len(usable_sources)}"
    )

    # ======================================
    # 3. PREPARE SOURCE EVIDENCE
    # ======================================

    source_material = []

    for index, source in enumerate(usable_sources, 1):

        source_material.append(f"""
SOURCE {index}

Title: {source.get('title', 'Untitled')}
URL: {source.get('url', 'URL unavailable')}

Content:
{source.get('content', '')[:3500]}
""")

    evidence = "\n".join(source_material)

    # ======================================
    # 4. PREPARE REVIEW PROMPT
    # ======================================

    prompt = f"""
You are an expert research source-grounding reviewer.

Your task is to evaluate whether the claims in the
research analysis are supported by the provided
extracted source material.

RESEARCH ANALYSIS:

{analysis[:8000]}

AVAILABLE SOURCE MATERIAL:

{evidence}

REVIEW CRITERIA:

1. Check whether important factual claims are supported.
2. Check whether source citations are used correctly.
3. Identify unsupported factual claims.
4. Identify misleading generalizations.
5. Check whether research limitations are disclosed.
6. Check whether the analysis accurately represents
   the provided source material.

IMPORTANT RULES:

- Use ONLY the provided source material.
- Do not invent facts or evidence.
- Do not use outside knowledge.
- Do not claim independent scientific verification.
- A single source is acceptable if the analysis
  clearly identifies itself as a single-source analysis.
- Do not reject an analysis only because it uses one source.
- If important claims are unsupported, request revision.
- If the evidence is insufficient to make a reliable
  judgment, request human review.

OUTPUT REQUIREMENTS:
Keep your review concise.
The feedback must not exceed 150 words.
Return only the requested status and feedback.
Return ONLY the following format:

STATUS: APPROVED

FEEDBACK:
Explain why the important claims are adequately supported.

OR

STATUS: REVISION_REQUIRED

FEEDBACK:
Identify specific unsupported claims or missing evidence.

OR

STATUS: NEEDS_HUMAN_REVIEW

FEEDBACK:
Explain why a human reviewer must inspect the analysis.
"""

    # ======================================
    # 5. CALL GROQ LLM
    # ======================================

    try:

        response = fact_checker_llm.invoke(prompt)

        print("\n[Fact Checker Agent] Raw Response Object:")
        print(repr(response))

        print("\n[Fact Checker Agent] Response Metadata:")
        print(response.response_metadata)

        response_content = response.content

        # Handle string response
        if isinstance(response_content, str):

            review_text = response_content.strip()

        # Handle structured or block-based response
        elif isinstance(response_content, list):

            text_parts = []

            for block in response_content:

                if isinstance(block, dict):

                    if block.get("type") == "text":
                        text_parts.append(
                            block.get("text", "")
                        )

                elif isinstance(block, str):

                    text_parts.append(block)

            review_text = "\n".join(text_parts).strip()

        else:

            review_text = str(response_content).strip()

    except Exception as error:

        print(
            f"\n[Fact Checker Agent] LLM Error: {error}"
        )

        return {
            "status": "NEEDS_HUMAN_REVIEW",
            "feedback": (
                "The Fact Checker encountered an LLM error. "
                f"Automated review could not be completed: {error}"
            )
        }

    # ======================================
    # 6. HANDLE EMPTY RESPONSE
    # ======================================

    print("\n[Fact Checker Agent] Response Content:")
    print(repr(review_text))

    if not review_text:

        print(
            "[Fact Checker Agent] ERROR: Empty LLM response."
        )

        return {
            "status": "NEEDS_HUMAN_REVIEW",
            "feedback": (
                "The Fact Checker LLM returned an empty response. "
                "Automated source-grounding review could not "
                "be completed. Manual review is required."
            )
        }

    # ======================================
    # 7. EXTRACT REVIEW STATUS
    # ======================================

    match = re.search(
        r"STATUS\s*:\s*(APPROVED|REVISION_REQUIRED|NEEDS_HUMAN_REVIEW)",
        review_text,
        re.IGNORECASE
    )

    if match:

        status = match.group(1).upper()

    else:

        status = "NEEDS_HUMAN_REVIEW"

        print(
            "[Fact Checker Agent] WARNING: "
            "Could not identify a valid review status."
        )

    # ======================================
    # 8. FINAL REVIEW RESULT
    # ======================================

    print(
        f"\n[Fact Checker Agent] Status: {status}"
    )

    return {
        "status": status,
        "feedback": review_text
    }
