import customtkinter as ctk
import sqlite3
import sys
import os
from tkinter import messagebox, filedialog
import csv
from datetime import datetime

class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.tr = app.tr

        # Determine DB path
        if hasattr(app, 'default_downloader') and hasattr(app.default_downloader, 'db_path'):
            self.db_path = app.default_downloader.db_path
        else:
            self.db_path = "resources/config/downloads.db"

        self.history_items = []
        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(header, text=self.tr("Download History"), font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        # Controls
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(control_frame, placeholder_text=self.tr("Search history..."))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        self.search_entry.bind("<Return>", lambda e: self.update_display())

        ctk.CTkButton(control_frame, text=self.tr("Search"), width=80, command=self.update_display).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text=self.tr("Export"), width=80, command=self.export_history).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text=self.tr("Clear"), width=80, fg_color="darkred", hover_color="red", command=self.clear_history).pack(side="left", padx=5)

        # Stats
        self.stats_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.stats_label.pack(anchor="w", padx=20, pady=5)

        # List
        self.history_scroll = ctk.CTkScrollableFrame(self, label_text="Recent Downloads")
        self.history_scroll.pack(fill="both", expand=True, padx=20, pady=10)

    def load_history(self):
        self.history_items = []
        if not os.path.exists(self.db_path):
            self.update_display()
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT media_url, file_path, file_size, user_id, post_id, downloaded_at FROM downloads ORDER BY downloaded_at DESC LIMIT 500")
                rows = cursor.fetchall()
                for row in rows:
                    self.history_items.append({
                        'url': row[0],
                        'file_path': row[1],
                        'file_size': row[2] or 0,
                        'user_id': row[3],
                        'post_id': row[4],
                        'date': row[5],
                        'status': "completed" if row[1] and os.path.exists(row[1]) else "deleted"
                    })
        except Exception as e:
            print(f"Error loading history: {e}")
            messagebox.showerror(
                self.tr("Error"),
                self.tr("Failed to load download history. Please try again later.")
            )

        self.update_display()

    def update_display(self):
        # Clear
        for w in self.history_scroll.winfo_children():
            w.destroy()

        search = self.search_entry.get().lower()
        filtered = [
            i for i in self.history_items
            if search in i['url'].lower() or (i['user_id'] and search in i['user_id'].lower())
        ]

        self.stats_label.configure(text=f"Total: {len(self.history_items)} | Showing: {len(filtered)}")

        for item in filtered:
            self.create_item_card(item)

    def create_item_card(self, item):
        card = ctk.CTkFrame(self.history_scroll)
        card.pack(fill="x", pady=2, padx=5)

        color = "green" if item['status'] == "completed" else "red"
        ctk.CTkLabel(card, text="●", text_color=color).pack(side="left", padx=10)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        url_short = (item['url'][:80] + '..') if len(item['url']) > 80 else item['url']
        ctk.CTkLabel(info, text=url_short, font=("Arial", 11), anchor="w").pack(fill="x")

        sz = item['file_size'] / (1024*1024)
        ctk.CTkLabel(info, text=f"{sz:.2f} MB | {item['date']}", font=("Arial", 9), text_color="gray", anchor="w").pack(fill="x")

        if item['status'] == 'completed':
            ctk.CTkButton(card, text="Open", width=60, height=24, command=lambda: self.open_file(item['file_path'])).pack(side="right", padx=10)

    def open_file(self, path):
        import subprocess
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.call(['open', path])
            else:  # Linux and other Unix-like systems
                subprocess.call(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def export_history(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['URL', 'Path', 'Size', 'Date'])
                    for i in self.history_items:
                        writer.writerow([i['url'], i['file_path'], i['file_size'], i['date']])
                messagebox.showinfo("Success", "Exported successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export history: {str(e)}")

    def clear_history(self):
        if messagebox.askyesno("Confirm", "Clear all history?"):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM downloads")
                    conn.commit()
                self.load_history()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Database error: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear history: {str(e)}")
