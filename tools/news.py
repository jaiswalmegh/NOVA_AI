
import requests

from config.settings import NEWS_API_KEY


class NewsTool:

    VALID_CATEGORIES = {
        "business",
        "entertainment",
        "general",
        "health",
        "science",
        "sports",
        "technology"
    }

    VALID_LANGUAGES = {
        "ar", "de", "en", "es", "fr",
        "he", "it", "nl", "no", "pt",
        "ru", "sv", "ud", "zh"
    }

    def __init__(self):

        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        self.timeout = 15

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "NOVA-AI/2.0"
        })

    # =========================================
    # TOP HEADLINES
    # =========================================

    def get_top_headlines(
        self,
        country="in",
        category=None,
        page_size=10
    ):

        if not self.api_key:
            return self._error(
                "News API key is missing. Add NEWS_API_KEY to your .env file."
            )

        if not isinstance(country, str) or len(country.strip()) != 2:
            return self._error(
                "Please provide a valid two-letter country code."
            )

        if category is not None:

            if not isinstance(category, str):
                return self._error("Invalid news category.")

            category = category.strip().lower()

            if category not in self.VALID_CATEGORIES:
                return self._error("Unsupported news category.")

        page_size = self._validate_page_size(page_size)

        params = {
            "country": country.strip().lower(),
            "pageSize": page_size
        }

        if category:
            params["category"] = category

        return self._make_request(
            endpoint="top-headlines",
            params=params,
            success_message="Latest headlines retrieved successfully."
        )

    # =========================================
    # SEARCH NEWS
    # =========================================

    def search_news(
        self,
        query,
        page_size=10,
        language="en"
    ):

        if not isinstance(query, str) or not query.strip():
            return self._error(
                "Please provide a valid news search query."
            )

        if not self.api_key:
            return self._error(
                "News API key is missing. Add NEWS_API_KEY to your .env file."
            )

        if not isinstance(language, str):
            return self._error("Invalid news language.")

        language = language.strip().lower()

        if language not in self.VALID_LANGUAGES:
            return self._error(
                "Unsupported language code for news search."
            )

        page_size = self._validate_page_size(page_size)

        params = {
            "q": query.strip(),
            "language": language,
            "sortBy": "publishedAt",
            "pageSize": page_size
        }

        return self._make_request(
            endpoint="everything",
            params=params,
            success_message="News search completed successfully."
        )

    # =========================================
    # VALIDATE PAGE SIZE
    # =========================================

    def _validate_page_size(self, page_size):

        try:

            if isinstance(page_size, bool):
                return 10

            return max(1, min(int(page_size), 100))

        except (ValueError, TypeError):

            return 10

    # =========================================
    # API REQUEST HANDLER
    # =========================================

    def _make_request(
        self,
        endpoint,
        params,
        success_message
    ):

        try:

            request_params = {
                **params,
                "apiKey": self.api_key
            }

            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=request_params,
                timeout=self.timeout
            )

            if response.status_code == 401:
                return self._error("Invalid News API key.")

            if response.status_code == 429:
                return self._error(
                    "News API rate limit reached. Please try again later."
                )

            if response.status_code == 426:
                return self._error(
                    "This News API endpoint requires a different subscription plan."
                )

            response.raise_for_status()

            data = response.json()

            if data.get("status") != "ok":
                return self._error(
                    data.get("message", "News service returned an error.")
                )

            articles = self._format_articles(
                data.get("articles", [])
            )

            return {
                "success": True,
                "total_results": data.get("totalResults", 0),
                "articles": articles,
                "message": success_message
            }

        except requests.Timeout:

            return self._error(
                "News service request timed out."
            )

        except requests.ConnectionError:

            return self._error(
                "Unable to connect to the news service. Check your internet connection."
            )

        except requests.HTTPError as error:

            print(f"NOVA News HTTP Error: {error}")

            return self._error(
                "News service returned an HTTP error."
            )

        except requests.RequestException as error:

            print(f"NOVA News API Error: {error}")

            return self._error(
                "Unable to connect to the news service."
            )

        except (ValueError, TypeError) as error:

            print(f"NOVA News Processing Error: {error}")

            return self._error(
                "Unable to process news information."
            )

    # =========================================
    # FORMAT ARTICLES
    # =========================================

    def _format_articles(self, articles):

        formatted = []

        for article in articles:

            if not isinstance(article, dict):
                continue

            source = article.get("source") or {}

            if not isinstance(source, dict):
                source = {}

            formatted.append({

                "title": article.get("title"),

                "description": article.get("description"),

                "source": source.get("name"),

                "author": article.get("author"),

                "url": article.get("url"),

                "image": article.get("urlToImage"),

                "published_at": article.get("publishedAt")

            })

        return formatted

    # =========================================
    # COMMON ERROR RESPONSE
    # =========================================

    def _error(self, message):

        return {
            "success": False,
            "total_results": 0,
            "articles": [],
            "message": message
        }

    # =========================================
    # CLOSE SESSION
    # =========================================

    def close(self):

        self.session.close()
