
import math
import customtkinter as ctk
import tkinter as tk

from ui.components import NOVATheme


class NOVAAIOrb(ctk.CTkFrame):

    def __init__(self, master, size=260, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            width=size,
            height=size,
            **kwargs
        )

        self.size = size
        self.state = "idle"
        self.animation_running = True
        self.animation_step = 0

        self.canvas = tk.Canvas(
            self,
            width=size,
            height=size,
            bg=NOVATheme.BACKGROUND,
            highlightthickness=0
        )

        self.canvas.pack(fill="both", expand=True)
        self.after(100, self._animate)

    def _get_colors(self):
        colors = {
            "idle": ("#31205C", "#8B5CF6", "#22D3EE"),
            "listening": ("#123D58", "#22D3EE", "#67E8F9"),
            "thinking": ("#44205E", "#A855F7", "#C084FC"),
            "speaking": ("#164E63", "#06B6D4", "#67E8F9")
        }

        return colors.get(self.state, colors["idle"])

    def _draw_orb(self):
        self.canvas.delete("all")

        center = self.size / 2
        base_radius = self.size * 0.25

        pulse = math.sin(self.animation_step * 0.08)
        outer_radius = base_radius + pulse * 5

        color_outer, color_main, color_inner = self._get_colors()

        # Outer glow rings
        for index in range(4, 0, -1):
            radius = outer_radius + index * 13

            self.canvas.create_oval(
                center - radius,
                center - radius,
                center + radius,
                center + radius,
                outline=color_outer,
                width=2
            )

        # Main orb
        self.canvas.create_oval(
            center - outer_radius,
            center - outer_radius,
            center + outer_radius,
            center + outer_radius,
            fill=color_main,
            outline=color_inner,
            width=3
        )

        # Inner core
        inner_radius = outer_radius * 0.55

        self.canvas.create_oval(
            center - inner_radius,
            center - inner_radius,
            center + inner_radius,
            center + inner_radius,
            fill=color_inner,
            outline=""
        )

        # Floating particles
        for index in range(8):
            angle = (
                self.animation_step * 0.035
                + index * math.pi / 4
            )

            orbit_radius = outer_radius + 27

            x = center + math.cos(angle) * orbit_radius
            y = center + math.sin(angle) * orbit_radius

            particle_size = 3

            self.canvas.create_oval(
                x - particle_size,
                y - particle_size,
                x + particle_size,
                y + particle_size,
                fill=color_inner,
                outline=""
            )

        # Centre symbol
        self.canvas.create_text(
            center,
            center,
            text="✦",
            fill="#FFFFFF",
            font=("Segoe UI", 25, "bold")
        )

    def _animate(self):
        if not self.winfo_exists():
            return

        if self.animation_running:
            self.animation_step += 1
            self._draw_orb()

        self.after(40, self._animate)

    def set_state(self, state):
        allowed_states = {
            "idle",
            "listening",
            "thinking",
            "speaking"
        }

        if state not in allowed_states:
            return False

        self.state = state
        return True

    def set_animation(self, enabled):
        self.animation_running = bool(enabled)

        if not self.animation_running:
            self.canvas.delete("all")
            self._draw_orb()

        return True

    def destroy(self):
        self.animation_running = False
        super().destroy()
