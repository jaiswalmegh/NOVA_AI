
import customtkinter as ctk


class NOVATheme:
    BACKGROUND = "#0B0F19"
    SIDEBAR = "#0D1220"
    SURFACE = "#151B2A"
    SURFACE_LIGHT = "#1B2032"
    CARD = SURFACE
    PANEL = SURFACE

    ACCENT = "#8B5CF6"
    ACCENT_HOVER = "#7C3AED"
    CYAN = "#22D3EE"
    GREEN = "#34D399"
    SUCCESS = GREEN
    RED = "#F87171"
    PURPLE = "#A78BFA"

    TEXT_PRIMARY = "#F1F5F9"
    TEXT_SECONDARY = "#8993A8"
    TEXT_MUTED = "#64748B"
    BORDER = "#34304F"

    FONT_FAMILY = "Segoe UI"
    CORNER_RADIUS = 12


class NOVAButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        style = kwargs.pop("style", "primary")

        defaults = {
            "height": 40,
            "corner_radius": NOVATheme.CORNER_RADIUS,
            "fg_color": NOVATheme.ACCENT,
            "hover_color": NOVATheme.ACCENT_HOVER,
            "text_color": "#FFFFFF",
            "font": (NOVATheme.FONT_FAMILY, 13, "bold"),
        }

        if style == "secondary":
            defaults.update({
                "fg_color": NOVATheme.SURFACE_LIGHT,
                "hover_color": NOVATheme.BORDER,
                "text_color": NOVATheme.TEXT_PRIMARY,
                "border_width": 1,
                "border_color": NOVATheme.BORDER,
            })

        defaults.update(kwargs)
        super().__init__(master, **defaults)


class NOVACard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        defaults = {
            "fg_color": NOVATheme.SURFACE,
            "corner_radius": 14,
            "border_width": 1,
            "border_color": NOVATheme.BORDER,
        }

        defaults.update(kwargs)
        super().__init__(master, **defaults)


class NOVALabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        size = kwargs.pop("size", 13)
        weight = kwargs.pop("weight", "normal")
        color = kwargs.pop("color", None)

        if color is not None and "text_color" not in kwargs:
            kwargs["text_color"] = color

        defaults = {
            "text_color": NOVATheme.TEXT_PRIMARY,
            "font": (NOVATheme.FONT_FAMILY, size, weight),
        }

        defaults.update(kwargs)
        super().__init__(master, **defaults)


class NOVAEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        defaults = {
            "height": 42,
            "corner_radius": 10,
            "fg_color": NOVATheme.SURFACE,
            "border_color": NOVATheme.BORDER,
            "text_color": NOVATheme.TEXT_PRIMARY,
            "placeholder_text_color": NOVATheme.TEXT_SECONDARY,
        }

        defaults.update(kwargs)
        super().__init__(master, **defaults)


class NOVAProgressBar(ctk.CTkProgressBar):
    def __init__(self, master, **kwargs):
        defaults = {
            "height": 8,
            "corner_radius": 5,
            "progress_color": NOVATheme.ACCENT,
            "fg_color": NOVATheme.SURFACE_LIGHT,
        }

        defaults.update(kwargs)
        super().__init__(master, **defaults)
