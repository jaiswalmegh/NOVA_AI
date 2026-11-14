
import logging
import threading
from pathlib import Path

import customtkinter as ctk

from config.settings import (
    APP_NAME,
    APP_VERSION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WIDTH,
    MIN_HEIGHT,
    LOGS_DIR
)

from core.assistant import NOVAAssistant

from services.settings_manager import SettingsManager
from services.notification_service import NotificationService
from services.scheduler import NOVAScheduler

from tools.reminders import ReminderManager
from tools.tool_setup import ToolSetup

from ui.dashboard import NOVADashboard
from ui.sidebar import NOVASidebar
from ui.chat_panel import NOVAChatPanel
from ui.settings_panel import NOVASettingsPanel

from ui.components import NOVATheme


class NOVAApplication(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.is_closing = False
        self.is_initialized = False

        self.current_page = None
        self.pages = {}

        # =====================================
        # WINDOW CONFIGURATION
        # =====================================

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(f"{APP_NAME} v{APP_VERSION}")

        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.minsize(
            MIN_WIDTH,
            MIN_HEIGHT
        )

        self.configure(
            fg_color=NOVATheme.BACKGROUND
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self._on_close
        )

        # =====================================
        # LOGGING
        # =====================================

        self._setup_logging()

        # =====================================
        # SHARED SERVICES
        # =====================================

        self.settings_manager = SettingsManager()

        self.notification_service = NotificationService(
            settings_manager=self.settings_manager
        )

        self.scheduler = NOVAScheduler(
            settings_manager=self.settings_manager,
            notification_service=self.notification_service
        )

        self.reminder_manager = ReminderManager(
            scheduler=self.scheduler
        )

        self.tool_setup = ToolSetup(
            reminder_manager=self.reminder_manager
        )

        # =====================================
        # AI ASSISTANT
        # =====================================

        self.assistant = NOVAAssistant(
            settings_manager=self.settings_manager,
            tool_setup=self.tool_setup
        )

        # =====================================
        # BUILD UI
        # =====================================

        self._build_layout()

        # =====================================
        # INITIALIZE AI
        # =====================================

        self._initialize_assistant_async()

        logging.info("NOVA application started.")

    # =========================================
    # LOGGING
    # =========================================

    def _setup_logging(self):

        try:

            Path(LOGS_DIR).mkdir(
                parents=True,
                exist_ok=True
            )

            logging.basicConfig(
                filename=str(
                    Path(LOGS_DIR) / "nova.log"
                ),
                level=logging.INFO,
                format=(
                    "%(asctime)s | "
                    "%(levelname)s | "
                    "%(message)s"
                ),
                encoding="utf-8"
            )

        except Exception as error:

            print(f"NOVA Logging Error: {error}")

    # =========================================
    # MAIN LAYOUT
    # =========================================

    def _build_layout(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = NOVASidebar(
            self,
            on_navigate=self.navigate
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns"
        )

        self.content = ctk.CTkFrame(
            self,
            fg_color=NOVATheme.BACKGROUND,
            corner_radius=0
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self._create_pages()

        for page in self.pages.values():

            page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            page.grid_remove()

        self.navigate("Dashboard")

    # =========================================
    # CREATE PAGES
    # =========================================

    def _create_pages(self):

        self.pages["Dashboard"] = NOVADashboard(
            self.content,
            on_action=self._handle_dashboard_action
        )

        self.pages["Chat"] = NOVAChatPanel(
            self.content,
            on_send=self._handle_message,
            on_clear=self.assistant.clear_conversation,
            on_speak=self._handle_speak
        )

        self.pages["Settings"] = NOVASettingsPanel(
            self.content,
            settings_manager=self.settings_manager
        )

        self.pages["Automations"] = self._create_feature_page(
            title="Automations",
            description=(
                "Manage reminders and automate tasks "
                "through NOVA."
            )
        )

        self.pages["Memory"] = self._create_feature_page(
            title="Memory",
            description=(
                "Ask NOVA to remember, recall or manage "
                "information."
            )
        )

        self.pages["Tools"] = self._create_feature_page(
            title="Tools",
            description=(
                "Explore calculations, web search, weather, "
                "news and more."
            )
        )

    # =========================================
    # FEATURE PAGE
    # =========================================

    def _create_feature_page(self, title, description):

        page = ctk.CTkFrame(
            self.content,
            fg_color=NOVATheme.BACKGROUND,
            corner_radius=0
        )

        ctk.CTkLabel(
            page,
            text=title,
            font=("Segoe UI", 28, "bold"),
            text_color=NOVATheme.TEXT_PRIMARY
        ).pack(
            anchor="w",
            padx=35,
            pady=(40, 10)
        )

        ctk.CTkLabel(
            page,
            text=description,
            font=("Segoe UI", 13),
            text_color=NOVATheme.TEXT_SECONDARY,
            wraplength=650,
            justify="left"
        ).pack(
            anchor="w",
            padx=35,
            pady=5
        )

        ctk.CTkButton(
            page,
            text="Open NOVA Chat",
            width=180,
            height=42,
            corner_radius=10,
            fg_color=NOVATheme.ACCENT,
            hover_color=NOVATheme.ACCENT_HOVER,
            command=lambda: self.navigate("Chat")
        ).pack(
            anchor="w",
            padx=35,
            pady=25
        )

        return page

    # =========================================
    # NAVIGATION
    # =========================================

    def navigate(self, page_name):

        if self.is_closing:
            return

        if page_name not in self.pages:

            logging.warning(
                "Unknown page: %s",
                page_name
            )

            return

        if self.current_page:

            previous_page = self.pages.get(
                self.current_page
            )

            if previous_page:
                previous_page.grid_remove()

        selected_page = self.pages[page_name]

        selected_page.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        selected_page.tkraise()

        self.current_page = page_name

        self._sync_sidebar(page_name)

        logging.info(
            "Navigation: %s",
            page_name
        )

    # =========================================
    # SIDEBAR SYNC
    # =========================================

    def _sync_sidebar(self, page_name):

        if not hasattr(self, "sidebar"):
            return

        if page_name not in self.sidebar.navigation_buttons:
            return

        self.sidebar.active_page = page_name

        for button in self.sidebar.navigation_buttons.values():

            button.configure(
                fg_color="transparent",
                text_color=NOVATheme.TEXT_SECONDARY
            )

        self.sidebar._set_active_style(page_name)

    # =========================================
    # AI INITIALIZATION
    # =========================================

    def _initialize_assistant_async(self):

        self.sidebar.set_status(
            "Initializing NOVA...",
            NOVATheme.CYAN
        )

        worker = threading.Thread(
            target=self._initialize_assistant,
            daemon=True
        )

        worker.start()

    def _initialize_assistant(self):

        try:

            result = self.assistant.initialize()

        except Exception as error:

            logging.exception(
                "NOVA initialization failed."
            )

            result = {
                "success": False,
                "message": str(error)
            }

        if self.is_closing:
            return

        try:

            self.after(
                0,
                lambda: self._finish_initialization(result)
            )

        except Exception:
            pass

    def _finish_initialization(self, result):

        if self.is_closing:
            return

        self.is_initialized = result.get(
            "success",
            False
        )

        self.pages["Dashboard"].set_connection_status(
            self.is_initialized
        )

        if self.is_initialized:

            self.sidebar.set_status(
                "NOVA is online",
                NOVATheme.SUCCESS
            )

            logging.info(
                "NOVA initialized successfully."
            )

        else:

            self.sidebar.set_status(
                "AI connection unavailable",
                NOVATheme.RED
            )

            logging.error(
                "NOVA initialization error: %s",
                result.get("message", "Unknown error")
            )

    # =========================================
    # DASHBOARD AI STATE
    # =========================================

    def _update_ai_state(self, state):

        if self.is_closing:
            return

        try:

            self.pages["Dashboard"].set_ai_state(
                state
            )

        except Exception:

            logging.exception(
                "Dashboard AI state update failed."
            )

    def _schedule_ai_state(self, state):

        if self.is_closing:
            return

        try:

            self.after(
                0,
                lambda: self._update_ai_state(state)
            )

        except Exception:
            pass

    # =========================================
    # CHAT MESSAGE HANDLER
    # =========================================

    def _handle_message(self, message):

        if self.is_closing:
            return "NOVA is shutting down."

        if not self.is_initialized:
            return (
                "NOVA is still initializing. "
                "Please try again shortly."
            )

        self._schedule_ai_state("thinking")

        try:

            response = self.assistant.process_message(
                message
            )

            return str(response)

        except Exception as error:

            logging.exception(
                "Message processing failed."
            )

            return (
                "NOVA encountered an error: "
                f"{error}"
            )

        finally:

            self._schedule_ai_state("idle")

    # =========================================
    # CHAT VOICE HANDLER
    # =========================================

    def _handle_speak(self, response):

        if self.is_closing:
            return False

        settings = self.settings_manager.get_all_settings()

        if not settings.get("voice_enabled", True):
            return False

        if not settings.get("auto_speak", False):
            return False

        return self.assistant.speak_response(response)

    # =========================================
    # DASHBOARD ACTIONS
    # =========================================

    def _handle_dashboard_action(self, action):

        if action == "Ask NOVA":

            self.navigate("Chat")

        elif action == "System Status":

            self.navigate("Chat")

            self._send_dashboard_prompt(
                "Show me my computer system status."
            )

        elif action == "Open Browser":

            self.navigate("Chat")

            self._send_dashboard_prompt(
                "Open my default web browser."
            )

        elif action == "Explore Tools":

            self.navigate("Tools")

    # =========================================
    # DASHBOARD PROMPT
    # =========================================

    def _send_dashboard_prompt(self, prompt):

        if self.is_closing:
            return

        chat_page = self.pages["Chat"]

        chat_page.message_input.delete(
            "1.0",
            "end"
        )

        chat_page.message_input.insert(
            "1.0",
            prompt
        )

        chat_page.send_message()

    # =========================================
    # APPLICATION STATUS
    # =========================================

    def get_application_status(self):

        return {
            "application": APP_NAME,
            "version": APP_VERSION,
            "initialized": self.is_initialized,
            "current_page": self.current_page,
            "closing": self.is_closing
        }

    # =========================================
    # SHUTDOWN
    # =========================================

    def _on_close(self):

        if self.is_closing:
            return

        self.is_closing = True

        logging.info(
            "NOVA application shutting down."
        )

        try:

            self.assistant.shutdown()

            logging.info(
                "NOVA services shut down successfully."
            )

        except Exception:

            logging.exception(
                "NOVA shutdown error."
            )

        try:
            self.destroy()

        except Exception:
            pass


# =============================================
# APPLICATION ENTRY POINT
# =============================================

def main():

    application = NOVAApplication()
    application.mainloop()


if __name__ == "__main__":
    main()
