import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import logging
import os
from app.utils.converter import MediaConverter

class ConverterPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.tr = app.tr
        self.converter = MediaConverter()
        self.converting = False
        self.conversion_thread = None  # Track conversion thread for proper cleanup

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text=self.tr("Media Converter (FFmpeg)"), font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        # Main Container
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Input File
        ctk.CTkLabel(main, text="Input File:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        input_frame = ctk.CTkFrame(main, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)

        self.input_entry = ctk.CTkEntry(input_frame)
        self.input_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(input_frame, text="File", width=80, command=self.browse_input).pack(side="left", padx=(5,0))
        ctk.CTkButton(input_frame, text="Folder", width=80, command=self.browse_folder).pack(side="left", padx=(5,0))

        # Info Box
        info_label = ctk.CTkLabel(main, text="Supports conversion between common formats using FFmpeg.\nSelect 'Custom FFmpeg Args' in Advanced Mode for more control.", font=("Arial", 11), text_color="gray", justify="left")
        info_label.pack(anchor="w", padx=20, pady=(0, 10))

        # Output Format
        ctk.CTkLabel(main, text="Output Settings:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        opts_frame = ctk.CTkFrame(main)
        opts_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(opts_frame, text="Format:").grid(row=0, column=0, padx=10, pady=10)
        self.format_combo = ctk.CTkComboBox(opts_frame, values=["mp4", "mkv", "webm", "avi", "mp3", "wav", "m4a", "gif"])
        self.format_combo.grid(row=0, column=1, padx=10, pady=10)
        self.format_combo.set("mp4")

        # Advanced Args (Conditional)
        self.adv_label = ctk.CTkLabel(opts_frame, text="Custom FFmpeg Args:")
        self.adv_entry = ctk.CTkEntry(opts_frame, width=300, placeholder_text="-vcodec libx264 -crf 23")

        # Check advanced mode
        self.refresh_advanced_visibility()

        # Progress
        self.progress_bar = ctk.CTkProgressBar(main)
        self.progress_bar.pack(fill="x", padx=20, pady=(40, 5))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(main, text="Ready", text_color="gray")
        self.status_label.pack(anchor="w", padx=20, pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.convert_btn = ctk.CTkButton(btn_frame, text="Start Conversion", command=self.start_conversion, font=("Arial", 14, "bold"))
        self.convert_btn.pack(side="left", padx=10)

        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="red", hover_color="darkred", command=self.cancel_conversion, state="disabled")
        self.cancel_btn.pack(side="left", padx=10)

    def refresh_advanced_visibility(self):
        if self.app.advanced_mode:
            self.adv_label.grid(row=1, column=0, padx=10, pady=10)
            self.adv_entry.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky="ew")
        else:
            self.adv_label.grid_forget()
            self.adv_entry.grid_forget()

    def browse_input(self):
        f = filedialog.askopenfilename()
        if f:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, f)

    def browse_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, d)

    def start_conversion(self):
        input_path = self.input_entry.get().strip()
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Invalid input file or folder.")
            return

        fmt = self.format_combo.get()
        args = self.adv_entry.get().strip() if self.app.advanced_mode else ""
        options = {"args": args}

        files_to_convert = []
        if os.path.isdir(input_path):
            # Batch mode
            valid_exts = {'.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv', '.wmv', '.m4v', '.mp3', '.wav', '.m4a'}
            for f in os.listdir(input_path):
                if os.path.splitext(f)[1].lower() in valid_exts:
                    full_path = os.path.join(input_path, f)
                    base, _ = os.path.splitext(full_path)
                    output_path = f"{base}_converted.{fmt}"
                    
                    # Check for existing output file to avoid silent overwrite
                    if os.path.exists(output_path):
                        overwrite = messagebox.askyesno(
                            "Confirm overwrite",
                            f"The output file already exists:\n\n{output_path}\n\nDo you want to overwrite it?"
                        )
                        if not overwrite:
                            continue
                    
                    files_to_convert.append((full_path, output_path))
        else:
            # Single file
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}_converted.{fmt}"
            
            # Check for existing output file to avoid silent overwrite
            if os.path.exists(output_path):
                overwrite = messagebox.askyesno(
                    "Confirm overwrite",
                    f"The output file already exists:\n\n{output_path}\n\nDo you want to overwrite it?"
                )
                if not overwrite:
                    return
            
            files_to_convert.append((input_path, output_path))

        if not files_to_convert:
            messagebox.showinfo("Info", "No valid media files found to convert.")
            return

        self.converting = True
        self.convert_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.status_label.configure(text=f"Starting batch ({len(files_to_convert)} files)...")

        # Run in thread and track it
        self.conversion_thread = threading.Thread(
            target=self.run_batch_conversion, 
            args=(files_to_convert, options),
            daemon=True
        )
        self.conversion_thread.start()

    def run_batch_conversion(self, file_list, options):
        total = len(file_list)
        success_count = 0

        for i, (input_path, output_path) in enumerate(file_list):
            if not self.converting: break

            def update(p, msg):
                # Calculate global progress
                global_p = (i + p) / total
                self.app.after(0, lambda: self.update_ui(global_p, f"File {i+1}/{total}: {msg}"))

            try:
                if self.converter.convert(input_path, output_path, options, update):
                    success_count += 1
            except Exception as e:
                logging.error(f"Error converting {input_path}: {e}")

        self.app.after(0, lambda: self.finish_conversion(success_count == total))

    def update_ui(self, p, msg):
        self.progress_bar.set(p)
        self.status_label.configure(text=msg)

    def finish_conversion(self, success):
        self.converting = False
        self.convert_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        if success:
            messagebox.showinfo("Success", "Conversion finished successfully!")
            self.status_label.configure(text="Finished.")

    def cancel_conversion(self):
        if self.converting:
            self.converter.cancel()
