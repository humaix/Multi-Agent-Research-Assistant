
from ddgs import DDGS


def search_web(query: str, max_results: int = 5) -> list[dict]:

    """
    Search the web and return structured results.

    Args:
        query: Topic or question to search.
        max_results: Maximum number of search results.

    Returns:
        List containing title, url and snippet.
    """

    # Validate query
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results must be between 1 and 10.")

    print(f"\n[Web Search Tool] Searching: {query}")

    try:

        # Initialize DDGS
        search_client = DDGS(timeout=15)

        # Perform search
        raw_results = search_client.text(
            query=query.strip(),
            max_results=max_results
        )

        results = []

        # Structure search results
        for item in raw_results or []:

            result = {
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", "")
            }

            results.append(result)

        print(f"[Web Search Tool] Found {len(results)} results.")

        return results

    except Exception as error:

        raise RuntimeError(
            f"Web search failed: {error}"
        ) from error
