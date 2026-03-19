from typing import Any

import customtkinter as ctk  # type: ignore[import-untyped]

try:
    from CTkToolTip import CTkToolTip as _CTkToolTip  # pyright: ignore[reportMissingImports]

    _HAS_CTK_TOOLTIP = True
except ImportError:
    _CTkToolTip = None
    _HAS_CTK_TOOLTIP = False


def add_tooltip(
    widget: Any,
    text: str,
    delay_ms: int = 500,
) -> None:
    """Добавляет подсказку при наведении на виджет. Использует CTkToolTip если доступен."""
    if _HAS_CTK_TOOLTIP and _CTkToolTip is not None:
        _CTkToolTip(widget, message=text, delay=delay_ms / 1000)
    else:
        _fallback_tooltip(widget, text, delay_ms)


def _fallback_tooltip(widget: Any, text: str, delay_ms: int) -> None:
    """Резервный тултип на Toplevel (если CTkToolTip не установлен)."""
    import tkinter as tk

    state: dict = {"after_id": None, "window": None}

    def show() -> None:
        state["after_id"] = None
        tw = tk.Toplevel(widget)
        tw.wm_overrideredirect(True)
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + widget.winfo_height() + 2
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=text,
            background="#2b2b2b",
            foreground="#ffffff",
            relief="solid",
        )
        label.pack()
        tw.attributes("-topmost", True)
        state["window"] = tw

    def on_enter(_: object) -> None:
        state["after_id"] = widget.after(delay_ms, show)

    def on_leave(_: object) -> None:
        if state["after_id"] is not None:
            widget.after_cancel(state["after_id"])
            state["after_id"] = None
        if state["window"] is not None:
            state["window"].destroy()
            state["window"] = None

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
