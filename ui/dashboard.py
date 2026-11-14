
import customtkinter as ctk

from ui.ai_orb import NOVAAIOrb
from ui.voice_visualizer import NOVAVoiceVisualizer


class NOVADashboard(ctk.CTkFrame):

    def __init__(self, master, on_action=None, **kwargs):

        super().__init__(
            master,
            fg_color="#0B0F19",
            corner_radius=0,
            **kwargs
        )

        self.on_action = on_action

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_main_area()
        self._build_quick_actions()

    def _build_header(self):

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(25, 10)
        )

        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Dashboard",
            font=("Segoe UI", 28, "bold"),
            text_color="#FFFFFF"
        )

        title.grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.status_label = ctk.CTkLabel(
            header,
            text="●  NOVA ONLINE",
            font=("Segoe UI", 11, "bold"),
            text_color="#22D3EE"
        )

        self.status_label.grid(
            row=0,
            column=1,
            sticky="e",
            padx=10
        )

        subtitle = ctk.CTkLabel(
            header,
            text="Your intelligent desktop companion",
            font=("Segoe UI", 12),
            text_color="#8993A8"
        )

        subtitle.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(5, 0)
        )

    def _build_main_area(self):

        main = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        main.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=10
        )

        main.grid_columnconfigure(0, weight=1)

        # Welcome section

        welcome = ctk.CTkLabel(
            main,
            text="How can I help you today?",
            font=("Segoe UI", 22, "bold"),
            text_color="#F1F5F9"
        )

        welcome.pack(pady=(5, 0))

        description = ctk.CTkLabel(
            main,
            text="Your AI workspace is ready.",
            font=("Segoe UI", 12),
            text_color="#8993A8"
        )

        description.pack(pady=(5, 0))

        # AI Orb

        self.ai_orb = NOVAAIOrb(
            main,
            size=240
        )

        self.ai_orb.pack(pady=(5, 0))

        # AI state

        self.ai_state_label = ctk.CTkLabel(
            main,
            text="NOVA IS STANDING BY",
            font=("Segoe UI", 11, "bold"),
            text_color="#A78BFA"
        )

        self.ai_state_label.pack(pady=(0, 0))

        # Voice Visualizer

        self.voice_visualizer = NOVAVoiceVisualizer(
            main,
            width=450,
            height=75
        )

        self.voice_visualizer.pack(pady=(0, 5))

        # System cards

        cards_container = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )

        cards_container.pack(
            fill="x",
            pady=(10, 0)
        )

        cards_container.grid_columnconfigure(
            (0, 1, 2),
            weight=1
        )

        self._create_status_card(
            cards_container,
            "AI ENGINE",
            "Groq Cloud",
            "#A78BFA",
            0
        )

        self._create_status_card(
            cards_container,
            "VOICE SYSTEM",
            "Ready",
            "#22D3EE",
            1
        )

        self._create_status_card(
            cards_container,
            "MEMORY",
            "Available",
            "#34D399",
            2
        )

    def _create_status_card(
        self,
        parent,
        title,
        value,
        accent,
        column
    ):

        card = ctk.CTkFrame(
            parent,
            fg_color="#151B2A",
            corner_radius=14,
            height=85
        )

        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=6
        )

        card.grid_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 10, "bold"),
            text_color="#8993A8"
        ).pack(
            anchor="w",
            padx=14,
            pady=(13, 4)
        )

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 15, "bold"),
            text_color=accent
        )

        value_label.pack(
            anchor="w",
            padx=14
        )

    def _build_quick_actions(self):

        section = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        section.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=30,
            pady=(5, 25)
        )

        ctk.CTkLabel(
            section,
            text="QUICK ACTIONS",
            font=("Segoe UI", 11, "bold"),
            text_color="#8993A8"
        ).pack(
            anchor="w",
            pady=(0, 12)
        )

        actions = [
            "Ask NOVA",
            "System Status",
            "Open Browser",
            "Explore Tools"
        ]

        buttons_frame = ctk.CTkFrame(
            section,
            fg_color="transparent"
        )

        buttons_frame.pack(
            fill="x"
        )

        for action in actions:

            button = ctk.CTkButton(
                buttons_frame,
                text=action,
                height=40,
                corner_radius=10,
                fg_color="#1B2032",
                hover_color="#34304F",
                border_width=1,
                border_color="#34304F",
                text_color="#E2E8F0",
                font=("Segoe UI", 12),
                command=lambda name=action: self._handle_action(name)
            )

            button.pack(
                side="left",
                expand=True,
                fill="x",
                padx=5
            )

    def _handle_action(self, action):

        if self.on_action:
            self.on_action(action)

    def set_ai_state(self, state):

        states = {
            "idle": ("NOVA IS STANDING BY", "#A78BFA"),
            "listening": ("LISTENING...", "#22D3EE"),
            "thinking": ("PROCESSING YOUR REQUEST...", "#C084FC"),
            "speaking": ("NOVA IS SPEAKING...", "#67E8F9")
        }

        if state not in states:
            return False

        text, color = states[state]

        self.ai_state_label.configure(
            text=text,
            text_color=color
        )

        self.ai_orb.set_state(state)
        self.voice_visualizer.set_state(state)

        return True

    def set_connection_status(self, connected):

        if connected:

            self.status_label.configure(
                text="●  NOVA ONLINE",
                text_color="#22D3EE"
            )

        else:

            self.status_label.configure(
                text="●  CONNECTION LOST",
                text_color="#F87171"
            )
