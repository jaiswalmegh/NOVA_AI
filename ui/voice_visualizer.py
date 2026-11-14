
import math
import random
import customtkinter as ctk
import tkinter as tk

from ui.components import NOVATheme


class NOVAVoiceVisualizer(ctk.CTkFrame):

    def __init__(self, master, width=500, height=100, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            width=width,
            height=height,
            **kwargs
        )

        self.width = width
        self.height = height
        self.state = "idle"
        self.animation_running = True
        self.animation_step = 0
        self.bar_count = 35

        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg=NOVATheme.BACKGROUND,
            highlightthickness=0
        )

        self.canvas.pack(fill="both", expand=True)
        self.after(100, self._animate)

    def _get_color(self):
        colors = {
            "idle": NOVATheme.ACCENT,
            "listening": NOVATheme.CYAN,
            "speaking": "#A78BFA",
            "thinking": "#C084FC"
        }

        return colors.get(self.state, NOVATheme.ACCENT)

    def _get_bar_height(self, index):
        center = (self.bar_count - 1) / 2
        distance = abs(index - center)
        max_distance = max(center, 1)

        envelope = 1 - (distance / max_distance)

        wave = math.sin(
            self.animation_step * 0.18 + index * 0.45
        )

        if self.state == "idle":
            amplitude = 8
        elif self.state == "listening":
            amplitude = 25
        elif self.state == "speaking":
            amplitude = 35
        else:
            amplitude = 18

        noise = (
            random.uniform(-3, 3)
            if self.state in ("listening", "speaking")
            else 0
        )

        height = 5 + abs(wave) * amplitude * envelope + noise

        return max(4, min(height, self.height * 0.42))

    def _draw_bars(self):
        self.canvas.delete("all")

        color = self._get_color()
        center_y = self.height / 2

        spacing = self.width / self.bar_count
        bar_width = max(2, spacing * 0.42)

        for index in range(self.bar_count):
            x = spacing * index + spacing / 2
            bar_height = self._get_bar_height(index)

            self.canvas.create_rectangle(
                x - bar_width / 2,
                center_y - bar_height,
                x + bar_width / 2,
                center_y + bar_height,
                fill=color,
                outline="",
                width=0
            )

    def _animate(self):
        if not self.winfo_exists():
            return

        if self.animation_running:
            self.animation_step += 1
            self._draw_bars()

        self.after(50, self._animate)

    def set_state(self, state):
        allowed_states = {
            "idle",
            "listening",
            "speaking",
            "thinking"
        }

        if state not in allowed_states:
            return False

        self.state = state
        return True

    def set_animation(self, enabled):
        self.animation_running = bool(enabled)

        if not self.animation_running:
            self.canvas.delete("all")

        return True

    def destroy(self):
        self.animation_running = False
        super().destroy()
