from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.core.preset_registry import (
    add_user_preset,
    get_all_presets,
    is_builtin,
    remove_user_preset,
)
from app.core.rules_presets import DEFAULT_PRESET_NAME
from app.core.services import FileOrganizerService
from app.ui.preset_editor import edit_preset
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

        available_presets = self._organizer.available_presets()
        current_preset = self._organizer.preset_name
        if current_preset not in available_presets:
            current_preset = DEFAULT_PRESET_NAME if DEFAULT_PRESET_NAME in available_presets else available_presets[0]
            self._organizer.set_preset(current_preset)

        ttk.Label(self._content, text="Путь").grid(row=0, column=0)
        self._path_var = tk.StringVar()
        ttk.Entry(self._content, textvariable=self._path_var).grid(row=0, column=1)
        ttk.Button(self._content, text="Обзор", command=self._on_browse).grid(
            row=0, column=2
        )

        ttk.Label(self._content, text="Конфигурация").grid(row=1, column=0)
        self._preset_var = tk.StringVar(value=current_preset)
        self._preset_combo = ttk.Combobox(
            self._content,
            textvariable=self._preset_var,
            values=available_presets,
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
        self._content.columnconfigure(0, weight=1)
        self._content.rowconfigure(2, weight=1)

        ttk.Label(self._content, text="Настройки").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        subfolders_cb = ttk.Checkbutton(
            self._content,
            text="Сортировать файлы в подпапках",
            variable=self._include_subfolders_var,
        )
        subfolders_cb.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))
        add_tooltip(
            subfolders_cb,
            "Если включено, файлы из вложенных папок тоже будут вытащены",
        )

        ttk.Label(self._content, text="Конфигурации сортировки:").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        list_frame = ttk.Frame(self._content)
        list_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 8))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self._presets_listbox = tk.Listbox(list_frame, height=10, selectmode="single")
        self._presets_listbox.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self._presets_listbox.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self._presets_listbox.configure(yscrollcommand=scroll.set)
        self._presets_listbox.bind("<<ListboxSelect>>", self._on_preset_select)

        btn_frame = ttk.Frame(self._content)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="w")
        ttk.Button(btn_frame, text="Добавить", command=self._on_add_preset).pack(side="left", padx=(0, 4))
        self._edit_btn = ttk.Button(btn_frame, text="Изменить", command=self._on_edit_preset)
        self._edit_btn.pack(side="left", padx=4)
        self._delete_btn = ttk.Button(btn_frame, text="Удалить", command=self._on_delete_preset)
        self._delete_btn.pack(side="left", padx=4)

        self._refresh_presets_list()
        self._on_preset_select(None)

    def _refresh_presets_list(self) -> None:
        if not hasattr(self, "_presets_listbox"):
            return
        selected_name = None
        selection = self._presets_listbox.curselection()
        if selection:
            selected_name = self._presets_listbox.get(selection[0])
        self._presets_listbox.delete(0, tk.END)
        names = list[str](get_all_presets().keys())
        for name in names:
            self._presets_listbox.insert(tk.END, name)
        if selected_name in names:
            index = names.index(selected_name)
            self._presets_listbox.selection_set(index)

    def _on_preset_select(self, _: tk.Event | None) -> None:
        if not hasattr(self, "_delete_btn"):
            return
        sel = self._presets_listbox.curselection()
        if not sel:
            self._edit_btn.state(["disabled"])
            self._delete_btn.state(["disabled"])
            return
        name = self._presets_listbox.get(sel[0])
        self._edit_btn.state(["!disabled"])
        self._delete_btn.state(["disabled"] if is_builtin(name) else ["!disabled"])

    def _on_add_preset(self) -> None:
        result = edit_preset(self.winfo_toplevel(), initial_name="", initial_mapping=None)
        if result:
            name, mapping = result
            try:
                add_user_preset(name, mapping)
            except ValueError as exc:
                messagebox.showerror("Конфигурации", str(exc))
                return
            self._refresh_presets_list()
            self._select_preset_in_list(name)
            messagebox.showinfo("Конфигурации", f"Конфигурация «{name}» сохранена.")

    def _on_edit_preset(self) -> None:
        sel = self._presets_listbox.curselection()
        if not sel:
            return
        name = self._presets_listbox.get(sel[0])
        if is_builtin(name):
            messagebox.showinfo("Конфигурации", "Встроенные конфигурации нельзя изменить")
            return
        presets = get_all_presets()
        result = edit_preset(self.winfo_toplevel(), initial_name=name, initial_mapping=presets[name])
        if result:
            new_name, mapping = result
            if new_name != name and is_builtin(new_name):
                messagebox.showerror("Конфигурации", "Нельзя переопределить встроенную конфигурацию")
                return
            remove_user_preset(name)
            add_user_preset(new_name, mapping)
            self._refresh_presets_list()
            self._select_preset_in_list(new_name)
            messagebox.showinfo("Конфигурации", "Конфигурация обновлена.")

    def _on_delete_preset(self) -> None:
        sel = self._presets_listbox.curselection()
        if not sel:
            return
        name = self._presets_listbox.get(sel[0])
        if is_builtin(name):
            return
        if not messagebox.askyesno("Удалить", f"Удалить конфигурацию «{name}»?", icon="question"):
            return
        remove_user_preset(name)
        self._refresh_presets_list()
        self._on_preset_select(None)
        if self._organizer.preset_name == name:
            self._organizer.set_preset(DEFAULT_PRESET_NAME)

    def _select_preset_in_list(self, name: str) -> None:
        if not hasattr(self, "_presets_listbox"):
            return
        names = list[str](get_all_presets().keys())
        if name not in names:
            return
        index = names.index(name)
        self._presets_listbox.selection_clear(0, tk.END)
        self._presets_listbox.selection_set(index)
        self._presets_listbox.activate(index)
        self._on_preset_select(None)

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
