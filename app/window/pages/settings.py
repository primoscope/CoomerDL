from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.tr = app.tr
        self.settings_helper = app.settings_helper

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(header, text=self.tr("Settings"), font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        # Advanced Mode Toggle
        self.adv_var = ctk.BooleanVar(value=self.app.advanced_mode)
        self.adv_switch = ctk.CTkSwitch(
            header,
            text=self.tr("Enable Advanced Settings"),
            variable=self.adv_var,
            command=self.toggle_advanced_mode
        )
        self.adv_switch.pack(side="right")

        # Tab View
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # Create Tabs
        self.tabs = {}
        self.tab_names = [
            ("General", self.settings_helper.render_general_tab, False),
            ("Downloads", self.settings_helper.render_downloads_tab, False),
            ("Structure", self.settings_helper.render_structure_tab, False),
            ("Universal", self.settings_helper.render_universal_tab, False),
            ("Database", self.settings_helper.render_db_tab, False),
            ("Cookies", self.settings_helper.render_cookies_tab, True),
            ("Scraper", self.settings_helper.render_scraper_tab, True),
            ("Network", self.settings_helper.render_network_tab, True),
            ("Filters", self.settings_helper.render_filters_tab, True),
            ("Logging", self.settings_helper.render_logging_tab, True)
        ]

        self.refresh_tabs()

    def refresh_tabs(self):
        """
        Refresh pattern:
        Determine which tabs should be visible for the current mode (basic/advanced),
        then reconcile that with the tabs that actually exist in the CTkTabview by
        deleting tabs that should no longer be shown and creating any missing ones.
        CTkTabview does not expose a simple "show/hide" API, so we manage tabs by
        adding/removing them. This may re-render content when a tab is recreated,
        but it keeps the UI state consistent and avoids hidden tabs with stale content.
        """

        should_show = []
        for name, render_func, is_advanced in self.tab_names:
            if not is_advanced or self.app.advanced_mode:
                should_show.append(name)

        # Remove tabs not needed
        current_tabs = list(self.tabs.keys())
        for name in current_tabs:
            if name not in should_show:
                self.tabview.delete(name)
                del self.tabs[name]

        # Add tabs needed
        for name, render_func, is_advanced in self.tab_names:
            if (not is_advanced or self.app.advanced_mode) and name not in self.tabs:
                tab = self.tabview.add(name)
                self.tabs[name] = tab
                # Render content
                try:
                    render_func(tab)
                except Exception as e:
                    ctk.CTkLabel(tab, text=f"Error loading tab: {e}").pack()

    def toggle_advanced_mode(self):
        self.app.advanced_mode = self.adv_var.get()
        self.app.settings['advanced_mode'] = self.app.advanced_mode
        self.settings_helper.save_settings()

        self.refresh_tabs()

        # Notify other pages that depend on advanced_mode (e.g. Home Page expander visibility).
        # Prefer a generic event-style callback if the app exposes one, and fall back to any
        # existing UI refresh method to preserve current behavior.
        if hasattr(self.app, "on_settings_changed"):
            try:
                self.app.on_settings_changed("advanced_mode")
            except TypeError:
                # Support a no-argument variant if that's how on_settings_changed is defined.
                self.app.on_settings_changed()
        elif hasattr(self.app, "update_ui_texts"):
            self.app.update_ui_texts()
