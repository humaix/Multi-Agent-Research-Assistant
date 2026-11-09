
print("[DEBUG] page_extract_test.py started!")

from tools.page_extractor import extract_page


def main():

    print("[DEBUG] Main function started!")

    url = (
        "https://www.frontiersin.org/journals/"
        "artificial-intelligence/articles/"
        "10.3389/frai.2026.1749527/full"
    )

    print("\n[TEST] Starting webpage extraction...")

    result = extract_page(url)

    print("\n========== PAGE EXTRACTION RESULT ==========\n")

    print("URL:", result["url"])
    print("Success:", result["success"])

    if result["success"]:

        print("Characters:", result["characters"])
        print("Truncated:", result["truncated"])

        print("\n========== EXTRACTED CONTENT ==========\n")

        print(result["content"][:2500])

    else:

        print("Extraction Error:", result["error"])


if __name__ == "__main__":
    main()
