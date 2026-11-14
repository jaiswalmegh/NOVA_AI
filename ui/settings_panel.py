
import customtkinter as ctk

from ui.components import NOVATheme
from services.settings_manager import SettingsManager


class NOVASettingsPanel(ctk.CTkFrame):

    def __init__(self, master, settings_manager=None, **kwargs):
        super().__init__(
            master,
            fg_color=NOVATheme.BACKGROUND,
            corner_radius=0,
            **kwargs
        )

        self.settings_manager = settings_manager or SettingsManager()

        saved = self.settings_manager.get_all_settings()

        self.voice_enabled = ctk.BooleanVar(value=saved["voice_enabled"])
        self.auto_speak = ctk.BooleanVar(value=saved["auto_speak"])
        self.notifications_enabled = ctk.BooleanVar(
            value=saved["notifications_enabled"]
        )
        self.memory_enabled = ctk.BooleanVar(value=saved["memory_enabled"])

        self.response_style = ctk.StringVar(
            value=saved["response_style"]
        )
        self.language = ctk.StringVar(value=saved["language"])

        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self,
            text="Settings",
            font=("Segoe UI", 30, "bold"),
            text_color=NOVATheme.TEXT_PRIMARY
        ).pack(anchor="w", padx=30, pady=(30, 5))

        ctk.CTkLabel(
            self,
            text="Customize your NOVA experience",
            font=("Segoe UI", 13),
            text_color=NOVATheme.TEXT_SECONDARY
        ).pack(anchor="w", padx=32, pady=(0, 25))

        self.settings_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=NOVATheme.BORDER,
            scrollbar_button_hover_color=NOVATheme.ACCENT
        )
        self.settings_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 25)
        )

        self._add_section("VOICE & AUDIO")

        self._add_switch(
            "Voice Recognition",
            "Allow NOVA to listen to your voice commands.",
            self.voice_enabled
        )

        self._add_switch(
            "Automatic Voice Responses",
            "NOVA will speak its responses aloud.",
            self.auto_speak
        )

        self._add_section("AI PERSONALIZATION")

        self._add_switch(
            "Conversation Memory",
            "Allow NOVA to retain useful conversation context.",
            self.memory_enabled
        )

        self._add_option(
            "Response Style",
            "Choose how NOVA communicates.",
            self.response_style,
            ["Balanced", "Professional", "Friendly", "Concise", "Detailed"]
        )

        self._add_option(
            "Language",
            "Select your preferred conversation language.",
            self.language,
            ["Auto Detect", "English", "Hindi", "Hinglish"]
        )

        self._add_section("SYSTEM")

        self._add_switch(
            "Desktop Notifications",
            "Allow NOVA to display desktop notifications.",
            self.notifications_enabled
        )

        self.save_button = ctk.CTkButton(
            self.settings_container,
            text="Save Settings",
            height=45,
            width=180,
            corner_radius=12,
            fg_color=NOVATheme.ACCENT,
            hover_color=NOVATheme.ACCENT_HOVER,
            font=("Segoe UI", 14, "bold"),
            command=self.save_settings
        )
        self.save_button.pack(anchor="w", pady=(30, 10))

        self.status_label = ctk.CTkLabel(
            self.settings_container,
            text="",
            font=("Segoe UI", 12),
            text_color=NOVATheme.CYAN
        )
        self.status_label.pack(anchor="w", pady=(0, 15))

    def _add_section(self, title):
        ctk.CTkLabel(
            self.settings_container,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color=NOVATheme.PURPLE
        ).pack(anchor="w", pady=(22, 12))

    def _add_switch(self, title, description, variable):
        card = ctk.CTkFrame(
            self.settings_container,
            fg_color=NOVATheme.SURFACE,
            corner_radius=14
        )
        card.pack(fill="x", pady=6)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(
            side="left",
            fill="both",
            expand=True,
            padx=18,
            pady=14
        )

        ctk.CTkLabel(
            content,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=NOVATheme.TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            content,
            text=description,
            font=("Segoe UI", 11),
            text_color=NOVATheme.TEXT_SECONDARY,
            wraplength=480,
            justify="left"
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkSwitch(
            card,
            text="",
            variable=variable,
            progress_color=NOVATheme.ACCENT,
            button_color="#FFFFFF",
            button_hover_color=NOVATheme.PURPLE
        ).pack(side="right", padx=20)

    def _add_option(self, title, description, variable, options):
        card = ctk.CTkFrame(
            self.settings_container,
            fg_color=NOVATheme.SURFACE,
            corner_radius=14
        )
        card.pack(fill="x", pady=6)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(
            side="left",
            fill="both",
            expand=True,
            padx=18,
            pady=14
        )

        ctk.CTkLabel(
            content,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=NOVATheme.TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            content,
            text=description,
            font=("Segoe UI", 11),
            text_color=NOVATheme.TEXT_SECONDARY
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkOptionMenu(
            card,
            variable=variable,
            values=options,
            width=145,
            height=34,
            fg_color="#282342",
            button_color=NOVATheme.ACCENT,
            button_hover_color=NOVATheme.ACCENT_HOVER,
            dropdown_fg_color=NOVATheme.SURFACE,
            dropdown_hover_color=NOVATheme.BORDER
        ).pack(side="right", padx=18)

    def get_settings(self):
        return {
            "voice_enabled": self.voice_enabled.get(),
            "auto_speak": self.auto_speak.get(),
            "memory_enabled": self.memory_enabled.get(),
            "notifications_enabled": self.notifications_enabled.get(),
            "response_style": self.response_style.get(),
            "language": self.language.get()
        }

    def save_settings(self):
        success = self.settings_manager.save_settings(
            self.get_settings()
        )

        if success:
            self.status_label.configure(
                text="✓ Settings saved successfully!",
                text_color=NOVATheme.SUCCESS
            )
        else:
            self.status_label.configure(
                text="✕ Unable to save settings.",
                text_color=NOVATheme.RED
            )

        return success
