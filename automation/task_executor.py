
from automation.system_control import SystemController
from automation.app_launcher import AppLauncher
from automation.file_manager import FileManager
from automation.browser_control import BrowserController


class TaskExecutor:

    def __init__(self):

        self.system = SystemController()
        self.app_launcher = AppLauncher()
        self.file_manager = FileManager()
        self.browser = BrowserController()

        self.available_actions = {
            "system_info",
            "cpu_usage",
            "ram_usage",
            "battery_status",
            "disk_usage",
            "lock_system",
            "open_application",
            "open_website",
            "google_search",
            "youtube_search"
        }

    def get_available_actions(self):

        return sorted(self.available_actions)

    def execute(self, action, parameters=None):

        if not isinstance(action, str):
            return self._result(
                False,
                "Invalid action."
            )

        action = action.strip().lower()
        parameters = parameters or {}

        if not isinstance(parameters, dict):
            return self._result(
                False,
                "Invalid action parameters."
            )

        if action not in self.available_actions:
            return self._result(
                False,
                "This action is not supported."
            )

        try:

            if action == "system_info":
                result = self.system.get_system_info()

            elif action == "cpu_usage":
                result = self.system.get_cpu_usage()

            elif action == "ram_usage":
                result = self.system.get_ram_usage()

            elif action == "battery_status":
                result = self.system.get_battery_status()

            elif action == "disk_usage":
                result = self.system.get_disk_usage(
                    parameters.get("path", "C:\\")
                )

            elif action == "lock_system":
                result = self.system.lock_system()

            elif action == "open_application":
                result = self.app_launcher.open_application(
                    parameters.get("application", "")
                )

            elif action == "open_website":
                result = self.browser.open_url(
                    parameters.get("url", "")
                )

            elif action == "google_search":
                result = self.browser.search_google(
                    parameters.get("query", "")
                )

            elif action == "youtube_search":
                result = self.browser.search_youtube(
                    parameters.get("query", "")
                )

            return self._result(
                True,
                "Action processed successfully.",
                result
            )

        except Exception as error:

            print(f"Task Execution Error: {error}")

            return self._result(
                False,
                "An error occurred while executing the action."
            )

    def _result(self, success, message, data=None):

        return {
            "success": success,
            "message": message,
            "data": data
        }
