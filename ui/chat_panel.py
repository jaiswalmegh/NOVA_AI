
import threading
import customtkinter as ctk

from config.settings import USER_NAME
from ui.components import NOVATheme, NOVAButton, NOVALabel


class NOVAChatPanel(ctk.CTkFrame):

    def __init__(
        self,
        master,
        on_send=None,
        on_clear=None,
        on_speak=None,
        **kwargs
    ):

        super().__init__(
            master,
            fg_color=NOVATheme.BACKGROUND,
            corner_radius=0,
            **kwargs
        )

        self.on_send = on_send
        self.on_clear = on_clear
        self.on_speak = on_speak

        self.messages = []
        self.is_processing = False
        self._typing_widget = None

        self._create_header()
        self._create_chat_area()
        self._create_input_area()

    # =========================================
    # HEADER
    # =========================================

    def _create_header(self):

        header = ctk.CTkFrame(
            self,
            fg_color=NOVATheme.BACKGROUND,
            height=75
        )

        header.pack(fill="x", padx=25, pady=(15, 5))
        header.pack_propagate(False)

        title_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        title_frame.pack(side="left", fill="y")

        NOVALabel(
            title_frame,
            text="AI Conversation",
            size=21,
            weight="bold"
        ).pack(anchor="w", pady=(10, 0))

        NOVALabel(
            title_frame,
            text="Your intelligent workspace",
            size=11,
            color=NOVATheme.TEXT_SECONDARY
        ).pack(anchor="w")

        self.clear_button = NOVAButton(
            header,
            text="Clear Chat",
            style="secondary",
            width=100,
            command=self.clear_chat
        )

        self.clear_button.pack(side="right", pady=15)

    # =========================================
    # CHAT AREA
    # =========================================

    def _create_chat_area(self):

        self.chat_container = ctk.CTkScrollableFrame(
            self,
            fg_color=NOVATheme.BACKGROUND,
            scrollbar_button_color=NOVATheme.BORDER,
            scrollbar_button_hover_color=NOVATheme.ACCENT
        )

        self.chat_container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.show_welcome_message()

    def show_welcome_message(self):

        welcome = ctk.CTkFrame(
            self.chat_container,
            fg_color="transparent"
        )

        welcome.pack(fill="x", pady=(70, 25))

        NOVALabel(
            welcome,
            text="✦",
            size=48,
            color=NOVATheme.ACCENT
        ).pack(pady=(0, 10))

        NOVALabel(
            welcome,
            text=f"Hello, {USER_NAME}!",
            size=27,
            weight="bold"
        ).pack(pady=5)

        NOVALabel(
            welcome,
            text="I'm NOVA. What can I help you with today?",
            size=13,
            color=NOVATheme.TEXT_SECONDARY
        ).pack(pady=5)

    # =========================================
    # INPUT AREA
    # =========================================

    def _create_input_area(self):

        input_outer = ctk.CTkFrame(
            self,
            fg_color=NOVATheme.BACKGROUND
        )

        input_outer.pack(
            fill="x",
            padx=25,
            pady=(5, 20)
        )

        input_frame = ctk.CTkFrame(
            input_outer,
            fg_color=NOVATheme.PANEL,
            corner_radius=16,
            border_width=1,
            border_color=NOVATheme.BORDER
        )

        input_frame.pack(fill="x")

        self.message_input = ctk.CTkTextbox(
            input_frame,
            height=55,
            corner_radius=12,
            fg_color="transparent",
            border_width=0,
            text_color=NOVATheme.TEXT_PRIMARY,
            font=("Segoe UI", 13),
            wrap="word"
        )

        self.message_input.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(15, 5),
            pady=8
        )

        self.message_input.bind(
            "<Return>",
            self._handle_enter
        )

        self.send_button = NOVAButton(
            input_frame,
            text="➤",
            width=48,
            height=42,
            command=self.send_message
        )

        self.send_button.pack(
            side="right",
            padx=10,
            pady=10
        )

        NOVALabel(
            input_outer,
            text="NOVA AI can make mistakes. Verify important information.",
            size=9,
            color=NOVATheme.TEXT_SECONDARY
        ).pack(pady=(8, 0))

    # =========================================
    # KEYBOARD INPUT
    # =========================================

    def _handle_enter(self, event):

        if event.state & 0x0001:
            return None

        self.send_message()

        return "break"

    # =========================================
    # SEND MESSAGE
    # =========================================

    def send_message(self):

        if self.is_processing:
            return

        message = self.message_input.get(
            "1.0",
            "end-1c"
        ).strip()

        if not message:
            return

        self.message_input.delete("1.0", "end")

        self.add_message("user", message)

        if not callable(self.on_send):

            self.add_message(
                "assistant",
                "Message handler is not available."
            )

            return

        self.is_processing = True
        self.set_input_enabled(False)

        self._show_typing_message()

        worker = threading.Thread(
            target=self._process_message,
            args=(message,),
            daemon=True
        )

        worker.start()

    # =========================================
    # PROCESS MESSAGE
    # =========================================

    def _process_message(self, message):

        try:

            response = self.on_send(message)

            if response is None:
                response = "I couldn't generate a response."

            self.after(
                0,
                lambda result=str(response): self._finish_message(result)
            )

        except Exception as error:

            error_message = str(error)

            try:

                self.after(
                    0,
                    lambda result=error_message: self._finish_message(
                        f"I ran into an error: {result}"
                    )
                )

            except Exception:
                pass

    # =========================================
    # TYPING INDICATOR
    # =========================================

    def _show_typing_message(self):

        self._remove_typing_message()

        self._typing_widget = ctk.CTkFrame(
            self.chat_container,
            fg_color="transparent"
        )

        self._typing_widget.pack(
            fill="x",
            pady=5
        )

        NOVALabel(
            self._typing_widget,
            text="✦ NOVA is thinking...",
            size=11,
            color=NOVATheme.ACCENT
        ).pack(anchor="w", padx=15)

        self.after(100, self._scroll_to_bottom)

    def _remove_typing_message(self):

        if self._typing_widget is not None:

            try:
                self._typing_widget.destroy()
            except Exception:
                pass

            self._typing_widget = None

    # =========================================
    # FINISH RESPONSE
    # =========================================

    def _finish_message(self, response):

        if not self.winfo_exists():
            return

        self._remove_typing_message()

        # Display complete response FIRST.
        self.add_message(
            "assistant",
            response
        )

        self.is_processing = False
        self.set_input_enabled(True)

        self.message_input.focus_set()

        # Start voice only AFTER text is displayed.
        if callable(self.on_speak):

            worker = threading.Thread(
                target=self._speak_response,
                args=(response,),
                daemon=True
            )

            worker.start()

    def _speak_response(self, response):

        try:

            if callable(self.on_speak):
                self.on_speak(response)

        except Exception as error:

            print(f"NOVA Chat Voice Error: {error}")

    # =========================================
    # ADD MESSAGE
    # =========================================

    def add_message(self, role, content):

        if not isinstance(content, str) or not content.strip():
            return

        is_user = role == "user"

        message_row = ctk.CTkFrame(
            self.chat_container,
            fg_color="transparent"
        )

        message_row.pack(
            fill="x",
            pady=10,
            padx=10
        )

        message_bubble = ctk.CTkFrame(
            message_row,
            fg_color="#252044" if is_user else NOVATheme.PANEL,
            corner_radius=14,
            border_width=1,
            border_color=(
                NOVATheme.ACCENT
                if is_user
                else NOVATheme.BORDER
            )
        )

        message_bubble.pack(
            side="right" if is_user else "left",
            padx=5,
            ipadx=5,
            ipady=5
        )

        sender = "YOU" if is_user else "✦ NOVA"

        NOVALabel(
            message_bubble,
            text=sender,
            size=10,
            color=(
                NOVATheme.CYAN
                if is_user
                else NOVATheme.ACCENT
            ),
            weight="bold"
        ).pack(
            anchor="w",
            padx=14,
            pady=(10, 3)
        )

        content_label = ctk.CTkLabel(
            message_bubble,
            text=content,
            font=("Segoe UI", 13),
            text_color=NOVATheme.TEXT_PRIMARY,
            justify="left",
            anchor="w",
            wraplength=650
        )

        content_label.pack(
            padx=14,
            pady=(3, 12)
        )

        self.messages.append({
            "role": role,
            "content": content
        })

        self.after(100, self._scroll_to_bottom)

    # =========================================
    # SCROLL
    # =========================================

    def _scroll_to_bottom(self):

        try:
            self.chat_container._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    # =========================================
    # CLEAR CHAT
    # =========================================

    def clear_chat(self):

        if self.is_processing:
            return

        self._remove_typing_message()

        for widget in self.chat_container.winfo_children():

            try:
                widget.destroy()
            except Exception:
                pass

        self.messages.clear()

        if callable(self.on_clear):
            self.on_clear()

        self.show_welcome_message()

    # =========================================
    # INPUT STATE
    # =========================================

    def set_input_enabled(self, enabled):

        state = "normal" if enabled else "disabled"

        self.message_input.configure(state=state)
        self.send_button.configure(state=state)
        self.clear_button.configure(state=state)
