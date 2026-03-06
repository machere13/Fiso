from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.core.services import FileOrganizerService

class MainWindow(ttk.Frame):
    def __init__(self, master: tk.Misc, organizer: FileOrganizerService, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._organizer = organizer
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Путь").grid(row=0, column=0)
        self._path_var = tk.StringVar()
        ttk.Entry(self, textvariable=self._path_var).grid(row=0, column=1)
        ttk.Button(self, text="Обзор", command=self._on_browse).grid(row=0, column=2)

        ttk.Label(self, text="Конфигурация").grid(row=1, column=0)
        self._preset_var = tk.StringVar(value=self._organizer.preset_name)
        self._preset_combo = ttk.Combobox(
            self,
            textvariable=self._preset_var,
            values=self._organizer.available_presets(),
            state="readonly",
        )
        self._preset_combo.grid(row=1, column=1)

        ttk.Button(self, text="Сортировать", command=self._on_sort).grid(row=2, column=1)

    def _on_browse(self) -> None:
        directory = filedialog.askdirectory()
        if directory:
            self._path_var.set(directory)

    def _on_sort(self) -> None:
        path_str = self._path_var.get().strip()
        if not path_str:
            messagebox.showwarning("Сортировка", "Сначала укажите папку")
            return

        self._organizer.set_preset(self._preset_var.get())

        root = Path(path_str)
        try:
            plan = self._organizer.build_plan(root)
            if not plan.items:
                messagebox.showinfo("Сортировка", "Не найдено файлов для перемещения")
                return
            self._organizer.apply_plan(plan)
            messagebox.showinfo("Сортировка", "Сортировка завершена")
        except Exception as exc:
            messagebox.showerror("Ошибка сортировки", str(exc))
