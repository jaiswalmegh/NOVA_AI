
import customtkinter as ctk

from ui.components import NOVATheme, NOVALabel, NOVACard
from config.settings import USER_NAME


class NOVASidebar(ctk.CTkFrame):

    def __init__(self, master, on_navigate=None, **kwargs):
        super().__init__(
            master,
            width=245,
            corner_radius=0,
            fg_color=NOVATheme.SIDEBAR,
            **kwargs
        )

        self.on_navigate = on_navigate
        self.navigation_buttons = {}
        self.active_page = "Dashboard"
        self.status_message = "NOVA is ready"
        self.status_color = NOVATheme.SUCCESS

        self.grid_propagate(False)

        self._create_brand()
        self._create_navigation()
        self._create_bottom_section()

    def _create_brand(self):
        brand_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        brand_frame.pack(
            fill="x",
            padx=20,
            pady=(28, 35)
        )

        logo = ctk.CTkLabel(
            brand_frame,
            text="✦",
            font=("Segoe UI", 34, "bold"),
            text_color=NOVATheme.ACCENT
        )

        logo.pack(side="left", padx=(0, 10))

        brand_text = ctk.CTkFrame(
            brand_frame,
            fg_color="transparent"
        )

        brand_text.pack(side="left")

        NOVALabel(
            brand_text,
            text="NOVA AI",
            size=21,
            weight="bold"
        ).pack(anchor="w")

        NOVALabel(
            brand_text,
            text="INTELLIGENT ASSISTANT",
            size=8,
            color=NOVATheme.TEXT_SECONDARY
        ).pack(anchor="w")

    def _create_navigation(self):
        NOVALabel(
            self,
            text="WORKSPACE",
            size=10,
            color=NOVATheme.TEXT_SECONDARY,
            weight="bold"
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 12)
        )

        navigation_items = [
            ("Dashboard", "⌂"),
            ("Chat", "◈"),
            ("Automations", "⚡"),
            ("Memory", "◉"),
            ("Tools", "⌘")
        ]

        for page, icon in navigation_items:
            self._create_nav_button(page, icon)

        NOVALabel(
            self,
            text="PREFERENCES",
            size=10,
            color=NOVATheme.TEXT_SECONDARY,
            weight="bold"
        ).pack(
            anchor="w",
            padx=24,
            pady=(30, 12)
        )

        self._create_nav_button("Settings", "⚙")

    def _create_nav_button(self, page, icon):
        button = ctk.CTkButton(
            self,
            text=f"   {icon}     {page}",
            height=44,
            corner_radius=10,
            anchor="w",
            font=("Segoe UI", 13),
            fg_color="transparent",
            hover_color=NOVATheme.CARD,
            text_color=NOVATheme.TEXT_SECONDARY,
            command=lambda selected_page=page: (
                self.navigate(selected_page)
            )
        )

        button.pack(
            fill="x",
            padx=14,
            pady=3
        )

        self.navigation_buttons[page] = button

        if page == self.active_page:
            self._set_active_style(page)

    def navigate(self, page):
        if page not in self.navigation_buttons:
            return

        self.active_page = page

        for button in self.navigation_buttons.values():
            button.configure(
                fg_color="transparent",
                text_color=NOVATheme.TEXT_SECONDARY
            )

        self._set_active_style(page)

        if callable(self.on_navigate):
            self.on_navigate(page)

    def _set_active_style(self, page):
        button = self.navigation_buttons.get(page)

        if button:
            button.configure(
                fg_color="#252044",
                text_color=NOVATheme.TEXT_PRIMARY
            )

    def _create_bottom_section(self):
        bottom_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=14,
            pady=18
        )

        status_card = NOVACard(bottom_frame)

        status_card.pack(
            fill="x",
            pady=(0, 14)
        )

        self.status_title = NOVALabel(
            status_card,
            text="●  SYSTEM STATUS",
            size=10,
            color=NOVATheme.SUCCESS,
            weight="bold"
        )

        self.status_title.pack(
            anchor="w",
            padx=12,
            pady=(12, 4)
        )

        self.status_label = NOVALabel(
            status_card,
            text=self.status_message,
            size=12,
            color=NOVATheme.TEXT_SECONDARY
        )

        self.status_label.pack(
            anchor="w",
            padx=12,
            pady=(0, 12)
        )

        profile_frame = ctk.CTkFrame(
            bottom_frame,
            fg_color=NOVATheme.PANEL,
            corner_radius=12
        )

        profile_frame.pack(fill="x")

        avatar = ctk.CTkLabel(
            profile_frame,
            text=(USER_NAME[:1].upper() or "U"),
            width=38,
            height=38,
            corner_radius=12,
            fg_color=NOVATheme.ACCENT,
            text_color="#FFFFFF",
            font=("Segoe UI", 15, "bold")
        )

        avatar.pack(
            side="left",
            padx=10,
            pady=10
        )

        profile_text = ctk.CTkFrame(
            profile_frame,
            fg_color="transparent"
        )

        profile_text.pack(
            side="left",
            fill="y",
            pady=10
        )

        NOVALabel(
            profile_text,
            text=USER_NAME,
            size=12,
            weight="bold"
        ).pack(anchor="w")

        NOVALabel(
            profile_text,
            text="Personal Workspace",
            size=9,
            color=NOVATheme.TEXT_SECONDARY
        ).pack(anchor="w")

    def set_status(self, message, color=None):
        self.status_message = message
        self.status_color = color or NOVATheme.SUCCESS

        if hasattr(self, "status_label"):
            self.status_label.configure(text=message)

        if hasattr(self, "status_title"):
            self.status_title.configure(text_color=self.status_color)
