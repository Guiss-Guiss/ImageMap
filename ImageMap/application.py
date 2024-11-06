import tkinter as tk
from tkinter import simpledialog, font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sys
import threading
import time
import torch
import logging
from PIL import Image, ImageTk
import queue
from file_explorer_dialog import FileExplorerDialog
from load_image import load_image
from calculate_unique_colors import calculate_unique_colors
from extract_color_palette import extract_color_palette
from save_image import save_image
from resize_and_remap_image import resize_and_remap_image
from multilingual_support import language_manager
from redirect import Redirect

logging.basicConfig(level=logging.INFO)

class Application(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH, expand=True)
        self.preview_label = None
        logging.info("Before create_widgets")
        self.create_widgets()
        logging.info(f"After create_widgets, preview_label: {self.preview_label}")
        self.image = None
        self.unique_colors_count = 0
        self.start_time = None
        self.stop_time = False
        self.elapsed_time_thread = None
        self.stop_elapsed_time = threading.Event()
        self.progress_queue = queue.Queue()
        self.create_settings_menu()

    def create_widgets(self):
        large_font = font.Font(family="Arial", size=10)

        self.text_output = tk.Text(self, height=15, width=80, font=large_font)
        self.text_output.pack(pady=10, padx=10)

        sys.stdout = Redirect(self.text_output)

        self.load_button = ttk.Button(self, text=language_manager.translate('load_image'), style='primary.TButton', command=self.load_image)
        self.load_button.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self, length=300, mode='determinate')
        self.progress_bar.pack(pady=10)

        self.time_label = ttk.Label(self, text=language_manager.translate('elapsed_time').format("00:00:00"), font=large_font)
        self.time_label.pack(pady=10)

        logging.info("Creating preview_label")
        self.preview_label = ttk.Label(self)
        self.preview_label.pack(pady=10)
        logging.info(f"preview_label created: {self.preview_label}")

        language_manager.add_observer('main_window', self.update_language)

    def create_settings_menu(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label=language_manager.translate('settings'), menu=settings_menu)

        language_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label=language_manager.translate('language'), menu=language_menu)

        for lang_code, lang_name in language_manager.get_languages().items():
            language_menu.add_command(label=lang_name, command=lambda lc=lang_code: self.change_language(lc))

    def change_language(self, lang_code):
        language_manager.set_language(lang_code)
        self.update_language(lang_code)

    def update_language(self, new_language):
        self.load_button.config(text=language_manager.translate('load_image'))

        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        else:
            elapsed_str = "00:00:00"

        self.time_label.config(text=language_manager.translate('elapsed_time').format(elapsed_str))
        self.master.title(language_manager.translate('starting_app'))
        self.create_settings_menu()

    def load_image(self):
        logging.info("Load image button clicked")
        self.start_time = None
        dialog = FileExplorerDialog(self.master)
        self.master.wait_window(dialog)
        if dialog.result:
            self.prepare_processing(dialog.result)
        else:
            logging.error(language_manager.translate('error_loading'))

    def prepare_processing(self, image_path):
        self.load_button.config(state='disabled')
        self.progress_bar.config(mode='determinate')
        self.progress_bar['value'] = 0
        self.update_progress_callback(0)
        self.start_time = time.time()
        self.stop_elapsed_time.clear()
        self.elapsed_time_thread = threading.Thread(target=self.update_elapsed_time)
        self.elapsed_time_thread.start()

        thread = threading.Thread(target=self.load_image_thread, args=(image_path,))
        thread.start()

    def update_elapsed_time(self):
        while not self.stop_elapsed_time.is_set():
            if self.start_time is not None and not self.stop_time:  # Use self.stop_time
                elapsed_time = time.time() - self.start_time
                elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                new_text = language_manager.translate('elapsed_time').format(elapsed_str)
                self.master.after(0, self.time_label.config, {'text': new_text})
            time.sleep(1)

    def load_image_thread(self, image_path):
        try:
            self.image = load_image(image_path)
            if self.image is None:
                logging.error(language_manager.translate('error_loading'))
                self.master.after(0, self.end_loading, False)
                return
            self.unique_colors_count = calculate_unique_colors(self.image)
            self.master.after(0, self.end_loading, True)
        except Exception as e:
            logging.error(f"{language_manager.translate('error_occurred').format(e)}", exc_info=True)
            self.master.after(0, self.end_loading, False)

    def end_loading(self, success):
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')
        self.load_button.config(state='normal')
        self.stop_elapsed_time.set()
        if self.elapsed_time_thread:
            self.elapsed_time_thread.join()

        if success:
            self.master.after(100, self.ask_parameters)
        else:
            logging.error(language_manager.translate('error_loading'))

    def ask_parameters(self):
        scale = simpledialog.askfloat(language_manager.translate('scale_factor'), language_manager.translate('scale_factor'), parent=self.master)
        if scale is None:
            return

        color_count = simpledialog.askinteger(language_manager.translate('color_palette'), language_manager.translate('color_palette'), parent=self.master)
        if color_count is None:
            return

        self.background_task(scale, color_count)

    def background_task(self, scale, color_count):
        logging.info(f"Starting background task with scale: {scale}, color_count: {color_count}")
        logging.info(f"Entering background_task, preview_label: {self.preview_label}")
        try:
            palette_list = extract_color_palette(self.image.cpu().numpy(), color_count, self.update_progress_callback)
            palette = torch.tensor(palette_list, device=self.image.device, dtype=self.image.dtype)
            
            processed_image = resize_and_remap_image(self.image, scale, palette, 512, self.update_progress_callback)

            # Display preview
            self.display_preview(processed_image)

            dialog = FileExplorerDialog(self.master, image_data=processed_image, mode="save")
            self.master.wait_window(dialog)

            if dialog.result:
                output_path = dialog.result
                save_image(processed_image, output_path)
                logging.info("Background task completed successfully")
                self.stop_time = True
            else:
                logging.info("Background task was cancelled")
                self.stop_time = True
        except Exception as e:
            logging.error(f"{language_manager.translate('error_occurred').format(e)}", exc_info=True)
            self.stop_time = True
        finally:
            self.stop_elapsed_time.set()
            if self.elapsed_time_thread:
                self.elapsed_time_thread.join()

    def update_progress_callback(self, progress):
        self.progress_queue.put(progress)
        if progress == 0:
            self.after(100, self.update_progress)

    def update_progress(self):
        try:
            while True:
                progress = self.progress_queue.get_nowait()
                self.progress_bar['value'] = progress
                self.update_idletasks()
        except queue.Empty:
            self.after(100, self.update_progress)

    def display_preview(self, processed_image):
        logging.info(f"Entering display_preview, preview_label: {self.preview_label}")
        logging.info("Entering display_preview method")
        logging.info(f"Processed image type: {type(processed_image)}")
        logging.info(f"Processed image shape: {processed_image.shape if hasattr(processed_image, 'shape') else 'No shape attribute'}")
        logging.info(language_manager.translate('image_preview'))

        if isinstance(processed_image, torch.Tensor):
            processed_image = processed_image.cpu().numpy()

        if processed_image.dtype != 'uint8':
            processed_image = (processed_image * 255).astype('uint8')

        logging.info("Converting tensor to PIL Image")
        pil_image = Image.fromarray(processed_image)
        logging.info(f"PIL Image created. Size: {pil_image.size}")

        # Resize for preview (adjust size as needed)
        pil_image.thumbnail((300, 300))

        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(pil_image)

        # Update preview label
        logging.info("Updating preview label")
        logging.info(f"self.preview_label: {self.preview_label}")
        self.preview_label.config(image=photo)
        self.preview_label.image = photo
        logging.info("Exiting display_preview method")