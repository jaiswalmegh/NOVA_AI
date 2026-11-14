
import json
import uuid
import threading

from datetime import datetime, timezone
from pathlib import Path

from config.settings import REMINDERS_DIR
from services.scheduler import NOVAScheduler


class ReminderManager:

    VALID_STATUSES = {
        "pending",
        "completed",
        "missed",
        "error"
    }

    def __init__(self, scheduler=None):

        self.storage_file = (
            Path(REMINDERS_DIR) / "reminders.json"
        )

        self.storage_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._lock = threading.RLock()

        self.reminders = self._load_reminders()

        self.scheduler = scheduler or NOVAScheduler(
            on_reminder_complete=self._mark_completed
        )
        self.scheduler.on_reminder_complete = self._mark_completed

# Ensure shared scheduler also updates reminder status.
        self._restore_pending_reminders()

    # =========================================
    # DATE AND TIME HELPERS
    # =========================================

    @staticmethod
    def _now():
        return datetime.now().astimezone()

    @staticmethod
    def _parse_datetime(value):

        if isinstance(value, datetime):
            parsed = value

        elif isinstance(value, str):

            parsed = datetime.fromisoformat(
                value.strip()
            )

        else:
            raise ValueError(
                "Reminder time must be a valid ISO date-time."
            )

        # Convert timezone-aware values to local timezone.
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone()

        return parsed

    # =========================================
    # LOAD REMINDERS
    # =========================================

    def _load_reminders(self):

        if not self.storage_file.exists():
            return []

        try:

            with open(
                self.storage_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(data, list):
                return []

            valid_reminders = []

            for item in data:

                if not isinstance(item, dict):
                    continue

                if not all(
                    key in item
                    for key in ("id", "title", "message", "run_at")
                ):
                    continue

                if item.get("status") not in self.VALID_STATUSES:
                    item["status"] = "error"

                valid_reminders.append(item)

            return valid_reminders

        except (json.JSONDecodeError, OSError) as error:

            print(f"NOVA Reminder Load Error: {error}")
            return []

    # =========================================
    # SAVE REMINDERS
    # =========================================

    def _save_reminders(self):

        temporary_file = self.storage_file.with_suffix(".tmp")

        try:

            with open(
                temporary_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.reminders,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

                file.flush()

            temporary_file.replace(self.storage_file)

            return True

        except OSError as error:

            print(f"NOVA Reminder Save Error: {error}")

            try:
                temporary_file.unlink(missing_ok=True)
            except OSError:
                pass

            return False

    # =========================================
    # MARK REMINDER COMPLETED
    # =========================================

    def _mark_completed(self, reminder_id):

        with self._lock:

            for reminder in self.reminders:

                if reminder.get("id") == str(reminder_id):

                    if reminder.get("status") != "pending":
                        return False

                    reminder["status"] = "completed"
                    reminder["completed_at"] = (
                        self._now().isoformat()
                    )

                    return self._save_reminders()

        return False

    # =========================================
    # RESTORE PENDING REMINDERS
    # =========================================

    def _restore_pending_reminders(self):

        now = self._now()

        with self._lock:

            for reminder in self.reminders:

                if reminder.get("status") != "pending":
                    continue

                try:

                    run_at = self._parse_datetime(
                        reminder["run_at"]
                    )

                    if run_at <= now:

                        reminder["status"] = "missed"
                        reminder["missed_at"] = now.isoformat()
                        continue

                    result = self.scheduler.add_reminder(
                        reminder_id=reminder["id"],
                        title=reminder["title"],
                        message=reminder["message"],
                        run_at=run_at
                    )

                    if not result.get("success"):
                        reminder["status"] = "error"

                except (ValueError, KeyError, TypeError) as error:

                    print(
                        f"NOVA Reminder Restore Error: {error}"
                    )

                    reminder["status"] = "error"

            self._save_reminders()

    # =========================================
    # ADD REMINDER
    # =========================================

    def add_reminder(
        self,
        title,
        message,
        run_at
    ):

        try:

            if not isinstance(title, str) or not title.strip():
                raise ValueError("Reminder title is required.")

            if not isinstance(message, str) or not message.strip():
                raise ValueError("Reminder message is required.")

            title = title.strip()
            message = message.strip()

            if len(title) > 200:
                raise ValueError("Reminder title is too long.")

            if len(message) > 2000:
                raise ValueError("Reminder message is too long.")

            run_at = self._parse_datetime(run_at)

            if run_at <= self._now():
                raise ValueError(
                    "Reminder time must be in the future."
                )

            reminder_id = str(uuid.uuid4())

            reminder = {
                "id": reminder_id,
                "title": title,
                "message": message,
                "run_at": run_at.isoformat(),
                "status": "pending",
                "created_at": self._now().isoformat()
            }

            with self._lock:

                result = self.scheduler.add_reminder(
                    reminder_id=reminder_id,
                    title=title,
                    message=message,
                    run_at=run_at
                )

                if not result.get("success"):
                    return result

                self.reminders.append(reminder)

                if not self._save_reminders():

                    self.scheduler.remove_reminder(
                        reminder_id
                    )

                    self.reminders.remove(reminder)

                    return {
                        "success": False,
                        "message": "Could not save reminder."
                    }

            return {
                "success": True,
                "message": "Reminder created successfully.",
                "reminder": reminder.copy()
            }

        except Exception as error:

            return {
                "success": False,
                "message": str(error)
            }

    # =========================================
    # GET REMINDERS
    # =========================================

    def get_reminders(self, status=None):

        if status is not None:

            if status not in self.VALID_STATUSES:

                return []

        with self._lock:

            if status is None:

                return [
                    item.copy()
                    for item in self.reminders
                ]

            return [
                item.copy()
                for item in self.reminders
                if item.get("status") == status
            ]

    # =========================================
    # GET SINGLE REMINDER
    # =========================================

    def get_reminder(self, reminder_id):

        with self._lock:

            for reminder in self.reminders:

                if reminder.get("id") == str(reminder_id):
                    return reminder.copy()

        return None

    # =========================================
    # DELETE REMINDER
    # =========================================

    def delete_reminder(self, reminder_id):

        reminder_id = str(reminder_id)

        with self._lock:

            for index, reminder in enumerate(self.reminders):

                if reminder.get("id") == reminder_id:

                    previous_status = reminder.get("status")

                    if previous_status == "pending":

                        self.scheduler.remove_reminder(
                            reminder_id
                        )

                    removed = self.reminders.pop(index)

                    if not self._save_reminders():

                        self.reminders.insert(
                            index,
                            removed
                        )

                        if previous_status == "pending":

                            try:

                                self.scheduler.add_reminder(
                                    reminder_id=removed["id"],
                                    title=removed["title"],
                                    message=removed["message"],
                                    run_at=self._parse_datetime(
                                        removed["run_at"]
                                    )
                                )

                            except Exception as error:
                                print(
                                    f"Reminder Restore Error: {error}"
                                )

                        return False

                    return True

        return False

    # =========================================
    # CLEAR REMINDERS
    # =========================================

    def clear_reminders(self):

        with self._lock:

            previous_reminders = self.reminders.copy()

            self.scheduler.remove_all_reminders()

            self.reminders.clear()

            if not self._save_reminders():

                self.reminders = previous_reminders

                self._restore_pending_reminders()

                return False

            return True

    # =========================================
    # REMINDER STATISTICS
    # =========================================

    def get_statistics(self):

        with self._lock:

            statistics = {
                "total": len(self.reminders),
                "pending": 0,
                "completed": 0,
                "missed": 0,
                "error": 0
            }

            for reminder in self.reminders:

                status = reminder.get("status")

                if status in statistics:
                    statistics[status] += 1

            return statistics

    # =========================================
    # SHUTDOWN
    # =========================================

    def shutdown(self):

        with self._lock:

            self._save_reminders()

        return self.scheduler.shutdown()
