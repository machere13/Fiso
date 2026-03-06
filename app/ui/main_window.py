from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.core.services import FileOrganizerService
from app.ui.tooltip import add_tooltip

class MainWindow(ttk.Frame):
    def __init__(self, master: tk.Misc, organizer: FileOrganizerService, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._organizer = organizer
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self)
        sidebar.grid(row=0, column=0)

        ttk.Button(sidebar, text="Главная", command=self._show_main_screen).grid(
            row=0, column=0
        )
        ttk.Button(sidebar, text="Настройки", command=self._show_settings_screen).grid(
            row=1, column=0
        )

        self._content = ttk.Frame(self)
        self._content.grid(row=0, column=1)
        self._content.columnconfigure(1, weight=1)

        self._include_subfolders_var = tk.BooleanVar(value=False)
        self._build_main_screen()

    def _build_main_screen(self) -> None:
        for child in self._content.winfo_children():
            child.destroy()

        ttk.Label(self._content, text="Путь").grid(row=0, column=0)
        self._path_var = tk.StringVar()
        ttk.Entry(self._content, textvariable=self._path_var).grid(row=0, column=1)
        ttk.Button(self._content, text="Обзор", command=self._on_browse).grid(
            row=0, column=2
        )

        ttk.Label(self._content, text="Конфигурация").grid(row=1, column=0)
        self._preset_var = tk.StringVar(value=self._organizer.preset_name)
        self._preset_combo = ttk.Combobox(
            self._content,
            textvariable=self._preset_var,
            values=self._organizer.available_presets(),
            state="readonly",
        )
        self._preset_combo.grid(row=1, column=1)

        ttk.Button(self._content, text="Сортировать", command=self._on_sort).grid(
            row=2, column=1
        )

    def _show_main_screen(self) -> None:
        self._build_main_screen()

    def _show_settings_screen(self) -> None:
        for child in self._content.winfo_children():
            child.destroy()
        ttk.Label(self._content, text="Настройки").grid(row=0, column=0)
        subfolders_cb = ttk.Checkbutton(
            self._content,
            text="Сортировать файлы в подпапках",
            variable=self._include_subfolders_var,
        )
        subfolders_cb.grid(row=1, column=0)
        add_tooltip(
            subfolders_cb,
            "Если включено, файлы из вложенных папок тоже будут вытащены",
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

        preset = self._preset_var.get()
        include_sub = self._include_subfolders_var.get()
        self._organizer.set_preset(preset)
        self._organizer.set_include_subfolders(include_sub)

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
