
import json
import os

from agents.analyst import analyze_sources


def main():

    print("\n[Main] Loading research data...")

    input_file = "outputs/research_sources.json"

    if not os.path.exists(input_file):
        raise FileNotFoundError(
            f"Research data not found: {input_file}"
        )

    # Load research sources
    with open(input_file, "r", encoding="utf-8") as file:
        research_data = json.load(file)

    sources = research_data.get("sources", [])

    print(f"[Main] Loaded {len(sources)} research sources.")

    if not sources:
        print("[Main] No extracted sources available.")
        return

    # Run Analyst Agent
    report = analyze_sources(sources)

    # Save analysis report
    output_file = "outputs/analysis_report.md"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(report)

    print("\n========== ANALYSIS REPORT ==========\n")
    print(report)

    print("\n[Main] Report saved to:", output_file)


if __name__ == "__main__":
    main()
