# Multi-Agent AI Research Assistant

A multi-agent research assistant built with **LangGraph**, **Groq**, and
**Streamlit**. It researches a user-provided topic, extracts readable
web content, generates a source-grounded analysis, checks the analysis
against retrieved sources, and pauses for human review before producing
the final report.

## Features

-   **Research planning:** The Planner Agent creates four research areas
    for the selected topic.
-   **Web research:** The Research Agent searches for relevant
    open-access research articles.
-   **Content extraction:** Trafilatura extracts readable content from
    accessible web pages.
-   **Source-grounded analysis:** The Analyst Agent prepares a
    structured preliminary analysis using the retrieved source material.
-   **Fact checking:** The Fact Checker reviews the analysis against the
    supplied sources and returns a review status and feedback.
-   **Analysis revision:** When required, the workflow can send the
    analysis back to the Analyst Agent with the Fact Checker's feedback,
    subject to the configured revision limit.
-   **Human-in-the-Loop:** LangGraph interrupts the workflow for a human
    decision. The reviewer can approve or reject the research and
    provide feedback.
-   **Report generation:** The Report Writer creates a Markdown report
    containing the research plan, analysis, review information, sources,
    inaccessible sources, and limitations.
-   **Streamlit interface:** Users can start research, review the
    analysis, submit a decision, and download the final Markdown report.

## Agent Workflow

``` text
User enters a research topic
          |
          v
     Planner Agent
          |
          v
    Research Agent
          |
          v
     Analyst Agent
          |
          v
   Fact Checker Agent
          |
          +---- REVISION_REQUIRED ----> Analyst Agent
          |
          +---- APPROVED / NEEDS_HUMAN_REVIEW
          |                  |
          v                  v
                 Human Review
                      |
               Approve / Reject
                      |
                      v
                Report Writer
                      |
                      v
                 Final Report
```

The workflow uses conditional routing. Analysis revisions are limited by
`MAX_ANALYSIS_REVISIONS`, and research attempts are controlled by
`MAX_RESEARCH_ATTEMPTS`, both configured in `integrated_graph.py`.

## Project Structure

``` text
Multi-Agent-Research-Assistant/
│
├── agents/
│   ├── analyst.py
│   └── fact_checker.py
│
├── tools/
│   ├── web_search.py
│   └── page_extractor.py
│
├── outputs/
│   ├── research_sources.json
│   └── final_research_report.md
│
├── integrated_graph.py
├── research_pipeline.py
├── llm_config.py
├── streamlit_app.py
├── requirements.txt
├── .env
└── README.md
```

Generated output files are created or updated when the research workflow
runs. Keep your `.env` file private and do not commit API keys to
version control.

## Technologies

-   Python
-   LangGraph
-   LangChain Groq integration
-   Groq API
-   DuckDuckGo Search (`ddgs`)
-   Trafilatura
-   Streamlit
-   python-dotenv

## Setup

### 1. Clone or download the project

Open the project folder in VS Code.

### 2. Create and activate a virtual environment (recommended)

On Windows PowerShell:

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the Python executable inside
`.venv` directly or follow your local PowerShell execution-policy
guidance.

### 3. Install dependencies

``` powershell
pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create a `.env` file in the project root:

``` env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own Groq API key. Do not share this
file or upload it to a public repository.

## Run the Streamlit App

From the project root, run:

``` powershell
streamlit run streamlit_app.py
```

Streamlit will provide a local URL, usually:

``` text
http://localhost:8501
```

### Using the application

1.  Enter a research topic.
2.  Select **Start Research**.
3.  Wait while the agents plan, search, analyze, and fact-check.
4.  Review the analysis and Fact Checker feedback when the Human Review
    screen appears.
5.  Enter optional feedback and select **Approve Research** or **Reject
    Research**.
6.  View the generated report and use the download button to save it as
    a Markdown file.

## Run from the Terminal

The graph can also be run without the Streamlit interface:

``` powershell
python integrated_graph.py
```

This mode uses terminal input for the human review decision.

## Configuration

The following limits are configured near the top of
`integrated_graph.py`:

``` python
MAX_RESEARCH_ATTEMPTS = 2
MAX_ANALYSIS_REVISIONS = 2
```

Adjust these values if you want to change the maximum research attempts
or analysis revisions.

## Outputs

The workflow writes its research data and final report under `outputs/`:

-   `research_sources.json` --- retrieved research source data.
-   `final_research_report.md` --- generated research report in Markdown
    format.

The Streamlit interface also provides a report download button.

## Important Notes and Limitations

-   The system can only analyze content it successfully retrieves and
    extracts. Some websites may block automated access or provide
    incomplete page content.
-   The number of usable sources can vary between runs.
-   Findings should be interpreted in light of the sources actually
    retrieved. A single-source analysis is preliminary and should not be
    treated as a broad literature consensus.
-   The Fact Checker evaluates whether the analysis is grounded in the
    supplied sources; this is not independent scientific verification.
-   Human review is included as a checkpoint before report generation.
-   The current graph uses LangGraph's in-memory `MemorySaver`
    checkpointer. Checkpoints are not persistent across application
    restarts.

## Security

-   Store API keys in `.env`.
-   Do not commit `.env`, virtual environments, or other secrets to a
    public repository.
-   Consider adding a `.gitignore` file containing at least:

``` gitignore
.env
.venv/
__pycache__/
*.py[cod]
```

## License

Add a license before distributing or publishing this project if you
intend to make its reuse terms explicit.
