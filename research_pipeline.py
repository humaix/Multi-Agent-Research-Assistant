
import os
import json

from tools.web_search import search_web
from tools.page_extractor import extract_page


def run_research(
    query: str,
    max_search_results: int = 8,
    max_successful_sources: int = 3
):

    print("\n[Research Pipeline] Starting research...")

    # Step 1: Search the web
    search_results = search_web(
        query=query,
        max_results=max_search_results
    )

    sources = []
    failed_sources = []

    # Step 2: Try all search results until enough sources are extracted
    for index, result in enumerate(search_results, 1):

        if len(sources) >= max_successful_sources:
            break

        title = result.get("title", "")
        url = result.get("url", "")

        if not url:
            continue

        print(
            f"\n[Research Pipeline] Processing source {index}: {title}"
        )

        extracted = extract_page(
            url=url,
            max_chars=5000,
            min_chars=1000
        )

        if extracted["success"]:

            sources.append({
                "title": title,
                "url": url,
                "content": extracted["content"],
                "characters": extracted["characters"],
                "truncated": extracted["truncated"]
            })

            print("[Research Pipeline] Source extracted successfully!")

        else:

            failed_sources.append({
                "title": title,
                "url": url,
                "error": extracted["error"]
            })

            print("[Research Pipeline] Source skipped.")
            print("[Research Pipeline] Reason:", extracted["error"])

    # Step 3: Create output directory
    os.makedirs("outputs", exist_ok=True)

    # Step 4: Prepare structured research data
    research_data = {
        "query": query,
        "total_search_results": len(search_results),
        "successful_extractions": len(sources),
        "failed_extractions": len(failed_sources),
        "sources": sources,
        "failed_sources": failed_sources
    }

    # Step 5: Save JSON
    output_file = "outputs/research_sources.json"

    with open(output_file, "w", encoding="utf-8") as file:

        json.dump(
            research_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Step 6: Display summary
    print("\n========== RESEARCH PIPELINE COMPLETE ==========")

    print("Search results:", len(search_results))
    print("Successfully extracted:", len(sources))
    print("Failed extractions:", len(failed_sources))

    print("Saved to:", output_file)

    if not sources:
        print("\n[Warning] No readable sources were extracted.")

    return research_data


if __name__ == "__main__":

    topic = (
        "Explainable AI in healthcare open access "
        "research articles full text"
    )

    run_research(topic)
