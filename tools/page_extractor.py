
# from urllib.parse import urlparse
# from trafilatura import fetch_url, extract


# def extract_page(url: str, max_chars: int = 12000) -> dict:

#     """
#     Download a webpage and extract its main text.

#     Returns:
#         URL, extracted content, status and error information.
#     """

#     # Validate URL
#     parsed_url = urlparse(url)

#     if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
#         raise ValueError("Invalid webpage URL.")

#     print(f"\n[Page Extractor] Fetching: {url}")

#     try:

#         # Download webpage HTML
#         downloaded = fetch_url(url)

#         if not downloaded:
#             return {
#                 "url": url,
#                 "success": False,
#                 "content": "",
#                 "error": "Page download failed or access was blocked."
#             }

#         # Extract main article content
#         content = extract(
#             downloaded,
#             url=url,
#             output_format="txt",
#             include_comments=False
#         )

#         if not content or not content.strip():
#             return {
#                 "url": url,
#                 "success": False,
#                 "content": "",
#                 "error": "No readable article content found."
#             }

#         # Limit extracted text
#         truncated = len(content) > max_chars
#         content = content[:max_chars]

#         print(
#             f"[Page Extractor] Extracted {len(content)} characters."
#         )

#         return {
#             "url": url,
#             "success": True,
#             "content": content,
#             "characters": len(content),
#             "truncated": truncated,
#             "error": None
#         }

#     except Exception as error:

#         return {
#             "url": url,
#             "success": False,
#             "content": "",
#             "error": str(error)
#         }



from urllib.parse import urlparse
from trafilatura import fetch_url, extract


def extract_page(
    url: str,
    max_chars: int = 12000,
    min_chars: int = 1000
) -> dict:

    """
    Download a webpage and extract its main text.

    Content shorter than min_chars is treated as
    insufficient for research analysis.
    """

    parsed_url = urlparse(url)

    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        raise ValueError("Invalid webpage URL.")

    print(f"\n[Page Extractor] Fetching: {url}")

    try:

        downloaded = fetch_url(url)

        if not downloaded:
            return {
                "url": url,
                "success": False,
                "content": "",
                "characters": 0,
                "truncated": False,
                "error": "Page download failed or access was blocked."
            }

        content = extract(
            downloaded,
            url=url,
            output_format="txt",
            include_comments=False
        )

        if not content or not content.strip():

            return {
                "url": url,
                "success": False,
                "content": "",
                "characters": 0,
                "truncated": False,
                "error": "No readable article content found."
            }

        content = content.strip()

        extracted_chars = len(content)

        # Quality gate: reject insufficient content
        if extracted_chars < min_chars:

            print(
                f"[Page Extractor] Insufficient content: "
                f"{extracted_chars} characters."
            )

            return {
                "url": url,
                "success": False,
                "content": content,
                "characters": extracted_chars,
                "truncated": False,
                "error": (
                    f"Insufficient content: {extracted_chars} characters. "
                    f"Minimum required: {min_chars}."
                )
            }

        truncated = extracted_chars > max_chars

        content = content[:max_chars]

        print(
            f"[Page Extractor] Extracted {len(content)} characters."
        )

        return {
            "url": url,
            "success": True,
            "content": content,
            "characters": extracted_chars,
            "truncated": truncated,
            "error": None
        }

    except Exception as error:

        return {
            "url": url,
            "success": False,
            "content": "",
            "characters": 0,
            "truncated": False,
            "error": str(error)
        }
