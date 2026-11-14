
import os
import subprocess
import webbrowser
from urllib.parse import urlparse


class AppLauncher:

    def __init__(self):

        self.applications = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "file explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
            "settings": "ms-settings:"
        }

    def open_application(self, application):

        if not isinstance(application, str) or not application.strip():
            return False

        application = application.lower().strip()

        executable = self.applications.get(application)

        if not executable:
            return False

        try:

            if executable.startswith("ms-settings:"):
                os.startfile(executable)
            else:
                subprocess.Popen([executable])

            return True

        except (OSError, subprocess.SubprocessError) as error:

            print(f"Application Launch Error: {error}")
            return False

    def open_website(self, url):

        if not isinstance(url, str) or not url.strip():
            return False

        url = url.strip()

        if "://" not in url:
            url = "https://" + url

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return False

        try:
            return webbrowser.open(url)

        except Exception as error:
            print(f"Website Launch Error: {error}")
            return False

    def get_supported_applications(self):

        return list(self.applications.keys())

    def register_application(self, name, executable):

        if not name or not executable:
            return False

        self.applications[name.lower().strip()] = executable.strip()

        return True
