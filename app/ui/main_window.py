import tkinter as tk
from tkinter import filedialog, ttk


class MainWindow(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)

        # стилизуется здесь, через грид
        ttk.Label(self, text="Путь").grid(row=0)

        self._path_var = tk.StringVar()
        # стилизуется здесь, через грид
        ttk.Entry(self, textvariable=self._path_var).grid(row=0)
        
        # стилизуется здесь, через грид
        ttk.Button(self, text="Обзор", command=self._on_browse).grid(row=0)

    def _on_browse(self) -> None:
        directory = filedialog.askdirectory()
        if directory:
            self._path_var.set(directory)

    def _on_sort(self) -> None: ...
