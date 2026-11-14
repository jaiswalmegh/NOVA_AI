
import requests

from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse, parse_qs, unquote


class WebSearch:

    def __init__(self):

        self.base_url = "https://html.duckduckgo.com/html/"
        self.timeout = 15

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _clean_url(self, url):

        if not isinstance(url, str) or not url.strip():
            return None

        url = url.strip()

        try:

            parsed = urlparse(url)

            # Handle DuckDuckGo redirect URLs.
            if parsed.netloc.endswith("duckduckgo.com"):

                redirect = parse_qs(parsed.query).get("uddg")

                if redirect:
                    url = unquote(redirect[0])

            parsed = urlparse(url)

            if parsed.scheme not in ("http", "https"):
                return None

            if not parsed.netloc:
                return None

            return url

        except Exception:
            return None

    def search(self, query, max_results=5):

        if not isinstance(query, str) or not query.strip():

            return {
                "success": False,
                "query": "",
                "total_results": 0,
                "results": [],
                "message": "Please provide a search query."
            }

        try:

            max_results = int(max_results)

            max_results = max(
                1,
                min(max_results, 10)
            )

        except (TypeError, ValueError):

            max_results = 5

        query = query.strip()

        try:

            response = self.session.post(
                self.base_url,
                data={"q": query},
                timeout=self.timeout
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            search_results = soup.select(".result")

            results = []
            visited_urls = set()

            for item in search_results:

                title_element = item.select_one(
                    ".result__title a"
                )

                snippet_element = item.select_one(
                    ".result__snippet"
                )

                if not title_element:
                    continue

                title = title_element.get_text(
                    " ",
                    strip=True
                )

                raw_url = title_element.get("href", "")

                url = self._clean_url(raw_url)

                snippet = (
                    snippet_element.get_text(
                        " ",
                        strip=True
                    )
                    if snippet_element
                    else ""
                )

                if not title or not url:
                    continue

                if url in visited_urls:
                    continue

                visited_urls.add(url)

                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source": urlparse(url).netloc
                })

                if len(results) >= max_results:
                    break

            return {
                "success": bool(results),
                "query": query,
                "total_results": len(results),
                "results": results,
                "message": (
                    "Search completed successfully."
                    if results
                    else "No search results found."
                )
            }

        except requests.RequestException as error:

            print(f"NOVA Web Search Error: {error}")

            return {
                "success": False,
                "query": query,
                "total_results": 0,
                "results": [],
                "message": "Unable to connect to the search service."
            }

        except Exception as error:

            print(f"NOVA Search Processing Error: {error}")

            return {
                "success": False,
                "query": query,
                "total_results": 0,
                "results": [],
                "message": "An error occurred while processing search results."
            }

    def search_url(self, query):

        if not isinstance(query, str) or not query.strip():
            return None

        return (
            "https://duckduckgo.com/?q="
            + quote_plus(query.strip())
        )

    def close(self):

        self.session.close()
