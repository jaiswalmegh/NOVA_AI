
from tools.tool_registry import ToolRegistry

from tools.calculator import Calculator
from tools.web_search import WebSearch
from tools.reminders import ReminderManager
from tools.weather import WeatherTool
from tools.wikipedia import WikipediaTool
from tools.news import NewsTool


class ToolSetup:

    def __init__(self, reminder_manager=None, registry=None):

        self.registry = registry or ToolRegistry()

        # Core tools
        self.calculator = Calculator()
        self.web_search = WebSearch()

        # Information tools
        self.weather = WeatherTool()
        self.wikipedia = WikipediaTool()
        self.news = NewsTool()

        # Reminder manager
        self.reminder_manager = (
            reminder_manager or ReminderManager()
        )

        self._registered = False

    # =========================================
    # REGISTER ALL TOOLS
    # =========================================

    def register_all_tools(self):

        if self._registered:

            return {
                "success": True,
                "registered": self.registry.get_tool_names(),
                "failed": [],
                "total": self.registry.get_tool_count()
            }

        registration_methods = {
            "calculator": self._register_calculator,
            "web_search": self._register_web_search,
            "weather": self._register_weather,
            "wikipedia_search": self._register_wikipedia_search,
            "wikipedia_summary": self._register_wikipedia_summary,
            "wikipedia_random": self._register_wikipedia_random,
            "news_headlines": self._register_news_headlines,
            "news_search": self._register_news_search,
            "add_reminder": self._register_add_reminder,
            "get_reminders": self._register_get_reminders,
            "delete_reminder": self._register_delete_reminder
        }

        results = {}

        for name, register_method in registration_methods.items():

            try:

                results[name] = register_method()

            except Exception as error:

                print(
                    f"NOVA Tool Registration Error [{name}]: {error}"
                )

                results[name] = False

        self._registered = all(results.values())

        return {
            "success": self._registered,

            "registered": [
                name for name, success in results.items()
                if success
            ],

            "failed": [
                name for name, success in results.items()
                if not success
            ],

            "total": self.registry.get_tool_count()
        }

    # =========================================
    # COMMON REGISTRATION HELPER
    # =========================================

    def _register(self, name, function, description, parameters):

        # Prevent duplicate registrations.
        if self.registry.has_tool(name):
            return True

        return self.registry.register_tool(
            name=name,
            function=function,
            description=description,
            parameters=parameters
        )

    # =========================================
    # CALCULATOR
    # =========================================

    def _register_calculator(self):

        return self._register(
            name="calculator",
            function=self.calculator.calculate,
            description=(
                "Perform mathematical calculations including arithmetic, "
                "logarithms, trigonometry and factorials. Use this for "
                "accurate mathematical results."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to calculate."
                    }
                },
                "required": ["expression"],
                "additionalProperties": False
            }
        )

    # =========================================
    # WEB SEARCH
    # =========================================

    def _register_web_search(self):

        return self._register(
            name="web_search",
            function=self.web_search.search,
            description=(
                "Search the internet for current information, facts, "
                "websites and recent developments. Use this when the "
                "user needs online information."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Topic or question to search online."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results."
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        )

    # =========================================
    # WEATHER
    # =========================================

    def _register_weather(self):

        return self._register(
            name="get_weather",
            function=self.weather.get_weather,
            description=(
                "Get current weather information for a city, including "
                "temperature, feels-like temperature, humidity, wind, "
                "pressure and weather conditions."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, for example Delhi or London."
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": (
                            "Use metric for Celsius or imperial for Fahrenheit."
                        )
                    }
                },
                "required": ["city"],
                "additionalProperties": False
            }
        )

    # =========================================
    # WIKIPEDIA SEARCH
    # =========================================

    def _register_wikipedia_search(self):

        return self._register(
            name="wikipedia_search",
            function=self.wikipedia.search,
            description=(
                "Search Wikipedia for articles related to a topic. "
                "Use this to discover relevant article titles."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Topic to search on Wikipedia."
                    },
                    "results": {
                        "type": "integer",
                        "description": "Number of article titles to return."
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        )

    # =========================================
    # WIKIPEDIA SUMMARY
    # =========================================

    def _register_wikipedia_summary(self):

        return self._register(
            name="wikipedia_summary",
            function=self.wikipedia.get_summary,
            description=(
                "Retrieve a Wikipedia article summary for a specific topic. "
                "Returns article title, summary and source URL."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic or Wikipedia article title."
                    },
                    "sentences": {
                        "type": "integer",
                        "description": "Number of summary sentences."
                    }
                },
                "required": ["topic"],
                "additionalProperties": False
            }
        )

    # =========================================
    # RANDOM WIKIPEDIA ARTICLE
    # =========================================

    def _register_wikipedia_random(self):

        return self._register(
            name="wikipedia_random",
            function=self.wikipedia.get_random_article,
            description=(
                "Retrieve a random Wikipedia article and its summary."
            ),
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )

    # =========================================
    # NEWS HEADLINES
    # =========================================

    def _register_news_headlines(self):

        return self._register(
            name="news_headlines",
            function=self.news.get_top_headlines,
            description=(
                "Retrieve current top news headlines by country and category. "
                "Default country is India. Categories include business, "
                "technology, sports, science, health and entertainment."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "country": {
                        "type": "string",
                        "description": "Two-letter country code, default in."
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "business",
                            "entertainment",
                            "general",
                            "health",
                            "science",
                            "sports",
                            "technology"
                        ],
                        "description": "Optional news category."
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of headlines to retrieve."
                    }
                },
                "additionalProperties": False
            }
        )

    # =========================================
    # NEWS SEARCH
    # =========================================

    def _register_news_search(self):

        return self._register(
            name="news_search",
            function=self.news.search_news,
            description=(
                "Search news articles for a specific topic or keyword. "
                "Returns article titles, descriptions, sources, URLs "
                "and publication dates."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Topic or keyword to search in news."
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of news articles to retrieve."
                    },
                    "language": {
                        "type": "string",
                        "description": "Two-letter language code, default en."
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        )

    # =========================================
    # ADD REMINDER
    # =========================================

    def _register_add_reminder(self):

        return self._register(
            name="add_reminder",
            function=self.reminder_manager.add_reminder,
            description=(
                "Create a reminder with a title, message and scheduled "
                "date and time. Use ISO 8601 date-time format."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Reminder title."
                    },
                    "message": {
                        "type": "string",
                        "description": "Reminder details."
                    },
                    "run_at": {
                        "type": "string",
                        "description": (
                            "ISO date-time, for example "
                            "2026-12-25T10:30:00"
                        )
                    }
                },
                "required": ["title", "message", "run_at"],
                "additionalProperties": False
            }
        )

    # =========================================
    # GET REMINDERS
    # =========================================

    def _register_get_reminders(self):

        return self._register(
            name="get_reminders",
            function=self.reminder_manager.get_reminders,
            description=(
                "Get saved reminders, optionally filtered by status: "
                "pending, completed, missed or error."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": [
                            "pending",
                            "completed",
                            "missed",
                            "error"
                        ],
                        "description": "Optional reminder status filter."
                    }
                },
                "additionalProperties": False
            }
        )

    # =========================================
    # DELETE REMINDER
    # =========================================

    def _register_delete_reminder(self):

        return self._register(
            name="delete_reminder",
            function=self.reminder_manager.delete_reminder,
            description=(
                "Delete an existing reminder using its reminder ID. "
                "Retrieve reminder IDs using get_reminders first."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "reminder_id": {
                        "type": "string",
                        "description": "ID of the reminder to delete."
                    }
                },
                "required": ["reminder_id"],
                "additionalProperties": False
            }
        )

    # =========================================
    # GET REGISTRY
    # =========================================

    def get_registry(self):

        return self.registry

    # =========================================
    # GET REMINDER MANAGER
    # =========================================

    def get_reminder_manager(self):

        return self.reminder_manager

    # =========================================
    # SHUTDOWN
    # =========================================

    def shutdown(self):

        services = [
            self.web_search,
            self.weather,
            self.news,
            self.reminder_manager
        ]

        for service in services:

            close_method = getattr(
                service,
                "close",
                None
            )

            shutdown_method = getattr(
                service,
                "shutdown",
                None
            )

            try:

                if callable(close_method):
                    close_method()

                elif callable(shutdown_method):
                    shutdown_method()

            except Exception as error:

                print(
                    f"NOVA Tool Shutdown Error: {error}"
                )
