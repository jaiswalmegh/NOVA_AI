
import wikipedia


class WikipediaTool:

    def __init__(self):

        self.language = "en"
        self.max_results = 5
        self.summary_sentences = 5

        self.set_language(self.language)

    # =========================================
    # LANGUAGE
    # =========================================

    def set_language(self, language):

        if not isinstance(language, str) or not language.strip():
            return False

        try:

            language = language.strip().lower()

            wikipedia.set_lang(language)

            self.language = language

            return True

        except Exception as error:

            print(f"Wikipedia Language Error: {error}")

            return False

    # =========================================
    # SEARCH ARTICLES
    # =========================================

    def search(self, query, results=None):

        if not isinstance(query, str) or not query.strip():

            return {
                "success": False,
                "query": query,
                "results": [],
                "message": "Please provide a valid search query."
            }

        try:

            if results is None:
                results = self.max_results

            if isinstance(results, bool):
                results = self.max_results

            results = int(results)

            results = max(1, min(results, 10))

        except (ValueError, TypeError):

            results = self.max_results

        try:

            pages = wikipedia.search(
                query.strip(),
                results=results
            )

            return {
                "success": bool(pages),
                "query": query.strip(),
                "results": pages,
                "message": (
                    "Wikipedia search completed successfully."
                    if pages
                    else "No matching Wikipedia pages found."
                )
            }

        except Exception as error:

            print(f"Wikipedia Search Error: {error}")

            return {
                "success": False,
                "query": query.strip(),
                "results": [],
                "message": "Unable to search Wikipedia right now."
            }

    # =========================================
    # GET ARTICLE SUMMARY
    # =========================================

    def get_summary(self, topic, sentences=None):

        if not isinstance(topic, str) or not topic.strip():

            return self._error(
                "Please provide a valid topic."
            )

        try:

            if sentences is None:
                sentences = self.summary_sentences

            if isinstance(sentences, bool):
                sentences = self.summary_sentences

            sentences = int(sentences)

            sentences = max(1, min(sentences, 15))

        except (ValueError, TypeError):

            sentences = self.summary_sentences

        try:

            page = wikipedia.page(
                topic.strip(),
                auto_suggest=True,
                redirect=True
            )

            summary = wikipedia.summary(
                page.title,
                sentences=sentences,
                auto_suggest=False,
                redirect=True
            )

            return {
                "success": True,
                "title": page.title,
                "summary": summary,
                "url": page.url,
                "language": self.language,
                "message": "Wikipedia information retrieved successfully."
            }

        except wikipedia.exceptions.DisambiguationError as error:

            return {
                "success": False,
                "title": None,
                "summary": None,
                "url": None,
                "suggestions": error.options[:10],
                "message": (
                    "Multiple topics found. "
                    "Please specify which topic you mean."
                )
            }

        except wikipedia.exceptions.PageError:

            return self._error(
                "No Wikipedia page found for this topic."
            )

        except Exception as error:

            print(f"Wikipedia Summary Error: {error}")

            return self._error(
                "Unable to retrieve Wikipedia information."
            )

    # =========================================
    # RANDOM ARTICLE
    # =========================================

    def get_random_article(self):

        try:

            title = wikipedia.random(pages=1)

            if not title:
                return self._error(
                    "No random article was found."
                )

            return self.get_summary(title)

        except Exception as error:

            print(f"Wikipedia Random Error: {error}")

            return self._error(
                "Unable to retrieve a random article."
            )

    # =========================================
    # COMMON ERROR RESPONSE
    # =========================================

    def _error(self, message):

        return {
            "success": False,
            "title": None,
            "summary": None,
            "url": None,
            "message": message
        }
