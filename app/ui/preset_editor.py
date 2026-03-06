import tkinter as tk
from tkinter import StringVar, messagebox, ttk
from tkinter.ttk import Frame

from app.core.rules_presets import ExtensionsMap

def _normalize_ext(ext: str) -> str:
    ext = ext.strip().lower()
    if ext and not ext.startswith("."):
        ext = "." + ext
    return ext

def _parse_extensions(text: str) -> set[str]:
    return {_normalize_ext(x) for x in text.replace(",", " ").split() if x.strip()}

def edit_preset(
    parent: tk.Misc,
    initial_name: str = "",
    initial_mapping: ExtensionsMap | None = None,
) -> tuple[str, ExtensionsMap] | None:
    initial_mapping = initial_mapping or {}
    result: list = []

    dialog = tk.Toplevel(parent)
    dialog.title("Редактор конфигурации" if initial_name else "Новая конфигурация")
    dialog.transient(parent)
    dialog.grab_set()

    main = ttk.Frame(dialog, padding=12)
    main.grid(row=0, column=0, sticky="nsew")
    dialog.columnconfigure(0, weight=1)
    dialog.rowconfigure(0, weight=1)

    ttk.Label(main, text="Название").grid(row=0, column=0)
    name_var = tk.StringVar(value=initial_name)
    ttk.Entry(main, textvariable=name_var, width=40).grid(
        row=1, column=0
    )

    ttk.Label(main, text="Папки и расширения").grid(
        row=2, column=0
    )
    rows_frame = ttk.Frame(main)
    rows_frame.grid(row=3, column=0)
    main.columnconfigure(0, weight=1)
    main.rowconfigure(3, weight=1)
    rows_frame.columnconfigure(0, weight=1)
    inner = ttk.Frame(rows_frame)
    inner.grid(row=0, column=0)
    inner.columnconfigure(0, weight=1)

    row_widgets: list[tuple[tk.StringVar, tk.StringVar, ttk.Frame]] = []

    def add_row(folder: str = "", exts: str = "") -> None:
        row_f = ttk.Frame(inner)
        row_f.grid(row=len(row_widgets), column=0, sticky="ew", pady=2)
        f_var = tk.StringVar(value=folder)
        e_var = tk.StringVar(value=exts)
        ttk.Entry(row_f, textvariable=f_var, width=18).grid(row=0, column=0)
        ttk.Entry(row_f, textvariable=e_var, width=30).grid(row=0, column=1)
        def remove() -> None:
            for i, (_, _, rf) in enumerate[tuple[StringVar, StringVar, Frame]](row_widgets):
                if rf == row_f:
                    row_widgets.pop(i)
                    row_f.destroy()
                    break
        ttk.Button(row_f, text="✕", width=2, command=remove).grid(row=0, column=2)
        row_widgets.append((f_var, e_var, row_f))

    for folder, exts in (initial_mapping or {}).items():
        add_row(folder, ", ".join(sorted(exts)))
    if not row_widgets:
        add_row()

    ttk.Button(rows_frame, text="+ Добавить папку", command=lambda: add_row()).grid(
        row=1, column=0, pady=(8, 0)
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

    btn_f = ttk.Frame(main)
    btn_f.grid(row=4, column=0)
    ttk.Button(btn_f, text="Отмена", command=on_cancel).pack(side="right")
    ttk.Button(btn_f, text="Сохранить", command=on_ok).pack(side="right")

    dialog.wait_window(dialog)
    return result[0] if result else None
