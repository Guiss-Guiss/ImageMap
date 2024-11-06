import tkinter as tk
from ttkbootstrap import Style
import sys
import os
from application import Application
from multilingual_support import language_manager

def main():
    print(language_manager.translate('starting_app'))
    print(language_manager.translate('python_version').format(sys.version))
    print(language_manager.translate('current_directory').format(os.getcwd()))
    print(language_manager.translate('default_language').format(language_manager.get_current_language()))

    root = tk.Tk()
    style = Style(theme='darkly')
    root.title(language_manager.translate('starting_app'))
    root.geometry("800x700")

    # Center the window on the screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    app = Application(root)
    root.mainloop()

if __name__ == "__main__":
    main()