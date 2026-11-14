
import webbrowser
from urllib.parse import urlparse


class BrowserController:

    def __init__(self):

        self.browser = webbrowser

        self.allowed_schemes = {
            "http",
            "https"
        }

    def validate_url(self, url):

        if not isinstance(url, str) or not url.strip():
            return None

        url = url.strip()

        if "://" not in url:
            url = "https://" + url

        try:

            parsed = urlparse(url)

            if parsed.scheme not in self.allowed_schemes:
                return None

            if not parsed.hostname:
                return None

            if any(char.isspace() for char in url):
                return None

            return url

        except ValueError:
            return None

    def open_url(self, url, new_tab=True):

        validated_url = self.validate_url(url)

        if not validated_url:
            return {
                "success": False,
                "message": "Invalid or unsupported website URL."
            }

        try:

            opened = self.browser.open(
                validated_url,
                new=2 if new_tab else 0
            )

            if opened:
                return {
                    "success": True,
                    "url": validated_url,
                    "message": "Website opened successfully."
                }

            return {
                "success": False,
                "message": "Could not open the website."
            }

        except Exception as error:

            print(f"Browser Error: {error}")

            return {
                "success": False,
                "message": "An error occurred while opening the website."
            }

    def search_google(self, query):

        if not isinstance(query, str) or not query.strip():
            return {
                "success": False,
                "message": "Please provide a search query."
            }

        from urllib.parse import quote_plus

        search_url = (
            "https://www.google.com/search?q="
            + quote_plus(query.strip())
        )

        return self.open_url(search_url)

    def search_youtube(self, query):

        if not isinstance(query, str) or not query.strip():
            return {
                "success": False,
                "message": "Please provide a search query."
            }

        from urllib.parse import quote_plus

        search_url = (
            "https://www.youtube.com/results?search_query="
            + quote_plus(query.strip())
        )

        return self.open_url(search_url)

    def open_homepage(self):

        return self.open_url("https://www.google.com")

