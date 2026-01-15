from __future__ import annotations

import customtkinter as ctk

class HelpPage(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.tr = app.tr

        self.create_widgets()

    def create_widgets(self):
        # Header
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text=self.tr("Help & User Guide"), font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        # Tab View
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_quick_start_tab()
        self.create_supported_sites_tab()
        self.create_troubleshooting_tab()
        self.create_about_tab()

    def create_quick_start_tab(self):
        tab = self.tabview.add(self.tr("Quick Start"))

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        content = [
            ("How to Download", 20),
            ("1. Go to the 'Home' tab.", 14),
            ("2. Paste one or more URLs into the text box. You can paste multiple URLs, one per line.", 12),
            ("3. Select a Download Folder.", 12),
            ("4. Click the 'Download' button.", 12),
            ("\nAdvanced Features", 20),
            ("- Enable 'Advanced Settings' in the Settings tab to see more options.", 12),
            ("- Use the 'Queue' tab to manage active downloads.", 12),
            ("- Use the 'Converter' tab to convert media files.", 12),
            ("\nPro Tips", 16),
            ("• Batch Downloads: Paste 100+ URLs at once!", 12),
            ("• Queue: You can pause/resume downloads in the queue.", 12),
            ("• History: Search your download history to find files quickly.", 12),
        ]

        for text, size in content:
            font = ctk.CTkFont(size=size, weight="bold" if size > 14 else "normal")
            ctk.CTkLabel(scroll, text=self.tr(text), font=font, anchor="w", wraplength=800).pack(fill="x", pady=5)

    def create_supported_sites_tab(self):
        tab = self.tabview.add(self.tr("Supported Sites"))

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        content = """
        CoomerDL supports 1000+ websites via yt-dlp and specialized scrapers.

        Native Scrapers (Fastest):
        • Coomer.su
        • Kemono.su
        • Erome.com
        • Bunkr-albums.io
        • SimpCity.su
        • Jpg5.su

        Video Sites (via yt-dlp):
        • YouTube, Vimeo, Dailymotion
        • Twitter/X, Reddit, TikTok, Instagram, Facebook
        • Twitch, Patreon

        Image Galleries (via gallery-dl):
        • DeviantArt, Pixiv, ArtStation
        • Tumblr, Pinterest
        """

        ctk.CTkLabel(scroll, text=content, font=("Courier", 12), justify="left", anchor="nw").pack(fill="both", expand=True, padx=20, pady=20)

    def create_troubleshooting_tab(self):
        tab = self.tabview.add(self.tr("Troubleshooting"))

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        items = [
            ("Downloads fail with 403/429 errors",
             "• 403 Forbidden: Use 'Settings -> Universal -> Cookies' to import browser cookies.\n• 429 Too Many Requests: Rate limited. Reduce 'Simultaneous Downloads' in Settings."),
            ("YouTube downloads fail",
             "• Ensure yt-dlp is updated.\n• Check your internet connection."),
            ("App won't start",
             "• Check Python version (3.8+ required).\n• Reinstall dependencies: pip install -r requirements.txt"),
        ]

        for title, desc in items:
            ctk.CTkLabel(scroll, text=title, font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x", pady=(15, 5))
            ctk.CTkLabel(scroll, text=desc, font=ctk.CTkFont(size=12), anchor="w", justify="left").pack(fill="x", padx=10)

    def create_about_tab(self):
        tab = self.tabview.add(self.tr("About"))

        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="CoomerDL", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=10)
        ctk.CTkLabel(frame, text="Universal Media Archiver", font=ctk.CTkFont(size=16)).pack(pady=5)
        ctk.CTkLabel(frame, text="Version: 2.0.0 (UI Overhaul)", text_color="gray").pack(pady=20)

        ctk.CTkButton(frame, text="Visit GitHub", command=lambda: self.open_url("https://github.com/primoscope/CoomerDL")).pack(pady=10)

    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)
