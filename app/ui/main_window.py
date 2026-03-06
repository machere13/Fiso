from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.core.interfaces import FileOrganizer

class MainWindow(ttk.Frame):
    def __init__(self, master: tk.Misc, organizer: FileOrganizer, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._organizer = organizer
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)

        #стилизуется здесь, через grid
        ttk.Label(self, text="Путь").grid(
            row=0, column=0
        )

        self._path_var = tk.StringVar()
        #стилизуется здесь, через grid
        ttk.Entry(self, textvariable=self._path_var).grid(
            row=0, column=1
        )

        #стилизуется здесь, через grid
        ttk.Button(self, text="Обзор", command=self._on_browse).grid(
            row=0, column=2
        )

        #стилизуется здесь, через grid
        ttk.Button(self, text="Сортировать", command=self._on_sort).grid(
            row=1, column=1
        )

    def _on_browse(self) -> None:
        directory = filedialog.askdirectory()
        if directory:
            self._path_var.set(directory)

    def _on_sort(self) -> None:
        path_str = self._path_var.get().strip()
        if not path_str:
            messagebox.showwarning("Сортировка", "Сначала укажите папку")
            return

        root = Path(path_str)
        try:
            plan = self._organizer.build_plan(root)
            if not plan.items:
                messagebox.showinfo(
                    "Сортировка", "Не найдено файлов для перемещения"
                )
                return
            self._organizer.apply_plan(plan)
            messagebox.showinfo(
                "Сортировка",
                f"Сортировка завершена",
            )
        except Exception as exc:
            messagebox.showerror("Ошибка сортировки", str(exc))

