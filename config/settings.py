
import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env", override=True)

# Application settings
APP_NAME = os.getenv("APP_NAME", "NOVA AI")
APP_VERSION = "2.0.0"
APP_ENV = os.getenv("APP_ENV", "development")

# User settings
USER_NAME = os.getenv("USER_NAME", "User")
ASSISTANT_NAME = "NOVA"

# AI provider settings
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "")

# API keys
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# UI settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 850
MIN_WIDTH = 1100
MIN_HEIGHT = 700

THEME = "dark"

# Project directories
CONFIG_DIR = BASE_DIR / "config"
CORE_DIR = BASE_DIR / "core"
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

MEMORY_DIR = DATA_DIR / "memory"
CONVERSATIONS_DIR = DATA_DIR / "conversations"
REMINDERS_DIR = DATA_DIR / "reminders"

# Ensure runtime directories exist
for directory in (
    MEMORY_DIR,
    CONVERSATIONS_DIR,
    REMINDERS_DIR,
    LOGS_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)
