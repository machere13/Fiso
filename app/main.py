from pathlib import Path

import customtkinter as ctk  # pyright: ignore[reportMissingImports]

from app.core.rules_repository import JsonRulesRepository
from app.core.services import FileOrganizerService
from app.ui.main_window import MainWindow


def main() -> None:
    ctk.set_appearance_mode("System")  # "System", "Dark" или "Light"
    ctk.set_default_color_theme("themes/breeze.json")

    root = ctk.CTk()
    root.title("Fiso")
    root.geometry("640x280")

    rules_repo = JsonRulesRepository(path=Path("rules.json"))
    organizer = FileOrganizerService(rules_repository=rules_repo)

    MainWindow(master=root, organizer=organizer).pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
