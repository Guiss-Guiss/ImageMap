import tkinter as tk
from tkinter import messagebox
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
import os
from datetime import datetime
from save_image import save_image
from multilingual_support import language_manager

class FileExplorerDialog(tk.Toplevel):
    def __init__(self, parent, image_data=None, mode="load"):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        self.mode = mode
        self.image_data = image_data
        self.title(language_manager.translate('select_image') if mode == "load" else language_manager.translate('save_image_as'))
        self.geometry("800x600")
        self.current_path = os.path.expanduser("~")
        self.create_widgets()
        self.populate_tree(self.current_path)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.close)

    def create_widgets(self):
        self.toolbar = ttk.Frame(self)
        self.back_button = ttk.Button(self.toolbar, text=language_manager.translate('back'), style='info.TButton', command=self.go_back)
        self.up_button = ttk.Button(self.toolbar, text=language_manager.translate('parent_folder'), style='info.TButton', command=self.go_up)
        self.back_button.pack(side=LEFT, padx=2)
        self.up_button.pack(side=LEFT, padx=2)

        if self.mode == "save":
            self.filename_entry = ttk.Entry(self.toolbar)
            self.filename_entry.pack(side=LEFT, expand=True, fill=X, padx=2)

        self.action_button = ttk.Button(self.toolbar, text=language_manager.translate('load_image') if self.mode == "load" else language_manager.translate('save_image'),
                                        style='info.TButton', command=self.main_action)
        self.action_button.pack(side=LEFT, padx=2)

        self.toolbar.pack(side=TOP, fill=X, pady=5)

        self.tree = ttk.Treeview(self, columns=("name", "size", "type", "modified"), show="headings")
        self.tree.heading("name", text=language_manager.translate('name'))
        self.tree.heading("size", text=language_manager.translate('size'))
        self.tree.heading("type", text=language_manager.translate('type'))
        self.tree.heading("modified", text=language_manager.translate('date_modified'))
        self.tree.column("name", width=200)
        self.tree.column("size", width=100)
        self.tree.column("type", width=100)
        self.tree.column("modified", width=150)
        self.tree.pack(expand=True, fill=BOTH)

        self.tree.bind("<Double-1>", self.on_double_click)

    def populate_tree(self, path):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            items = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.exists(full_path):
                    stats = os.stat(full_path)
                    file_type = language_manager.translate('file') if os.path.isfile(full_path) else language_manager.translate('folder')
                    modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    size = f"{stats.st_size / 1024:.2f} {language_manager.translate('kb')}"
                    items.append((item, size, file_type, modified))

            items.sort(key=lambda x: x[0].lower())

            for item in items:
                self.tree.insert("", "end", values=item)
        except PermissionError:
            messagebox.showerror(language_manager.translate('error_occurred'), language_manager.translate('access_denied'), parent=self)
        except Exception as e:
            messagebox.showerror(language_manager.translate('error_occurred'), str(e), parent=self)

    def on_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            file_name = self.tree.item(item, "values")[0]
            file_path = os.path.join(self.current_path, file_name)
            if os.path.isfile(file_path) and self.mode == "load":
                self.result = file_path
                self.close()
            elif os.path.isdir(file_path):
                self.current_path = file_path
                self.populate_tree(self.current_path)

    def go_back(self):
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.current_path = parent
            self.populate_tree(self.current_path)

    def go_up(self):
        self.go_back()

    def main_action(self):
        if self.mode == "load":
            self.select_file()
        else:
            self.save_file()

    def save_file(self):
        file_name = self.filename_entry.get()
        if not file_name:
            messagebox.showerror(language_manager.translate('error_occurred'), language_manager.translate('enter_filename'), parent=self)
            return

        full_path = os.path.join(self.current_path, file_name + ".png")
        try:
            save_image(self.image_data, full_path)
            messagebox.showinfo(language_manager.translate('save_image'), language_manager.translate('image_saved_successfully'), parent=self)
            self.result = full_path
            self.close()
        except Exception as e:
            messagebox.showerror(language_manager.translate('error_occurred'), str(e), parent=self)

    def select_file(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            file_name = self.tree.item(item, "values")[0]
            file_path = os.path.join(self.current_path, file_name)
            if os.path.isfile(file_path):
                self.result = file_path
                self.close()
            else:
                messagebox.showinfo(language_manager.translate('error_occurred'), language_manager.translate('select_file'), parent=self)
        else:
            messagebox.showinfo(language_manager.translate('error_occurred'), language_manager.translate('select_file'), parent=self)

    def close(self):
        self.parent.focus_set()
        self.destroy()