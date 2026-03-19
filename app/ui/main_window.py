from pathlib import Path

import customtkinter as ctk  # type: ignore[import-untyped]
from tkinter import filedialog, messagebox

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


class MainWindow(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, organizer: FileOrganizerService, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._organizer = organizer
        self._selected_preset_name: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, fg_color="transparent")
        sidebar.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        ctk.CTkButton(sidebar, text="Главная", command=self._show_main_screen).grid(
            row=0, column=0, pady=4
        )
        ctk.CTkButton(sidebar, text="Настройки", command=self._show_settings_screen).grid(
            row=1, column=0, pady=4
        )

        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self._content.grid_columnconfigure(1, weight=1)

        self._include_subfolders_var = ctk.BooleanVar(value=False)
        self._build_main_screen()

    def _build_main_screen(self) -> None:
        for child in self._content.winfo_children():
            child.destroy()

        available_presets = self._organizer.available_presets()
        current_preset = self._organizer.preset_name
        if current_preset not in available_presets:
            current_preset = DEFAULT_PRESET_NAME if DEFAULT_PRESET_NAME in available_presets else available_presets[0]
            self._organizer.set_preset(current_preset)

        ctk.CTkLabel(self._content, text="Путь").grid(row=0, column=0, padx=(0, 8), pady=4, sticky="w")
        self._path_var = ctk.StringVar()
        ctk.CTkEntry(self._content, textvariable=self._path_var, width=300).grid(
            row=0, column=1, padx=4, pady=4, sticky="ew"
        )
        ctk.CTkButton(self._content, text="Обзор", command=self._on_browse, width=80).grid(
            row=0, column=2, padx=4, pady=4
        )

        ctk.CTkLabel(self._content, text="Конфигурация").grid(row=1, column=0, padx=(0, 8), pady=4, sticky="w")
        self._preset_var = ctk.StringVar(value=current_preset)
        self._preset_combo = ctk.CTkComboBox(
            self._content,
            values=available_presets,
            variable=self._preset_var,
            width=300,
        )
        self._preset_combo.grid(row=1, column=1, padx=4, pady=4, sticky="w")

        ctk.CTkButton(self._content, text="Сортировать", command=self._on_sort, width=120).grid(
            row=2, column=1, padx=4, pady=12
        )

    def _show_main_screen(self) -> None:
        self._build_main_screen()

    def _show_settings_screen(self) -> None:
        for child in self._content.winfo_children():
            child.destroy()
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self._content, text="Настройки", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )
        subfolders_cb = ctk.CTkCheckBox(
            self._content,
            text="Сортировать файлы в подпапках",
            variable=self._include_subfolders_var,
        )
        subfolders_cb.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))
        add_tooltip(
            subfolders_cb,
            "Если включено, файлы из вложенных папок тоже будут вытащены",
        )

        ctk.CTkLabel(self._content, text="Конфигурации сортировки:").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        list_frame = ctk.CTkScrollableFrame(self._content, height=180)
        list_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 8))
        list_frame.grid_columnconfigure(0, weight=1)
        self._presets_frame = list_frame
        self._preset_buttons: dict[str, ctk.CTkButton] = {}

        btn_frame = ctk.CTkFrame(self._content, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="w")
        ctk.CTkButton(btn_frame, text="Добавить", command=self._on_add_preset, width=100).pack(
            side="left", padx=(0, 8)
        )
        self._edit_btn = ctk.CTkButton(btn_frame, text="Изменить", command=self._on_edit_preset, width=100)
        self._edit_btn.pack(side="left", padx=4)
        self._delete_btn = ctk.CTkButton(btn_frame, text="Удалить", command=self._on_delete_preset, width=100)
        self._delete_btn.pack(side="left", padx=4)

        self._refresh_presets_list()
        self._on_preset_select()

    def _refresh_presets_list(self) -> None:
        if not hasattr(self, "_presets_frame"):
            return
        selected_name = self._selected_preset_name
        for btn in self._preset_buttons.values():
            btn.destroy()
        self._preset_buttons.clear()

        names = list(get_all_presets().keys())
        for i, name in enumerate(names):
            btn = ctk.CTkButton(
                self._presets_frame,
                text=name,
                command=lambda n=name: self._on_preset_click(n),
                anchor="w",
                fg_color="transparent" if self._selected_preset_name != name else None,
            )
            btn.grid(row=i, column=0, sticky="ew", pady=2)
            self._presets_frame.grid_columnconfigure(0, weight=1)
            self._preset_buttons[name] = btn

        if selected_name in names:
            self._selected_preset_name = selected_name
        elif names:
            self._selected_preset_name = names[0]
        else:
            self._selected_preset_name = None

        self._update_presets_buttons_style()
        self._on_preset_select()

    def _on_preset_click(self, name: str) -> None:
        self._selected_preset_name = name
        self._update_presets_buttons_style()
        self._on_preset_select()

    def _update_presets_buttons_style(self) -> None:
        for name, btn in self._preset_buttons.items():
            btn.configure(fg_color=None if name == self._selected_preset_name else "transparent")

    def _on_preset_select(self) -> None:
        if not hasattr(self, "_delete_btn"):
            return
        if self._selected_preset_name is None:
            self._edit_btn.configure(state="disabled")
            self._delete_btn.configure(state="disabled")
            return
        self._edit_btn.configure(state="normal")
        self._delete_btn.configure(state="disabled" if is_builtin(self._selected_preset_name) else "normal")

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
        if self._selected_preset_name is None:
            return
        name = self._selected_preset_name
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
        if self._selected_preset_name is None:
            return
        name = self._selected_preset_name
        if is_builtin(name):
            return
        if not messagebox.askyesno("Удалить", f"Удалить конфигурацию «{name}»?", icon="question"):
            return
        remove_user_preset(name)
        self._refresh_presets_list()
        self._on_preset_select()
        if self._organizer.preset_name == name:
            self._organizer.set_preset(DEFAULT_PRESET_NAME)

    def _select_preset_in_list(self, name: str) -> None:
        names = list(get_all_presets().keys())
        if name not in names:
            return
        self._selected_preset_name = name
        self._refresh_presets_list()

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
