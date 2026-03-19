from typing import Any

import customtkinter as ctk  # pyright: ignore[reportMissingImports]
from tkinter import messagebox

from app.core.rules_presets import ExtensionsMap


def _normalize_ext(ext: str) -> str:
    ext = ext.strip().lower()
    if ext and not ext.startswith("."):
        ext = "." + ext
    return ext


def _parse_extensions(text: str) -> set[str]:
    return {_normalize_ext(x) for x in text.replace(",", " ").split() if x.strip()}


def edit_preset(
    parent: Any,
    initial_name: str = "",
    initial_mapping: ExtensionsMap | None = None,
) -> tuple[str, ExtensionsMap] | None:
    initial_mapping = initial_mapping or {}
    result: list[tuple[str, ExtensionsMap]] = []

    dialog = ctk.CTkToplevel(parent)
    dialog.title("Редактор конфигурации" if initial_name else "Новая конфигурация")
    dialog.transient(parent)
    dialog.grab_set()

    main = ctk.CTkFrame(dialog, fg_color="transparent")
    main.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    dialog.grid_columnconfigure(0, weight=1)
    dialog.grid_rowconfigure(0, weight=1)

    ctk.CTkLabel(main, text="Название").grid(row=0, column=0, sticky="w", pady=(0, 4))
    name_var = ctk.StringVar(value=initial_name)
    ctk.CTkEntry(main, textvariable=name_var, width=350).grid(
        row=1, column=0, sticky="ew", pady=(0, 12)
    )

    ctk.CTkLabel(main, text="Папки и расширения").grid(
        row=2, column=0, sticky="w", pady=(0, 4)
    )
    rows_frame = ctk.CTkFrame(main, fg_color="transparent")
    rows_frame.grid(row=3, column=0, sticky="nsew")
    main.grid_columnconfigure(0, weight=1)
    main.grid_rowconfigure(3, weight=1)
    rows_frame.grid_columnconfigure(0, weight=1)
    inner = ctk.CTkScrollableFrame(rows_frame, height=150, fg_color="transparent")
    inner.grid(row=0, column=0, sticky="ew")
    inner.grid_columnconfigure(1, weight=1)

    row_widgets: list[tuple[ctk.StringVar, ctk.StringVar, ctk.CTkFrame]] = []

    def add_row(folder: str = "", exts: str = "") -> None:
        row_f = ctk.CTkFrame(inner, fg_color="transparent")
        row_f.grid(row=len(row_widgets), column=0, sticky="ew", pady=2)
        row_f.grid_columnconfigure(1, weight=1)
        f_var = ctk.StringVar(value=folder)
        e_var = ctk.StringVar(value=exts)
        ctk.CTkEntry(row_f, textvariable=f_var, width=120).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkEntry(row_f, textvariable=e_var, width=200).grid(row=0, column=1, padx=4)
        remove_btn = ctk.CTkButton(row_f, text="✕", width=32, command=lambda: remove_row(row_f))
        remove_btn.grid(row=0, column=2)
        row_widgets.append((f_var, e_var, row_f))

    def remove_row(row_f: ctk.CTkFrame) -> None:
        for i, (_, _, rf) in enumerate(row_widgets):
            if rf == row_f:
                row_widgets.pop(i)
                row_f.destroy()
                break

    for folder, exts in (initial_mapping or {}).items():
        add_row(folder, ", ".join(sorted(exts)))
    if not row_widgets:
        add_row()

    ctk.CTkButton(rows_frame, text="+ Добавить папку", command=lambda: add_row()).grid(
        row=1, column=0, pady=(8, 0), sticky="w"
    )

    def on_ok() -> None:
        name = name_var.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Введите название конфигурации", parent=dialog)
            return
        mapping: ExtensionsMap = {}
        for f_var, e_var, _ in row_widgets:
            folder = f_var.get().strip()
            exts = _parse_extensions(e_var.get())
            if folder and exts:
                mapping[folder] = exts
        if not mapping:
            messagebox.showwarning(
                "Ошибка",
                "Добавьте хотя бы одну папку с расширениями",
                parent=dialog,
            )
            return
        result.append((name, mapping))
        dialog.destroy()

    def on_cancel() -> None:
        dialog.destroy()

    btn_f = ctk.CTkFrame(main, fg_color="transparent")
    btn_f.grid(row=4, column=0, pady=(16, 0))
    ctk.CTkButton(btn_f, text="Отмена", command=on_cancel, width=80).pack(side="right", padx=(0, 8))
    ctk.CTkButton(btn_f, text="Сохранить", command=on_ok, width=80).pack(side="right")

    dialog.wait_window(dialog)
    return result[0] if result else None
