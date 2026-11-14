
import threading

from plyer import notification

from config.settings import APP_NAME
from services.settings_manager import SettingsManager


class NotificationService:

    def __init__(self, settings_manager=None):

        self.settings_manager = (
            settings_manager or SettingsManager()
        )

        self.app_name = APP_NAME or "NOVA AI"
        self._lock = threading.RLock()

    # =========================================
    # SEND NOTIFICATION
    # =========================================

    def send(
        self,
        title,
        message,
        timeout=5
    ):

        if not isinstance(title, str) or not title.strip():
            return False

        if not isinstance(message, str) or not message.strip():
            return False

        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            return False

        if timeout <= 0 or timeout > 60:
            return False

        try:

            settings = self.settings_manager.get_all_settings()

            if not settings.get("notifications_enabled", True):
                return False

            with self._lock:

                notification.notify(
                    title=title.strip()[:100],
                    message=message.strip()[:1000],
                    app_name=self.app_name,
                    timeout=int(timeout)
                )

            return True

        except Exception as error:

            print(f"NOVA Notification Error: {error}")
            return False

    # =========================================
    # REMINDER NOTIFICATION
    # =========================================

    def reminder(self, message):

        return self.send(
            title="NOVA Reminder",
            message=message
        )

    # =========================================
    # TASK COMPLETED
    # =========================================

    def task_completed(self, task_name):

        if not isinstance(task_name, str) or not task_name.strip():
            return False

        return self.send(
            title="Task Completed",
            message=f"NOVA has completed: {task_name.strip()}"
        )

    # =========================================
    # ALERT
    # =========================================

    def alert(self, message):

        return self.send(
            title="NOVA Alert",
            message=message
        )

    # =========================================
    # SUCCESS NOTIFICATION
    # =========================================

    def success(self, message):

        return self.send(
            title="NOVA Success",
            message=message
        )

    # =========================================
    # ERROR NOTIFICATION
    # =========================================

    def error(self, message):

        return self.send(
            title="NOVA Error",
            message=message
        )

    # =========================================
    # TEST NOTIFICATION
    # =========================================

    def test_notification(self):

        return self.send(
            title="NOVA AI",
            message="Notifications are working successfully!"
        )

    # =========================================
    # SETTINGS
    # =========================================

    def set_enabled(self, enabled):

        if not isinstance(enabled, bool):
            return False

        return self.settings_manager.update_setting(
            "notifications_enabled",
            enabled
        )

    def is_enabled(self):

        settings = self.settings_manager.get_all_settings()

        return settings.get(
            "notifications_enabled",
            True
        )
