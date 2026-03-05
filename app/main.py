import tkinter as tk

from app.ui.main_window import MainWindow

def main() -> None:
    root = tk.Tk()
    root.title("Fiso")
    root.geometry("600x200")
    MainWindow(master=root).pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
