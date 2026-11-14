
import threading

from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

from services.notification_service import NotificationService
from services.settings_manager import SettingsManager


class NOVAScheduler:

    def __init__(
        self,
        settings_manager=None,
        notification_service=None,
        on_reminder_complete=None
    ):

        self.settings_manager = (
            settings_manager or SettingsManager()
        )

        self.notification_service = (
            notification_service
            or NotificationService(self.settings_manager)
        )

        self.on_reminder_complete = on_reminder_complete

        self._lock = threading.RLock()
        self.is_running = False
        self.is_shutdown = False

        self.scheduler = BackgroundScheduler(
            daemon=True,
            timezone=datetime.now().astimezone().tzinfo
        )

    # =========================================
    # START SCHEDULER
    # =========================================

    def start(self):

        with self._lock:

            if self.is_shutdown:
                return False

            if self.is_running:
                return True

            try:

                self.scheduler.start()
                self.is_running = True

                return True

            except Exception as error:

                print(f"NOVA Scheduler Start Error: {error}")
                return False

    # =========================================
    # ADD REMINDER
    # =========================================

    def add_reminder(
        self,
        reminder_id,
        title,
        message,
        run_at
    ):

        try:

            if not isinstance(reminder_id, str) or not reminder_id.strip():
                raise ValueError("Invalid reminder ID.")

            if not isinstance(title, str) or not title.strip():
                raise ValueError("Reminder title is required.")

            if not isinstance(message, str) or not message.strip():
                raise ValueError("Reminder message is required.")

            if isinstance(run_at, str):
                run_at = datetime.fromisoformat(run_at)

            if not isinstance(run_at, datetime):
                raise ValueError("Invalid reminder date and time.")

            if run_at.tzinfo is None:
                run_at = run_at.astimezone()

            if run_at <= datetime.now().astimezone():
                raise ValueError("Reminder time must be in the future.")

            with self._lock:

                if self.is_shutdown:
                    raise RuntimeError(
                        "Scheduler has already been shut down."
                    )

                if not self.is_running:

                    if not self.start():
                        raise RuntimeError(
                            "Could not start reminder scheduler."
                        )

                self.scheduler.add_job(
                    self._trigger_reminder,
                    trigger="date",
                    run_date=run_at,
                    args=[
                        reminder_id,
                        title.strip(),
                        message.strip()
                    ],
                    id=reminder_id,
                    replace_existing=True,
                    misfire_grace_time=300,
                    max_instances=1,
                    coalesce=True
                )

            return {
                "success": True,
                "message": "Reminder scheduled successfully.",
                "reminder_id": reminder_id
            }

        except Exception as error:

            return {
                "success": False,
                "message": str(error),
                "reminder_id": None
            }

    # =========================================
    # TRIGGER REMINDER
    # =========================================

    def _trigger_reminder(
        self,
        reminder_id,
        title,
        message
    ):

        notification_success = False

        try:

            notification_result = self.notification_service.send(
                title=title,
                message=message
            )

            notification_success = (
                notification_result is not False
            )

        except Exception as error:

            print(f"NOVA Notification Error: {error}")

        # Mark reminder completed even if notification
        # delivery fails, to prevent repeated triggering.
        if callable(self.on_reminder_complete):

            try:

                self.on_reminder_complete(reminder_id)

            except Exception as error:

                print(
                    f"NOVA Reminder Callback Error: {error}"
                )

        return notification_success

    # =========================================
    # REMOVE REMINDER
    # =========================================

    def remove_reminder(self, reminder_id):

        try:

            with self._lock:

                self.scheduler.remove_job(
                    str(reminder_id)
                )

            return True

        except JobLookupError:
            return False

        except Exception as error:

            print(f"NOVA Scheduler Remove Error: {error}")
            return False

    # =========================================
    # GET SCHEDULED REMINDERS
    # =========================================

    def get_scheduled_reminders(self):

        try:

            with self._lock:

                jobs = self.scheduler.get_jobs()

                return [
                    {
                        "id": job.id,
                        "next_run": (
                            job.next_run_time.isoformat()
                            if job.next_run_time
                            else None
                        )
                    }
                    for job in jobs
                ]

        except Exception as error:

            print(f"NOVA Scheduler Query Error: {error}")
            return []

    # =========================================
    # REMOVE ALL REMINDERS
    # =========================================

    def remove_all_reminders(self):

        try:

            with self._lock:

                self.scheduler.remove_all_jobs()

            return True

        except Exception as error:

            print(f"NOVA Scheduler Clear Error: {error}")
            return False

    # =========================================
    # SCHEDULER STATUS
    # =========================================

    def get_status(self):

        return {
            "running": self.is_running,
            "shutdown": self.is_shutdown,
            "scheduled_jobs": len(
                self.get_scheduled_reminders()
            )
        }

    # =========================================
    # SHUTDOWN
    # =========================================

    def shutdown(self):

        with self._lock:

            if self.is_shutdown:
                return True

            try:

                if self.is_running:
                    self.scheduler.shutdown(wait=False)

                self.is_running = False
                self.is_shutdown = True

                return True

            except Exception as error:

                print(f"NOVA Scheduler Shutdown Error: {error}")
                return False
