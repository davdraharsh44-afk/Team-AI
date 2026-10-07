from ddgs import DDGS

# =========================
# INTERNET SEARCH
# =========================

def search_internet(query):

    try:

        results = []

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                region="in-en",
                safesearch="off",
                timelimit="d",
                max_results=8
            )

            for result in search_results:

                results.append({
                    "title": result.get("title", ""),
                    "body": result.get("body", ""),
                    "href": result.get("href", "")
                })

        return results

    except Exception as e:

        print("Internet Search Error:", e)

        return []