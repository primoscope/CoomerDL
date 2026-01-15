"""
Schedule Dialog for managing scheduled downloads.
"""
from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional
from datetime import datetime, timedelta
from downloader.scheduler import (
    DownloadScheduler,
    ScheduledJob,
    ScheduleType,
    ScheduleStatus
)


class ScheduleDialog(ctk.CTkToplevel):
    """Dialog for creating and editing scheduled downloads."""
    
    def __init__(
        self,
        parent,
        tr: Callable[[str], str],
        scheduler: DownloadScheduler,
        job: Optional[ScheduledJob] = None
    ):
        """
        Initialize the schedule dialog.
        
        Args:
            parent: Parent window
            tr: Translation function
            scheduler: Download scheduler instance
            job: Existing job to edit (None for new job)
        """
        super().__init__(parent)
        
        self.tr = tr
        self.scheduler = scheduler
        self.job = job or ScheduledJob()
        self.result: Optional[ScheduledJob] = None
        
        # Window configuration
        self.title(self.tr("Schedule Download" if job is None else "Edit Schedule"))
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.populate_from_job()
    
    def create_widgets(self) -> None:
        """Create all widgets."""
        # Main frame with padding
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        row = 0
        
        # Name
        ctk.CTkLabel(main_frame, text=self.tr("Name:")).grid(
            row=row, column=0, sticky='w', pady=5
        )
        self.name_entry = ctk.CTkEntry(main_frame, width=350)
        self.name_entry.grid(row=row, column=1, pady=5)
        row += 1
        
        # URL
        ctk.CTkLabel(main_frame, text=self.tr("URL:")).grid(
            row=row, column=0, sticky='w', pady=5
        )
        self.url_entry = ctk.CTkEntry(main_frame, width=350)
        self.url_entry.grid(row=row, column=1, pady=5)
        row += 1
        
        # Download Folder
        ctk.CTkLabel(main_frame, text=self.tr("Folder:")).grid(
            row=row, column=0, sticky='w', pady=5
        )
        self.folder_entry = ctk.CTkEntry(main_frame, width=350)
        self.folder_entry.grid(row=row, column=1, pady=5)
        row += 1
        
        # Separator
        ctk.CTkLabel(main_frame, text="").grid(row=row, column=0, pady=10)
        row += 1
        
        # Schedule Type
        ctk.CTkLabel(main_frame, text=self.tr("Schedule Type:")).grid(
            row=row, column=0, sticky='w', pady=5
        )
        self.schedule_type_var = ctk.StringVar(value=ScheduleType.ONCE.value)
        self.schedule_type_menu = ctk.CTkOptionMenu(
            main_frame,
            variable=self.schedule_type_var,
            values=[st.value for st in ScheduleType],
            command=self.on_schedule_type_changed,
            width=350
        )
        self.schedule_type_menu.grid(row=row, column=1, pady=5)
        row += 1
        
        # Once options
        self.once_frame = ctk.CTkFrame(main_frame)
        self.once_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        self.once_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.once_frame, text=self.tr("Date:")).grid(
            row=0, column=0, sticky='w', padx=5, pady=5
        )
        self.once_date_entry = ctk.CTkEntry(self.once_frame, placeholder_text="YYYY-MM-DD")
        self.once_date_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ctk.CTkLabel(self.once_frame, text=self.tr("Time:")).grid(
            row=1, column=0, sticky='w', padx=5, pady=5
        )
        self.once_time_entry = ctk.CTkEntry(self.once_frame, placeholder_text="HH:MM")
        self.once_time_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        row += 1
        
        # Daily options
        self.daily_frame = ctk.CTkFrame(main_frame)
        self.daily_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        self.daily_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.daily_frame, text=self.tr("Time:")).grid(
            row=0, column=0, sticky='w', padx=5, pady=5
        )
        self.daily_time_entry = ctk.CTkEntry(self.daily_frame, placeholder_text="HH:MM")
        self.daily_time_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        row += 1
        
        # Weekly options
        self.weekly_frame = ctk.CTkFrame(main_frame)
        self.weekly_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        self.weekly_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.weekly_frame, text=self.tr("Day:")).grid(
            row=0, column=0, sticky='w', padx=5, pady=5
        )
        self.weekly_day_var = ctk.StringVar(value="Monday")
        self.weekly_day_menu = ctk.CTkOptionMenu(
            self.weekly_frame,
            variable=self.weekly_day_var,
            values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )
        self.weekly_day_menu.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        ctk.CTkLabel(self.weekly_frame, text=self.tr("Time:")).grid(
            row=1, column=0, sticky='w', padx=5, pady=5
        )
        self.weekly_time_entry = ctk.CTkEntry(self.weekly_frame, placeholder_text="HH:MM")
        self.weekly_time_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        row += 1
        
        # Interval options
        self.interval_frame = ctk.CTkFrame(main_frame)
        self.interval_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=5)
        self.interval_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.interval_frame, text=self.tr("Every:")).grid(
            row=0, column=0, sticky='w', padx=5, pady=5
        )
        interval_subframe = ctk.CTkFrame(self.interval_frame)
        interval_subframe.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        interval_subframe.grid_columnconfigure(0, weight=1)
        
        self.interval_entry = ctk.CTkEntry(interval_subframe, width=80)
        self.interval_entry.grid(row=0, column=0, padx=(0, 5))
        self.interval_entry.insert(0, "60")
        
        ctk.CTkLabel(interval_subframe, text=self.tr("minutes")).grid(
            row=0, column=1
        )
        row += 1
        
        # Enabled checkbox
        self.enabled_var = ctk.BooleanVar(value=True)
        self.enabled_checkbox = ctk.CTkCheckBox(
            main_frame,
            text=self.tr("Enabled"),
            variable=self.enabled_var
        )
        self.enabled_checkbox.grid(row=row, column=0, columnspan=2, sticky='w', pady=10)
        row += 1
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text=self.tr("Save"),
            command=self.save,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text=self.tr("Cancel"),
            command=self.cancel,
            width=120
        ).pack(side="left", padx=5)
        
        # Initially show appropriate frame
        self.on_schedule_type_changed(ScheduleType.ONCE.value)
    
    def on_schedule_type_changed(self, value: str) -> None:
        """Handle schedule type change."""
        # Hide all frames
        self.once_frame.grid_remove()
        self.daily_frame.grid_remove()
        self.weekly_frame.grid_remove()
        self.interval_frame.grid_remove()
        
        # Show appropriate frame
        if value == ScheduleType.ONCE.value:
            self.once_frame.grid()
        elif value == ScheduleType.DAILY.value:
            self.daily_frame.grid()
        elif value == ScheduleType.WEEKLY.value:
            self.weekly_frame.grid()
        elif value == ScheduleType.INTERVAL.value:
            self.interval_frame.grid()
    
    def populate_from_job(self) -> None:
        """Populate fields from existing job."""
        if self.job.id is None:
            return
        
        self.name_entry.insert(0, self.job.name)
        self.url_entry.insert(0, self.job.url)
        self.folder_entry.insert(0, self.job.download_folder)
        self.schedule_type_var.set(self.job.schedule_type.value)
        self.enabled_var.set(self.job.enabled)
        
        if self.job.schedule_type == ScheduleType.ONCE and self.job.next_run:
            self.once_date_entry.insert(0, self.job.next_run.strftime("%Y-%m-%d"))
            self.once_time_entry.insert(0, self.job.next_run.strftime("%H:%M"))
        elif self.job.schedule_type == ScheduleType.DAILY and self.job.time_of_day:
            self.daily_time_entry.insert(0, self.job.time_of_day)
        elif self.job.schedule_type == ScheduleType.WEEKLY:
            if self.job.day_of_week is not None:
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                self.weekly_day_var.set(days[self.job.day_of_week])
            if self.job.time_of_day:
                self.weekly_time_entry.insert(0, self.job.time_of_day)
        elif self.job.schedule_type == ScheduleType.INTERVAL:
            self.interval_entry.delete(0, 'end')
            self.interval_entry.insert(0, str(self.job.interval_minutes))
        
        self.on_schedule_type_changed(self.job.schedule_type.value)
    
    def validate(self) -> bool:
        """Validate form inputs."""
        if not self.name_entry.get().strip():
            messagebox.showerror(self.tr("Error"), self.tr("Please enter a name"))
            return False
        
        if not self.url_entry.get().strip():
            messagebox.showerror(self.tr("Error"), self.tr("Please enter a URL"))
            return False
        
        if not self.folder_entry.get().strip():
            messagebox.showerror(self.tr("Error"), self.tr("Please enter a download folder"))
            return False
        
        schedule_type = ScheduleType(self.schedule_type_var.get())
        
        if schedule_type == ScheduleType.ONCE:
            if not self.once_date_entry.get() or not self.once_time_entry.get():
                messagebox.showerror(self.tr("Error"), self.tr("Please enter date and time"))
                return False
            try:
                datetime.strptime(self.once_date_entry.get(), "%Y-%m-%d")
                datetime.strptime(self.once_time_entry.get(), "%H:%M")
            except ValueError:
                messagebox.showerror(self.tr("Error"), self.tr("Invalid date or time format"))
                return False
        
        elif schedule_type == ScheduleType.DAILY:
            if not self.daily_time_entry.get():
                messagebox.showerror(self.tr("Error"), self.tr("Please enter time"))
                return False
            try:
                datetime.strptime(self.daily_time_entry.get(), "%H:%M")
            except ValueError:
                messagebox.showerror(self.tr("Error"), self.tr("Invalid time format"))
                return False
        
        elif schedule_type == ScheduleType.WEEKLY:
            if not self.weekly_time_entry.get():
                messagebox.showerror(self.tr("Error"), self.tr("Please enter time"))
                return False
            try:
                datetime.strptime(self.weekly_time_entry.get(), "%H:%M")
            except ValueError:
                messagebox.showerror(self.tr("Error"), self.tr("Invalid time format"))
                return False
        
        elif schedule_type == ScheduleType.INTERVAL:
            try:
                minutes = int(self.interval_entry.get())
                if minutes <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror(self.tr("Error"), self.tr("Please enter a valid interval in minutes"))
                return False
        
        return True
    
    def save(self) -> None:
        """Save the scheduled job."""
        if not self.validate():
            return
        
        # Build job from form
        self.job.name = self.name_entry.get().strip()
        self.job.url = self.url_entry.get().strip()
        self.job.download_folder = self.folder_entry.get().strip()
        self.job.schedule_type = ScheduleType(self.schedule_type_var.get())
        self.job.enabled = self.enabled_var.get()
        
        if self.job.schedule_type == ScheduleType.ONCE:
            date_str = self.once_date_entry.get()
            time_str = self.once_time_entry.get()
            self.job.next_run = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        
        elif self.job.schedule_type == ScheduleType.DAILY:
            self.job.time_of_day = self.daily_time_entry.get()
        
        elif self.job.schedule_type == ScheduleType.WEEKLY:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            self.job.day_of_week = days.index(self.weekly_day_var.get())
            self.job.time_of_day = self.weekly_time_entry.get()
        
        elif self.job.schedule_type == ScheduleType.INTERVAL:
            self.job.interval_minutes = int(self.interval_entry.get())
        
        # Save to database
        if self.job.id is None:
            self.scheduler.add_job(self.job)
        else:
            self.scheduler.update_job(self.job)
        
        self.result = self.job
        self.grab_release()
        self.destroy()
    
    def cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = None
        self.grab_release()
        self.destroy()
