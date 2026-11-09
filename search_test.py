
from tools.web_search import search_web


def main():

    query = "Recent advances in explainable AI in healthcare"

    try:

        results = search_web(
            query=query,
            max_results=5
        )

        print("\n========== WEB SEARCH RESULTS ==========\n")

        if not results:
            print("No search results found.")
            return

        for index, result in enumerate(results, 1):

            print(f"\nResult {index}")
            print("-" * 50)

            print("Title:", result["title"])
            print("URL:", result["url"])
            print("Snippet:", result["snippet"])

    except Exception as error:

        print("\nSearch Error:", error)


if __name__ == "__main__":
    main()
