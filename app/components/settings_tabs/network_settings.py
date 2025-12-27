"""
Network Settings Tab for Settings Window.
"""
import customtkinter as ctk


class NetworkSettingsTab:
    """UI component for advanced network settings."""
    
    def __init__(self, parent_frame, translate, settings):
        """
        Initialize the network settings tab.
        
        Args:
            parent_frame: Parent CTk frame.
            translate: Translation function.
            settings: Settings dictionary.
        """
        self.parent = parent_frame
        self.translate = translate
        self.settings = settings
        
        # Initialize network settings if not present
        if 'network' not in self.settings:
            self.settings['network'] = {
                'per_domain_concurrent': 3,
                'global_concurrent': 5,
                'delay_between_requests': 500,
                'max_retries': 5,
                'base_delay': 2.0,
                'max_delay_cap': 60,
                'use_exponential_backoff': True,
                'proxy_type': 'none',
                'proxy_url': '',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        
        self.render()
    
    def render(self):
        """Render the network settings UI."""
        # Main container with scrollbar
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            self.parent,
            text=self.translate("Network Settings"),
            font=("Helvetica", 16, "bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Rate limiting section
        rate_frame = ctk.CTkFrame(self.parent)
        rate_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        rate_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            rate_frame,
            text=self.translate("Rate Limiting:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        
        # Per-domain concurrent downloads
        ctk.CTkLabel(
            rate_frame,
            text=self.translate("Per-domain concurrent downloads:"),
            anchor="w"
        ).grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        self.per_domain_var = ctk.IntVar(
            value=self.settings['network'].get('per_domain_concurrent', 3)
        )
        ctk.CTkEntry(
            rate_frame,
            textvariable=self.per_domain_var,
            width=80
        ).grid(row=1, column=1, sticky="w", padx=15, pady=5)
        
        # Global concurrent downloads
        ctk.CTkLabel(
            rate_frame,
            text=self.translate("Global concurrent downloads:"),
            anchor="w"
        ).grid(row=2, column=0, sticky="w", padx=15, pady=5)
        
        self.global_concurrent_var = ctk.IntVar(
            value=self.settings['network'].get('global_concurrent', 5)
        )
        ctk.CTkEntry(
            rate_frame,
            textvariable=self.global_concurrent_var,
            width=80
        ).grid(row=2, column=1, sticky="w", padx=15, pady=5)
        
        # Delay between requests
        ctk.CTkLabel(
            rate_frame,
            text=self.translate("Delay between requests (ms):"),
            anchor="w"
        ).grid(row=3, column=0, sticky="w", padx=15, pady=(5, 15))
        
        self.delay_var = ctk.IntVar(
            value=self.settings['network'].get('delay_between_requests', 500)
        )
        ctk.CTkEntry(
            rate_frame,
            textvariable=self.delay_var,
            width=80
        ).grid(row=3, column=1, sticky="w", padx=15, pady=(5, 15))
        
        # Retry policy section
        retry_frame = ctk.CTkFrame(self.parent)
        retry_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        retry_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            retry_frame,
            text=self.translate("Retry Policy:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        
        # Max retries
        ctk.CTkLabel(
            retry_frame,
            text=self.translate("Max retries:"),
            anchor="w"
        ).grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        self.max_retries_var = ctk.IntVar(
            value=self.settings['network'].get('max_retries', 5)
        )
        ctk.CTkEntry(
            retry_frame,
            textvariable=self.max_retries_var,
            width=80
        ).grid(row=1, column=1, sticky="w", padx=15, pady=5)
        
        # Base delay
        ctk.CTkLabel(
            retry_frame,
            text=self.translate("Base delay (seconds):"),
            anchor="w"
        ).grid(row=2, column=0, sticky="w", padx=15, pady=5)
        
        self.base_delay_var = ctk.DoubleVar(
            value=self.settings['network'].get('base_delay', 2.0)
        )
        ctk.CTkEntry(
            retry_frame,
            textvariable=self.base_delay_var,
            width=80
        ).grid(row=2, column=1, sticky="w", padx=15, pady=5)
        
        # Max delay cap
        ctk.CTkLabel(
            retry_frame,
            text=self.translate("Max delay cap (seconds):"),
            anchor="w"
        ).grid(row=3, column=0, sticky="w", padx=15, pady=5)
        
        self.max_delay_var = ctk.IntVar(
            value=self.settings['network'].get('max_delay_cap', 60)
        )
        ctk.CTkEntry(
            retry_frame,
            textvariable=self.max_delay_var,
            width=80
        ).grid(row=3, column=1, sticky="w", padx=15, pady=5)
        
        # Exponential backoff
        self.backoff_var = ctk.BooleanVar(
            value=self.settings['network'].get('use_exponential_backoff', True)
        )
        ctk.CTkCheckBox(
            retry_frame,
            text=self.translate("Use exponential backoff with jitter"),
            variable=self.backoff_var
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=15, pady=(5, 15))
        
        # Proxy configuration section
        proxy_frame = ctk.CTkFrame(self.parent)
        proxy_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        proxy_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            proxy_frame,
            text=self.translate("Proxy Configuration:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        
        self.proxy_type_var = ctk.StringVar(
            value=self.settings['network'].get('proxy_type', 'none')
        )
        
        ctk.CTkRadioButton(
            proxy_frame,
            text=self.translate("No proxy"),
            variable=self.proxy_type_var,
            value="none"
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=2)
        
        ctk.CTkRadioButton(
            proxy_frame,
            text=self.translate("System proxy"),
            variable=self.proxy_type_var,
            value="system"
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=15, pady=2)
        
        custom_proxy_frame = ctk.CTkFrame(proxy_frame, fg_color="transparent")
        custom_proxy_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=15, pady=2)
        custom_proxy_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkRadioButton(
            custom_proxy_frame,
            text=self.translate("Custom:"),
            variable=self.proxy_type_var,
            value="custom"
        ).grid(row=0, column=0, sticky="w")
        
        self.proxy_url_var = ctk.StringVar(
            value=self.settings['network'].get('proxy_url', '')
        )
        ctk.CTkEntry(
            custom_proxy_frame,
            textvariable=self.proxy_url_var,
            placeholder_text="http://proxy.example.com:8080"
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # User agent section
        ua_frame = ctk.CTkFrame(self.parent)
        ua_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))
        ua_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            ua_frame,
            text=self.translate("User Agent:"),
            font=("Helvetica", 12, "bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.user_agent_var = ctk.StringVar(
            value=self.settings['network'].get('user_agent', default_ua)
        )
        
        ua_menu = ctk.CTkOptionMenu(
            ua_frame,
            values=[
                "Chrome (Windows)",
                "Firefox (Windows)",
                "Safari (macOS)",
                "Edge (Windows)",
                "Custom..."
            ],
            command=self._on_ua_changed
        )
        ua_menu.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 5))
        
        self.ua_entry = ctk.CTkEntry(
            ua_frame,
            textvariable=self.user_agent_var
        )
        self.ua_entry.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
    
    def _on_ua_changed(self, choice):
        """Handle user agent selection change."""
        user_agents = {
            "Chrome (Windows)": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Firefox (Windows)": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Safari (macOS)": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Edge (Windows)": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        }
        
        if choice in user_agents:
            self.user_agent_var.set(user_agents[choice])
    
    def get_settings(self):
        """Get the current settings values."""
        return {
            'per_domain_concurrent': self.per_domain_var.get(),
            'global_concurrent': self.global_concurrent_var.get(),
            'delay_between_requests': self.delay_var.get(),
            'max_retries': self.max_retries_var.get(),
            'base_delay': self.base_delay_var.get(),
            'max_delay_cap': self.max_delay_var.get(),
            'use_exponential_backoff': self.backoff_var.get(),
            'proxy_type': self.proxy_type_var.get(),
            'proxy_url': self.proxy_url_var.get(),
            'user_agent': self.user_agent_var.get(),
        }
