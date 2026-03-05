import tkinter as tk
from tkinter import ttk

class MainWindow(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._build_ui()

    def _build_ui(self) -> None: ...

    def _on_browse(self) -> None: ...

    def _on_sort(self) -> None: ...
