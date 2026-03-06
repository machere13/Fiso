from pathlib import Path

import tkinter as tk

from app.core.rules_repository import JsonRulesRepository
from app.core.services import FileOrganizerService
from app.ui.main_window import MainWindow


def main() -> None:
    root = tk.Tk()
    root.title("Fiso")
    root.geometry("600x200")

    rules_repo = JsonRulesRepository(path=Path("rules.json"))
    organizer = FileOrganizerService(rules_repository=rules_repo)

    MainWindow(master=root, organizer=organizer).pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
