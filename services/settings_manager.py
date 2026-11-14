
import json
import threading
from pathlib import Path

from config.settings import DATA_DIR


class SettingsManager:

    DEFAULT_SETTINGS = {
        "voice_enabled": True,
        "auto_speak": True,
        "memory_enabled": True,
        "notifications_enabled": True,
        "response_style": "Balanced",
        "language": "Auto Detect"
    }

    ALLOWED_VALUES = {
        "response_style": [
            "Balanced",
            "Professional",
            "Friendly",
            "Concise",
            "Detailed"
        ],
        "language": [
            "Auto Detect",
            "English",
            "Hindi",
            "Hinglish"
        ]
    }

    def __init__(self):

        self.settings_dir = Path(DATA_DIR) / "settings"
        self.settings_file = self.settings_dir / "user_settings.json"

        self.settings_dir.mkdir(parents=True, exist_ok=True)

        self._lock = threading.RLock()

        self.settings = self.DEFAULT_SETTINGS.copy()

        self.load_settings()

    # =========================================
    # VALIDATE SETTINGS
    # =========================================

    def _validate_setting(self, key, value):

        if key not in self.DEFAULT_SETTINGS:
            return False

        default_value = self.DEFAULT_SETTINGS[key]

        if isinstance(default_value, bool):
            return isinstance(value, bool)

        if isinstance(default_value, str):

            if not isinstance(value, str):
                return False

            if not value.strip():
                return False

            allowed = self.ALLOWED_VALUES.get(key)

            if allowed and value not in allowed:
                return False

            return True

        return True

    # =========================================
    # LOAD SETTINGS
    # =========================================

    def load_settings(self):

        with self._lock:

            if not self.settings_file.exists():

                self.settings = self.DEFAULT_SETTINGS.copy()
                self.save_settings()

                return self.settings.copy()

            try:

                with open(
                    self.settings_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    saved = json.load(file)

                if not isinstance(saved, dict):
                    raise ValueError("Invalid settings format")

                loaded = self.DEFAULT_SETTINGS.copy()

                for key, value in saved.items():

                    if self._validate_setting(key, value):
                        loaded[key] = value

                self.settings = loaded

                return self.settings.copy()

            except (
                OSError,
                json.JSONDecodeError,
                ValueError
            ) as error:

                print(f"Settings Load Error: {error}")

                self.settings = self.DEFAULT_SETTINGS.copy()

                return self.settings.copy()

    # =========================================
    # SAVE SETTINGS
    # =========================================

    def save_settings(self, new_settings=None):

        with self._lock:

            if new_settings is not None:

                if not isinstance(new_settings, dict):
                    return False

                updated = self.settings.copy()

                for key, value in new_settings.items():

                    if not self._validate_setting(key, value):
                        return False

                    updated[key] = value

                self.settings = updated

            temp_file = self.settings_file.with_suffix(".tmp")

            try:

                self.settings_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

                with open(
                    temp_file,
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        self.settings,
                        file,
                        indent=4,
                        ensure_ascii=False
                    )

                temp_file.replace(self.settings_file)

                return True

            except OSError as error:

                print(f"Settings Save Error: {error}")

                try:
                    if temp_file.exists():
                        temp_file.unlink()
                except OSError:
                    pass

                return False

    # =========================================
    # GET SINGLE SETTING
    # =========================================

    def get_setting(self, key, default=None):

        with self._lock:

            return self.settings.get(key, default)

    # =========================================
    # UPDATE SINGLE SETTING
    # =========================================

    def update_setting(self, key, value):

        with self._lock:

            if not self._validate_setting(key, value):
                return False

            old_value = self.settings.get(key)

            self.settings[key] = value

            if self.save_settings():
                return True

            self.settings[key] = old_value

            return False

    # =========================================
    # GET ALL SETTINGS
    # =========================================

    def get_all_settings(self):

        with self._lock:

            return self.settings.copy()

    # =========================================
    # RESET SETTINGS
    # =========================================

    def reset_settings(self):

        with self._lock:

            old_settings = self.settings.copy()

            self.settings = self.DEFAULT_SETTINGS.copy()

            if self.save_settings():
                return True

            self.settings = old_settings

            return False

    # =========================================
    # CHECK SETTING
    # =========================================

    def is_enabled(self, key):

        with self._lock:

            value = self.settings.get(key, False)

            return value is True
