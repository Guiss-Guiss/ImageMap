import tkinter as tk

class Redirect:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.after(0, self._write, text)

    def _write(self, text):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)
        self.widget.update_idletasks()

    def flush(self):
        pass