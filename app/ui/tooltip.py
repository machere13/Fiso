import tkinter as tk

def add_tooltip(widget: tk.Misc, text: str, delay_ms: int = 500) -> None:
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
            background="#fff",
            foreground="#000",
            relief="solid",
        )
        label.pack()
        tw.attributes("-topmost", True)
        state["window"] = tw

    def on_enter(_: tk.Event) -> None:
        state["after_id"] = widget.after(delay_ms, show)

    def on_leave(_: tk.Event) -> None:
        if state["after_id"] is not None:
            widget.after_cancel(state["after_id"])
            state["after_id"] = None
        if state["window"] is not None:
            state["window"].destroy()
            state["window"] = None

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
